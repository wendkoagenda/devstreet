/** Sommaire du guide utilisateur (fichiers sous /guide/…, servis depuis public/guide). */

export type GuidePage = {
  /** Chemin relatif sans .md (ex. forum/fil) */
  slug: string;
  /** Clé i18n pour le titre du sommaire */
  titleKey: string;
};

export type GuideSection = {
  id: string;
  titleKey: string;
  pages: GuidePage[];
};

export const GUIDE_SECTIONS: GuideSection[] = [
  {
    id: "start",
    titleKey: "guide.section_start",
    pages: [
      { slug: "index", titleKey: "guide.page_home" },
      { slug: "demarrage", titleKey: "guide.page_start" },
    ],
  },
  {
    id: "forum",
    titleKey: "guide.section_forum",
    pages: [
      { slug: "forum/index", titleKey: "guide.page_forum" },
      { slug: "forum/fil", titleKey: "guide.page_feed" },
      { slug: "forum/types-publication", titleKey: "guide.page_pub_types" },
      { slug: "forum/communautes", titleKey: "guide.page_communities" },
      { slug: "forum/chaines", titleKey: "guide.page_channels" },
      { slug: "forum/messagerie", titleKey: "guide.page_messages" },
      { slug: "forum/favoris", titleKey: "guide.page_favorites" },
      { slug: "forum/profil-membre", titleKey: "guide.page_member" },
    ],
  },
  {
    id: "marketplace",
    titleKey: "guide.section_marketplace",
    pages: [
      { slug: "marketplace/index", titleKey: "guide.page_marketplace" },
      { slug: "marketplace/explorer-offres", titleKey: "guide.page_offers" },
      { slug: "marketplace/reseau", titleKey: "guide.page_network" },
      { slug: "marketplace/candidatures", titleKey: "guide.page_applications" },
      { slug: "marketplace/disponibilites", titleKey: "guide.page_availability" },
      { slug: "marketplace/cv", titleKey: "guide.page_cv" },
      { slug: "marketplace/mes-offres", titleKey: "guide.page_my_offers" },
      { slug: "marketplace/talents", titleKey: "guide.page_talents" },
      { slug: "marketplace/vivier", titleKey: "guide.page_pool" },
    ],
  },
  {
    id: "projets",
    titleKey: "guide.section_projects",
    pages: [
      { slug: "projets/index", titleKey: "guide.page_projects" },
      { slug: "projets/explorer", titleKey: "guide.page_explore_projects" },
      { slug: "projets/mes-projets", titleKey: "guide.page_my_projects" },
    ],
  },
  {
    id: "admin",
    titleKey: "guide.section_admin",
    pages: [
      { slug: "administration/index", titleKey: "guide.page_admin" },
      { slug: "administration/utilisateurs-roles", titleKey: "guide.page_users_roles" },
      { slug: "administration/marketplace-admin", titleKey: "guide.page_mkt_admin" },
    ],
  },
  {
    id: "compte",
    titleKey: "guide.section_account",
    pages: [
      { slug: "compte/onboarding", titleKey: "guide.page_onboarding" },
      { slug: "compte/mon-profil", titleKey: "guide.page_my_profile" },
    ],
  },
];

export function guideFileUrl(slug: string): string {
  const path = slug === "index" ? "index.md" : `${slug}.md`;
  return `/guide/${path}`;
}

export function isKnownGuideSlug(slug: string): boolean {
  return GUIDE_SECTIONS.some((section) =>
    section.pages.some((page) => page.slug === slug)
  );
}
