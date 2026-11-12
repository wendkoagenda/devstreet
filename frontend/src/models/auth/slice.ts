import { create } from "zustand";
import { AuthState } from "./schema";
import { getInitialAuthState, purgeLegacyAuthStorage } from "./functions/utils";
import { hasPermission as checkPermission } from "./permissions/utils";
import { fetchSession, logoutRequest } from "./functions/session-api";
import {
  clearRedirectPath,
  saveRedirectPath,
} from "./functions/redirect-after-login";
import { SESSION_EXPIRED_EVENT } from "@/helpers/api/base-query";
import { ensureCsrfToken, resetCsrfToken } from "@/helpers/api/csrf";

// Vrai une fois le premier chargement de la page traité (voir internalInitialize)
let startupHandled = false;
// Initialisation en cours (partagée entre les appels simultanés)
let initPromise: Promise<void> | null = null;

/**
 * La session vit dans des cookies HttpOnly posés par le serveur : ce store ne garde que le profil
 * et les permissions (en mémoire), relus via GET /api/auth/me. Aucun jeton n'est accessible au JavaScript.
 */
export const useAuthSlice = create<AuthState>((set, get) => {
  /** Reset complet de l'état en mémoire. */
  const resetAuthState = () => {
    resetCsrfToken();
    set(getInitialAuthState());
  };

  /**
   * Fin de session subie (cookie expiré, renouvellement impossible) :
   * mémorise la page courante pour y revenir après reconnexion, puis réinitialise.
   * À ne pas utiliser pour une déconnexion volontaire (voir logout).
   */
  const expireSession = () => {
    saveRedirectPath();
    resetAuthState();
  };

  /** Lit la session auprès du serveur et met le store à jour. Retourne false s'il n'y en a pas. */
  const loadSession = async (): Promise<boolean> => {
    const session = await fetchSession();
    if (!session) return false;
    set({
      isAuthenticated: true,
      isLoading: false,
      user: session.user,
      permissions: [...session.permissions],
      isInitialized: true,
    });
    return true;
  };

  /** Restaure la session au chargement de la page à partir des cookies. */
  const internalInitialize = async () => {
    set({ isLoading: true });

    // Premier chargement de la page uniquement (et non une ré-initialisation après déconnexion)
    const isStartup = !startupHandled;
    startupHandled = true;

    // Les anciennes versions stockaient jetons et profil dans le localStorage
    purgeLegacyAuthStorage();

    // Prépare le jeton CSRF (cookie lisible) pour les premières requêtes modifiantes
    await ensureCsrfToken();

    try {
      if (await loadSession()) return;
    } catch (error) {
      // Serveur injoignable ou en erreur : on affiche l'écran de connexion, la cause reste dans la console
      console.error("Session illisible au démarrage :", error);
    }

    // Pas de session : ouverture directe d'une page protégée, on y reviendra après connexion
    if (isStartup && window.location.pathname !== "/") {
      saveRedirectPath();
    }
    set({ ...getInitialAuthState(), isInitialized: true });
  };

  // Le renouvellement automatique (voir base-query.ts) a échoué : la session est terminée
  if (typeof window !== "undefined") {
    window.addEventListener(SESSION_EXPIRED_EVENT, () => {
      if (get().isAuthenticated) expireSession();
    });
  }

  return {
    isAuthenticated: false,
    isLoading: true,
    permissions: [],
    user: null,
    isInitialized: false,
    isChangePasswordDialogOpen: false,

    setPermissions: (permissions) => {
      set({ permissions: [...permissions] });
    },

    hasPermission: (permission) => {
      const { permissions } = get();
      return checkPermission(permissions, permission);
    },

    getCurrentUserId: () => {
      const { user } = get();
      return user?.id || null;
    },

    // ======================== MÉTHODES D'AUTHENTIFICATION ========================
    /** À appeler après une connexion réussie : le serveur a posé les cookies, on charge le profil. */
    loadSession,

    logout: async () => {
      // Invalide le refresh token côté serveur et supprime les cookies (erreurs ignorées)
      await logoutRequest();

      resetAuthState();
      // Déconnexion volontaire : on ne ramène pas l'utilisateur à sa page à la prochaine connexion
      clearRedirectPath();
    },

    initializeAuth: async () => {
      // Déjà initialisé (connecté ou non) : après un login ou un logout l'état est tenu à jour par le store
      if (get().isInitialized) return;

      // Plusieurs composants peuvent demander l'initialisation en même temps : une seule requête
      initPromise ??= internalInitialize().finally(() => {
        initPromise = null;
      });
      await initPromise;
    },

    reinitializeAuth: () => {
      resetAuthState();
    },

    // ======================== GESTION DES DIALOGUES ========================
    openChangePasswordDialog: () => {
      set({ isChangePasswordDialogOpen: true });
    },

    closeChangePasswordDialog: () => {
      set({ isChangePasswordDialogOpen: false });
    },
  };
});

// ======================== HOOKS SPÉCIALISÉS ========================
/**
 * Hook pour la gestion du dialogue de changement de mot de passe
 */
export const useChangePasswordDialogStore = () => {
  const isChangePasswordDialogOpen = useAuthSlice(
    (state) => state.isChangePasswordDialogOpen
  );
  const openChangePasswordDialog = useAuthSlice(
    (state) => state.openChangePasswordDialog
  );
  const closeChangePasswordDialog = useAuthSlice(
    (state) => state.closeChangePasswordDialog
  );

  return {
    isChangePasswordDialogOpen,
    openChangePasswordDialog,
    closeChangePasswordDialog,
  };
};
