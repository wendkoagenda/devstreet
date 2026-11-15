import { useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { PAGE_SIZE } from "@/helpers/api/pagination";
import {
  useGetEspacesInfiniteQuery,
  useGetPublicationsInfiniteQuery,
} from "../api";
import type { Espace } from "../schema";
import { FeedComposer } from "../components/feed-composer";
import { FeedIndexAside } from "../components/feed-index-aside";
import {
  FeedTabs,
  type FeedScopeId,
  type FeedSortId,
  type FeedTypeFilterId,
} from "../components/feed-tabs";
import { PublicationCard } from "../components/publication-card";

function typeForFilter(filter: FeedTypeFilterId): string | undefined {
  if (filter === "discussions") return "DISCUSSION";
  if (filter === "showcase") return "APPLICATION";
  if (filter === "entraide") return "ENTRAIDE";
  if (filter === "choix") return "CHOIX";
  if (filter === "sondage") return "SONDAGE";
  return undefined;
}

function feedForQuery(
  scope: FeedScopeId,
  sort: FeedSortId
): "pour-vous" | "abonnements" | "populaires" | undefined {
  if (scope === "abonnements") return "abonnements";
  if (sort === "populaires") return "populaires";
  return "pour-vous";
}

function topByMembers(espaces: Espace[], limit = 3) {
  return [...espaces]
    .sort((a, b) => (b.membres_count ?? 0) - (a.membres_count ?? 0))
    .slice(0, limit);
}

export default function FeedPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const tagFilter = searchParams.get("tag")?.trim() || null;
  const [scope, setScope] = useState<FeedScopeId>(
    searchParams.get("tab") === "abonnements" ? "abonnements" : "pour-vous"
  );
  const [typeFilter, setTypeFilter] = useState<FeedTypeFilterId>("tout");
  const [sort, setSort] = useState<FeedSortId>("recents");
  const [publishOpen, setPublishOpen] = useState(false);
  const loadMoreRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (searchParams.get("tab") === "abonnements") {
      setScope("abonnements");
      const next = new URLSearchParams(searchParams);
      next.delete("tab");
      setSearchParams(next, { replace: true });
    }
  }, [searchParams, setSearchParams]);

  useEffect(() => {
    if (tagFilter) setScope("pour-vous");
  }, [tagFilter]);

  useEffect(() => {
    if (searchParams.get("publish") !== "1") return;
    setPublishOpen(true);
    const next = new URLSearchParams(searchParams);
    next.delete("publish");
    setSearchParams(next, { replace: true });
  }, [searchParams, setSearchParams]);

  const typeApi = typeForFilter(typeFilter);
  const feedMode = feedForQuery(scope, sort);

  const clearTagFilter = () => {
    const next = new URLSearchParams(searchParams);
    next.delete("tag");
    setSearchParams(next, { replace: true });
  };

  const {
    data: pubsData,
    isLoading: pubsLoading,
    isFetching,
    isFetchingNextPage,
    isError: pubsError,
    refetch: refetchPubs,
    fetchNextPage,
    hasNextPage,
  } = useGetPublicationsInfiniteQuery({
    page_size: PAGE_SIZE,
    ...(typeApi ? { type: typeApi } : {}),
    ...(feedMode ? { feed: feedMode } : {}),
    ...(tagFilter ? { tag: tagFilter } : {}),
  });

  const { data: communautesData } = useGetEspacesInfiniteQuery({
    type: "COMMUNAUTE",
    page_size: 20,
  });

  const { data: chainesData } = useGetEspacesInfiniteQuery({
    type: "CHAINE",
    page_size: 20,
  });

  const results = useMemo(
    () => pubsData?.pages.flatMap((page) => page.results) ?? [],
    [pubsData?.pages]
  );

  const topCommunautes = useMemo(
    () =>
      topByMembers(
        communautesData?.pages.flatMap((page) => page.results) ?? [],
        3
      ),
    [communautesData?.pages]
  );

  const topChaines = useMemo(
    () =>
      topByMembers(
        chainesData?.pages.flatMap((page) => page.results) ?? [],
        3
      ),
    [chainesData?.pages]
  );

  const peers = useMemo(() => {
    const seen = new Set<number>();
    const list: Array<{
      id: number;
      username: string;
      full_name: string;
      photo?: string;
      following?: boolean;
    }> = [];
    for (const pub of results) {
      const auteur = pub.auteur;
      if (!auteur?.id || seen.has(auteur.id)) continue;
      seen.add(auteur.id);
      list.push({
        id: auteur.id,
        username: auteur.username,
        full_name: auteur.full_name || auteur.username,
        photo: auteur.photo,
        following: Boolean(pub.following_auteur),
      });
      if (list.length >= 4) break;
    }
    return list;
  }, [results]);

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
    <div className="mx-auto w-full max-w-7xl">
      <Dialog open={publishOpen} onOpenChange={setPublishOpen}>
        <DialogContent className="max-h-[90dvh] w-[min(100vw-1.5rem,40rem)] max-w-none overflow-y-auto sm:rounded-xl">
          <DialogHeader>
            <DialogTitle>Nouvelle publication</DialogTitle>
          </DialogHeader>
          {publishOpen ? (
            <FeedComposer
              key="publish-modal"
              forceExpanded
              bare
              onCreated={(id) => {
                setPublishOpen(false);
                navigate(`/forum/publications/${id}`);
              }}
              onCancel={() => setPublishOpen(false)}
            />
          ) : null}
        </DialogContent>
      </Dialog>

      <div className="grid grid-cols-1 gap-8 xl:grid-cols-[minmax(0,1fr)_18rem]">
        <div className="min-w-0 space-y-6">
          <header className="space-y-1.5">
            <h1 className="text-xl font-bold tracking-tight text-foreground sm:text-2xl">
              {t("forum.feed_title")}
            </h1>
            {tagFilter ? (
              <p className="text-xs text-muted-foreground">
                {t("forum.feed_tag_prefix")}{" "}
                <button
                  type="button"
                  onClick={clearTagFilter}
                  className="font-mono font-medium text-brand hover:underline"
                >
                  #{tagFilter}
                </button>
                {" — "}
                {t("forum.feed_tag_suffix")}
              </p>
            ) : null}
          </header>

          <FeedTabs
            scope={scope}
            onScopeChange={setScope}
            typeFilter={typeFilter}
            onTypeFilterChange={setTypeFilter}
            sort={sort}
            onSortChange={setSort}
          />

          <div className="space-y-4 sm:space-y-5" aria-live="polite">
            {pubsLoading ? (
              <p className="py-10 text-center text-sm text-muted-foreground">
                {t("forum.feed_loading")}
              </p>
            ) : null}

            {pubsError ? (
              <div className="space-y-2 py-8 text-center">
                <p className="text-sm text-destructive">
                  {t("forum.feed_error")}
                </p>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => refetchPubs()}
                >
                  {t("forum.feed_retry")}
                </Button>
              </div>
            ) : null}

            {!pubsLoading && !pubsError && results.length === 0 ? (
              <p className="rounded-xl border border-dashed border-border px-4 py-8 text-center text-sm text-muted-foreground">
                {t("forum.feed_empty")}
              </p>
            ) : null}

            {!pubsLoading && !pubsError
              ? results.map((publication) => (
                  <PublicationCard
                    key={publication.id}
                    publication={publication}
                  />
                ))
              : null}

            <div ref={loadMoreRef} className="h-6 w-full" aria-hidden />

            {isFetchingNextPage ? (
              <p className="pb-2 text-center text-xs text-muted-foreground">
                {t("forum.feed_loading")}
              </p>
            ) : null}
          </div>
        </div>

        <div className="hidden xl:block">
          <FeedIndexAside
            peers={peers}
            topCommunautes={topCommunautes}
            topChaines={topChaines}
          />
        </div>
      </div>
    </div>
  );
}
