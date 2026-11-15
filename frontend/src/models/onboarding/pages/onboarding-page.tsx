import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { splitAccountType, getHomePath } from "@/models/auth/account-type/capabilities";
import { useAuthSlice } from "@/models/auth/slice";
import { useGetMySkillsQuery } from "@/models/marketplace-offers/api";
import { useMySpace } from "@/models/marketplace-space/hooks/use-my-space";
import { AccountTypeStep } from "../components/account-type-step";
import { CompanyStep } from "../components/company-step";
import { DevProfilStep } from "../components/dev-profil-step";
import { DevSkillsStep } from "../components/dev-skills-step";
import { OnboardingShell } from "../components/onboarding-shell";
import { SummaryStep } from "../components/summary-step";
import { buildCompletionItems } from "../completion";

type Kind = "dev" | "entreprise";
type DevStage = "profil" | "skills" | "done";

const skippedKey = (userId: number) => `onboarding.skipped.v1.${userId}`;

/** Étapes reportées, mémorisées pour la durée de l'onglet sous la forme « dev,entreprise ». */
function readSkipped(userId: number): Kind[] {
  let raw: string | null = null;
  try {
    raw = window.sessionStorage.getItem(skippedKey(userId));
  } catch (error) {
    console.warn("Étapes reportées illisibles (stockage bloqué), l'assistant repart de zéro", error);
  }
  return (raw ?? "")
    .split(",")
    .filter((item): item is Kind => item === "dev" || item === "entreprise");
}

function writeSkipped(userId: number, skipped: Kind[]) {
  try {
    window.sessionStorage.setItem(skippedKey(userId), skipped.join(","));
  } catch (error) {
    console.warn("Étapes reportées non mémorisées (stockage bloqué)", error);
  }
}

/**
 * Assistant d'onboarding : choix du type de compte, création guidée du profil dev et/ou de l'entreprise,
 * puis récapitulatif. L'étape courante est déduite de l'état du compte (type enregistré, profils existants) :
 * un rafraîchissement ramène donc à l'étape en cours.
 * `?add=dev|entreprise` ajoute le type manquant ; `?resume=1` rouvre les étapes reportées.
 */
export default function OnboardingPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const user = useAuthSlice((state) => state.user);
  const userId = user?.id ?? null;
  const { profil, company, hasProfil, isRecruiter, isLoading, isError, refetch } = useMySpace();
  const { data: mySkills = [] } = useGetMySkillsQuery(undefined, { skip: !hasProfil });

  const addParam = searchParams.get("add");
  const addType: Kind | undefined =
    addParam === "dev" || addParam === "entreprise" ? addParam : undefined;
  const resume = searchParams.get("resume") === "1";

  const [skipped, setSkipped] = useState<Kind[]>(() =>
    userId == null || resume ? [] : readSkipped(userId)
  );
  const [devStage, setDevStage] = useState<DevStage>("profil");
  const [companyDone, setCompanyDone] = useState(false);

  useEffect(() => {
    if (userId != null && resume) writeSkipped(userId, []);
  }, [userId, resume]);

  const skip = (kind: Kind) => {
    setSkipped((current) => {
      const next = current.includes(kind) ? current : [...current, kind];
      if (userId != null) writeSkipped(userId, next);
      return next;
    });
  };

  const types = useMemo(() => splitAccountType(user?.account_type), [user?.account_type]);
  const wantsDev = types.includes("dev");
  const wantsEntreprise = types.includes("entreprise");

  if (!user) return null;

  const needsTypeStep = types.length === 0 || (addType !== undefined && !types.includes(addType));

  if (needsTypeStep) {
    return (
      <AccountTypeStep
        onlyType={addType}
        onDone={() => {
          // Le nouveau type est dans la session : l'étape suivante se déduit du compte
          setDevStage("profil");
          setCompanyDone(false);
        }}
      />
    );
  }

  if (isLoading) {
    return (
      <OnboardingShell title="Chargement de votre espace…">
        <Skeleton className="h-32 w-full" />
      </OnboardingShell>
    );
  }

  if (isError) {
    return (
      <OnboardingShell
        title="Impossible de charger votre espace"
        description="Vérifiez votre connexion, puis réessayez."
      >
        <Button type="button" onClick={() => void refetch()}>
          Réessayer
        </Button>
      </OnboardingShell>
    );
  }

  const devSkipped = skipped.includes("dev");
  const entrepriseSkipped = skipped.includes("entreprise");

  const devNeeded =
    wantsDev && !devSkipped && (devStage === "skills" || (devStage === "profil" && !hasProfil));
  const entrepriseNeeded = wantsEntreprise && !entrepriseSkipped && !isRecruiter && !companyDone;

  const devCount = wantsDev && !devSkipped ? 2 : 0;
  const entrepriseCount = wantsEntreprise && !entrepriseSkipped ? 1 : 0;
  const stepCount = devCount + entrepriseCount;

  if (devNeeded && devStage === "profil") {
    return (
      <DevProfilStep
        stepIndex={0}
        stepCount={stepCount}
        onDone={() => setDevStage("skills")}
        onSkip={() => skip("dev")}
      />
    );
  }

  if (devNeeded && devStage === "skills") {
    return (
      <DevSkillsStep
        stepIndex={1}
        stepCount={stepCount}
        onDone={() => setDevStage("done")}
      />
    );
  }

  if (entrepriseNeeded) {
    return (
      <CompanyStep
        stepIndex={devCount}
        stepCount={stepCount}
        onDone={() => setCompanyDone(true)}
        onSkip={() => skip("entreprise")}
      />
    );
  }

  const items = buildCompletionItems({
    wantsDev,
    wantsEntreprise,
    profil,
    company,
    skillsCount: mySkills.length,
  });

  return (
    <SummaryStep
      items={items}
      onFinish={() => navigate(getHomePath(user), { replace: true })}
    />
  );
}
