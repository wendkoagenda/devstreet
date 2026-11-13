import { useEffect, useMemo, useRef } from "react";
import { Link } from "react-router-dom";
import { Bookmark } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PAGE_SIZE } from "@/helpers/api/pagination";
import { useGetPublicationsInfiniteQuery } from "../api";
import { PublicationCard } from "../components/publication-card";

export default function FavoritesPage() {
  const loadMoreRef = useRef<HTMLDivElement | null>(null);
  const {
    data,
    isLoading,
    isFetching,
    isFetchingNextPage,
    isError,
    refetch,
    fetchNextPage,
    hasNextPage,
  } = useGetPublicationsInfiniteQuery({
    page_size: PAGE_SIZE,
    feed: "favoris",
  });

  const results = useMemo(
    () => data?.pages.flatMap((page) => page.results) ?? [],
    [data?.pages]
  );

  useEffect(() => {
    const node = loadMoreRef.current;
    if (!node) return;
    const observer = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        if (
          entry?.isIntersecting &&
          hasNextPage &&
          !isFetchingNextPage &&
          !isFetching
        ) {
          void fetchNextPage();
        }
      },
      { rootMargin: "240px 0px" }
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, [fetchNextPage, hasNextPage, isFetching, isFetchingNextPage]);

  return (
    <div className="mx-auto w-full max-w-3xl space-y-5">
      <header className="space-y-1">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Forum
        </p>
        <h1 className="flex items-center gap-2 text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
          <Bookmark className="size-7 text-brand" aria-hidden />
          Mes favoris
        </h1>
        <p className="text-sm text-muted-foreground">
          Publications que tu as mises de côté.
        </p>
      </header>

      <section className="space-y-5" aria-live="polite">
        {isLoading ? (
          <div className="rounded-2xl border border-border bg-card px-4 py-12 text-center text-sm text-muted-foreground">
            Chargement des favoris…
          </div>
        ) : null}

        {isError ? (
          <div className="space-y-3 rounded-2xl border border-border bg-card px-4 py-12 text-center">
            <p className="text-sm text-destructive">
              Impossible de charger tes favoris.
            </p>
            <Button type="button" variant="outline" onClick={() => void refetch()}>
              Réessayer
            </Button>
          </div>
        ) : null}

        {!isLoading && !isError && results.length === 0 ? (
          <div className="space-y-3 rounded-2xl border border-dashed border-border bg-card px-4 py-12 text-center text-sm text-muted-foreground">
            <p>Aucun favori pour l’instant.</p>
            <Button asChild variant="outline" size="sm">
              <Link to="/">Parcourir le fil</Link>
            </Button>
          </div>
        ) : null}

        {!isLoading && !isError
          ? results.map((publication) => (
              <PublicationCard key={publication.id} publication={publication} />
            ))
          : null}

        <div ref={loadMoreRef} className="h-8 w-full" aria-hidden />

        {isFetchingNextPage ? (
          <p className="pb-4 text-center text-sm text-muted-foreground">
            Chargement…
          </p>
        ) : null}
      </section>
    </div>
  );
}
