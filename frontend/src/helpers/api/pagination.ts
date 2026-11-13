/**
 * Listes paginées côté serveur : format de réponse DRF et paramètres de requête.
 * Le serveur pagine, recherche et trie ; le tableau n'a que la page courante.
 */

export const PAGE_SIZE = 20;

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

/** Paramètres de liste acceptés par le backend. */
export type ListParams = {
  page?: number;
  page_size?: number;
  search?: string;
  ordering?: string;
  type?: string;
  auteur?: number | string;
  conversation?: number | string;
  cursor?: string | null;
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
export const toQueryString = (params?: ListParams | void): string => {
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
