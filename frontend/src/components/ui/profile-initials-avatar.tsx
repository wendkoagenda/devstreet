import { Building2 } from "lucide-react";
import { OpenToWorkRing } from "@/components/ui/open-to-work-ring";
import { cn } from "@/lib/utils";

const SIZES = {
  sm: { box: "size-8 text-xs", text: false },
  md: { box: "size-10 text-xs", text: false },
  lg: { box: "size-14 text-base", text: true },
  xl: { box: "size-20 text-xl", text: true },
} as const;

function initials(name: string): string {
  return (
    name
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase() ?? "")
      .join("") || "?"
  );
}

/**
 * Pastille d'initiales d'un profil de la marketplace. Un profil dev ouvert aux opportunités porte l'arc
 * « Open to work » ; le texte de l'arc n'est écrit que sur la grande taille, où il reste lisible.
 */
export function ProfileInitialsAvatar({
  name,
  openToWork = false,
  size = "md",
  kind = "dev",
  className,
}: {
  name: string;
  /** Profil dev ouvert aux opportunités (jamais pour un profil entreprise). */
  openToWork?: boolean;
  size?: keyof typeof SIZES;
  /** « entreprise » : carré arrondi avec une icône de bâtiment, pour ne jamais confondre avec un dev (rond, initiales). */
  kind?: "dev" | "entreprise";
  className?: string;
}) {
  const { box, text } = SIZES[size];
  if (kind === "entreprise") {
    return (
      <span className={cn("relative inline-flex shrink-0", className)} aria-hidden>
        <span
          className={cn(
            "flex items-center justify-center rounded-xl border border-brand-soft-border bg-brand-soft text-brand-strong",
            box
          )}
        >
          <Building2 className={size === "sm" ? "size-4" : size === "md" ? "size-5" : "size-7"} />
        </span>
      </span>
    );
  }
  return (
    <span className={cn("relative inline-flex shrink-0", className)} aria-hidden={!openToWork}>
      <span
        className={cn(
          "flex items-center justify-center rounded-full border border-border bg-muted font-semibold text-foreground",
          box
        )}
        aria-hidden
      >
        {initials(name)}
      </span>
      {openToWork ? <OpenToWorkRing showText={text} /> : null}
    </span>
  );
}
