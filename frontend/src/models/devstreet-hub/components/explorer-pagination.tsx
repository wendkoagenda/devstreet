import { ArrowLeft, ArrowRight, ChevronLeft, ChevronRight } from "lucide-react";
import { useTranslation } from "react-i18next";
import { cn } from "@/lib/utils";

interface ExplorerPaginationProps {
  page: number;
  pageCount: number;
  count: number;
  pageSize: number;
  isBusy: boolean;
  onPageChange: (page: number) => void;
}

type PageSlot = number | "gap-start" | "gap-end";

/** Pages affichées autour de la page courante, avec première et dernière page toujours visibles. */
const pageSlots = (page: number, pageCount: number): PageSlot[] => {
  if (pageCount <= 5) return Array.from({ length: pageCount }, (_, i) => i + 1);
  const start = Math.max(2, page - 1);
  const end = Math.min(pageCount - 1, page + 1);
  const slots: PageSlot[] = [1];
  if (start > 2) slots.push("gap-start");
  for (let p = start; p <= end; p += 1) slots.push(p);
  if (end < pageCount - 1) slots.push("gap-end");
  slots.push(pageCount);
  return slots;
};

const navButton =
  "flex h-8 items-center gap-1 rounded-lg border px-3 text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:border-border disabled:bg-secondary disabled:text-muted-foreground disabled:opacity-70";

export function ExplorerPagination({
  page,
  pageCount,
  count,
  pageSize,
  isBusy,
  onPageChange,
}: ExplorerPaginationProps) {
  const { t } = useTranslation();
  if (count === 0) return null;

  const first = (page - 1) * pageSize + 1;
  const last = Math.min(page * pageSize, count);
  const hasPrevious = page > 1;
  const hasNext = page < pageCount;

  return (
    <>
      {/* Ordinateur : pages numérotées */}
      <section className="mb-8 hidden items-center justify-between gap-4 rounded-xl border border-border bg-card p-4 shadow-sm md:flex">
        <p className="text-xs text-muted-foreground">
          {t("hub.pagination.range_prefix")}{" "}
          <span className="font-bold text-foreground">{first}</span>{" "}
          {t("hub.pagination.range_to")}{" "}
          <span className="font-bold text-foreground">{last}</span>{" "}
          {t("hub.pagination.range_of")}{" "}
          <span className="font-bold text-foreground">{count}</span>{" "}
          {t("hub.pagination.projects", { count })}
        </p>
        <nav aria-label={t("hub.pagination.label")} className="inline-flex items-center gap-1.5">
          <button
            type="button"
            className={cn(navButton, "border-border bg-card text-foreground hover:bg-muted")}
            disabled={!hasPrevious || isBusy}
            onClick={() => onPageChange(page - 1)}
          >
            <ChevronLeft aria-hidden className="h-4 w-4" />
            {t("hub.pagination.previous")}
          </button>
          {pageSlots(page, pageCount).map((slot) =>
            typeof slot === "number" ? (
              <button
                key={slot}
                type="button"
                aria-current={slot === page ? "page" : undefined}
                aria-label={t("hub.pagination.page", { page: slot })}
                disabled={isBusy && slot !== page}
                onClick={() => slot !== page && onPageChange(slot)}
                className={cn(
                  "h-8 min-w-8 rounded-lg border px-2 text-xs transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                  slot === page
                    ? "border-primary bg-primary font-bold text-primary-foreground shadow-sm"
                    : "border-transparent text-muted-foreground hover:border-border hover:bg-muted hover:text-foreground"
                )}
              >
                {slot}
              </button>
            ) : (
              <span key={slot} aria-hidden className="px-1 text-xs text-muted-foreground">
                …
              </span>
            )
          )}
          <button
            type="button"
            className={cn(navButton, "border-border bg-card text-foreground shadow-sm hover:bg-muted")}
            disabled={!hasNext || isBusy}
            onClick={() => onPageChange(page + 1)}
          >
            {t("hub.pagination.next")}
            <ChevronRight aria-hidden className="h-4 w-4" />
          </button>
        </nav>
      </section>

      {/* Mobile : précédente / suivante */}
      <nav aria-label={t("hub.pagination.label")} className="mb-6 md:hidden">
        <div className="grid grid-cols-2 gap-3">
          <button
            type="button"
            className={cn(navButton, "h-11 justify-center rounded-xl border-border bg-secondary text-sm text-foreground hover:bg-muted")}
            disabled={!hasPrevious || isBusy}
            onClick={() => onPageChange(page - 1)}
          >
            <ArrowLeft aria-hidden className="h-4 w-4" />
            {t("hub.pagination.previous_short")}
          </button>
          <button
            type="button"
            className={cn(navButton, "h-11 justify-center rounded-xl border-border bg-card text-sm text-foreground hover:bg-muted")}
            disabled={!hasNext || isBusy}
            onClick={() => onPageChange(page + 1)}
          >
            {t("hub.pagination.next_short")}
            <ArrowRight aria-hidden className="h-4 w-4" />
          </button>
        </div>
        <p className="mt-3 text-center text-xs text-muted-foreground">
          {t("hub.pagination.mobile_summary", { page, pageCount, count })}
        </p>
      </nav>
    </>
  );
}
