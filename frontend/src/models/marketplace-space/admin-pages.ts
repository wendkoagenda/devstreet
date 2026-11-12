import type { usePermissions } from "@/hooks/use-permissions";

type PermissionKey = keyof ReturnType<typeof usePermissions>;

/** Pages d'administration des 13 modèles de la marketplace (CRUD généré), réservées aux rôles qui en ont la permission. */
export const MARKETPLACE_ADMIN_PAGES: {
  title: string;
  description: string;
  path: string;
  permission: PermissionKey;
}[] = [
  { title: "Entreprises", description: "Sociétés qui recrutent", path: "/admin/marketplace/companies", permission: "canViewCompanies" },
  { title: "Compétences", description: "Référentiel des compétences", path: "/admin/marketplace/skills", permission: "canViewSkills" },
  { title: "Profils", description: "Profils des utilisateurs", path: "/admin/marketplace/profils", permission: "canViewProfils" },
  { title: "Offres", description: "Offres publiées par les entreprises", path: "/admin/marketplace/offers", permission: "canViewOffers" },
  { title: "Candidatures", description: "Candidatures aux offres", path: "/admin/marketplace/candidatures", permission: "canViewCandidatures" },
  { title: "Compétences des profils", description: "Niveau par profil et par compétence", path: "/admin/marketplace/profil-skills", permission: "canViewProfilSkills" },
  { title: "Expériences", description: "Parcours professionnel des profils", path: "/admin/marketplace/experiences", permission: "canViewExperiences" },
  { title: "Prestations", description: "Réalisations des profils", path: "/admin/marketplace/prestations", permission: "canViewPrestations" },
  { title: "Historique des profils", description: "Modifications des profils", path: "/admin/marketplace/profil-histories", permission: "canViewProfilHistories" },
  { title: "Disponibilités", description: "Périodes du calendrier des profils", path: "/admin/marketplace/availabilities", permission: "canViewAvailabilities" },
  { title: "Avis", description: "Avis entre profils", path: "/admin/marketplace/reviews", permission: "canViewReviews" },
  { title: "Swipes", description: "Likes et passes", path: "/admin/marketplace/swipes", permission: "canViewSwipes" },
  { title: "Connexions", description: "Mises en relation entre profils", path: "/admin/marketplace/connections", permission: "canViewConnections" },
];
