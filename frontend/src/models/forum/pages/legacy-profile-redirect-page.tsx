import { useEffect } from "react";
import {
  Link,
  Navigate,
  useLocation,
  useNavigate,
  useParams,
} from "react-router-dom";
import { Button } from "@/components/ui/button";
import { profilePath, type ProfileSection } from "@/helpers/routes/profile-path";
import { useGetPublicProfileQuery } from "../api";

/**
 * Anciennes adresses par numéro de membre (/forum/profil/:userId, /hub/profiles/:userId)
 * → /profil/<nom d'utilisateur>, en conservant l'onglet demandé.
 */
export default function LegacyProfileRedirectPage({
  section,
}: {
  section?: ProfileSection;
}) {
  const { userId: rawId } = useParams<{ userId: string }>();
  const location = useLocation();
  const navigate = useNavigate();
  const isMeAlias = rawId === "me" || rawId === "moi";
  const userId = Number(rawId);
  const validId = Number.isFinite(userId) && userId > 0;
  const { data, isLoading, isError } = useGetPublicProfileQuery(userId, {
    skip: !validId || isMeAlias,
  });

  useEffect(() => {
    if (!data?.username) return;
    const target = profilePath(data.username, section);
    // Un ?section= déjà présent dans l'ancien lien est conservé s'il n'est pas imposé
    const oldParams = new URLSearchParams(location.search);
    const [pathname, query = ""] = target.split("?");
    const nextParams = new URLSearchParams(query);
    if (!section && oldParams.get("section")) {
      nextParams.set("section", oldParams.get("section") as string);
    }
    navigate(
      {
        pathname,
        search: nextParams.toString() ? `?${nextParams.toString()}` : "",
      },
      { replace: true }
    );
  }, [data?.username, section, location.search, navigate]);

  if (isMeAlias) return <Navigate to="/profil/me" replace />;

  if (validId && (isLoading || data?.username)) {
    return (
      <p className="py-16 text-center text-sm text-muted-foreground">
        Ouverture du profil…
      </p>
    );
  }

  if (!validId || isError) {
    return (
      <div className="mx-auto max-w-md space-y-3 py-16 text-center">
        <p className="text-sm text-muted-foreground">Profil introuvable.</p>
        <Button asChild variant="outline">
          <Link to="/">Retour au fil</Link>
        </Button>
      </div>
    );
  }

  return null;
}
