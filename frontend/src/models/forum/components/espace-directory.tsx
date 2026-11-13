import { useEffect, useMemo, useRef, useState } from "react";
import { Loader2, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { Espace } from "../schema";
import { EspaceListItem } from "./espace-list-item";

type EspaceDirectoryProps = {
  espaces: Espace[];
  hrefFor: (espace: Espace) => string;
  search: string;
  onSearchChange: (value: string) => void;
  searchPlaceholder: string;
  mineTitle: string;
  otherTitle: string;
  emptyLabel: string;
  emptySearchLabel: string;
  isLoading?: boolean;
  isFetchingNextPage?: boolean;
  hasNextPage?: boolean;
  onLoadMore?: () => void;
};

export function useDebouncedValue(value: string, delayMs = 300) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = window.setTimeout(() => setDebounced(value), delayMs);
    return () => window.clearTimeout(timer);
  }, [value, delayMs]);
  return debounced;
}

export function EspaceDirectory({
  espaces,
  hrefFor,
  search,
  onSearchChange,
  searchPlaceholder,
  mineTitle,
  otherTitle,
  emptyLabel,
  emptySearchLabel,
  isLoading = false,
  isFetchingNextPage = false,
  hasNextPage = false,
  onLoadMore,
}: EspaceDirectoryProps) {
  const loadMoreRef = useRef<HTMLDivElement | null>(null);

  const { mine, others } = useMemo(() => {
    const mineList: Espace[] = [];
    const otherList: Espace[] = [];
    for (const espace of espaces) {
      if (espace.mon_role) mineList.push(espace);
      else otherList.push(espace);
    }
    otherList.sort(
      (a, b) => (b.membres_count ?? 0) - (a.membres_count ?? 0)
    );
    return { mine: mineList, others: otherList };
  }, [espaces]);

  useEffect(() => {
    const node = loadMoreRef.current;
    if (!node || !onLoadMore) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        if (entry?.isIntersecting && hasNextPage && !isFetchingNextPage) {
          onLoadMore();
        }
      },
      { rootMargin: "240px 0px" }
    );

    observer.observe(node);
    return () => observer.disconnect();
  }, [hasNextPage, isFetchingNextPage, onLoadMore]);

  const hasAny = espaces.length > 0;
  const hasQuery = search.trim().length > 0;

  return (
    <div className="space-y-5">
      <div className="relative">
        <Search
          className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
          aria-hidden
        />
        <Input
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
          placeholder={searchPlaceholder}
          className="pl-9"
          aria-label={searchPlaceholder}
        />
      </div>

      {isLoading && !hasAny ? (
        <p className="rounded-2xl border border-dashed border-border px-4 py-10 text-center text-sm text-muted-foreground">
          Chargement…
        </p>
      ) : null}

      {!isLoading && !hasAny ? (
        <p className="rounded-2xl border border-dashed border-border px-4 py-10 text-center text-sm text-muted-foreground">
          {hasQuery ? emptySearchLabel : emptyLabel}
        </p>
      ) : null}

      {hasAny ? (
        <>
          {mine.length > 0 ? (
            <section className="space-y-3">
              <h2 className="px-1 text-sm font-semibold text-foreground">
                {mineTitle}
                <span className="ml-1 font-normal text-muted-foreground">
                  ({mine.length}
                  {hasNextPage ? "+" : ""})
                </span>
              </h2>
              <div className="grid gap-3 sm:grid-cols-2">
                {mine.map((espace) => (
                  <EspaceListItem
                    key={espace.id}
                    espace={espace}
                    href={hrefFor(espace)}
                  />
                ))}
              </div>
            </section>
          ) : null}

          {others.length > 0 ? (
            <section className="space-y-3">
              <h2 className="px-1 text-sm font-semibold text-foreground">
                {otherTitle}
                <span className="ml-1 font-normal text-muted-foreground">
                  ({others.length}
                  {hasNextPage ? "+" : ""})
                </span>
              </h2>
              <div className="grid gap-3 sm:grid-cols-2">
                {others.map((espace) => (
                  <EspaceListItem
                    key={espace.id}
                    espace={espace}
                    href={hrefFor(espace)}
                  />
                ))}
              </div>
            </section>
          ) : null}
        </>
      ) : null}

      <div ref={loadMoreRef} className="h-6 w-full" aria-hidden />

      {isFetchingNextPage ? (
        <p className="flex items-center justify-center gap-2 pb-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
          Chargement…
        </p>
      ) : null}

      {!isFetchingNextPage && hasNextPage && onLoadMore ? (
        <div className="flex justify-center pb-2">
          <Button type="button" variant="outline" size="sm" onClick={onLoadMore}>
            Voir plus
          </Button>
        </div>
      ) : null}
    </div>
  );
}
