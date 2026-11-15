import { ProfileInitialsAvatar } from "@/components/ui/profile-initials-avatar";
import { Link, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
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
  offerFacts,
} from "../labels";
import type { CandidatureStatus, OfferStatus } from "../schema";

function CandidaturesTable({ offerId }: { offerId: number }) {
  const { t } = useTranslation();
  const { data, isLoading } = useGetOfferCandidaturesQuery(offerId);
  const [decide, { isLoading: isDeciding }] = useDecideCandidatureMutation();

  const change = async (id: number, status: Exclude<CandidatureStatus, "sent">) => {
    try {
      await decide({ id, status }).unwrap();
      CreationSuccessSonner(
        status === "accepted"
          ? t("marketplace.offer_manage.accepted_email")
          : t("marketplace.offer_manage.updated")
      );
    } catch {
      CreationErrorSonner(t("marketplace.offer_manage.update_error"));
    }
  };

  if (isLoading) return <Skeleton className="h-32 w-full" />;
  if (!data || data.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        {t("marketplace.offer_manage.empty_candidatures")}
      </p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>{t("marketplace.offer_manage.col_candidate")}</TableHead>
            <TableHead>{t("marketplace.offer_manage.col_score")}</TableHead>
            <TableHead>{t("marketplace.offer_manage.col_status")}</TableHead>
            <TableHead className="whitespace-nowrap text-right">
              {t("marketplace.offer_manage.col_decision")}
            </TableHead>
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
                    <ProfileInitialsAvatar
                      name={profil?.name ?? ""}
                      openToWork={Boolean(profil?.is_open_to_work)}
                      size="sm"
                    />
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
                    {t(`marketplace.labels.candidature_status.${candidature.status}`, {
                      defaultValue: CANDIDATURE_STATUS_LABELS[candidature.status],
                    })}
                  </Badge>
                </TableCell>
                <TableCell>
                  <div className="flex flex-wrap justify-end gap-1.5">
                    {profil?.email ? (
                      <Button asChild size="sm" variant="ghost">
                        <a href={`mailto:${profil.email}`}>{t("marketplace.contact")}</a>
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
                            {t("marketplace.offer_manage.shortlist")}
                          </Button>
                        ) : null}
                        {candidature.status !== "rejected" ? (
                          <Button
                            size="sm"
                            variant="outline"
                            disabled={isDeciding}
                            onClick={() => change(candidature.id, "rejected")}
                          >
                            {t("marketplace.offer_manage.reject")}
                          </Button>
                        ) : null}
                        <Button
                          size="sm"
                          disabled={isDeciding}
                          onClick={() => change(candidature.id, "accepted")}
                        >
                          {t("marketplace.offer_manage.accept")}
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
  const { t } = useTranslation();
  const { data, isLoading } = useGetRecommendedProfilsQuery(offerId);

  if (isLoading) return <Skeleton className="h-32 w-full" />;
  if (!data || data.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        {t("marketplace.offer_manage.empty_recommended")}
      </p>
    );
  }

  return (
    <div className="grid gap-3 md:grid-cols-2">
      {data.map((talent) => (
        <Link key={talent.id} to={`/marketplace/profiles/${talent.id}`} className="group block">
          <Card className="h-full transition-colors group-hover:bg-muted">
            <CardContent className="flex items-start gap-3 p-4">
              <ProfileInitialsAvatar name={talent.name} openToWork={talent.is_open_to_work} />
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
                {talent.applied ? (
                  <Badge variant="secondary">
                    {t("marketplace.offer_manage.already_applied")}
                  </Badge>
                ) : null}
              </div>
              {talent.score !== undefined ? (
                <ScoreBadge
                  score={talent.score}
                  caption={t("marketplace.offer_manage.score_caption")}
                />
              ) : null}
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  );
}

function OfferManageContent() {
  const { t } = useTranslation();
  const { id } = useParams();
  const offerId = Number(id);
  const { data: offer, isLoading, isError } = useGetMyOfferQuery(offerId, { skip: !id });
  const [updateOffer, { isLoading: isUpdating }] = useUpdateMyOfferMutation();

  const setStatus = async (status: OfferStatus) => {
    try {
      await updateOffer({ id: offerId, status }).unwrap();
      CreationSuccessSonner(
        status === "open"
          ? t("marketplace.offer_manage.published")
          : t("marketplace.offer_manage.closed")
      );
    } catch {
      CreationErrorSonner(t("marketplace.offer_manage.status_error"));
    }
  };

  if (isLoading) return <Skeleton className="mx-auto h-40 w-full max-w-5xl" />;
  if (isError || !offer) {
    return (
      <div className="mx-auto w-full max-w-4xl rounded-lg border border-dashed border-input bg-card p-8 text-center text-sm text-muted-foreground">
        {t("marketplace.offer_manage.missing")}{" "}
        <Link to="/marketplace/my-offers" className="underline">
          {t("marketplace.offer_manage.back_to_my_offers")}
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
              {t(`marketplace.labels.offer_status.${offer.status}`, {
                defaultValue: OFFER_STATUS_LABELS[offer.status],
              })}
            </Badge>
          </h1>
          <span className="text-xs text-muted-foreground">
            {offerFacts(offer).join(" · ")} ·{" "}
            {t("marketplace.offer_manage.views", { count: offer.views_count ?? 0 })}
          </span>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button asChild variant="outline">
            <Link to={`/marketplace/my-offers/${offer.id}/edit`}>
              {t("marketplace.offer_manage.edit")}
            </Link>
          </Button>
          {offer.status === "open" ? (
            <Button variant="outline" disabled={isUpdating} onClick={() => setStatus("closed")}>
              {t("marketplace.offer_manage.close")}
            </Button>
          ) : (
            <Button disabled={isUpdating} onClick={() => setStatus("open")}>
              {t("marketplace.offer_manage.publish")}
            </Button>
          )}
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">
            {t("marketplace.offer_manage.received_applications")}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <CandidaturesTable offerId={offer.id} />
        </CardContent>
      </Card>

      <section className="flex flex-col gap-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-base font-semibold text-foreground">
            {t("marketplace.offer_manage.recommended_title")}
          </h2>
          <span className="text-xs text-muted-foreground">
            {t("marketplace.offer_manage.recommended_sub")}
          </span>
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
