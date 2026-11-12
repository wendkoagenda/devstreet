import { Link, useParams } from "react-router-dom";
import { ExternalLink, Star } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { formatDate, initialsOf } from "@/models/marketplace-offers/labels";
import { RequireProfil } from "@/models/marketplace-space/components/guards";
import { countryName } from "@/models/marketplace-space/options";
import { useGetPublicProfileQuery } from "../api";

function ProfileViewContent() {
  const { id } = useParams();
  const { data: profil, isLoading, isError } = useGetPublicProfileQuery(Number(id), {
    skip: !id,
  });

  if (isLoading) return <Skeleton className="mx-auto h-72 w-full max-w-5xl" />;
  if (isError || !profil) {
    return (
      <div className="mx-auto w-full max-w-4xl rounded-lg border border-dashed border-input bg-card p-8 text-center text-sm text-muted-foreground">
        Ce profil n'existe pas ou n'est pas visible.{" "}
        <Link to="/marketplace/offers" className="underline">
          Retour
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
          <span
            className="flex size-14 shrink-0 items-center justify-center rounded-full border border-border bg-muted text-base font-semibold text-foreground"
            aria-hidden
          >
            {initialsOf(profil.name)}
          </span>
          <div className="flex min-w-0 flex-col gap-1">
            <CardTitle className="text-xl">{profil.name}</CardTitle>
            <span className="text-xs text-muted-foreground">
              {[profil.headline, profil.city, countryName(profil.country)].filter(Boolean).join(" · ")}
            </span>
            {profil.rating_avg !== null ? (
              <span className="flex items-center gap-1 text-xs text-muted-foreground">
                <Star className="size-3.5" aria-hidden />
                {profil.rating_avg} / 5 · {profil.reviews_count} avis
              </span>
            ) : null}
          </div>
        </CardHeader>
        <CardContent className="flex flex-col gap-6">
          {profil.bio ? (
            <p className="whitespace-pre-line text-sm leading-relaxed text-foreground">{profil.bio}</p>
          ) : null}

          {profil.experiences.length > 0 ? (
            <section className="flex flex-col gap-3">
              <h2 className="text-sm font-semibold text-foreground">Expériences</h2>
              {profil.experiences.map((experience) => (
                <div key={experience.id} className="flex flex-col gap-0.5 border-l-2 border-border pl-3">
                  <span className="text-sm font-medium text-foreground">
                    {experience.title}, {experience.company_name}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {formatDate(experience.start_date)} –{" "}
                    {experience.is_current || !experience.end_date ? "aujourd'hui" : formatDate(experience.end_date)}
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

          {profil.skills_detail.length > 0 ? (
            <section className="flex flex-col gap-2">
              <h2 className="text-sm font-semibold text-foreground">Compétences</h2>
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
            <section className="flex flex-col gap-1">
              <h2 className="text-sm font-semibold text-foreground">Langues</h2>
              <p className="text-sm text-muted-foreground">{profil.languages.join(", ")}</p>
            </section>
          ) : null}

          {profil.reviews.length > 0 ? (
            <section className="flex flex-col gap-3">
              <h2 className="text-sm font-semibold text-foreground">Avis</h2>
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
          <CardTitle className="text-sm">Contact et liens</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <div className="flex flex-wrap gap-1.5">
            <Badge variant={profil.is_open_to_work ? "default" : "secondary"}>
              {profil.is_open_to_work ? "Ouvert aux opportunités" : "Non disponible"}
            </Badge>
            <Badge variant="outline">{profil.years_of_experience} an(s) d'expérience</Badge>
          </div>
          {profil.email ? (
            <Button asChild>
              <a href={`mailto:${profil.email}`}>Contacter</a>
            </Button>
          ) : (
            <p className="text-xs text-muted-foreground">
              Les coordonnées sont visibles après une candidature, une connexion ou l'ajout au vivier.
            </p>
          )}
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
            Membre depuis le {formatDate(profil.member_since)}
          </span>
        </CardContent>
      </Card>
    </div>
  );
}

/** Fiche d'un profil : expériences, compétences, avis publics et coordonnées selon les droits du lecteur. */
export default function ProfileViewPage() {
  return (
    <RequireProfil>
      <ProfileViewContent />
    </RequireProfil>
  );
}
