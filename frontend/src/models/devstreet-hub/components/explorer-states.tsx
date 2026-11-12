import { AlertTriangle, LogIn, Plus, RotateCw, SearchX } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import type { CreateAction } from "./explorer-toolbar";

export function ProjectGridSkeleton() {
  const { t } = useTranslation();
  return (
    <div
      role="status"
      aria-label={t("hub.explorer.loading")}
      className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2"
    >
      {Array.from({ length: 4 }, (_, index) => (
        <div key={index} className="rounded-xl border border-border bg-card p-5 shadow-sm">
          <div className="mb-3 flex items-start justify-between gap-3">
            <Skeleton className="h-5 w-1/2" />
            <Skeleton className="h-7 w-14" />
          </div>
          <Skeleton className="mb-4 h-3 w-1/3" />
          <Skeleton className="mb-2 h-3 w-full" />
          <Skeleton className="mb-4 h-3 w-4/5" />
          <div className="mb-4 flex gap-1.5">
            <Skeleton className="h-6 w-16" />
            <Skeleton className="h-6 w-20" />
            <Skeleton className="h-6 w-14" />
          </div>
          <div className="flex justify-between border-t border-border/70 pt-3">
            <Skeleton className="h-3 w-28" />
            <Skeleton className="h-3 w-24" />
          </div>
        </div>
      ))}
      <span className="sr-only">{t("hub.explorer.loading")}</span>
    </div>
  );
}

interface EmptyStateProps {
  hasActiveFilters: boolean;
  createAction: CreateAction;
  onClearFilters: () => void;
  onCreate: () => void;
}

export function ExplorerEmptyState({
  hasActiveFilters,
  createAction,
  onClearFilters,
  onCreate,
}: EmptyStateProps) {
  const { t } = useTranslation();

  return (
    <section className="mb-6 flex flex-col items-center justify-center rounded-xl border border-dashed border-input bg-card px-6 py-12 text-center shadow-sm sm:py-16">
      <span className="mb-4 flex h-12 w-12 items-center justify-center rounded-full border border-border bg-secondary text-muted-foreground">
        <SearchX aria-hidden className="h-6 w-6" />
      </span>
      <h2 className="mb-1.5 text-sm font-bold text-foreground">
        {hasActiveFilters ? t("hub.empty.filtered_title") : t("hub.empty.title")}
      </h2>
      <p className="mb-5 max-w-sm text-[13px] text-muted-foreground">
        {hasActiveFilters ? t("hub.empty.filtered_text") : t("hub.empty.text")}
      </p>
      {hasActiveFilters ? (
        <Button type="button" variant="outline" onClick={onClearFilters} className="h-9 rounded-lg text-xs font-semibold">
          {t("hub.explorer.clear_all")}
        </Button>
      ) : createAction !== "hidden" ? (
        <Button type="button" onClick={onCreate} className="h-9 gap-1.5 rounded-lg text-xs font-semibold">
          {createAction === "login" ? <LogIn aria-hidden /> : <Plus aria-hidden className="text-brand" />}
          {createAction === "login" ? t("hub.explorer.create_login") : t("hub.explorer.create")}
        </Button>
      ) : null}
    </section>
  );
}

interface ErrorStateProps {
  status: number | null;
  isRetrying: boolean;
  onRetry: () => void;
}

const errorMessageKey = (status: number | null): string => {
  if (status === null) return "hub.error.network";
  if (status === 429) return "hub.common.rate_limited";
  if (status === 403) return "hub.error.forbidden";
  return "hub.error.generic";
};

export function ExplorerErrorState({ status, isRetrying, onRetry }: ErrorStateProps) {
  const { t } = useTranslation();

  return (
    <section
      role="alert"
      className="mb-6 flex flex-col items-start justify-between gap-4 rounded-xl border border-destructive/30 bg-destructive/5 p-5 sm:flex-row sm:items-center"
    >
      <div className="flex items-start gap-3">
        <AlertTriangle aria-hidden className="mt-0.5 h-5 w-5 shrink-0 text-destructive" />
        <div>
          <h2 className="text-sm font-bold text-foreground">{t("hub.error.title")}</h2>
          <p className="mt-1 text-[13px] text-muted-foreground">{t(errorMessageKey(status))}</p>
        </div>
      </div>
      <Button
        type="button"
        variant="outline"
        onClick={onRetry}
        disabled={isRetrying}
        className="h-9 shrink-0 gap-2 rounded-lg border-destructive/30 text-xs font-semibold text-destructive hover:bg-destructive/10 hover:text-destructive"
      >
        <RotateCw aria-hidden className={isRetrying ? "animate-spin" : undefined} />
        {t("hub.common.retry")}
      </Button>
    </section>
  );
}
