import { ProfileInitialsAvatar } from "@/components/ui/profile-initials-avatar";
import { Link, Navigate, useParams } from "react-router-dom";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Download, ExternalLink, Pencil, Star } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { CreationErrorSonner } from "@/helpers/api/feed-backs";
import { formatDate } from "@/models/marketplace-offers/labels";
import { downloadCv } from "@/models/marketplace-profile/download-cv";
import { MY_DEV_PROFILE_PATH, profilePath } from "@/helpers/routes/profile-path";
import { countryName } from "@/models/marketplace-space/options";
import { useGetPublicProfileQuery } from "../api";

/** Fiche d'un profil dev : expériences, compétences, avis publics et coordonnées selon les droits du lecteur. */
export function DevProfileView({
  profilId,
  onEdit,
}: {
  profilId: number;
  /** Sur mon propre profil : action du bouton « Mettre à jour » (par défaut, ouvre mon profil dev). */
  onEdit?: () => void;
}) {
  const { t, i18n } = useTranslation();
  const { data: profil, isLoading, isError } = useGetPublicProfileQuery(profilId, {
    skip: !profilId,
  });
  const [downloading, setDownloading] = useState(false);

  const download = async () => {
    if (!profil) return;
    setDownloading(true);
    try {
      await downloadCv(profil.id);
    } catch {
      CreationErrorSonner(t("marketplace.network.download_cv_error"));
    } finally {
      setDownloading(false);
    }
  };

  if (isLoading) return <Skeleton className="mx-auto h-72 w-full max-w-5xl" />;
  if (isError || !profil) {
    return (
      <div className="mx-auto w-full max-w-4xl rounded-lg border border-dashed border-input bg-card p-8 text-center text-sm text-muted-foreground">
        {t("marketplace.network.profile_hidden")}{" "}
        <Link to={MY_DEV_PROFILE_PATH} className="underline">
          {t("marketplace.network.my_dev_profile")}
        </Link>
      </div>
    );
  }

  const links = [
    { label: "GitHub", url: profil.github_url },
    { label: "LinkedIn", url: profil.linkedin_url },
    { label: "Portfolio", url: profil.portfolio_url },
  ].filter((link) => link.url);

  return (
    <div className="mx-auto grid w-full max-w-5xl items-start gap-4 lg:grid-cols-[minmax(0,1fr)_300px]">
      <Card>
        <CardHeader className="flex-row items-center gap-4 space-y-0">
          <ProfileInitialsAvatar name={profil.name} openToWork={profil.is_open_to_work} size="lg" />
          <div className="flex min-w-0 flex-col gap-1">
            <CardTitle className="text-xl">{profil.name}</CardTitle>
            <span className="text-xs text-muted-foreground">
              {[profil.headline, profil.city, countryName(profil.country, i18n.language)]
                .filter(Boolean)
                .join(" · ")}
            </span>
            {profil.rating_avg !== null ? (
              <span className="flex items-center gap-1 text-xs text-muted-foreground">
                <Star className="size-3.5" aria-hidden />
                {t("marketplace.network.reviews_summary", {
                  avg: profil.rating_avg,
                  count: profil.reviews_count,
                })}
              </span>
            ) : null}
          </div>
        </CardHeader>
        <CardContent className="flex flex-col gap-6">
          {profil.bio ? (
            <p className="whitespace-pre-line text-sm leading-relaxed text-foreground">{profil.bio}</p>
          ) : null}

          {profil.experiences.length > 0 ? (
            <section id="dev-experiences" className="flex scroll-mt-4 flex-col gap-3">
              <h2 className="text-sm font-semibold text-foreground">
                {t("marketplace.network.experiences")}
              </h2>
              {profil.experiences.map((experience) => (
                <div key={experience.id} className="flex flex-col gap-0.5 border-l-2 border-border pl-3">
                  <span className="text-sm font-medium text-foreground">
                    {experience.title}, {experience.company_name}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {formatDate(experience.start_date)} –{" "}
                    {experience.is_current || !experience.end_date
                      ? t("marketplace.network.today")
                      : formatDate(experience.end_date)}
                    {experience.location ? ` · ${experience.location}` : ""}
                  </span>
                  {experience.description ? (
                    <span className="text-xs leading-relaxed text-muted-foreground">
                      {experience.description}
                    </span>
                  ) : null}
                </div>
              ))}
            </section>
          ) : null}

          {(profil.prestations?.length ?? 0) > 0 ? (
            <section className="flex flex-col gap-3">
              <h2 className="text-sm font-semibold text-foreground">
                {t("marketplace.network.services")}
              </h2>
              {profil.prestations.map((prestation) => (
                <div key={prestation.id} className="flex flex-col gap-0.5 border-l-2 border-border pl-3">
                  <span className="text-sm font-medium text-foreground">{prestation.title}</span>
                  <span className="text-xs text-muted-foreground">
                    {t("marketplace.network.delivery_meta", {
                      price: Number(prestation.price).toLocaleString(
                        i18n.language.startsWith("fr") ? "fr-FR" : "en-US"
                      ),
                      currency: prestation.currency,
                      days: prestation.delivery_days,
                      revisions: prestation.revisions,
                    })}
                  </span>
                  {prestation.description ? (
                    <span className="text-xs leading-relaxed text-muted-foreground">
                      {prestation.description}
                    </span>
                  ) : null}
                </div>
              ))}
            </section>
          ) : null}

          {profil.skills_detail.length > 0 ? (
            <section id="dev-skills" className="flex scroll-mt-4 flex-col gap-2">
              <h2 className="text-sm font-semibold text-foreground">
                {t("marketplace.network.skills")}
              </h2>
              {profil.skills_detail.map((skill) => (
                <div key={skill.name} className="flex items-center gap-3 text-xs">
                  <span className="w-32 shrink-0 text-foreground">{skill.name}</span>
                  <div
                    className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted"
                    role="progressbar"
                    aria-label={skill.name}
                    aria-valuemin={0}
                    aria-valuemax={5}
                    aria-valuenow={skill.level}
                  >
                    <div className="h-full rounded-full bg-primary" style={{ width: `${(skill.level / 5) * 100}%` }} />
                  </div>
                </div>
              ))}
            </section>
          ) : null}

          {profil.languages.length > 0 ? (
            <section id="dev-languages" className="flex scroll-mt-4 flex-col gap-1">
              <h2 className="text-sm font-semibold text-foreground">
                {t("marketplace.network.languages")}
              </h2>
              <p className="text-sm text-muted-foreground">{profil.languages.join(", ")}</p>
            </section>
          ) : null}

          {profil.reviews.length > 0 ? (
            <section id="dev-reviews" className="flex scroll-mt-4 flex-col gap-3">
              <h2 className="text-sm font-semibold text-foreground">
                {t("marketplace.network.reviews")}
              </h2>
              {profil.reviews.map((review) => (
                <div key={`${review.author}-${review.created_at}`} className="flex flex-col gap-0.5">
                  <span className="text-xs font-medium text-foreground">
                    {review.author} · {review.rating} / 5 · {formatDate(review.created_at)}
                  </span>
                  {review.comment ? (
                    <span className="text-xs text-muted-foreground">{review.comment}</span>
                  ) : null}
                </div>
              ))}
            </section>
          ) : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm">{t("marketplace.network.contact_links")}</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <div className="flex flex-wrap gap-1.5">
            <Badge variant="outline">
              {t("marketplace.network.years_badge", {
                count: profil.years_of_experience,
              })}
            </Badge>
          </div>
          {profil.is_self ? (
            // Mon propre profil : pas de « Contacter », mais un accès direct pour mettre à jour mes informations
            <>
              {onEdit ? (
                <Button type="button" onClick={onEdit}>
                  <Pencil className="size-4" aria-hidden />
                  {t("marketplace.network.update_my_profile")}
                </Button>
              ) : (
                <Button asChild>
                  <Link to={MY_DEV_PROFILE_PATH}>
                    <Pencil className="size-4" aria-hidden />
                    {t("marketplace.network.update_my_profile")}
                  </Link>
                </Button>
              )}
            </>
          ) : profil.email ? (
            <Button asChild>
              <a href={`mailto:${profil.email}`}>{t("marketplace.network.contact")}</a>
            </Button>
          ) : (
            <p className="text-xs text-muted-foreground">
              {t("marketplace.network.contact_locked")}
            </p>
          )}
          {profil.can_download_cv ? (
            <Button type="button" variant="outline" disabled={downloading} onClick={download}>
              <Download className="size-4" />
              {t("marketplace.network.download_cv")}
            </Button>
          ) : null}
          {links.map((link) => (
            <a
              key={link.label}
              href={link.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-xs text-foreground hover:underline"
            >
              <ExternalLink className="size-3.5" aria-hidden />
              {link.label}
            </a>
          ))}
          <span className="text-xs text-muted-foreground">
            {t("marketplace.network.member_since", {
              date: formatDate(profil.member_since),
            })}
          </span>
        </CardContent>
      </Card>
    </div>
  );
}

/** Ancienne fiche /marketplace/profiles/:id → onglet « Profil dev » de la page /profil/<nom>. */
export default function ProfileViewPage() {
  const { t } = useTranslation();
  const { id } = useParams();
  const { data: profil, isLoading, isError } = useGetPublicProfileQuery(Number(id), {
    skip: !id,
  });

  if (isLoading) return <Skeleton className="mx-auto h-72 w-full max-w-5xl" />;
  if (isError || !profil?.username) {
    return (
      <div className="mx-auto w-full max-w-4xl rounded-lg border border-dashed border-input bg-card p-8 text-center text-sm text-muted-foreground">
        {t("marketplace.network.profile_missing")}{" "}
        <Link to="/marketplace/offers" className="underline">
          {t("marketplace.network.back")}
        </Link>
      </div>
    );
  }
  return <Navigate to={profilePath(profil.username, "dev")} replace />;
}
