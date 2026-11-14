import { cn } from "@/lib/utils";
import { useGetTagsSuivisQuery } from "../api";

type FavorisTagQuickSelectProps = {
  /** Slug du thème actuellement sélectionné. */
  activeSlug?: string | null;
  /** Sélection / désélection rapide. */
  onSelect: (slug: string | null) => void;
  /** Variante visuelle compacte (sidebar) ou barre (page). */
  variant?: "bar" | "sidebar";
  /** Message si aucun thème suivi (sidebar uniquement par défaut). */
  emptyHint?: string;
  className?: string;
};

/**
 * Sélection rapide parmi les thèmes suivis (« Mes favoris »).
 * Un clic active le filtre ; un second clic sur le même thème le retire.
 */
export function FavorisTagQuickSelect({
  activeSlug = null,
  onSelect,
  variant = "bar",
  emptyHint = "Suis un thème depuis une publication pour le retrouver ici.",
  className,
}: FavorisTagQuickSelectProps) {
  const { data: tags = [], isLoading } = useGetTagsSuivisQuery();

  if (isLoading) {
    return (
      <p
        className={cn(
          "font-mono text-[11px] text-muted-foreground/70",
          className
        )}
      >
        …
      </p>
    );
  }

  if (tags.length === 0) {
    if (variant === "sidebar") {
      return (
        <p
          className={cn(
            "text-[11px] leading-snug text-muted-foreground/70",
            className
          )}
        >
          {emptyHint}
        </p>
      );
    }
    return null;
  }

  if (variant === "sidebar") {
    return (
      <ul
        className={cn("space-y-0.5", className)}
        role="listbox"
        aria-label="Mes favoris"
      >
        {tags.map((tag) => {
          const active = activeSlug === tag.slug;
          return (
            <li key={tag.id} role="option" aria-selected={active}>
              <button
                type="button"
                onClick={() => onSelect(active ? null : tag.slug)}
                className={cn(
                  "flex w-full items-center justify-between gap-2 rounded-md px-1.5 py-1 text-left font-mono text-[12px] transition-colors",
                  active
                    ? "bg-sidebar-accent font-medium text-sidebar-accent-foreground"
                    : "text-sidebar-foreground/70 hover:bg-sidebar-accent/60 hover:text-sidebar-accent-foreground"
                )}
              >
                <span className="truncate">#{tag.slug}</span>
                {active ? (
                  <span
                    className="size-1.5 shrink-0 rounded-full bg-muted-foreground"
                    aria-hidden
                  />
                ) : null}
              </button>
            </li>
          );
        })}
      </ul>
    );
  }

  return (
    <div className={cn("space-y-1.5", className)}>
      <div className="flex items-center justify-between gap-2">
        <p className="font-mono text-[10px] font-medium uppercase tracking-[0.14em] text-muted-foreground">
          Mes favoris
        </p>
        {activeSlug ? (
          <button
            type="button"
            onClick={() => onSelect(null)}
            className="text-[11px] font-medium text-muted-foreground hover:text-foreground"
          >
            Tout voir
          </button>
        ) : null}
      </div>
      <div
        className="flex gap-1.5 overflow-x-auto pb-0.5 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
        role="listbox"
        aria-label="Sélection rapide Mes favoris"
      >
        {tags.map((tag) => {
          const active = activeSlug === tag.slug;
          return (
            <button
              key={tag.id}
              type="button"
              role="option"
              aria-selected={active}
              onClick={() => onSelect(active ? null : tag.slug)}
              className={cn(
                "shrink-0 rounded-md border px-2.5 py-1 font-mono text-[12px] transition-colors",
                active
                  ? "border-brand-soft-border bg-brand-soft font-medium text-brand"
                  : "border-border bg-card text-muted-foreground hover:border-brand-soft-border hover:bg-brand-soft/50 hover:text-foreground"
              )}
            >
              #{tag.slug}
            </button>
          );
        })}
      </div>
    </div>
  );
}
