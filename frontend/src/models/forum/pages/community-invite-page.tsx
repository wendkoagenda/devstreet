import { Link, useNavigate, useParams } from "react-router-dom";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  usePreviewInvitationQuery,
  useRejoindreViaInvitationMutation,
} from "../api";

export default function CommunityInvitePage() {
  const { code = "" } = useParams();
  const navigate = useNavigate();
  const { data, isLoading, isError, refetch } = usePreviewInvitationQuery(code, {
    skip: !code,
  });
  const [rejoindre, { isLoading: joining }] = useRejoindreViaInvitationMutation();

  const handleJoin = async () => {
    try {
      await rejoindre(code).unwrap();
      toast.success("Tu as rejoint la communauté");
      navigate(`/forum/communautes/${data?.espace_id}`);
    } catch {
      toast.error("Impossible de rejoindre via ce lien");
    }
  };

  if (!code) {
    return (
      <div className="mx-auto max-w-lg py-10 text-center text-sm text-destructive">
        Lien invalide.
      </div>
    );
  }

  if (isLoading) {
    return (
      <p className="mx-auto max-w-lg py-10 text-center text-sm text-muted-foreground">
        Vérification du lien…
      </p>
    );
  }

  if (isError || !data) {
    return (
      <div className="mx-auto max-w-lg space-y-3 py-10 text-center">
        <p className="text-sm text-destructive">
          Lien d&apos;invitation invalide ou révoqué.
        </p>
        <Button type="button" variant="outline" onClick={() => refetch()}>
          Réessayer
        </Button>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-lg space-y-4 py-6">
      <section className="rounded-2xl border border-border bg-card p-6 text-center">
        <p className="text-xs uppercase tracking-wide text-muted-foreground">
          Invitation
        </p>
        <h1 className="mt-2 text-2xl font-semibold text-foreground">
          {data.espace_nom}
        </h1>
        {data.espace_description ? (
          <p className="mt-2 text-sm text-muted-foreground">
            {data.espace_description}
          </p>
        ) : null}

        <div className="mt-6 flex flex-col gap-2">
          {data.deja_membre ? (
            <Button asChild>
              <Link to={`/forum/communautes/${data.espace_id}`}>
                Ouvrir la communauté
              </Link>
            </Button>
          ) : (
            <Button type="button" disabled={joining} onClick={handleJoin}>
              {joining ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
              Rejoindre
            </Button>
          )}
          {data.previsualisation_autorisee && !data.deja_membre ? (
            <Button asChild variant="outline">
              <Link
                to={`/forum/communautes/${data.espace_id}?invite=${encodeURIComponent(code)}`}
              >
                Prévisualiser
              </Link>
            </Button>
          ) : null}
        </div>
      </section>
    </div>
  );
}
