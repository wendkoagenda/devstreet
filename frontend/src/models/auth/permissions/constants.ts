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
