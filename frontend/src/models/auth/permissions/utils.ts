/**
 * Les rôles et permissions viennent du serveur (GET /api/auth/me) et sont gardés en mémoire dans le store
 * d'authentification. Aucun jeton n'est lu ni décodé côté navigateur.
 */

/**
 * Valide si un utilisateur a une permission spécifique parmi les permissions fournies
 */
export const hasPermission = (
  userPermissions: string[] | null = null,
  permission: string
): boolean => {
  const permissions = userPermissions ?? [];

  if (permissions.length === 0) return false;

  // Vérification exacte
  if (permissions.includes(permission)) return true;

  // Vérification avec wildcards (ex: users.* pour users.create, users.read, etc.)
  return permissions.some((userPerm) => {
    if (userPerm.endsWith(".*")) {
      const basePermission = userPerm.slice(0, -2);
      return permission.startsWith(basePermission + ".");
    }
    return false;
  });
};

/**
 * Vérification de plusieurs permissions (toutes requises)
 */
export const hasAllPermissions = (
  userPermissions: string[] | null = null,
  requiredPermissions: string[]
): boolean => {
  return requiredPermissions.every((permission) =>
    hasPermission(userPermissions, permission)
  );
};

/**
 * Vérification de plusieurs permissions (au moins une requise)
 */
export const hasAnyPermission = (
  userPermissions: string[] | null = null,
  requiredPermissions: string[]
): boolean => {
  return requiredPermissions.some((permission) =>
    hasPermission(userPermissions, permission)
  );
};

/**
 * Vérification si l'utilisateur a un rôle spécifique
 */
export const hasRole = (
  userRoles: string[] | null = null,
  roleName: string
): boolean => {
  return userRoles?.includes(roleName) ?? false;
};

/**
 * Vérification de plusieurs rôles (tous requis)
 */
export const hasAllRoles = (
  userRoles: string[] | null = null,
  requiredRoles: string[]
): boolean => {
  return requiredRoles.every((role) => hasRole(userRoles, role));
};

/**
 * Vérification de plusieurs rôles (au moins un requis)
 */
export const hasAnyRole = (
  userRoles: string[] | null = null,
  requiredRoles: string[]
): boolean => {
  return requiredRoles.some((role) => hasRole(userRoles, role));
};
