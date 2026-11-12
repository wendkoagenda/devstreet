import { API_URL, resetCsrfToken } from "@/helpers/api/csrf";
import { refreshSession } from "@/helpers/api/base-query";
import { User } from "../schema";

export type SessionData = { user: User; permissions: string[] };

/**
 * Lit la session courante (utilisateur, rôles, permissions lus en base par le serveur).
 * Sur 401 (cookie d'accès expiré), tente un renouvellement puis relit une fois.
 * Retourne null s'il n'y a pas de session valide (401). Toute autre erreur (serveur injoignable,
 * erreur 5xx) LÈVE : elle ne doit pas passer pour une simple absence de session.
 */
export const fetchSession = async (): Promise<SessionData | null> => {
  const read = () => fetch(`${API_URL}/auth/me`, { credentials: "include" });

  let response = await read();
  if (response.status === 401 && (await refreshSession())) {
    response = await read();
  }
  if (response.status === 401) return null;
  if (!response.ok) {
    throw new Error(`Lecture de la session impossible (HTTP ${response.status})`);
  }
  return (await response.json()) as SessionData;
};

/**
 * Déconnexion côté serveur : invalide le refresh token et supprime les cookies.
 * Les erreurs sont ignorées : la déconnexion locale a lieu dans tous les cas.
 */
export const logoutRequest = async (): Promise<void> => {
  try {
    await fetch(`${API_URL}/auth/logout`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: "{}",
    });
  } catch (error) {
    // Serveur injoignable : la déconnexion locale a lieu quand même, mais on garde la trace
    console.error("Déconnexion côté serveur impossible :", error);
  } finally {
    resetCsrfToken();
  }
};
