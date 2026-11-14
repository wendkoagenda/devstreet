import type { ReactNode } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

export type StatItem = {
  label: string;
  value: ReactNode;
  hint?: ReactNode;
  /** Mise en évidence (violet d'accent) : ce qui demande une action, par exemple « à traiter ». */
  highlight?: boolean;
};

const COLUMNS: Record<number, string> = {
  1: "sm:grid-cols-1",
  2: "sm:grid-cols-2",
  3: "sm:grid-cols-3",
  4: "sm:grid-cols-2 lg:grid-cols-4",
};

/** Une ligne de petites statistiques, en haut d'une page. Même présentation partout. */
export function StatsStrip({
  items,
  isLoading = false,
  className,
}: {
  items: StatItem[];
  isLoading?: boolean;
  className?: string;
}) {
  if (isLoading) return <Skeleton className={cn("h-[68px] w-full rounded-xl", className)} />;
  if (items.length === 0) return null;

  return (
    <div
      className={cn("grid grid-cols-2 gap-2", COLUMNS[Math.min(items.length, 4)] ?? COLUMNS[4], className)}
      role="list"
      aria-label="Statistiques"
    >
      {items.map((item) => (
        <div
          key={item.label}
          role="listitem"
          className={cn(
            "flex min-w-0 flex-col gap-0.5 rounded-xl border px-3.5 py-2.5",
            item.highlight
              ? "border-brand bg-brand-soft"
              : "border-brand-soft-border bg-card"
          )}
        >
          <span className="truncate text-xs text-muted-foreground">{item.label}</span>
          <span
            className={cn(
              "text-xl font-semibold leading-tight",
              item.highlight ? "text-brand-strong" : "text-foreground"
            )}
          >
            {item.value}
          </span>
          {item.hint ? <span className="truncate text-[11px] text-muted-foreground">{item.hint}</span> : null}
        </div>
      ))}
    </div>
  );
}
