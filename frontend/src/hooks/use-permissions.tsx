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

        canViewGados: false,
        canCreateGados: false,
        canUpdateGados: false,
        canDeleteGados: false,

        canViewFusions: false,
        canCreateFusions: false,
        canUpdateFusions: false,
        canDeleteFusions: false,

        canViewDragons: false,
        canCreateDragons: false,
        canUpdateDragons: false,
        canDeleteDragons: false,

        canViewElitesties: false,
        canCreateElitesties: false,
        canUpdateElitesties: false,
        canDeleteElitesties: false,

        canViewElitests: false,
        canCreateElitests: false,
        canUpdateElitests: false,
        canDeleteElitests: false,

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

      canViewGados: hasPermission(permissions, getPermission("GADO", "VIEW")),
      canCreateGados: hasPermission(permissions, getPermission("GADO", "CREATE")),
      canUpdateGados: hasPermission(permissions, getPermission("GADO", "UPDATE")),
      canDeleteGados: hasPermission(permissions, getPermission("GADO", "DELETE")),

      canViewFusions: hasPermission(permissions, getPermission("FUSION", "VIEW")),
      canCreateFusions: hasPermission(permissions, getPermission("FUSION", "CREATE")),
      canUpdateFusions: hasPermission(permissions, getPermission("FUSION", "UPDATE")),
      canDeleteFusions: hasPermission(permissions, getPermission("FUSION", "DELETE")),

      canViewDragons: hasPermission(permissions, getPermission("DRAGON", "VIEW")),
      canCreateDragons: hasPermission(permissions, getPermission("DRAGON", "CREATE")),
      canUpdateDragons: hasPermission(permissions, getPermission("DRAGON", "UPDATE")),
      canDeleteDragons: hasPermission(permissions, getPermission("DRAGON", "DELETE")),

      canViewElitesties: hasPermission(permissions, getPermission("ELITESTY", "VIEW")),
      canCreateElitesties: hasPermission(permissions, getPermission("ELITESTY", "CREATE")),
      canUpdateElitesties: hasPermission(permissions, getPermission("ELITESTY", "UPDATE")),
      canDeleteElitesties: hasPermission(permissions, getPermission("ELITESTY", "DELETE")),

      canViewElitests: hasPermission(permissions, getPermission("ELITEST", "VIEW")),
      canCreateElitests: hasPermission(permissions, getPermission("ELITEST", "CREATE")),
      canUpdateElitests: hasPermission(permissions, getPermission("ELITEST", "UPDATE")),
      canDeleteElitests: hasPermission(permissions, getPermission("ELITEST", "DELETE")),

      isSuperAdmin: hasPermission(permissions, "*"),
      permissions,
    };
  }, [permissions, isAuthenticated]);
};
