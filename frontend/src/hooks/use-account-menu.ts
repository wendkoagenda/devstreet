import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { profilePath } from "@/helpers/routes/profile-path";
import {
  CreationErrorSonner,
  CreationSuccessSonner,
} from "@/helpers/api/feed-backs";
import { useAuth } from "@/models/auth/hooks/useAuth";
import { useAuthSlice } from "@/models/auth/slice";

/** Logique partagée profil / déconnexion (topbar + sidebar footer). */
export function useAccountMenu() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { logout } = useAuth();
  const user = useAuthSlice((state) => state.user);
  const isAuthenticated = useAuthSlice((state) => state.isAuthenticated);
  const authReady = useAuthSlice((state) => state.isInitialized);

  const displayName =
    user?.full_name || user?.username || t("topbar.profile_fallback");

  const goToProfile = () => {
    if (user?.username) navigate(profilePath(user.username));
    else navigate("/profil/me");
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/welcome", { replace: true });
      CreationSuccessSonner(t("auth.logout_success"));
    } catch (error) {
      console.error("Logout failed:", error);
      CreationErrorSonner(t("auth.logout_error"));
    }
  };

  return {
    user,
    isAuthenticated,
    authReady,
    displayName,
    goToProfile,
    handleLogout,
  };
}
