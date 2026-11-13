/**
 * Mémorise la page où se trouvait l'utilisateur quand sa session expire,
 * pour l'y ramener après sa reconnexion.
 *
 * Stocké dans sessionStorage (propre à l'onglet, survit à un rechargement,
 * disparaît à la fermeture de l'onglet).
 */

export const REDIRECT_STORAGE_KEY = "auth.redirect_after_login";

/** Page de destination par défaut après connexion (accueil). */
export const DEFAULT_REDIRECT_PATH = "/";

/** Pages publiques d'authentification : jamais mémorisées (on n'y revient pas après connexion). */
export const PUBLIC_AUTH_PATHS = ["/login", "/forgot-password", "/welcome"];

/**
 * N'accepte que des chemins internes : commence par "/" (mais pas "//" ni "/\"),
 * ce qui empêche une redirection vers un site externe, et exclut les pages publiques d'authentification.
 */
export const isSafeRedirectPath = (path: unknown): path is string => {
  if (typeof path !== "string" || !path.startsWith("/")) return false;
  if (path.startsWith("//") || path.startsWith("/\\")) return false;
  const pathname = path.split(/[?#]/)[0];
  return !PUBLIC_AUTH_PATHS.includes(pathname);
};

const getCurrentPath = () =>
  window.location.pathname + window.location.search + window.location.hash;

/** Sauvegarde le chemin donné, ou la page courante par défaut. Sans effet si le chemin est invalide. */
export const saveRedirectPath = (path: string = getCurrentPath()) => {
  if (!isSafeRedirectPath(path)) return;
  try {
    sessionStorage.setItem(REDIRECT_STORAGE_KEY, path);
  } catch (error) {
    // sessionStorage indisponible (navigation privée, quota) : la page ne sera pas mémorisée
    console.warn("Impossible de mémoriser la page d'origine :", error);
  }
};

export const clearRedirectPath = () => {
  try {
    sessionStorage.removeItem(REDIRECT_STORAGE_KEY);
  } catch (error) {
    console.warn("Impossible d'oublier la page d'origine :", error);
  }
};

/**
 * Retourne la page à rouvrir après connexion, SANS l'oublier.
 * Retourne `fallback` si rien n'est sauvegardé ou si la valeur est invalide.
 * Lecture idempotente : sûre à appeler pendant un rendu React (StrictMode rend deux fois).
 */
export const peekRedirectPath = (fallback: string = DEFAULT_REDIRECT_PATH): string => {
  let saved: string | null = null;
  try {
    saved = sessionStorage.getItem(REDIRECT_STORAGE_KEY);
  } catch (error) {
    console.warn("Impossible de relire la page d'origine :", error);
  }
  return isSafeRedirectPath(saved) ? saved : fallback;
};

/** Retourne la page à rouvrir après connexion et l'oublie (usage unique). */
export const consumeRedirectPath = (fallback: string = DEFAULT_REDIRECT_PATH): string => {
  const path = peekRedirectPath(fallback);
  clearRedirectPath();
  return path;
};
