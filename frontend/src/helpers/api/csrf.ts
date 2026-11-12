import { requireEnv } from "@/config/env";

/**
 * Jeton CSRF : les requêtes authentifiées par cookie HttpOnly doivent renvoyer le jeton dans l'en-tête
 * X-CSRFToken (le cookie `csrftoken` seul ne suffit pas, c'est le principe du « double submit »).
 */

export const API_URL: string = requireEnv(
  "VITE_API_URL",
  import.meta.env.VITE_API_URL
);
export const API_V1_URL: string = requireEnv(
  "VITE_API_V1_URL",
  import.meta.env.VITE_API_V1_URL
);

const CSRF_COOKIE = "csrftoken";

// Repli quand le cookie n'est pas lisible (API sur un autre hôte que la page)
let csrfTokenMemory: string | null = null;

const readCsrfCookie = (): string | null => {
  const entry = document.cookie
    .split("; ")
    .find((row) => row.startsWith(`${CSRF_COOKIE}=`));
  return entry ? decodeURIComponent(entry.slice(CSRF_COOKIE.length + 1)) : null;
};

export const getCsrfToken = (): string | null =>
  readCsrfCookie() ?? csrfTokenMemory;

/** Retourne le jeton CSRF, en le demandant au serveur (qui pose aussi le cookie) s'il manque. */
export const ensureCsrfToken = async (): Promise<string | null> => {
  const existing = getCsrfToken();
  if (existing) return existing;

  try {
    const response = await fetch(`${API_URL}/auth/csrf`, {
      credentials: "include",
    });
    if (response.ok) {
      const data = (await response.json()) as { csrfToken?: string };
      csrfTokenMemory = data.csrfToken ?? null;
    }
  } catch (error) {
    // La requête modifiante qui suit échouera (403) : on garde une trace de la cause
    console.error("Impossible de récupérer le jeton CSRF :", error);
  }
  return getCsrfToken();
};

/** Oublie le jeton mémorisé (déconnexion). */
export const resetCsrfToken = () => {
  csrfTokenMemory = null;
};
