import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { PAGE_SIZE } from "@/helpers/api/pagination";
import { useGetPublicationsInfiniteQuery } from "../api";
import { FeedComposer } from "../components/feed-composer";
import { FeedTabs, type FeedTabId } from "../components/feed-tabs";
import { PublicationCard } from "../components/publication-card";
import { ResumeQuotidienBanner } from "../components/resume-quotidien-banner";

function typeForTab(tab: FeedTabId): string | undefined {
  if (tab === "discussions") return "DISCUSSION";
  if (tab === "showcase") return "APPLICATION";
  return undefined;
}

function feedForTab(
  tab: FeedTabId
): "pour-vous" | "abonnements" | "populaires" | undefined {
  if (tab === "pour-vous") return "pour-vous";
  if (tab === "abonnements") return "abonnements";
  if (tab === "populaires") return "populaires";
  return undefined;
}

export default function FeedPage() {
  const navigate = useNavigate();
  const [tab, setTab] = useState<FeedTabId>("pour-vous");
  const typeFilter = typeForTab(tab);
  const feedMode = feedForTab(tab);
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
    ...(typeFilter ? { type: typeFilter } : {}),
    ...(feedMode ? { feed: feedMode } : {}),
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
          {tab === "showcase"
            ? "Projets"
            : tab === "abonnements"
              ? "Suivis"
              : tab === "populaires"
                ? "Tendances"
                : "Accueil"}
        </p>
        <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
          {tab === "showcase"
            ? "Showcase & dépôts"
            : tab === "abonnements"
              ? "Abonnements"
              : tab === "populaires"
                ? "Populaires"
                : "Fil d'actualité"}
        </h1>
        {tab === "showcase" ? (
          <p className="text-sm text-muted-foreground">
            Applications partagées par la communauté — teste, commente, aide.
          </p>
        ) : null}
        {tab === "abonnements" ? (
          <p className="text-sm text-muted-foreground">
            Publications des membres que tu suis et des chaînes auxquelles tu
            es abonné.
          </p>
        ) : null}
        {tab === "populaires" ? (
          <p className="text-sm text-muted-foreground">
            Les publications les plus likées et commentées du fil général.
          </p>
        ) : null}
      </header>

      <FeedComposer
        onCreated={(id) => navigate(`/forum/publications/${id}`)}
      />

      <ResumeQuotidienBanner
        onOpenAbonnements={() => setTab("abonnements")}
      />

      <FeedTabs value={tab} onChange={setTab} />

      <section className="space-y-5" aria-live="polite">
        {isLoading ? (
          <div className="rounded-2xl border border-border bg-card px-4 py-12 text-center text-sm text-muted-foreground">
            Chargement du fil…
          </div>
        ) : null}

        {isError ? (
          <div className="space-y-3 rounded-2xl border border-border bg-card px-4 py-12 text-center">
            <p className="text-sm text-destructive">
              Impossible de charger le fil.
            </p>
            <Button type="button" variant="outline" onClick={() => refetch()}>
              Réessayer
            </Button>
          </div>
        ) : null}

        {!isLoading && !isError && results.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-border bg-card px-4 py-12 text-center text-sm text-muted-foreground">
            {tab === "abonnements"
              ? "Rien ici pour l’instant. Suis des membres ou abonne-toi à des chaînes."
              : tab === "populaires"
                ? "Pas encore assez d’engagement pour un classement."
                : "Aucune publication ici pour le moment. Lance la première discussion."}
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

        {!isLoading && !isError && !hasNextPage && results.length > 0 ? (
          <p className="pb-4 text-center text-xs text-muted-foreground">
            Fin du fil
          </p>
        ) : null}
      </section>
    </div>
  );
}
