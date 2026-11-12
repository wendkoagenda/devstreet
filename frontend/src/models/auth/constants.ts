/**
 * Constantes pour la gestion de l'authentification
 *
 * La session vit dans des cookies HttpOnly posés par le serveur : le JavaScript ne stocke aucun jeton.
 */

// Anciennes clés du localStorage (avant les cookies HttpOnly) : purgées au démarrage
export const LEGACY_STORAGE_KEYS = [
  "accessToken",
  "refreshToken",
  "isAuthenticated",
  "tokenCreatedAt",
  "user",
  "user_id",
  "user_email",
  "user_username",
  "user_full_name",
  "user_roles",
] as const;
