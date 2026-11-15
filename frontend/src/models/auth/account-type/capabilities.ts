import type { AccountType, User } from "../schema";

/**
 * Capacités par type de compte : source unique pour le menu, le garde de routes et la visite guidée.
 * Pour ouvrir une page à un compte entreprise, il suffit d'ajouter son préfixe à ENTREPRISE_ALLOWED_PREFIXES.
 */

export const ONBOARDING_PATH = "/onboarding";

/** Accueil d'un compte entreprise seule (la marketplace, côté recruteur). */
export const ENTREPRISE_HOME_PATH = "/marketplace/my-offers";

/** Accueil des autres comptes : le fil du forum. */
export const DEFAULT_HOME_PATH = "/";

/**
 * Pages accessibles à un compte entreprise seule : la marketplace, plus ce qui la concerne
 * même quand c'est rangé ailleurs (messagerie, profil, compte, profils publics, invitation d'entreprise).
 */
export const ENTREPRISE_ALLOWED_PREFIXES = [
  "/marketplace",
  "/messages",
  "/profil",
  "/my-account",
  "/entreprise",
  "/forum/profil",
  "/forum/u",
  "/hub/profiles",
  ONBOARDING_PATH,
  "/welcome",
  "/login",
  "/forgot-password",
] as const;

const matchesPrefix = (pathname: string, prefix: string) =>
  pathname === prefix || pathname.startsWith(`${prefix}/`);

/** Types simples (dev, entreprise) portés par un type de compte. */
export function splitAccountType(accountType: AccountType | undefined): Array<"dev" | "entreprise"> {
  if (accountType === "both") return ["dev", "entreprise"];
  if (accountType === "dev" || accountType === "entreprise") return [accountType];
  return [];
}

/** Compte entreprise seule : hors administrateur, avec le seul type entreprise. */
export function isEntrepriseOnly(user: Pick<User, "account_type" | "is_admin"> | null): boolean {
  return Boolean(user) && !user?.is_admin && user?.account_type === "entreprise";
}

export function isPathAllowedForEntreprise(pathname: string): boolean {
  return ENTREPRISE_ALLOWED_PREFIXES.some((prefix) => matchesPrefix(pathname, prefix));
}

/** Page d'accueil selon le type de compte. */
export function getHomePath(user: Pick<User, "account_type" | "is_admin"> | null): string {
  return isEntrepriseOnly(user) ? ENTREPRISE_HOME_PATH : DEFAULT_HOME_PATH;
}

/**
 * Redirection imposée par le type de compte, ou null si la page est autorisée :
 * - choix du type obligatoire tant qu'il n'est pas fait (hors administrateur) ;
 * - un compte entreprise seule ne quitte pas la liste des pages autorisées.
 */
export function getAccessRedirect(
  user: Pick<User, "account_type" | "is_admin" | "onboarding_required"> | null,
  pathname: string
): string | null {
  if (!user) return null;
  if (user.onboarding_required && !matchesPrefix(pathname, ONBOARDING_PATH)) {
    return ONBOARDING_PATH;
  }
  if (isEntrepriseOnly(user) && !isPathAllowedForEntreprise(pathname)) {
    return ENTREPRISE_HOME_PATH;
  }
  return null;
}
