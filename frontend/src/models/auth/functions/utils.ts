import { LEGACY_STORAGE_KEYS } from "../constants";

/**
 * Supprime les anciens jetons et informations utilisateur du localStorage
 * (laissés par les versions qui y stockaient la session).
 */
export const purgeLegacyAuthStorage = () => {
  try {
    LEGACY_STORAGE_KEYS.forEach((key) => localStorage.removeItem(key));
  } catch (error) {
    console.warn("localStorage indisponible, purge des anciennes clés ignorée :", error);
  }
};

/**
 * État « non connecté » après un reset (déconnexion, expiration) : on sait qu'il n'y a pas de session,
 * donc l'initialisation est terminée (sinon les routes protégées resteraient blanches).
 */
export const getInitialAuthState = () => ({
  isAuthenticated: false,
  isLoading: false,
  permissions: [],
  user: null,
  isInitialized: true,
});
