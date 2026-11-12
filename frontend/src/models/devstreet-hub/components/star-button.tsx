import { Loader2, Star } from "lucide-react";
import { useTranslation } from "react-i18next";
import { cn } from "@/lib/utils";
import type { ProjectStarView } from "../hooks/use-project-star";

interface StarButtonProps {
  projectTitle: string;
  view: ProjectStarView;
  onToggle: () => void;
  /** Affiche le libellé « Étoile » (header fiche). Sinon icône + compteur (cartes). */
  showLabel?: boolean;
  className?: string;
}

export function StarButton({
  projectTitle,
  view,
  onToggle,
  showLabel = false,
  className,
}: StarButtonProps) {
  const { t } = useTranslation();
  const { starred, count, isPending, isAvailable } = view;

  const label = !isAvailable
    ? t("hub.star.unavailable", { title: projectTitle })
    : starred
      ? t("hub.star.remove", { title: projectTitle })
      : t("hub.star.add", { title: projectTitle });

  return (
    <button
      type="button"
      onClick={onToggle}
      disabled={!isAvailable || isPending}
      aria-pressed={isAvailable ? starred : undefined}
      aria-label={label}
      title={label}
      className={cn(
        "inline-flex h-7 shrink-0 items-stretch overflow-hidden rounded-md border text-xs font-medium transition-colors",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1",
        "disabled:cursor-not-allowed disabled:opacity-60",
        starred
          ? "border-border bg-secondary text-foreground"
          : "border-border bg-card text-foreground enabled:hover:bg-secondary",
        className
      )}
    >
      <span className="inline-flex items-center gap-1.5 px-2.5">
        {isPending ? (
          <Loader2 aria-hidden className="size-3.5 animate-spin text-muted-foreground" />
        ) : (
          <Star
            aria-hidden
            className={cn(
              "size-3.5",
              starred ? "fill-warning text-warning" : "text-muted-foreground"
            )}
          />
        )}
        {showLabel ? (
          <span className="text-foreground">
            {starred ? t("hub.star.label_on") : t("hub.star.label")}
          </span>
        ) : null}
      </span>
      <span
        className={cn(
          "inline-flex min-w-[1.75rem] items-center justify-center border-l border-border px-2 tabular-nums",
          "bg-secondary/60 text-foreground"
        )}
        aria-hidden
      >
        {count}
      </span>
    </button>
  );
}
