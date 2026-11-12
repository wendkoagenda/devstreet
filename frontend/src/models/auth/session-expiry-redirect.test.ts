// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from "vitest";
import { REDIRECT_STORAGE_KEY } from "./functions/redirect-after-login";

// Aucun appel réseau dans ces tests : la session et la déconnexion sont simulées.
const api = vi.hoisted(() => ({
  fetchSession: vi.fn(),
  logoutRequest: vi.fn(),
}));
vi.mock("./functions/session-api", () => api);
vi.mock("@/helpers/api/csrf", () => ({
  ensureCsrfToken: vi.fn().mockResolvedValue("csrf"),
  resetCsrfToken: vi.fn(),
  API_URL: "/api",
  API_V1_URL: "/api/v1",
  getCsrfToken: vi.fn(),
}));

const SESSION = {
  user: { id: 1, full_name: "Ada L", username: "ada", email: "ada@example.com", roles: ["admin"] },
  permissions: ["users.view"],
};

// Le store garde un état de module (premier chargement) : on le recharge à chaque test.
const loadSlice = async () => {
  vi.resetModules();
  return (await import("./slice")).useAuthSlice;
};

describe("session par cookies et redirection après expiration", () => {
  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
    api.fetchSession.mockReset().mockResolvedValue(null);
    api.logoutRequest.mockReset().mockResolvedValue(undefined);
  });

  it("restaure l'utilisateur et ses permissions depuis le serveur", async () => {
    api.fetchSession.mockResolvedValue(SESSION);
    const useAuthSlice = await loadSlice();
    await useAuthSlice.getState().initializeAuth();

    const state = useAuthSlice.getState();
    expect(state.isAuthenticated).toBe(true);
    expect(state.isInitialized).toBe(true);
    expect(state.user?.email).toBe("ada@example.com");
    expect(state.permissions).toEqual(["users.view"]);
  });

  it("ne garde aucun jeton ni profil dans le navigateur et purge les anciens", async () => {
    localStorage.setItem("accessToken", "ancien");
    localStorage.setItem("refreshToken", "ancien");
    localStorage.setItem("user_full_name", "ancien");
    api.fetchSession.mockResolvedValue(SESSION);

    const useAuthSlice = await loadSlice();
    await useAuthSlice.getState().initializeAuth();

    expect(localStorage.length).toBe(0);
    expect(useAuthSlice.getState()).not.toHaveProperty("accessToken");
    expect(useAuthSlice.getState()).not.toHaveProperty("refreshToken");
  });

  it("mémorise la page ouverte sans session valide (lien direct ou session expirée)", async () => {
    window.history.pushState({}, "", "/elitests?page=3");

    const useAuthSlice = await loadSlice();
    await useAuthSlice.getState().initializeAuth();

    expect(useAuthSlice.getState().isAuthenticated).toBe(false);
    expect(useAuthSlice.getState().isInitialized).toBe(true);
    expect(sessionStorage.getItem(REDIRECT_STORAGE_KEY)).toBe("/elitests?page=3");
  });

  it("affiche l'écran de connexion quand le serveur est injoignable au démarrage", async () => {
    const consoleError = vi.spyOn(console, "error").mockImplementation(() => {});
    api.fetchSession.mockRejectedValue(new TypeError("Failed to fetch"));
    window.history.pushState({}, "", "/login");

    const useAuthSlice = await loadSlice();
    await useAuthSlice.getState().initializeAuth();

    expect(useAuthSlice.getState().isAuthenticated).toBe(false);
    expect(useAuthSlice.getState().isInitialized).toBe(true);
    expect(consoleError).toHaveBeenCalled(); // la cause n'est pas silencieuse
    consoleError.mockRestore();
  });

  it("ne mémorise pas la racine ni les pages publiques d'authentification", async () => {
    for (const path of ["/", "/login", "/forgot-password"]) {
      window.history.pushState({}, "", path);
      const useAuthSlice = await loadSlice();
      await useAuthSlice.getState().initializeAuth();
      expect(sessionStorage.getItem(REDIRECT_STORAGE_KEY)).toBeNull();
    }
  });

  it("ne mémorise rien quand la session est valide au chargement", async () => {
    api.fetchSession.mockResolvedValue(SESSION);
    window.history.pushState({}, "", "/users");

    const useAuthSlice = await loadSlice();
    await useAuthSlice.getState().initializeAuth();

    expect(sessionStorage.getItem(REDIRECT_STORAGE_KEY)).toBeNull();
  });

  it("mémorise la page quand le renouvellement de la session échoue en cours d'utilisation", async () => {
    api.fetchSession.mockResolvedValue(SESSION);
    window.history.pushState({}, "", "/users");

    const useAuthSlice = await loadSlice();
    await useAuthSlice.getState().initializeAuth();
    expect(useAuthSlice.getState().isAuthenticated).toBe(true);

    // L'utilisateur navigue puis le refresh token est refusé (événement émis par base-query)
    window.history.pushState({}, "", "/roles?tab=permissions");
    window.dispatchEvent(new Event("auth:session-expired"));

    expect(useAuthSlice.getState().isAuthenticated).toBe(false);
    expect(useAuthSlice.getState().user).toBeNull();
    expect(sessionStorage.getItem(REDIRECT_STORAGE_KEY)).toBe("/roles?tab=permissions");
  });

  it("ignore l'événement d'expiration quand personne n'est connecté", async () => {
    window.history.pushState({}, "", "/login");
    const useAuthSlice = await loadSlice();
    await useAuthSlice.getState().initializeAuth();
    window.history.pushState({}, "", "/roles");

    window.dispatchEvent(new Event("auth:session-expired"));

    expect(sessionStorage.getItem(REDIRECT_STORAGE_KEY)).toBeNull();
  });

  it("n'en garde pas trace après une déconnexion volontaire, et prévient le serveur", async () => {
    api.fetchSession.mockResolvedValue(SESSION);
    window.history.pushState({}, "", "/users");
    sessionStorage.setItem(REDIRECT_STORAGE_KEY, "/ancienne-page");

    const useAuthSlice = await loadSlice();
    await useAuthSlice.getState().initializeAuth();
    await useAuthSlice.getState().logout();

    expect(api.logoutRequest).toHaveBeenCalledTimes(1);
    expect(useAuthSlice.getState().isAuthenticated).toBe(false);
    expect(useAuthSlice.getState().isInitialized).toBe(true);
    expect(sessionStorage.getItem(REDIRECT_STORAGE_KEY)).toBeNull();
  });

  it("n'interroge le serveur qu'une fois pour des initialisations simultanées", async () => {
    api.fetchSession.mockResolvedValue(SESSION);
    const useAuthSlice = await loadSlice();

    await Promise.all([
      useAuthSlice.getState().initializeAuth(),
      useAuthSlice.getState().initializeAuth(),
      useAuthSlice.getState().initializeAuth(),
    ]);

    expect(api.fetchSession).toHaveBeenCalledTimes(1);
  });
});
