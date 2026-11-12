import { isAdminPermission } from "@/models/auth/permissions/constants";
import { useAuthSlice } from "@/models/auth/slice";
import { ReactNode, useMemo } from "react";

interface RequirePermissionProps {
  permission: string | string[];
  children: ReactNode;
  fallback?: ReactNode;
  loadingState?: ReactNode;
}

export function RequirePermission({
  permission,
  children,
  fallback = null,
  loadingState = null,
}: RequirePermissionProps) {
  const { isAuthenticated, isLoading, permissions } = useAuthSlice();

  const hasRequiredPermission = useMemo(() => {
    if (!isAuthenticated || !permissions) return false;

    // Vérifier si l'utilisateur a toutes les permissions admin
    if (permissions.includes("*")) return true;

    const requiredPermissions = Array.isArray(permission)
      ? permission
      : [permission];

    // Vérifier si l'utilisateur a au moins une des permissions requises
    return requiredPermissions.some(
      (perm) => permissions.includes(perm) || isAdminPermission(perm)
    );
  }, [permissions, permission, isAuthenticated]);

  // État de chargement
  if (isLoading) {
    return <>{loadingState}</>;
  }

  // Non authentifié ou permission manquante
  if (!isAuthenticated || !hasRequiredPermission) {
    return <>{fallback}</>;
  }

  // Permission accordée
  return <>{children}</>;
}
