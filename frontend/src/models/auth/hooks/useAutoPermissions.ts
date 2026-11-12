import { useEffect } from "react";
import { useGetUserPermissionsQuery } from "@/models/roles-permissions/Api";
import { useAuthSlice } from "../slice";

/**
 * Hook qui charge automatiquement les permissions de l'utilisateur
 * et les synchronise avec le store Zustand
 */
export const useAutoPermissions = () => {
  const isAuthenticated = useAuthSlice((state) => state.isAuthenticated);
  const getCurrentUserId = useAuthSlice((state) => state.getCurrentUserId);
  const setPermissions = useAuthSlice((state) => state.setPermissions);

  const userId = getCurrentUserId();

  const {
    data: permissions = [],
    isLoading,
    isError,
  } = useGetUserPermissionsQuery(Number(userId) || 0, {
    skip: !isAuthenticated || !userId,
    refetchOnMountOrArgChange: true,
    refetchOnReconnect: true,
    refetchOnFocus: true,
  });

  // Synchroniser les permissions avec le store Zustand
  useEffect(() => {
    if (permissions && !isLoading && !isError) {
      setPermissions(permissions);
    } else if (isError) {
      setPermissions([]);
    }
  }, [permissions, isLoading, isError, setPermissions]);

  return {
    permissions,
    isLoadingPermissions: isLoading,
    permissionsError: isError,
  };
};
