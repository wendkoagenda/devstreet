import {
  BaseQueryFn,
  FetchArgs,
  FetchBaseQueryError,
  fetchBaseQuery,
} from "@reduxjs/toolkit/query/react";
import { API_URL, API_V1_URL, ensureCsrfToken } from "./csrf";

/** Événement émis quand la session ne peut plus être renouvelée (le store d'authentification l'écoute). */
export const SESSION_EXPIRED_EVENT = "auth:session-expired";

// Routes publiques : un 401 n'y signifie pas « session expirée » (mauvais identifiants, code invalide…)
const NO_REFRESH_PATHS = [
  "/auth/login",
  "/auth/token/refresh",
  "/auth/csrf",
  "/auth/logout",
  "/auth/forgot-password",
  "/auth/verify-reset-code",
  "/auth/reset-password",
];

let refreshInFlight: Promise<boolean> | null = null;

/**
 * Renouvelle la session : le serveur lit le refresh token dans son cookie HttpOnly et pose de nouveaux cookies.
 * Les appels simultanés partagent un seul renouvellement (le refresh token ne sert qu'une fois).
 * Retourne false si le serveur refuse le renouvellement ; une panne réseau LÈVE (l'appelant décide).
 */
export const refreshSession = (): Promise<boolean> => {
  if (!refreshInFlight) {
    refreshInFlight = (async () => {
      const response = await fetch(`${API_URL}/auth/token/refresh`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: "{}",
      });
      return response.ok;
    })().finally(() => {
      refreshInFlight = null;
    });
  }
  return refreshInFlight;
};

const buildQuery = (baseUrl: string) =>
  fetchBaseQuery({
    baseUrl,
    credentials: "include",
    prepareHeaders: async (headers, { type }) => {
      // Requêtes modifiantes : le jeton CSRF accompagne le cookie de session
      if (type === "mutation") {
        const token = await ensureCsrfToken();
        if (token) headers.set("X-CSRFToken", token);
      }
      return headers;
    },
  });

const urlOf = (args: string | FetchArgs) =>
  typeof args === "string" ? args : args.url;

/**
 * Sur 401 (cookie d'accès expiré) : renouvelle la session puis rejoue la requête une fois.
 * Si le renouvellement échoue, la session est terminée.
 */
const withReauth =
  (
    baseUrl: string
  ): BaseQueryFn<string | FetchArgs, unknown, FetchBaseQueryError> =>
  async (args, api, extraOptions) => {
    const query = buildQuery(baseUrl);
    let result = await query(args, api, extraOptions);

    if (
      result.error?.status === 401 &&
      !NO_REFRESH_PATHS.some((path) => urlOf(args).startsWith(path))
    ) {
      let renewed: boolean;
      try {
        renewed = await refreshSession();
      } catch (error) {
        // Serveur injoignable : la session n'est pas forcément terminée, on garde l'erreur d'origine
        console.error("Renouvellement de la session impossible :", error);
        return result;
      }
      if (renewed) {
        result = await query(args, api, extraOptions);
      }
      if (result.error?.status === 401) {
        window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT));
      }
    }
    return result;
  };

export const baseQuery = withReauth(API_V1_URL);
export const authBaseQuery = withReauth(API_URL);
