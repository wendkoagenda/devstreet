import { useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { usePermissions } from "@/hooks/use-permissions";
import { useAuthSlice } from "@/models/auth/slice";
import { saveRedirectPath } from "@/models/auth/functions/redirect-after-login";
import {
  PROJECT_CREATE,
  PROJECT_STAR,
} from "@/models/auth/permissions/constants";

/**
 * Session et droits DevStreet Hub lus dans le socle IAM existant. Ces indicateurs ne servent qu'à
 * adapter l'affichage : chaque action reste contrôlée par le serveur.
 */
export function useHubAccess() {
  const navigate = useNavigate();
  const isAuthenticated = useAuthSlice((state) => state.isAuthenticated);
  const isInitialized = useAuthSlice((state) => state.isInitialized);
  const userId = useAuthSlice((state) => state.user?.id ?? null);
  const { hasPermission, isSuperAdmin } = usePermissions();

  /** Envoie le visiteur vers la connexion existante, puis le ramène sur la page courante. */
  const requestLogin = useCallback(() => {
    saveRedirectPath();
    navigate("/login");
  }, [navigate]);

  return {
    isAuthenticated,
    isInitialized,
    userId,
    canCreateProject: isSuperAdmin || hasPermission(PROJECT_CREATE),
    canStarProject: isSuperAdmin || hasPermission(PROJECT_STAR),
    requestLogin,
  };
}
