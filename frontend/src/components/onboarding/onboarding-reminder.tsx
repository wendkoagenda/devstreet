import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useAccountType } from "@/models/auth/account-type/use-account-type";
import { useMySpace } from "@/models/marketplace-space/hooks/use-my-space";

/**
 * Rappel affiché tant que le membre a choisi un type de compte mais n'a pas créé le profil
 * ou l'entreprise correspondant (création reportée avec « Terminer plus tard »).
 */
export function OnboardingReminder() {
  const { isAdmin, hasDevType, hasEntrepriseType, onboardingRequired } = useAccountType();
  const { hasProfil, isRecruiter, isLoading, isError } = useMySpace();

  if (isAdmin || onboardingRequired || isLoading || isError) return null;

  const missing: string[] = [];
  if (hasDevType && !hasProfil) missing.push("votre profil dev");
  if (hasEntrepriseType && !isRecruiter) missing.push("votre entreprise");
  if (missing.length === 0) return null;

  return (
    <div
      role="status"
      className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-brand-soft-border bg-brand-soft px-4 py-3 text-sm"
    >
      <p className="text-foreground">
        Terminez la création de {missing.join(" et ")} pour profiter pleinement de DevStreet.
      </p>
      <Button asChild size="sm">
        <Link to="/onboarding?resume=1">Terminer</Link>
      </Button>
    </div>
  );
}
