import { useEffect, useCallback } from "react";
import { useAuthSlice } from "../slice";
import { useLoginMutation } from "../api";

export const useAuth = () => {
  const isAuthenticated = useAuthSlice((state) => state.isAuthenticated);
  const isInitialized = useAuthSlice((state) => state.isInitialized);
  const loadSession = useAuthSlice((state) => state.loadSession);
  const logout = useAuthSlice((state) => state.logout);
  const initializeAuth = useAuthSlice((state) => state.initializeAuth);

  const [login, { isLoading: isLoginLoading }] = useLoginMutation();

  // Restaure la session depuis les cookies au premier affichage
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  const handleLogin = useCallback(
    async (credentials: { email: string; password: string }) => {
      try {
        // Le serveur pose les cookies HttpOnly ; on charge ensuite le profil et les permissions
        const response = await login(credentials).unwrap();
        if (!(await loadSession())) {
          throw new Error("Session introuvable après la connexion");
        }
        return response;
      } catch (error) {
        console.error("Login failed:", error);
        throw error;
      }
    },
    [login, loadSession]
  );

  // Déconnexion
  const handleLogout = useCallback(async () => {
    await logout();
  }, [logout]);

  return {
    isAuthenticated,
    isLoginLoading,
    isInitialized,
    login: handleLogin,
    logout: handleLogout,
  };
};
