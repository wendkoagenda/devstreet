/** Sections de la page de profil d'un membre (paramètre `?section=`). */
export type ProfileSection =
  | "publications"
  | "projets"
  | "contributions"
  | "dev"
  | "entreprise";

/** Mon profil dev (profil pro) : raccourci vers l'onglet « Profil dev » de ma page de profil. */
export const MY_DEV_PROFILE_PATH = "/profil/me?section=dev";

/** Adresse unique du profil d'un membre : /profil/<nom d'utilisateur>. */
export function profilePath(username: string, section?: ProfileSection): string {
  const base = `/profil/${encodeURIComponent(username)}`;
  return section && section !== "publications" ? `${base}?section=${section}` : base;
}
