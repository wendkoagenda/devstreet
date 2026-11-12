export type Permission = {
  category: string;
  actions: Record<string, string>;
};

export const PERMISSIONS = {
  USER: {
    category: "users",
    actions: {
      VIEW: "users.view",
      CREATE: "users.create",
      DELETE: "users.delete",
      UPDATE: "users.update",
    },
  },
  ROLE: {
    category: "roles",
    actions: {
      VIEW: "roles.view",
      CREATE: "roles.create",
      DELETE: "roles.delete",
      UPDATE: "roles.update",
    },
  },
  DEVSTREET_HUB_PROJECT: {
    category: "projects",
    actions: {
      CREATE: "projects.create",
      STAR: "projects.star",
    },
  },
  COMPANY: {
    category: "companies",
    actions: {
      VIEW: "companies.view",
      CREATE: "companies.create",
      DELETE: "companies.delete",
      UPDATE: "companies.update",
    },
  },
  SKILL: {
    category: "skills",
    actions: {
      VIEW: "skills.view",
      CREATE: "skills.create",
      DELETE: "skills.delete",
      UPDATE: "skills.update",
    },
  },
  PROFIL: {
    category: "profils",
    actions: {
      VIEW: "profils.view",
      CREATE: "profils.create",
      DELETE: "profils.delete",
      UPDATE: "profils.update",
    },
  },
  OFFER: {
    category: "offers",
    actions: {
      VIEW: "offers.view",
      CREATE: "offers.create",
      DELETE: "offers.delete",
      UPDATE: "offers.update",
    },
  },
  CANDIDATURE: {
    category: "candidatures",
    actions: {
      VIEW: "candidatures.view",
      CREATE: "candidatures.create",
      DELETE: "candidatures.delete",
      UPDATE: "candidatures.update",
    },
  },
  PROFILSKILL: {
    category: "profil-skills",
    actions: {
      VIEW: "profil-skills.view",
      CREATE: "profil-skills.create",
      DELETE: "profil-skills.delete",
      UPDATE: "profil-skills.update",
    },
  },
  EXPERIENCE: {
    category: "experiences",
    actions: {
      VIEW: "experiences.view",
      CREATE: "experiences.create",
      DELETE: "experiences.delete",
      UPDATE: "experiences.update",
    },
  },
  PRESTATION: {
    category: "prestations",
    actions: {
      VIEW: "prestations.view",
      CREATE: "prestations.create",
      DELETE: "prestations.delete",
      UPDATE: "prestations.update",
    },
  },
  PROFILHISTORY: {
    category: "profil-histories",
    actions: {
      VIEW: "profil-histories.view",
      CREATE: "profil-histories.create",
      DELETE: "profil-histories.delete",
      UPDATE: "profil-histories.update",
    },
  },
  AVAILABILITY: {
    category: "availabilities",
    actions: {
      VIEW: "availabilities.view",
      CREATE: "availabilities.create",
      DELETE: "availabilities.delete",
      UPDATE: "availabilities.update",
    },
  },
  REVIEW: {
    category: "reviews",
    actions: {
      VIEW: "reviews.view",
      CREATE: "reviews.create",
      DELETE: "reviews.delete",
      UPDATE: "reviews.update",
    },
  },
  SWIPE: {
    category: "swipes",
    actions: {
      VIEW: "swipes.view",
      CREATE: "swipes.create",
      DELETE: "swipes.delete",
      UPDATE: "swipes.update",
    },
  },
  CONNECTION: {
    category: "connections",
    actions: {
      VIEW: "connections.view",
      CREATE: "connections.create",
      DELETE: "connections.delete",
      UPDATE: "connections.update",
    },
  },
} as const;

export type PermissionKey = keyof typeof PERMISSIONS;

export const getPermission = (
  entity: PermissionKey,
  action: string
): string => {
  return PERMISSIONS[entity].actions[
    action as keyof (typeof PERMISSIONS)[typeof entity]["actions"]
  ];
};

export const isAdminPermission = (permission: string): boolean => {
  return permission === "*";
};

export type PermissionActions<T extends PermissionKey> = {
  [K in keyof (typeof PERMISSIONS)[T]["actions"]]: string;
};

export const USER_VIEW = PERMISSIONS.USER.actions.VIEW;
export const USER_CREATE = PERMISSIONS.USER.actions.CREATE;
export const USER_DELETE = PERMISSIONS.USER.actions.DELETE;
export const USER_UPDATE = PERMISSIONS.USER.actions.UPDATE;

export const ROLE_VIEW = PERMISSIONS.ROLE.actions.VIEW;
export const ROLE_CREATE = PERMISSIONS.ROLE.actions.CREATE;
export const ROLE_DELETE = PERMISSIONS.ROLE.actions.DELETE;
export const ROLE_UPDATE = PERMISSIONS.ROLE.actions.UPDATE;

export const PROJECT_CREATE = PERMISSIONS.DEVSTREET_HUB_PROJECT.actions.CREATE;
export const PROJECT_STAR = PERMISSIONS.DEVSTREET_HUB_PROJECT.actions.STAR;

export const COMPANY_VIEW = PERMISSIONS.COMPANY.actions.VIEW;
export const COMPANY_CREATE = PERMISSIONS.COMPANY.actions.CREATE;
export const COMPANY_DELETE = PERMISSIONS.COMPANY.actions.DELETE;
export const COMPANY_UPDATE = PERMISSIONS.COMPANY.actions.UPDATE;

export const SKILL_VIEW = PERMISSIONS.SKILL.actions.VIEW;
export const SKILL_CREATE = PERMISSIONS.SKILL.actions.CREATE;
export const SKILL_DELETE = PERMISSIONS.SKILL.actions.DELETE;
export const SKILL_UPDATE = PERMISSIONS.SKILL.actions.UPDATE;

export const PROFIL_VIEW = PERMISSIONS.PROFIL.actions.VIEW;
export const PROFIL_CREATE = PERMISSIONS.PROFIL.actions.CREATE;
export const PROFIL_DELETE = PERMISSIONS.PROFIL.actions.DELETE;
export const PROFIL_UPDATE = PERMISSIONS.PROFIL.actions.UPDATE;

export const OFFER_VIEW = PERMISSIONS.OFFER.actions.VIEW;
export const OFFER_CREATE = PERMISSIONS.OFFER.actions.CREATE;
export const OFFER_DELETE = PERMISSIONS.OFFER.actions.DELETE;
export const OFFER_UPDATE = PERMISSIONS.OFFER.actions.UPDATE;

export const CANDIDATURE_VIEW = PERMISSIONS.CANDIDATURE.actions.VIEW;
export const CANDIDATURE_CREATE = PERMISSIONS.CANDIDATURE.actions.CREATE;
export const CANDIDATURE_DELETE = PERMISSIONS.CANDIDATURE.actions.DELETE;
export const CANDIDATURE_UPDATE = PERMISSIONS.CANDIDATURE.actions.UPDATE;

export const PROFILSKILL_VIEW = PERMISSIONS.PROFILSKILL.actions.VIEW;
export const PROFILSKILL_CREATE = PERMISSIONS.PROFILSKILL.actions.CREATE;
export const PROFILSKILL_DELETE = PERMISSIONS.PROFILSKILL.actions.DELETE;
export const PROFILSKILL_UPDATE = PERMISSIONS.PROFILSKILL.actions.UPDATE;

export const EXPERIENCE_VIEW = PERMISSIONS.EXPERIENCE.actions.VIEW;
export const EXPERIENCE_CREATE = PERMISSIONS.EXPERIENCE.actions.CREATE;
export const EXPERIENCE_DELETE = PERMISSIONS.EXPERIENCE.actions.DELETE;
export const EXPERIENCE_UPDATE = PERMISSIONS.EXPERIENCE.actions.UPDATE;

export const PRESTATION_VIEW = PERMISSIONS.PRESTATION.actions.VIEW;
export const PRESTATION_CREATE = PERMISSIONS.PRESTATION.actions.CREATE;
export const PRESTATION_DELETE = PERMISSIONS.PRESTATION.actions.DELETE;
export const PRESTATION_UPDATE = PERMISSIONS.PRESTATION.actions.UPDATE;

export const PROFILHISTORY_VIEW = PERMISSIONS.PROFILHISTORY.actions.VIEW;
export const PROFILHISTORY_CREATE = PERMISSIONS.PROFILHISTORY.actions.CREATE;
export const PROFILHISTORY_DELETE = PERMISSIONS.PROFILHISTORY.actions.DELETE;
export const PROFILHISTORY_UPDATE = PERMISSIONS.PROFILHISTORY.actions.UPDATE;

export const AVAILABILITY_VIEW = PERMISSIONS.AVAILABILITY.actions.VIEW;
export const AVAILABILITY_CREATE = PERMISSIONS.AVAILABILITY.actions.CREATE;
export const AVAILABILITY_DELETE = PERMISSIONS.AVAILABILITY.actions.DELETE;
export const AVAILABILITY_UPDATE = PERMISSIONS.AVAILABILITY.actions.UPDATE;

export const REVIEW_VIEW = PERMISSIONS.REVIEW.actions.VIEW;
export const REVIEW_CREATE = PERMISSIONS.REVIEW.actions.CREATE;
export const REVIEW_DELETE = PERMISSIONS.REVIEW.actions.DELETE;
export const REVIEW_UPDATE = PERMISSIONS.REVIEW.actions.UPDATE;

export const SWIPE_VIEW = PERMISSIONS.SWIPE.actions.VIEW;
export const SWIPE_CREATE = PERMISSIONS.SWIPE.actions.CREATE;
export const SWIPE_DELETE = PERMISSIONS.SWIPE.actions.DELETE;
export const SWIPE_UPDATE = PERMISSIONS.SWIPE.actions.UPDATE;

export const CONNECTION_VIEW = PERMISSIONS.CONNECTION.actions.VIEW;
export const CONNECTION_CREATE = PERMISSIONS.CONNECTION.actions.CREATE;
export const CONNECTION_DELETE = PERMISSIONS.CONNECTION.actions.DELETE;
export const CONNECTION_UPDATE = PERMISSIONS.CONNECTION.actions.UPDATE;
