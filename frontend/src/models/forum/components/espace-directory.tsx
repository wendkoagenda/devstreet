import { useEffect, useMemo, useState } from "react";
import { Search } from "lucide-react";
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
  /** Limite « À découvrir » hors recherche (défaut 10). */
  discoverLimit?: number;
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
  discoverLimit = 10,
}: EspaceDirectoryProps) {
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
    const hasQuery = search.trim().length > 0;
    return {
      mine: mineList,
      others: hasQuery ? otherList : otherList.slice(0, discoverLimit),
    };
  }, [espaces, search, discoverLimit]);

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

      {!hasAny ? (
        <p className="rounded-2xl border border-dashed border-border px-4 py-10 text-center text-sm text-muted-foreground">
          {hasQuery ? emptySearchLabel : emptyLabel}
        </p>
      ) : (
        <>
          {mine.length > 0 ? (
            <section className="space-y-3">
              <h2 className="px-1 text-sm font-semibold text-foreground">
                {mineTitle}
                <span className="ml-1 font-normal text-muted-foreground">
                  ({mine.length})
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
                  (
                  {hasQuery
                    ? others.length
                    : `top ${others.length}`}
                  )
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
      )}
    </div>
  );
}
