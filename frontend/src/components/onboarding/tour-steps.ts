export type TourStep = {
  id: string;
  /** Sélecteur data-tour ; absent = carte centrée (accueil). */
  target?: string;
  titleKey: string;
  bodyKey: string;
  /** Côté préféré de la carte par rapport à la cible. */
  placement?: "right" | "left" | "bottom" | "top" | "center";
};

/** Parcours premier login : bienvenue puis menus principaux. */
export const APP_TOUR_STEPS: TourStep[] = [
  {
    id: "welcome",
    titleKey: "tour.welcome_title",
    bodyKey: "tour.welcome_body",
    placement: "center",
  },
  {
    id: "forum",
    target: "nav-forum",
    titleKey: "tour.forum_title",
    bodyKey: "tour.forum_body",
    placement: "right",
  },
  {
    id: "communities",
    target: "nav-communities",
    titleKey: "tour.communities_title",
    bodyKey: "tour.communities_body",
    placement: "right",
  },
  {
    id: "channels",
    target: "nav-channels",
    titleKey: "tour.channels_title",
    bodyKey: "tour.channels_body",
    placement: "right",
  },
  {
    id: "messages",
    target: "nav-messages",
    titleKey: "tour.messages_title",
    bodyKey: "tour.messages_body",
    placement: "right",
  },
  {
    id: "favorites",
    target: "nav-favorites",
    titleKey: "tour.favorites_title",
    bodyKey: "tour.favorites_body",
    placement: "right",
  },
  {
    id: "marketplace",
    target: "nav-marketplace",
    titleKey: "tour.marketplace_title",
    bodyKey: "tour.marketplace_body",
    placement: "right",
  },
  {
    id: "projects",
    target: "nav-projects",
    titleKey: "tour.projects_title",
    bodyKey: "tour.projects_body",
    placement: "right",
  },
  {
    id: "search",
    target: "topbar-search",
    titleKey: "tour.search_title",
    bodyKey: "tour.search_body",
    placement: "bottom",
  },
  {
    id: "publish",
    target: "topbar-publish",
    titleKey: "tour.publish_title",
    bodyKey: "tour.publish_body",
    placement: "bottom",
  },
];

export const tourStorageKey = (userId: number | string) =>
  `devstreet.tour.v1.${userId}`;
