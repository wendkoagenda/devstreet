import { BadgeCheck } from "lucide-react";
import type { Publication } from "../schema";

type ChoixSectionProps = {
  publication: Publication;
};

/** Décision retenue — le vote vit dans la carte publication. */
export function ChoixSection({ publication }: ChoixSectionProps) {
  const decided = Boolean(publication.decided_at);
  const options = publication.options ?? [];
  const retained = options.find(
    (option) => option.id === publication.option_retenue
  );

  if (!(decided && retained)) return null;

  return (
    <div className="space-y-4">
      <section className="rounded-2xl border border-brand-soft-border bg-brand-soft/30 px-4 py-3 shadow-sm">
        <p className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-strong">
          <BadgeCheck className="h-4 w-4" />
          Décision : {retained.libelle}
        </p>
        {publication.justification_finale ? (
          <p className="mt-2 whitespace-pre-wrap text-sm text-foreground/90">
            {publication.justification_finale}
          </p>
        ) : null}
      </section>
    </div>
  );
}
