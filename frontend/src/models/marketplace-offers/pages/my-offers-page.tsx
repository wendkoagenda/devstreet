import { Link } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { RequireRecruiter } from "@/models/marketplace-space/components/guards";
import { useGetMyOffersQuery } from "../api";
import { OFFER_STATUS_LABELS, formatDate, offerFacts } from "../labels";

function MyOffersContent() {
  const { data, isLoading, isError } = useGetMyOffersQuery();

  return (
    <div className="mx-auto flex w-full max-w-4xl flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-col gap-1">
          <h1 className="text-xl font-semibold text-foreground">Mes offres</h1>
          <p className="text-sm text-muted-foreground">
            Les offres de votre entreprise et les candidatures reçues.
          </p>
        </div>
        <Button asChild>
          <Link to="/marketplace/my-offers/new">Publier une offre</Link>
        </Button>
      </div>

      {isLoading ? (
        <Skeleton className="h-32 w-full" />
      ) : isError ? (
        <p className="rounded-lg border border-destructive/40 bg-card p-6 text-sm text-destructive">
          Impossible de charger vos offres.
        </p>
      ) : data && data.length > 0 ? (
        data.map((offer) => (
          <Link key={offer.id} to={`/marketplace/my-offers/${offer.id}`} className="group block">
            <Card className="transition-colors group-hover:bg-muted">
              <CardContent className="flex flex-wrap items-center gap-4 p-5">
                <div className="flex min-w-0 flex-1 basis-64 flex-col gap-1">
                  <span className="flex flex-wrap items-center gap-2 text-sm font-semibold text-foreground">
                    {offer.title}
                    <Badge variant={offer.status === "open" ? "default" : "secondary"}>
                      {OFFER_STATUS_LABELS[offer.status]}
                    </Badge>
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {offerFacts(offer).join(" · ")}
                    {offer.published_at ? ` · publiée le ${formatDate(offer.published_at)}` : ""}
                  </span>
                </div>
                <div className="flex flex-col items-end text-xs text-muted-foreground">
                  <span className="text-lg font-semibold text-foreground">
                    {offer.candidatures_count ?? 0}
                  </span>
                  candidature(s)
                  {offer.candidatures_new ? (
                    <span className="text-foreground">{offer.candidatures_new} nouvelle(s)</span>
                  ) : null}
                </div>
              </CardContent>
            </Card>
          </Link>
        ))
      ) : (
        <div className="flex flex-col items-center gap-3 rounded-lg border border-dashed border-input bg-card p-8 text-center text-sm text-muted-foreground">
          Vous n'avez pas encore d'offre.
          <Button asChild>
            <Link to="/marketplace/my-offers/new">Publier ma première offre</Link>
          </Button>
        </div>
      )}
    </div>
  );
}

/** Mes offres (recruteur) : liste des offres de l'entreprise avec leur nombre de candidatures. */
export default function MyOffersPage() {
  return (
    <RequireRecruiter>
      <MyOffersContent />
    </RequireRecruiter>
  );
}
