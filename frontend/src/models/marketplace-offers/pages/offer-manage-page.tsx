import { Link, useParams } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { CreationErrorSonner, CreationSuccessSonner } from "@/helpers/api/feed-backs";
import { RequireRecruiter } from "@/models/marketplace-space/components/guards";
import {
  useDecideCandidatureMutation,
  useGetMyOfferQuery,
  useGetOfferCandidaturesQuery,
  useGetRecommendedProfilsQuery,
  useUpdateMyOfferMutation,
} from "../api";
import { ScoreBadge } from "../components/score";
import {
  CANDIDATURE_STATUS_LABELS,
  OFFER_STATUS_LABELS,
  formatDate,
  initialsOf,
  offerFacts,
} from "../labels";
import type { CandidatureStatus, OfferStatus } from "../schema";

function CandidaturesTable({ offerId }: { offerId: number }) {
  const { data, isLoading } = useGetOfferCandidaturesQuery(offerId);
  const [decide, { isLoading: isDeciding }] = useDecideCandidatureMutation();

  const change = async (id: number, status: Exclude<CandidatureStatus, "sent">) => {
    try {
      await decide({ id, status }).unwrap();
      CreationSuccessSonner(
        status === "accepted"
          ? "Candidature acceptée : le candidat est prévenu par e-mail"
          : "Candidature mise à jour"
      );
    } catch {
      CreationErrorSonner("Impossible de mettre à jour la candidature");
    }
  };

  if (isLoading) return <Skeleton className="h-32 w-full" />;
  if (!data || data.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        Aucune candidature pour le moment.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Candidat</TableHead>
            <TableHead>Score</TableHead>
            <TableHead>Statut</TableHead>
            <TableHead className="text-right">Décision</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((candidature) => {
            const profil = candidature.profil;
            const locked = candidature.status === "accepted";
            return (
              <TableRow key={candidature.id}>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <span
                      className="flex size-8 shrink-0 items-center justify-center rounded-full border border-border bg-muted text-xs font-semibold"
                      aria-hidden
                    >
                      {initialsOf(profil?.name ?? "")}
                    </span>
                    <span className="flex flex-col">
                      <Link
                        to={`/marketplace/profiles/${profil?.id}`}
                        className="text-sm font-medium text-foreground hover:underline"
                      >
                        {profil?.name}
                      </Link>
                      <span className="text-xs text-muted-foreground">
                        {profil?.headline} · {formatDate(candidature.created_at)}
                      </span>
                      {candidature.message ? (
                        <span className="mt-1 max-w-sm text-xs text-muted-foreground">
                          « {candidature.message} »
                        </span>
                      ) : null}
                    </span>
                  </div>
                </TableCell>
                <TableCell className="font-semibold">{candidature.score}</TableCell>
                <TableCell>
                  <Badge variant={candidature.status === "accepted" ? "default" : "secondary"}>
                    {CANDIDATURE_STATUS_LABELS[candidature.status]}
                  </Badge>
                </TableCell>
                <TableCell>
                  <div className="flex flex-wrap justify-end gap-1.5">
                    {profil?.email ? (
                      <Button asChild size="sm" variant="ghost">
                        <a href={`mailto:${profil.email}`}>Contacter</a>
                      </Button>
                    ) : null}
                    {!locked ? (
                      <>
                        {candidature.status !== "shortlisted" ? (
                          <Button
                            size="sm"
                            variant="outline"
                            disabled={isDeciding}
                            onClick={() => change(candidature.id, "shortlisted")}
                          >
                            Retenir
                          </Button>
                        ) : null}
                        {candidature.status !== "rejected" ? (
                          <Button
                            size="sm"
                            variant="outline"
                            disabled={isDeciding}
                            onClick={() => change(candidature.id, "rejected")}
                          >
                            Refuser
                          </Button>
                        ) : null}
                        <Button
                          size="sm"
                          disabled={isDeciding}
                          onClick={() => change(candidature.id, "accepted")}
                        >
                          Accepter
                        </Button>
                      </>
                    ) : null}
                  </div>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}

function RecommendedProfils({ offerId }: { offerId: number }) {
  const { data, isLoading } = useGetRecommendedProfilsQuery(offerId);

  if (isLoading) return <Skeleton className="h-32 w-full" />;
  if (!data || data.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        Aucun profil recommandé pour le moment.
      </p>
    );
  }

  return (
    <div className="grid gap-3 md:grid-cols-2">
      {data.map((talent) => (
        <Link key={talent.id} to={`/marketplace/profiles/${talent.id}`} className="group block">
          <Card className="h-full transition-colors group-hover:bg-muted">
            <CardContent className="flex items-start gap-3 p-4">
              <span
                className="flex size-10 shrink-0 items-center justify-center rounded-full border border-border bg-muted text-xs font-semibold"
                aria-hidden
              >
                {initialsOf(talent.name)}
              </span>
              <div className="flex min-w-0 flex-1 flex-col gap-1.5">
                <span className="text-sm font-semibold text-foreground">{talent.name}</span>
                <span className="text-xs text-muted-foreground">
                  {[talent.headline, talent.city].filter(Boolean).join(" · ")}
                </span>
                <div className="flex flex-wrap gap-1">
                  {talent.skills.slice(0, 4).map((skill) => (
                    <Badge key={skill} variant="outline">
                      {skill}
                    </Badge>
                  ))}
                </div>
                {talent.applied ? <Badge variant="secondary">A déjà postulé</Badge> : null}
              </div>
              {talent.score !== undefined ? <ScoreBadge score={talent.score} caption="score" /> : null}
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  );
}

function OfferManageContent() {
  const { id } = useParams();
  const offerId = Number(id);
  const { data: offer, isLoading, isError } = useGetMyOfferQuery(offerId, { skip: !id });
  const [updateOffer, { isLoading: isUpdating }] = useUpdateMyOfferMutation();

  const setStatus = async (status: OfferStatus) => {
    try {
      await updateOffer({ id: offerId, status }).unwrap();
      CreationSuccessSonner(status === "open" ? "Offre publiée" : "Offre clôturée");
    } catch {
      CreationErrorSonner("Impossible de changer le statut de l'offre");
    }
  };

  if (isLoading) return <Skeleton className="mx-auto h-40 w-full max-w-5xl" />;
  if (isError || !offer) {
    return (
      <div className="mx-auto w-full max-w-4xl rounded-lg border border-dashed border-input bg-card p-8 text-center text-sm text-muted-foreground">
        Cette offre n'existe pas.{" "}
        <Link to="/marketplace/my-offers" className="underline">
          Retour à mes offres
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex flex-col gap-1">
          <h1 className="flex flex-wrap items-center gap-2 text-xl font-semibold text-foreground">
            {offer.title}
            <Badge variant={offer.status === "open" ? "default" : "secondary"}>
              {OFFER_STATUS_LABELS[offer.status]}
            </Badge>
          </h1>
          <span className="text-xs text-muted-foreground">
            {offerFacts(offer).join(" · ")} · {offer.views_count ?? 0} vue(s)
          </span>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button asChild variant="outline">
            <Link to={`/marketplace/my-offers/${offer.id}/edit`}>Modifier</Link>
          </Button>
          {offer.status === "open" ? (
            <Button variant="outline" disabled={isUpdating} onClick={() => setStatus("closed")}>
              Clôturer
            </Button>
          ) : (
            <Button disabled={isUpdating} onClick={() => setStatus("open")}>
              Publier
            </Button>
          )}
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Candidatures reçues</CardTitle>
        </CardHeader>
        <CardContent>
          <CandidaturesTable offerId={offer.id} />
        </CardContent>
      </Card>

      <section className="flex flex-col gap-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-base font-semibold text-foreground">
            Profils recommandés pour votre offre
          </h2>
          <span className="text-xs text-muted-foreground">Score calculé sur 100 par règles</span>
        </div>
        <RecommendedProfils offerId={offer.id} />
      </section>
    </div>
  );
}

/** Gestion d'une offre (recruteur) : candidatures et décisions, profils recommandés, statut. */
export default function OfferManagePage() {
  return (
    <RequireRecruiter>
      <OfferManageContent />
    </RequireRecruiter>
  );
}
