import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CreationErrorSonner } from "@/helpers/api/feed-backs";
import { formatDate } from "@/models/marketplace-offers/labels";
import { RequireRecruiter } from "@/models/marketplace-space/components/guards";
import { useGetDeckQuery, useSwipeMutation, useUndoSwipeMutation } from "../api";
import { SwipeDeck, type CardFacts } from "../components/swipe-deck";
import type { DeckCard } from "../schema";

function describe(card: DeckCard): CardFacts {
  const rating =
    card.rating_avg !== null
      ? `, note moyenne ${card.rating_avg} / 5 (${card.reviews_count} avis)`
      : "";
  return {
    k1: "Disponible",
    v1: card.available_from ? `dès le ${formatDate(card.available_from)}` : "à convenir",
    k2: "Score recommandation",
    v2: card.score !== null ? `${card.score} / 100` : "Aucune offre ouverte",
    proof: `${card.years_of_experience} an(s) d'expérience${rating}.`,
    source: "Proposé par le moteur de recommandation (score par règles)",
  };
}

function TalentsContent() {
  const { data, isLoading, isError } = useGetDeckQuery("recruit", {
    refetchOnMountOrArgChange: true,
  });
  const [swipe] = useSwipeMutation();
  const [undo] = useUndoSwipeMutation();

  if (isLoading) return <Skeleton className="mx-auto h-96 w-full max-w-md" />;
  if (isError || !data) {
    return (
      <p className="mx-auto max-w-md rounded-lg border border-destructive/40 bg-card p-6 text-sm text-destructive">
        Impossible de charger les profils. Réessayez dans un instant.
      </p>
    );
  }

  return (
    <SwipeDeck
      cards={data}
      title="Découvrir des profils"
      likeVerb="garder le profil dans votre vivier"
      likeStamp="Vivier"
      likeAria="Garder dans le vivier"
      keptLabel={(kept) => `Vivier : ${kept}`}
      describe={describe}
      matchedText={(name) => name}
      emptyAction={
        <Button asChild>
          <Link to="/marketplace/talents/pool">Voir mon vivier</Link>
        </Button>
      }
      onSwipe={async (card, direction) => {
        try {
          return await swipe({ target_id: card.id, direction, context: "recruit" }).unwrap();
        } catch {
          CreationErrorSonner("Impossible d'enregistrer ce choix");
          return null;
        }
      }}
      onUndo={async () => {
        try {
          await undo("recruit").unwrap();
          return true;
        } catch {
          CreationErrorSonner("Impossible d'annuler le dernier choix");
          return false;
        }
      }}
    />
  );
}

/** Talents : parcourir des profils à la façon d'un swipe et constituer le vivier de l'entreprise. */
export default function TalentsPage() {
  return (
    <RequireRecruiter>
      <TalentsContent />
    </RequireRecruiter>
  );
}
