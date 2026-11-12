import { useMemo } from "react";
import { useAuthSlice } from "../models/auth/slice";
import { getPermission } from "@/models/auth/permissions/constants";
import { hasPermission } from "@/models/auth/permissions/utils";

export const usePermissions = () => {
  const permissions = useAuthSlice((state) => state.permissions);
  const isAuthenticated = useAuthSlice((state) => state.isAuthenticated);

  return useMemo(() => {
    if (!isAuthenticated) {
      return {
        hasPermission: () => false,

        canViewUsers: false,
        canCreateUsers: false,
        canUpdateUsers: false,
        canDeleteUsers: false,

        canViewRoles: false,
        canCreateRoles: false,
        canUpdateRoles: false,
        canDeleteRoles: false,

        isSuperAdmin: false,
        permissions: [],
      };
    }

    return {
      hasPermission: (permission: string) => hasPermission(permissions, permission),
      canViewUsers: hasPermission(permissions, getPermission("USER", "VIEW")),
      canCreateUsers: hasPermission(permissions, getPermission("USER", "CREATE")),
      canUpdateUsers: hasPermission(permissions, getPermission("USER", "UPDATE")),
      canDeleteUsers: hasPermission(permissions, getPermission("USER", "DELETE")),

      canViewRoles: hasPermission(permissions, getPermission("ROLE", "VIEW")),
      canCreateRoles: hasPermission(permissions, getPermission("ROLE", "CREATE")),
      canUpdateRoles: hasPermission(permissions, getPermission("ROLE", "UPDATE")),
      canDeleteRoles: hasPermission(permissions, getPermission("ROLE", "DELETE")),

      isSuperAdmin: hasPermission(permissions, "*"),
      permissions,
    };
  }, [permissions, isAuthenticated]);
};
