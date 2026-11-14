/**
 * Listes paginées côté serveur : format de réponse DRF et paramètres de requête.
 * Le serveur pagine, recherche et trie ; le tableau n'a que la page courante.
 */

import type { FetchBaseQueryError } from "@reduxjs/toolkit/query";

export const PAGE_SIZE = 20;

/** Taille de page maximale acceptée par le backend (StandardPagination.max_page_size). */
export const MAX_PAGE_SIZE = 100;

/** Garde-fou : nombre maximal de pages lues par `fetchAllPages` (soit 5 000 éléments). */
const MAX_PAGES = 50;

/** Réponse paginée du backend (StandardPagination). */
export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

/** Réponse paginée par curseur (FeedCursorPagination / scroll infini). */
export type CursorPaginated<T> = {
  next: string | null;
  previous: string | null;
  results: T[];
};

/** Paramètres de liste acceptés par le backend (clés métier optionnelles + index ouvert). */
export type ListParams = {
  page?: number;
  page_size?: number;
  search?: string;
  ordering?: string;
  type?: string;
  acces?: string;
  mine?: number | string | boolean;
  auteur?: number | string;
  conversation?: number | string;
  cursor?: string | null;
  feed?: string;
  espace?: number | string;
  invite?: string;
  q?: string;
  limit?: number | string;
  ref?: string;
  path?: string;
  tag?: string;
  [key: string]: string | number | boolean | null | undefined;
};

/** Extrait le paramètre `cursor` d'une URL `next` / `previous` DRF. */
export const cursorFromUrl = (url: string | null | undefined): string | undefined => {
  if (!url) return undefined;
  try {
    const parsed = new URL(url, "http://localhost");
    return parsed.searchParams.get("cursor") ?? undefined;
  } catch {
    const match = /(?:\?|&)cursor=([^&]+)/.exec(url);
    return match ? decodeURIComponent(match[1]) : undefined;
  }
};

/** Chaîne de requête (« ?page=2&search=abc ») sans les paramètres vides ; chaîne vide s'il n'y en a aucun. */
export const toQueryString = (params?: ListParams | Record<string, string | number | boolean | null | undefined> | void): string => {
  if (!params) return "";
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      query.set(key, String(value));
    }
  });
  const text = query.toString();
  return text ? `?${text}` : "";
};

/** Nombre de pages pour `count` éléments (au moins 1, pour que le tableau vide ait une page). */
export const pageCountOf = (count: number, pageSize: number = PAGE_SIZE): number =>
  Math.max(1, Math.ceil(count / pageSize));

/** Paramètre `ordering` du backend à partir de l'état de tri de TanStack Table (premier tri seulement). */
export const orderingOf = (
  sorting: ReadonlyArray<{ id: string; desc: boolean }>
): string | undefined =>
  sorting.length > 0 ? `${sorting[0].desc ? "-" : ""}${sorting[0].id}` : undefined;

type PageResult<T> =
  | { data: Paginated<T>; error?: undefined }
  | { data?: undefined; error: FetchBaseQueryError };

/**
 * Lit toutes les pages d'une liste paginée côté serveur et renvoie les éléments à plat.
 * Pour les listes bornées par nature (invitations, avis, ordinateurs connectés) que l'interface affiche en entier :
 * le serveur reste paginé (100 éléments par requête au plus), la liste complète est reconstituée ici.
 * `fetchPage` reçoit la chaîne de requête de la page (« ?page=2&page_size=100 »).
 */
export const fetchAllPages = async <T>(
  fetchPage: (queryString: string) => unknown
): Promise<{ data: T[] } | { error: FetchBaseQueryError }> => {
  const items: T[] = [];
  for (let page = 1; page <= MAX_PAGES; page += 1) {
    const result = (await fetchPage(
      toQueryString({ page, page_size: MAX_PAGE_SIZE })
    )) as PageResult<T>;
    if (result.error) return { error: result.error };
    items.push(...result.data.results);
    if (!result.data.next) break;
  }
  return { data: items };
};
