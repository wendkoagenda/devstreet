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
  ELITEST: {
    category: "elitests",
    actions: {
      VIEW: "elitests.view",
      CREATE: "elitests.create",
      DELETE: "elitests.delete",
      UPDATE: "elitests.update",
    },
  },
  ELITESTY: {
    category: "elitesties",
    actions: {
      VIEW: "elitesties.view",
      CREATE: "elitesties.create",
      DELETE: "elitesties.delete",
      UPDATE: "elitesties.update",
    },
  },
  DRAGON: {
    category: "dragons",
    actions: {
      VIEW: "dragons.view",
      CREATE: "dragons.create",
      DELETE: "dragons.delete",
      UPDATE: "dragons.update",
    },
  },
  FUSION: {
    category: "fusions",
    actions: {
      VIEW: "fusions.view",
      CREATE: "fusions.create",
      DELETE: "fusions.delete",
      UPDATE: "fusions.update",
    },
  },
  GADO: {
    category: "gados",
    actions: {
      VIEW: "gados.view",
      CREATE: "gados.create",
      DELETE: "gados.delete",
      UPDATE: "gados.update",
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

export const ELITEST_VIEW = PERMISSIONS.ELITEST.actions.VIEW;
export const ELITEST_CREATE = PERMISSIONS.ELITEST.actions.CREATE;
export const ELITEST_DELETE = PERMISSIONS.ELITEST.actions.DELETE;
export const ELITEST_UPDATE = PERMISSIONS.ELITEST.actions.UPDATE;

export const ELITESTY_VIEW = PERMISSIONS.ELITESTY.actions.VIEW;
export const ELITESTY_CREATE = PERMISSIONS.ELITESTY.actions.CREATE;
export const ELITESTY_DELETE = PERMISSIONS.ELITESTY.actions.DELETE;
export const ELITESTY_UPDATE = PERMISSIONS.ELITESTY.actions.UPDATE;

export const DRAGON_VIEW = PERMISSIONS.DRAGON.actions.VIEW;
export const DRAGON_CREATE = PERMISSIONS.DRAGON.actions.CREATE;
export const DRAGON_DELETE = PERMISSIONS.DRAGON.actions.DELETE;
export const DRAGON_UPDATE = PERMISSIONS.DRAGON.actions.UPDATE;

export const FUSION_VIEW = PERMISSIONS.FUSION.actions.VIEW;
export const FUSION_CREATE = PERMISSIONS.FUSION.actions.CREATE;
export const FUSION_DELETE = PERMISSIONS.FUSION.actions.DELETE;
export const FUSION_UPDATE = PERMISSIONS.FUSION.actions.UPDATE;

export const GADO_VIEW = PERMISSIONS.GADO.actions.VIEW;
export const GADO_CREATE = PERMISSIONS.GADO.actions.CREATE;
export const GADO_DELETE = PERMISSIONS.GADO.actions.DELETE;
export const GADO_UPDATE = PERMISSIONS.GADO.actions.UPDATE;
