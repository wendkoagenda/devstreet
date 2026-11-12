import { Loader2, Star } from "lucide-react";
import { useTranslation } from "react-i18next";
import { cn } from "@/lib/utils";
import type { ProjectStarView } from "../hooks/use-project-star";

interface StarButtonProps {
  projectTitle: string;
  view: ProjectStarView;
  onToggle: () => void;
  className?: string;
}

export function StarButton({ projectTitle, view, onToggle, className }: StarButtonProps) {
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
        "relative z-10 inline-flex h-7 shrink-0 items-center gap-1.5 rounded-lg border px-2.5 text-xs transition-colors",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-card",
        "disabled:cursor-not-allowed disabled:opacity-60",
        starred
          ? "border-brand-soft-border bg-brand-soft text-brand-strong"
          : "border-border bg-secondary text-muted-foreground enabled:hover:border-brand-soft-border enabled:hover:bg-brand-soft enabled:hover:text-brand-strong",
        className
      )}
    >
      {isPending ? (
        <Loader2 aria-hidden className="h-4 w-4 animate-spin" />
      ) : (
        <Star
          aria-hidden
          className={cn("h-4 w-4", starred ? "fill-brand text-brand" : "text-muted-foreground")}
        />
      )}
      <span className="font-bold text-foreground">{count}</span>
    </button>
  );
}
