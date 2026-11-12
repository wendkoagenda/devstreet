import { Link, useParams } from "react-router-dom";
import { BadgeCheck } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { RequireProfil } from "@/models/marketplace-space/components/guards";
import { countryName } from "@/models/marketplace-space/options";
import { useGetOfferQuery } from "../api";
import { ScoreBreakdown } from "../components/score";
import {
  CANDIDATURE_STATUS_LABELS,
  formatBudget,
  formatDate,
  offerFacts,
} from "../labels";

function OfferDetailContent() {
  const { id } = useParams();
  const { data: offer, isLoading, isError } = useGetOfferQuery(Number(id), {
    skip: !id,
  });

  if (isLoading) {
    return (
      <div className="mx-auto flex w-full max-w-4xl flex-col gap-4">
        <Skeleton className="h-56 w-full" />
      </div>
    );
  }
  if (isError || !offer) {
    return (
      <div className="mx-auto w-full max-w-4xl rounded-lg border border-dashed border-input bg-card p-8 text-center text-sm text-muted-foreground">
        Cette offre n'existe pas ou n'est plus disponible.{" "}
        <Link to="/marketplace/offers" className="underline">
          Retour aux offres
        </Link>
      </div>
    );
  }

  const place = [offer.city, countryName(offer.country)].filter(Boolean).join(", ");
  const budget = formatBudget(offer);
  const matched = new Set(offer.matched_skill_ids ?? []);
  const canApply = offer.status === "open" && !offer.is_own && !offer.my_candidature;

  return (
    <div className="mx-auto grid w-full max-w-5xl items-start gap-4 lg:grid-cols-[minmax(0,1fr)_320px]">
      <Card>
        <CardHeader className="gap-1">
          <CardTitle className="text-xl">{offer.title}</CardTitle>
          <span className="flex flex-wrap items-center gap-1 text-xs text-muted-foreground">
            {offer.company.name}
            {offer.company.is_verified ? (
              <>
                <BadgeCheck className="size-3.5" aria-hidden />
                entreprise vérifiée
              </>
            ) : null}
            <span>· {place}</span>
          </span>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <div className="flex flex-wrap gap-1.5">
            {offerFacts(offer).map((fact) => (
              <Badge key={fact} variant="secondary">
                {fact}
              </Badge>
            ))}
            {budget ? <Badge variant="secondary">{budget}</Badge> : null}
            {offer.start_date ? (
              <Badge variant="secondary">Dès le {formatDate(offer.start_date)}</Badge>
            ) : null}
          </div>

          <p className="whitespace-pre-line text-sm leading-relaxed text-foreground">
            {offer.description}
          </p>

          {offer.skills.length > 0 ? (
            <div className="flex flex-col gap-2">
              <span className="text-xs font-medium text-muted-foreground">
                Compétences requises
              </span>
              <div className="flex flex-wrap gap-1.5">
                {offer.skills.map((skill) => (
                  <Badge key={skill.id} variant={matched.has(skill.id) ? "default" : "outline"}>
                    {skill.name}
                  </Badge>
                ))}
              </div>
            </div>
          ) : null}

          <div className="flex flex-wrap items-center justify-end gap-2">
            {offer.is_own ? (
              <Button asChild>
                <Link to={`/marketplace/my-offers/${offer.id}`}>Gérer l'offre</Link>
              </Button>
            ) : offer.my_candidature ? (
              <>
                <Badge variant="secondary">
                  Candidature {CANDIDATURE_STATUS_LABELS[offer.my_candidature.status].toLowerCase()}
                </Badge>
                <Button asChild variant="outline">
                  <Link to="/marketplace/applications">Suivre ma candidature</Link>
                </Button>
              </>
            ) : canApply ? (
              <Button asChild>
                <Link to={`/marketplace/offers/${offer.id}/apply`}>Postuler</Link>
              </Button>
            ) : (
              <Badge variant="secondary">Offre fermée</Badge>
            )}
          </div>
        </CardContent>
      </Card>

      {offer.breakdown && offer.score !== undefined ? (
        <Card>
          <CardHeader className="flex-row items-center justify-between space-y-0">
            <CardTitle className="text-sm">Pourquoi cette offre ?</CardTitle>
            <span className="text-lg font-semibold text-foreground">{offer.score}</span>
          </CardHeader>
          <CardContent>
            <ScoreBreakdown items={offer.breakdown} />
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}

/** Fiche d'une offre : description, compétences et détail du score pour le profil connecté. */
export default function OfferDetailPage() {
  return (
    <RequireProfil>
      <OfferDetailContent />
    </RequireProfil>
  );
}
