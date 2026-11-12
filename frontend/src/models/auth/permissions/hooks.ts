import { useCallback, useEffect } from "react";
import { useAuthSlice } from "../slice";
import { useGetUserPermissionsQuery } from "@/models/roles-permissions/Api";
import {
  hasPermission,
  hasAllPermissions,
  hasAnyPermission,
  hasRole,
  hasAllRoles,
  hasAnyRole,
} from "./utils";

/**
 * Hook pour la gestion des permissions utilisateur
 */
export const usePermissions = () => {
  const {
    isAuthenticated,
    permissions,
    user,
    setPermissions,
    getCurrentUserId,
  } = useAuthSlice();

  const userId = getCurrentUserId();

  // Hook RTK Query pour charger les permissions
  const {
    data: permissionsData,
    isLoading: isLoadingPermissions,
    error: permissionsError,
    refetch: refetchPermissions,
  } = useGetUserPermissionsQuery(Number(userId) || 0, {
    skip: !isAuthenticated || !userId,
  });

  // Mettre à jour Zustand dès que RTK Query renvoie les permissions
  useEffect(() => {
    if (permissionsData) {
      setPermissions(permissionsData);
    }
  }, [permissionsData, setPermissions]);

  // Vérification d'une permission spécifique
  const checkPermission = useCallback(
    (permission: string): boolean => {
      return hasPermission(permissions, permission);
    },
    [permissions],
  );

  // Vérification de plusieurs permissions (toutes requises)
  const checkAllPermissions = useCallback(
    (requiredPermissions: string[]): boolean => {
      return hasAllPermissions(permissions, requiredPermissions);
    },
    [permissions],
  );

  // Vérification de plusieurs permissions (au moins une requise)
  const checkAnyPermission = useCallback(
    (requiredPermissions: string[]): boolean => {
      return hasAnyPermission(permissions, requiredPermissions);
    },
    [permissions],
  );

  // Vérification si l'utilisateur a un rôle spécifique
  const checkRole = useCallback(
    (roleName: string): boolean => {
      return hasRole(user?.roles, roleName);
    },
    [user?.roles],
  );

  // Vérification de plusieurs rôles (tous requis)
  const checkAllRoles = useCallback(
    (requiredRoles: string[]): boolean => {
      return hasAllRoles(user?.roles, requiredRoles);
    },
    [user?.roles],
  );

  // Vérification de plusieurs rôles (au moins un requis)
  const checkAnyRole = useCallback(
    (requiredRoles: string[]): boolean => {
      return hasAnyRole(user?.roles, requiredRoles);
    },
    [user?.roles],
  );

  // Rechargement manuel des permissions
  const reloadPermissions = useCallback(async () => {
    if (userId) {
      await refetchPermissions();
    }
  }, [userId, refetchPermissions]);

  return {
    permissions,
    userRoles: user?.roles || [],
    isLoadingPermissions,
    permissionsError,
    hasPermission: checkPermission,
    hasAllPermissions: checkAllPermissions,
    hasAnyPermission: checkAnyPermission,
    hasRole: checkRole,
    hasAllRoles: checkAllRoles,
    hasAnyRole: checkAnyRole,
    reloadPermissions,
  };
};
