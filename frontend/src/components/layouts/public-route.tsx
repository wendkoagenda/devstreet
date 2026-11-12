import { useEffect, useRef } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@/models/auth/hooks/useAuth";
import {
  clearRedirectPath,
  peekRedirectPath,
} from "@/models/auth/functions/redirect-after-login";

const PublicRoute = () => {
  const { isAuthenticated, isInitialized } = useAuth();

  // Cible de redirection figée dès que l'utilisateur est connecté. Sans cela, le rendu suivant
  // (après l'effacement ci-dessous) viserait l'accueil et <Navigate> relancerait une navigation.
  // La lecture est idempotente, donc sûre pendant un rendu (StrictMode rend deux fois).
  const redirectTarget = useRef<string | null>(null);
  if (!isAuthenticated) {
    redirectTarget.current = null;
  } else if (redirectTarget.current === null) {
    redirectTarget.current = peekRedirectPath();
  }

  // Une fois la navigation lancée, la page mémorisée ne doit plus servir
  useEffect(() => {
    if (isAuthenticated) clearRedirectPath();
  }, [isAuthenticated]);

  if (!isInitialized) {
    return null;
  }

  // Un utilisateur connecté quitte les pages publiques : retour à la page où sa session
  // a expiré si elle est mémorisée, sinon accueil.
  return isAuthenticated ? (
    <Navigate to={redirectTarget.current ?? peekRedirectPath()} replace />
  ) : (
    <Outlet />
  );
};

export default PublicRoute;
