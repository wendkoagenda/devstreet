import { useState } from "react";
import { Code2, Building2, Layers, type LucideIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { CreationErrorSonner } from "@/helpers/api/feed-backs";
import { useAuthSlice } from "@/models/auth/slice";
import { useSetAccountTypeMutation, type ChoosableAccountType } from "../api";
import { ACCOUNT_TYPE_OPTIONS } from "../schema";
import { OnboardingShell } from "./onboarding-shell";

const ICONS: Record<ChoosableAccountType, LucideIcon> = {
  dev: Code2,
  entreprise: Building2,
  both: Layers,
};

/**
 * Choix du type de compte. En mode « ajout » (le membre a déjà un type), seul le type manquant est proposé
 * et le choix est une simple confirmation.
 */
export function AccountTypeStep({
  onlyType,
  onDone,
}: {
  /** Type manquant à ajouter ; absent = premier choix (les trois options). */
  onlyType?: "dev" | "entreprise";
  onDone: () => void;
}) {
  const loadSession = useAuthSlice((state) => state.loadSession);
  const [setAccountType, { isLoading }] = useSetAccountTypeMutation();
  const options = onlyType
    ? ACCOUNT_TYPE_OPTIONS.filter((option) => option.value === onlyType)
    : ACCOUNT_TYPE_OPTIONS;
  const [selected, setSelected] = useState<ChoosableAccountType | null>(onlyType ?? null);

  const handleConfirm = async () => {
    if (!selected) return;
    try {
      await setAccountType(selected).unwrap();
      // Le serveur a enregistré le type et les rôles : on relit la session (menu, droits)
      await loadSession();
      onDone();
    } catch (error) {
      console.error("Choix du type de compte impossible :", error);
      CreationErrorSonner("Impossible d'enregistrer votre choix. Réessayez.");
    }
  };

  return (
    <OnboardingShell
      title={onlyType ? `Ajouter un espace ${onlyType === "dev" ? "dev" : "entreprise"}` : "Quel profil souhaitez-vous ?"}
      description={
        onlyType
          ? "Votre espace actuel est conservé. Nous allons vous guider pour créer celui-ci."
          : "Choisissez ce que vous venez faire sur DevStreet. Vous pourrez ajouter l'autre type plus tard."
      }
    >
      <div role="radiogroup" aria-label="Type de profil" className="flex flex-col gap-3">
        {options.map((option) => {
          const Icon = ICONS[option.value];
          const active = selected === option.value;
          return (
            <button
              key={option.value}
              type="button"
              role="radio"
              aria-checked={active}
              onClick={() => setSelected(option.value)}
              className={cn(
                "flex items-start gap-3 rounded-xl border p-4 text-left transition-colors",
                active
                  ? "border-brand bg-brand-soft"
                  : "border-border hover:bg-muted"
              )}
            >
              <Icon className="mt-0.5 size-5 shrink-0 text-foreground" aria-hidden />
              <span className="flex flex-col gap-0.5">
                <span className="text-sm font-semibold text-foreground">{option.title}</span>
                <span className="text-[13px] text-muted-foreground">{option.description}</span>
              </span>
            </button>
          );
        })}
      </div>

      <Button
        type="button"
        className="mt-6 w-full"
        disabled={!selected || isLoading}
        onClick={() => void handleConfirm()}
      >
        {isLoading ? "Enregistrement…" : "Continuer"}
      </Button>
    </OnboardingShell>
  );
}
