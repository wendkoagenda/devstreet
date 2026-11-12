import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useDebouncedValue } from "@/hooks/use-debounced-value";
import { PAGE_SIZE, pageCountOf } from "@/helpers/api/pagination";
import { useGetProjectsQuery, useGetTechnologiesQuery } from "../api";
import type { Technology } from "../schema";

const SEARCH_DEBOUNCE_MS = 350;

const readPositiveInt = (value: string | null): number | null => {
  if (!value) return null;
  const parsed = Number(value);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : null;
};

/**
 * Recherche temporisée, filtre technologie, pagination et état URL pour l'écran 01.
 * Un seul filtre technologie à la fois (capacité API actuelle).
 */
export function useProjectExplorer() {
  const [searchParams, setSearchParams] = useSearchParams();

  const urlSearch = searchParams.get("search")?.trim() ?? "";
  const technology = searchParams.get("technology")?.trim() ?? "";
  const owner = readPositiveInt(searchParams.get("owner"));
  const page = Math.max(1, readPositiveInt(searchParams.get("page")) ?? 1);

  const [searchInput, setSearchInput] = useState(urlSearch);
  const debouncedSearch = useDebouncedValue(searchInput, SEARCH_DEBOUNCE_MS);

  useEffect(() => {
    setSearchInput(urlSearch);
  }, [urlSearch]);

  const patchParams = (mutate: (params: URLSearchParams) => void) => {
    const params = new URLSearchParams(searchParams);
    mutate(params);
    setSearchParams(params, { replace: true });
  };

  useEffect(() => {
    const next = debouncedSearch.trim();
    if (next === urlSearch) return;
    patchParams((params) => {
      if (next) params.set("search", next);
      else params.delete("search");
      params.delete("page");
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps -- synchronise seulement la recherche temporisée
  }, [debouncedSearch]);

  const listParams = useMemo(
    () => ({
      page,
      page_size: PAGE_SIZE,
      search: urlSearch || undefined,
      technology: technology || undefined,
      owner: owner ?? undefined,
    }),
    [page, urlSearch, technology, owner]
  );

  const projectsQuery = useGetProjectsQuery(listParams);
  const technologiesQuery = useGetTechnologiesQuery({
    page_size: 100,
    ordering: "label",
  });

  const technologies = useMemo(
    () => technologiesQuery.data?.results ?? [],
    [technologiesQuery.data?.results]
  );
  const technologiesById = useMemo(() => {
    const map = new Map<number, Technology>();
    for (const item of technologies) map.set(item.id, item);
    return map;
  }, [technologies]);

  const selectedTechnology =
    technologies.find((item) => item.slug === technology) ?? null;

  const setTechnology = (slug: string) => {
    patchParams((params) => {
      if (slug) params.set("technology", slug);
      else params.delete("technology");
      params.delete("page");
    });
  };

  const setPage = (nextPage: number) => {
    patchParams((params) => {
      if (nextPage <= 1) params.delete("page");
      else params.set("page", String(nextPage));
    });
  };

  const clearSearch = () => {
    setSearchInput("");
    patchParams((params) => {
      params.delete("search");
      params.delete("page");
    });
  };

  const clearTechnology = () => setTechnology("");

  const clearOwner = () => {
    patchParams((params) => {
      params.delete("owner");
      params.delete("page");
    });
  };

  const clearAll = () => {
    setSearchInput("");
    setSearchParams({}, { replace: true });
  };

  const count = projectsQuery.data?.count ?? 0;
  const projects = projectsQuery.data?.results ?? [];

  return {
    searchInput,
    setSearchInput,
    filters: {
      search: urlSearch,
      technology,
      owner,
      page,
    },
    selectedTechnology,
    setTechnology,
    setPage,
    clearSearch,
    clearTechnology,
    clearOwner,
    clearAll,
    projects,
    technologies,
    technologiesById,
    count,
    pageCount: pageCountOf(count, PAGE_SIZE),
    pageSize: PAGE_SIZE,
    isLoading: projectsQuery.isLoading,
    isFetching: projectsQuery.isFetching,
    error: projectsQuery.error,
    retry: () => void projectsQuery.refetch(),
    isCatalogLoading: technologiesQuery.isLoading,
    catalogError: technologiesQuery.error,
    retryCatalog: () => void technologiesQuery.refetch(),
    hasActiveFilters: Boolean(urlSearch || technology || owner !== null),
  };
}
