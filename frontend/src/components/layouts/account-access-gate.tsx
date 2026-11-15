import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuthSlice } from "@/models/auth/slice";
import { getAccessRedirect } from "@/models/auth/account-type/capabilities";

/**
 * Garde de routes selon le type de compte (à placer sous AppLayout, autour de toutes les pages) :
 * - le choix du type de compte est imposé tant qu'il n'est pas fait ;
 * - un compte entreprise seule est ramené à la marketplace hors de ses pages autorisées.
 * Les visiteurs non connectés ne sont pas concernés (pages publiques du hub, connexion).
 */
export default function AccountAccessGate() {
  const location = useLocation();
  const isInitialized = useAuthSlice((state) => state.isInitialized);
  const user = useAuthSlice((state) => state.user);

  if (!isInitialized) return null;

  const redirect = getAccessRedirect(user, location.pathname);
  if (redirect) return <Navigate to={redirect} replace />;

  return <Outlet />;
}
