import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { CreationErrorSonner } from "@/helpers/api/feed-backs";
import { formatDate, initialsOf } from "@/models/marketplace-offers/labels";
import { RequireProfil } from "@/models/marketplace-space/components/guards";
import { Link } from "react-router-dom";
import {
  useGetConnectionsQuery,
  useGetDeckQuery,
  useSwipeMutation,
  useUndoSwipeMutation,
} from "../api";
import { SwipeDeck, type CardFacts } from "../components/swipe-deck";
import type { DeckCard } from "../schema";

function describe(card: DeckCard): CardFacts {
  const common = card.common_skills ?? [];
  return {
    k1: "En commun",
    v1: common.length > 0 ? `${common.length} compétence(s)` : "Aucune pour l'instant",
    k2: "Ville",
    v2: card.city || card.country,
    proof: common.length > 0 ? `Compétences partagées : ${common.join(", ")}.` : `${card.years_of_experience} an(s) d'expérience.`,
    source: "Dev proche de vous : compétences et ville en commun",
  };
}

function Connections() {
  const { data, isLoading } = useGetConnectionsQuery();

  return (
    <section id="connections" className="mx-auto flex w-full max-w-3xl flex-col gap-3">
      <h2 className="text-base font-semibold text-foreground">Mes connexions</h2>
      {isLoading ? (
        <Skeleton className="h-20 w-full" />
      ) : data && data.length > 0 ? (
        <div className="grid gap-3 sm:grid-cols-2">
          {data.map((friend) => (
            <Card key={friend.id}>
              <CardContent className="flex items-center gap-3 p-4">
                <span
                  className="flex size-10 shrink-0 items-center justify-center rounded-full border border-border bg-muted text-xs font-semibold"
                  aria-hidden
                >
                  {initialsOf(friend.name)}
                </span>
                <span className="flex min-w-0 flex-1 flex-col">
                  <Link
                    to={`/marketplace/profiles/${friend.id}`}
                    className="truncate text-sm font-semibold text-foreground hover:underline"
                  >
                    {friend.name}
                  </Link>
                  <span className="truncate text-xs text-muted-foreground">
                    Connectés le {formatDate(friend.matched_at)}
                  </span>
                </span>
                {friend.email ? (
                  <Button asChild size="sm" variant="outline">
                    <a href={`mailto:${friend.email}`}>Lui écrire</a>
                  </Button>
                ) : null}
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">
          Pas encore de connexion : quand deux devs se choisissent mutuellement, ils apparaissent ici.
        </p>
      )}
    </section>
  );
}

function NetworkContent() {
  const { data, isLoading, isError } = useGetDeckQuery("network", {
    refetchOnMountOrArgChange: true,
  });
  const [swipe] = useSwipeMutation();
  const [undo] = useUndoSwipeMutation();
  const { data: connections } = useGetConnectionsQuery();

  const seeConnections = () =>
    document.getElementById("connections")?.scrollIntoView({ behavior: "smooth" });

  return (
    <div className="flex flex-col gap-10">
      {isLoading ? (
        <Skeleton className="mx-auto h-96 w-full max-w-md" />
      ) : isError || !data ? (
        <p className="mx-auto max-w-md rounded-lg border border-destructive/40 bg-card p-6 text-sm text-destructive">
          Impossible de charger les profils. Réessayez dans un instant.
        </p>
      ) : (
        <SwipeDeck
          cards={data}
          title="Rencontrer des devs"
          likeVerb="proposer de devenir amis"
          likeStamp="Ami"
          likeAria="Devenir amis"
          keptLabel={(kept) => `Demandes d'amitié : ${kept}`}
          describe={describe}
          matchedText={(name) =>
            `${name} veut aussi être votre ami. Vous pouvez maintenant échanger et coder ensemble.`
          }
          matchedAction={
            <Button onClick={seeConnections}>
              Voir mes connexions{connections && connections.length > 0 ? ` (${connections.length})` : ""}
            </Button>
          }
          emptyAction={<Badge variant="secondary">Revenez demain</Badge>}
          onSwipe={async (card, direction) => {
            try {
              return await swipe({ target_id: card.id, direction, context: "network" }).unwrap();
            } catch {
              CreationErrorSonner("Impossible d'enregistrer ce choix");
              return null;
            }
          }}
          onUndo={async () => {
            try {
              await undo("network").unwrap();
              return true;
            } catch {
              CreationErrorSonner("Impossible d'annuler le dernier choix");
              return false;
            }
          }}
        />
      )}
      <Connections />
    </div>
  );
}

/** Réseau : rencontrer d'autres devs (like réciproque = connexion) et retrouver ses connexions. */
export default function NetworkPage() {
  return (
    <RequireProfil>
      <NetworkContent />
    </RequireProfil>
  );
}
