// @vitest-environment jsdom
import { StrictMode } from "react";
import { cleanup, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { REDIRECT_STORAGE_KEY } from "@/models/auth/functions/redirect-after-login";
import PublicRoute from "./public-route";

const authState = vi.hoisted(() => ({
  isAuthenticated: false,
  isInitialized: true,
}));

// Comme le vrai hook (mises à jour du store, requêtes de permissions…), ce mock provoque un
// re-rendu de PublicRoute juste après son montage.
vi.mock("@/models/auth/hooks/useAuth", async () => {
  const React = await import("react");
  return {
    useAuth: () => {
      const [, setTick] = React.useState(0);
      React.useEffect(() => {
        setTick(1);
      }, []);
      return authState;
    },
  };
});

/** Affiche l'adresse courante pour vérifier où l'on a réellement atterri. */
const LocationProbe = () => <div data-testid="path">{useLocation().pathname}</div>;

const renderApp = () =>
  render(
    <StrictMode>
      <MemoryRouter initialEntries={["/login"]}>
        <Routes>
          <Route element={<PublicRoute />}>
            <Route element={<div>page-login</div>} path="/login" />
          </Route>
          <Route element={<div>page-accueil</div>} path="/" />
          <Route element={<div>page-roles</div>} path="/roles" />
        </Routes>
      </MemoryRouter>
    </StrictMode>
  );

describe("PublicRoute : redirection d'un utilisateur connecté", () => {
  beforeEach(() => {
    sessionStorage.clear();
    authState.isAuthenticated = false;
    authState.isInitialized = true;
  });
  afterEach(cleanup);

  it("affiche la page publique quand on n'est pas connecté", () => {
    renderApp();
    expect(screen.getByText("page-login")).toBeTruthy();
  });

  it("ramène à la page mémorisée une fois connecté, puis l'oublie", () => {
    sessionStorage.setItem(REDIRECT_STORAGE_KEY, "/roles");
    authState.isAuthenticated = true;

    renderApp();

    expect(screen.getByText("page-roles")).toBeTruthy();
    expect(sessionStorage.getItem(REDIRECT_STORAGE_KEY)).toBeNull();
  });

  it("reste sur la page mémorisée quand PublicRoute se re-rend après le nettoyage", () => {
    // PublicRoute reste monté après la navigation (comme dans l'application, où le store provoque
    // d'autres rendus) : la cible ne doit pas redevenir l'accueil une fois la sauvegarde effacée.
    sessionStorage.setItem(REDIRECT_STORAGE_KEY, "/roles");
    authState.isAuthenticated = true;

    render(
      <StrictMode>
        <MemoryRouter initialEntries={["/login"]}>
          <LocationProbe />
          <Routes>
            <Route element={<PublicRoute />}>
              <Route element={<div>page-login</div>} path="/login" />
              <Route element={<div>page-roles</div>} path="/roles" />
            </Route>
            <Route element={<div>page-accueil</div>} path="/" />
          </Routes>
        </MemoryRouter>
      </StrictMode>
    );

    expect(screen.getByTestId("path").textContent).toBe("/roles");
    expect(sessionStorage.getItem(REDIRECT_STORAGE_KEY)).toBeNull();
  });

  it("va à l'accueil quand rien n'est mémorisé", () => {
    authState.isAuthenticated = true;
    renderApp();
    expect(screen.getByText("page-accueil")).toBeTruthy();
  });

  it("ignore une valeur mémorisée dangereuse", () => {
    sessionStorage.setItem(REDIRECT_STORAGE_KEY, "//evil.example");
    authState.isAuthenticated = true;
    renderApp();
    expect(screen.getByText("page-accueil")).toBeTruthy();
  });
});
