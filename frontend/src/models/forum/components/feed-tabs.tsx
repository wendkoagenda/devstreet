import { ChevronDown } from "lucide-react";
import { useTranslation } from "react-i18next";
import { cn } from "@/lib/utils";

export type FeedScopeId = "pour-vous" | "abonnements";
export type FeedTypeFilterId =
  | "tout"
  | "discussions"
  | "showcase"
  | "entraide"
  | "choix"
  | "sondage";
export type FeedSortId = "recents" | "populaires";

/** @deprecated — préférer FeedScopeId + FeedTypeFilterId */
export type FeedTabId =
  | FeedScopeId
  | FeedSortId
  | "discussions"
  | "showcase"
  | "derniers";

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
  const { t } = useTranslation();

  const scopes: Array<{ id: FeedScopeId; label: string }> = [
    { id: "pour-vous", label: t("forum.tab_for_you") },
    { id: "abonnements", label: t("forum.tab_following") },
  ];

  const typeChips: Array<{ id: FeedTypeFilterId; label: string }> = [
    { id: "tout", label: t("forum.tab_all") },
    { id: "discussions", label: t("forum.tab_discussions") },
    { id: "showcase", label: t("forum.tab_showcase") },
    { id: "entraide", label: t("forum.tab_help") },
    { id: "choix", label: t("forum.tab_choice") },
    { id: "sondage", label: t("forum.tab_poll") },
  ];

  return (
    <div className="space-y-3">
      <div
        role="tablist"
        aria-label={t("forum.feed_scope_aria")}
        className="flex gap-5 border-b border-border"
      >
        {scopes.map((item) => {
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
          aria-label={t("forum.feed_type_aria")}
          className="flex flex-wrap gap-1.5"
        >
          {typeChips.map((chip) => {
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
          <span className="sr-only">{t("forum.feed_sort_aria")}</span>
          <select
            value={sort}
            onChange={(event) =>
              onSortChange(event.target.value as FeedSortId)
            }
            className="h-8 appearance-none rounded-lg border border-border bg-card py-1 pl-2.5 pr-7 text-xs font-medium text-muted-foreground outline-none transition-colors hover:text-foreground focus-visible:ring-2 focus-visible:ring-brand/30"
          >
            <option value="recents">{t("forum.sort_recent")}</option>
            <option value="populaires">{t("forum.sort_popular")}</option>
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
