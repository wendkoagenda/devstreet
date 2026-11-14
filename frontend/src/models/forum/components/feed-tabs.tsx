import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

export type FeedScopeId = "pour-vous" | "abonnements";
export type FeedTypeFilterId = "tout" | "discussions" | "showcase" | "entraide";
export type FeedSortId = "recents" | "populaires";

/** @deprecated — préférer FeedScopeId + FeedTypeFilterId */
export type FeedTabId =
  | FeedScopeId
  | FeedSortId
  | "discussions"
  | "showcase"
  | "derniers";

const SCOPES: Array<{ id: FeedScopeId; label: string }> = [
  { id: "pour-vous", label: "Pour vous" },
  { id: "abonnements", label: "Abonnements" },
];

const TYPE_CHIPS: Array<{ id: FeedTypeFilterId; label: string }> = [
  { id: "tout", label: "Tout" },
  { id: "discussions", label: "Discussions" },
  { id: "showcase", label: "Showcase" },
  { id: "entraide", label: "Code Review" },
];

type FeedTabsProps = {
  scope: FeedScopeId;
  onScopeChange: (scope: FeedScopeId) => void;
  typeFilter: FeedTypeFilterId;
  onTypeFilterChange: (type: FeedTypeFilterId) => void;
  sort: FeedSortId;
  onSortChange: (sort: FeedSortId) => void;
};

export function FeedTabs({
  scope,
  onScopeChange,
  typeFilter,
  onTypeFilterChange,
  sort,
  onSortChange,
}: FeedTabsProps) {
  return (
    <div className="space-y-3">
      <div
        role="tablist"
        aria-label="Portée du fil"
        className="flex gap-5 border-b border-border"
      >
        {SCOPES.map((item) => {
          const active = scope === item.id;
          return (
            <button
              key={item.id}
              type="button"
              role="tab"
              aria-selected={active}
              onClick={() => onScopeChange(item.id)}
              className={cn(
                "-mb-px border-b-2 pb-2.5 text-sm font-medium transition-colors",
                active
                  ? "border-brand text-foreground"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              )}
            >
              {item.label}
            </button>
          );
        })}
      </div>

      <div className="flex flex-wrap items-center justify-between gap-2">
        <div
          role="group"
          aria-label="Type de publication"
          className="flex flex-wrap gap-1.5"
        >
          {TYPE_CHIPS.map((chip) => {
            const active = typeFilter === chip.id;
            return (
              <button
                key={chip.id}
                type="button"
                aria-pressed={active}
                onClick={() => onTypeFilterChange(chip.id)}
                className={cn(
                  "rounded-full px-3 py-1 text-xs font-medium transition-colors",
                  active
                    ? "bg-foreground text-background"
                    : "bg-muted/70 text-muted-foreground hover:bg-muted hover:text-foreground"
                )}
              >
                {chip.label}
              </button>
            );
          })}
        </div>

        <label className="relative inline-flex items-center">
          <span className="sr-only">Trier le fil</span>
          <select
            value={sort}
            onChange={(event) =>
              onSortChange(event.target.value as FeedSortId)
            }
            className="h-8 appearance-none rounded-lg border border-border bg-card py-1 pl-2.5 pr-7 text-xs font-medium text-muted-foreground outline-none transition-colors hover:text-foreground focus-visible:ring-2 focus-visible:ring-brand/30"
          >
            <option value="recents">Trier : Récents</option>
            <option value="populaires">Trier : Populaires</option>
          </select>
          <ChevronDown
            className="pointer-events-none absolute right-2 size-3.5 text-muted-foreground"
            aria-hidden
          />
        </label>
      </div>
    </div>
  );
}
