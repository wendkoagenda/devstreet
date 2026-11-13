import { useEffect } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useGetPublicProfileByUsernameQuery } from "../api";

/** Résout /forum/u/:username → /forum/profil/:id */
export default function UsernameProfileRedirectPage() {
  const { username = "" } = useParams<{ username: string }>();
  const navigate = useNavigate();
  const { data, isLoading, isError } = useGetPublicProfileByUsernameQuery(
    username,
    { skip: !username.trim() }
  );

  useEffect(() => {
    if (data?.id) {
      navigate(`/forum/profil/${data.id}`, { replace: true });
    }
  }, [data?.id, navigate]);

  if (isLoading || data?.id) {
    return (
      <p className="py-16 text-center text-sm text-muted-foreground">
        Ouverture du profil…
      </p>
    );
  }

  if (isError || !username.trim()) {
    return (
      <div className="mx-auto max-w-md space-y-3 py-16 text-center">
        <p className="text-sm text-destructive">
          Impossible de trouver @{username || "ce membre"}.
        </p>
        <Button asChild variant="outline">
          <Link to="/">Retour au fil</Link>
        </Button>
      </div>
    );
  }

  return null;
}
