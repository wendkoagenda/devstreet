import { useState } from "react";
import { Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CreationErrorSonner } from "@/helpers/api/feed-backs";
import { cn } from "@/lib/utils";
import {
  useGetSkillOptionsQuery,
  useSetMySkillsMutation,
} from "@/models/marketplace-offers/api";
import { OnboardingShell } from "./onboarding-shell";

/** Niveau et ancienneté par défaut : le membre les affine ensuite dans son profil. */
const DEFAULT_LEVEL = 3;
const DEFAULT_YEARS = 1;
const MAX_SKILLS = 10;

/** Étape dev 2/2 : compétences clés (facultatif, le niveau se précise plus tard dans le profil). */
export function DevSkillsStep({
  stepIndex,
  stepCount,
  onDone,
}: {
  stepIndex: number;
  stepCount: number;
  onDone: () => void;
}) {
  const { data: skills = [], isLoading, isError } = useGetSkillOptionsQuery();
  const [setMySkills, { isLoading: saving }] = useSetMySkillsMutation();
  const [selected, setSelected] = useState<number[]>([]);

  const toggle = (id: number) => {
    setSelected((current) => {
      if (current.includes(id)) return current.filter((item) => item !== id);
      return current.length >= MAX_SKILLS ? current : [...current, id];
    });
  };

  const handleContinue = async () => {
    if (selected.length === 0) {
      onDone();
      return;
    }
    try {
      await setMySkills(
        selected.map((skill_id) => ({ skill_id, level: DEFAULT_LEVEL, years: DEFAULT_YEARS }))
      ).unwrap();
      onDone();
    } catch (error) {
      console.error("Enregistrement des compétences impossible :", error);
      CreationErrorSonner("Impossible d'enregistrer vos compétences. Réessayez ou passez cette étape.");
    }
  };

  return (
    <OnboardingShell
      title="Vos compétences clés"
      description={`Choisissez jusqu'à ${MAX_SKILLS} compétences. Vous précisez votre niveau plus tard dans votre profil.`}
      stepIndex={stepIndex}
      stepCount={stepCount}
    >
      {isLoading ? (
        <div className="flex flex-wrap gap-2">
          {Array.from({ length: 8 }, (_, index) => (
            <Skeleton key={index} className="h-8 w-20 rounded-full" />
          ))}
        </div>
      ) : isError ? (
        <p role="alert" className="text-sm text-destructive">
          Impossible de charger les compétences. Vous pourrez les ajouter depuis votre profil.
        </p>
      ) : (
        <div className="flex max-h-72 flex-wrap gap-2 overflow-y-auto" role="group" aria-label="Compétences">
          {skills.map((skill) => {
            const active = selected.includes(skill.id);
            return (
              <button
                key={skill.id}
                type="button"
                aria-pressed={active}
                onClick={() => toggle(skill.id)}
                className={cn(
                  "inline-flex items-center gap-1 rounded-full border px-3 py-1 text-[13px] transition-colors",
                  active
                    ? "border-brand bg-brand-soft text-brand-strong"
                    : "border-border text-foreground hover:bg-muted"
                )}
              >
                {active ? <Check className="size-3" aria-hidden /> : null}
                {skill.name}
              </button>
            );
          })}
        </div>
      )}

      <div className="mt-6 flex items-center justify-between gap-3">
        <Button type="button" variant="ghost" onClick={onDone} disabled={saving}>
          Passer
        </Button>
        <Button type="button" onClick={() => void handleContinue()} disabled={saving}>
          {saving ? "Enregistrement…" : selected.length > 0 ? `Continuer (${selected.length})` : "Continuer"}
        </Button>
      </div>
    </OnboardingShell>
  );
}
