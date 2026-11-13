import { Link, useNavigate, useParams } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useGetPublicationQuery } from "../api";
import { ChoixSection } from "../components/choix-section";
import { CommentsSection } from "../components/comments-section";
import { PublicationCard } from "../components/publication-card";

export default function PublicationDetailPage() {
  const navigate = useNavigate();
  const { id } = useParams();
  const publicationId = Number(id);
  const { data, isLoading, isError, refetch } = useGetPublicationQuery(
    publicationId,
    { skip: !Number.isFinite(publicationId) || publicationId <= 0 }
  );

  const fallbackHref = (() => {
    if (!data?.espace?.id) return "/";
    if (data.espace.type === "CHAINE") {
      return `/forum/chaines/${data.espace.id}`;
    }
    return `/forum/communautes/${data.espace.id}`;
  })();

  const backLabel = (() => {
    if (data?.espace?.type === "CHAINE") return "Retour à la chaîne";
    if (data?.espace?.type === "COMMUNAUTE") return "Retour à la communauté";
    if (data?.auteur?.id) return "Retour";
    return "Fil d'actualité";
  })();

  const handleBack = () => {
    if (window.history.length > 1) {
      navigate(-1);
      return;
    }
    navigate(fallbackHref);
  };

  if (!Number.isFinite(publicationId) || publicationId <= 0) {
    return (
      <div className="mx-auto max-w-3xl py-10 text-center">
        <p className="text-sm text-destructive">Publication introuvable.</p>
        <Button asChild className="mt-4" variant="outline">
          <Link to="/">Retour au fil</Link>
        </Button>
      </div>
    );
  }

  if (isLoading) {
    return (
      <p className="mx-auto max-w-3xl py-10 text-center text-sm text-muted-foreground">
        Chargement…
      </p>
    );
  }

  if (isError || !data) {
    return (
      <div className="mx-auto max-w-3xl space-y-3 py-10 text-center">
        <p className="text-sm text-destructive">
          Impossible de charger cette publication.
        </p>
        <div className="flex justify-center gap-2">
          <Button type="button" variant="outline" onClick={() => refetch()}>
            Réessayer
          </Button>
          <Button asChild variant="ghost">
            <Link to="/">Retour au fil</Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-3xl space-y-4">
      <Button
        type="button"
        variant="ghost"
        className="-ml-2 gap-2"
        onClick={handleBack}
      >
        <ArrowLeft className="h-4 w-4" />
        {backLabel}
      </Button>
      <PublicationCard publication={data} showFullBody disableCardNav />
      {data.type === "CHOIX" ? <ChoixSection publication={data} /> : null}
      <CommentsSection
        publicationId={data.id}
        publicationType={data.type}
        publicationAuthorId={data.auteur?.id ?? null}
        acceptedReplyId={data.reponse_acceptee ?? null}
        allowAnonymousFeedback={data.type === "APPLICATION"}
        choixOptions={data.type === "CHOIX" ? data.options ?? [] : []}
        defaultOptionId={
          data.type === "CHOIX" ? data.mon_avis_option_id ?? null : null
        }
        commentsClosed={
          data.espace?.type === "CHAINE" &&
          data.espace.commentaires_ouverts === false
        }
      />
    </div>
  );
}
