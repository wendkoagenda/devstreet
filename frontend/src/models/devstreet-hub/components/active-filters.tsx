import { SlidersHorizontal, X } from "lucide-react";
import { useTranslation } from "react-i18next";

export interface ActiveFilter {
  key: string;
  label: string;
  onRemove: () => void;
}

interface ActiveFiltersProps {
  filters: ActiveFilter[];
  count: number;
  isCountKnown: boolean;
  onClearAll: () => void;
}

export function ActiveFilters({ filters, count, isCountKnown, onClearAll }: ActiveFiltersProps) {
  const { t } = useTranslation();
  const countText = isCountKnown ? (
    <span aria-live="polite">
      <span className="font-bold text-foreground">{count}</span>{" "}
      {t("hub.explorer.projects_available", { count })}
    </span>
  ) : null;

  return (
    <div className="mb-4 flex flex-col items-start justify-between gap-2 px-1 sm:flex-row sm:items-center">
      <div className="flex flex-wrap items-center gap-2">
        {filters.length > 0 && (
          <>
            <span className="mr-1 flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
              <SlidersHorizontal aria-hidden className="h-3.5 w-3.5 text-brand" />
              {t("hub.explorer.active_filters")}
            </span>
            {filters.map((filter) => (
              <span
                key={filter.key}
                className="inline-flex h-6 items-center gap-1.5 rounded-md border border-border bg-card px-2.5 text-[11px] text-foreground shadow-sm"
              >
                <span aria-hidden className="h-1.5 w-1.5 rounded-full bg-brand" />
                <span className="max-w-[16rem] truncate">{filter.label}</span>
                <button
                  type="button"
                  onClick={filter.onRemove}
                  aria-label={t("hub.explorer.remove_filter", { filter: filter.label })}
                  className="ml-0.5 flex items-center rounded-sm text-muted-foreground transition-colors hover:text-destructive focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <X aria-hidden className="h-3.5 w-3.5" />
                </button>
              </span>
            ))}
            <button
              type="button"
              onClick={onClearAll}
              className="ml-1 rounded-sm text-xs text-brand-strong transition-colors hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              {t("hub.explorer.clear_all")}
            </button>
          </>
        )}
      </div>
      {countText && (
        <div className="self-end text-xs font-medium text-muted-foreground sm:self-auto">
          {countText}
        </div>
      )}
    </div>
  );
}
