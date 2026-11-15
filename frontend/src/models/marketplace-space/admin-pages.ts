import type { usePermissions } from "@/hooks/use-permissions";

type PermissionKey = keyof ReturnType<typeof usePermissions>;

/** Pages d'administration des 13 modèles de la marketplace (CRUD généré), réservées aux rôles qui en ont la permission. */
export const MARKETPLACE_ADMIN_PAGES: {
  titleKey: string;
  descriptionKey: string;
  path: string;
  permission: PermissionKey;
}[] = [
  {
    titleKey: "marketplace.admin.companies",
    descriptionKey: "marketplace.admin.companies_desc",
    path: "/admin/marketplace/companies",
    permission: "canViewCompanies",
  },
  {
    titleKey: "marketplace.admin.skills",
    descriptionKey: "marketplace.admin.skills_desc",
    path: "/admin/marketplace/skills",
    permission: "canViewSkills",
  },
  {
    titleKey: "marketplace.admin.profiles",
    descriptionKey: "marketplace.admin.profiles_desc",
    path: "/admin/marketplace/profils",
    permission: "canViewProfils",
  },
  {
    titleKey: "marketplace.admin.offers",
    descriptionKey: "marketplace.admin.offers_desc",
    path: "/admin/marketplace/offers",
    permission: "canViewOffers",
  },
  {
    titleKey: "marketplace.admin.applications",
    descriptionKey: "marketplace.admin.applications_desc",
    path: "/admin/marketplace/candidatures",
    permission: "canViewCandidatures",
  },
  {
    titleKey: "marketplace.admin.profile_skills",
    descriptionKey: "marketplace.admin.profile_skills_desc",
    path: "/admin/marketplace/profil-skills",
    permission: "canViewProfilSkills",
  },
  {
    titleKey: "marketplace.admin.experiences",
    descriptionKey: "marketplace.admin.experiences_desc",
    path: "/admin/marketplace/experiences",
    permission: "canViewExperiences",
  },
  {
    titleKey: "marketplace.admin.services",
    descriptionKey: "marketplace.admin.services_desc",
    path: "/admin/marketplace/prestations",
    permission: "canViewPrestations",
  },
  {
    titleKey: "marketplace.admin.profile_history",
    descriptionKey: "marketplace.admin.profile_history_desc",
    path: "/admin/marketplace/profil-histories",
    permission: "canViewProfilHistories",
  },
  {
    titleKey: "marketplace.admin.availabilities",
    descriptionKey: "marketplace.admin.availabilities_desc",
    path: "/admin/marketplace/availabilities",
    permission: "canViewAvailabilities",
  },
  {
    titleKey: "marketplace.admin.reviews",
    descriptionKey: "marketplace.admin.reviews_desc",
    path: "/admin/marketplace/reviews",
    permission: "canViewReviews",
  },
  {
    titleKey: "marketplace.admin.swipes",
    descriptionKey: "marketplace.admin.swipes_desc",
    path: "/admin/marketplace/swipes",
    permission: "canViewSwipes",
  },
  {
    titleKey: "marketplace.admin.connections",
    descriptionKey: "marketplace.admin.connections_desc",
    path: "/admin/marketplace/connections",
    permission: "canViewConnections",
  },
];
