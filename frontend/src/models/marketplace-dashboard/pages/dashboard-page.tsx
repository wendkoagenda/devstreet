import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import {
  Briefcase,
  CalendarDays,
  Eye,
  Handshake,
  Inbox,
  Send,
  Star,
  Users,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuthSlice } from "@/models/auth/slice";
import { OfferCard } from "@/models/marketplace-offers/components/offer-card";
import { ScoreBadge } from "@/models/marketplace-offers/components/score";
import {
  CANDIDATURE_STATUS_LABELS,
  OFFER_STATUS_LABELS,
  formatDate,
  initialsOf,
} from "@/models/marketplace-offers/labels";
import { AVAILABILITY_LABELS } from "@/models/marketplace-profile/schema";
import { RequireProfil } from "@/models/marketplace-space/components/guards";
import { useGetDashboardQuery } from "../api";
import { ProgressBar, StatCard, StatusBars, WeeklyBars } from "../components/charts";
import type { Dashboard } from "../schema";

function Section({ title, action, children }: { title: string; action?: ReactNode; children: ReactNode }) {
  return (
    <section className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-base font-semibold text-foreground">{title}</h2>
        {action}
      </div>
      {children}
    </section>
  );
}

function Panel({ title, children }: { title: string; children: ReactNode }) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm">{title}</CardTitle>
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}

function Empty({ children }: { children: ReactNode }) {
  return <p className="text-sm text-muted-foreground">{children}</p>;
}

function RecruiterSection({ data }: { data: NonNullable<Dashboard["recruiter"]> }) {
  const received = data.candidatures;
  return (
    <Section
      title={`Recrutement · ${data.company.name}`}
      action={
        <div className="flex gap-2">
          <Button asChild size="sm" variant="outline">
            <Link to="/marketplace/talents">Découvrir des talents</Link>
          </Button>
          <Button asChild size="sm">
            <Link to="/marketplace/my-offers/new">Publier une offre</Link>
          </Button>
        </div>
      }
    >
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Offres ouvertes"
          value={data.offers.open}
          hint={`${data.offers.draft} brouillon(s) · ${data.offers.closed} clôturée(s)`}
          icon={<Briefcase className="size-5" />}
        />
        <StatCard
          label="Candidatures reçues"
          value={received.total}
          hint={`${received.sent} à traiter · ${received.accepted} acceptée(s)`}
          icon={<Inbox className="size-5" />}
        />
        <StatCard label="Vues des offres" value={data.views_total} icon={<Eye className="size-5" />} />
        <StatCard
          label="Vivier de talents"
          value={data.pool_size}
          hint={<Link to="/marketplace/talents/pool" className="underline">Voir le vivier</Link>}
          icon={<Users className="size-5" />}
        />
      </div>

      <div className="grid gap-3 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
        <Panel title="Candidatures reçues par semaine">
          <WeeklyBars weeks={data.weekly} />
        </Panel>
        <Panel title="Où en sont les candidatures">
          <StatusBars counts={received} />
        </Panel>
      </div>

      <div className="grid gap-3 lg:grid-cols-2">
        <Panel title="Offres les plus actives">
          {data.top_offers.length === 0 ? (
            <Empty>Aucune candidature reçue pour le moment.</Empty>
          ) : (
            <ul className="flex flex-col divide-y divide-border">
              {data.top_offers.map((offer) => (
                <li key={offer.id} className="flex items-center justify-between gap-3 py-2 first:pt-0 last:pb-0">
                  <span className="flex min-w-0 flex-col">
                    <Link
                      to={`/marketplace/my-offers/${offer.id}`}
                      className="truncate text-sm font-medium text-foreground hover:underline"
                    >
                      {offer.title}
                    </Link>
                    <span className="text-xs text-muted-foreground">
                      {OFFER_STATUS_LABELS[offer.status]}
                      {offer.candidatures_new ? ` · ${offer.candidatures_new} nouvelle(s)` : ""}
                    </span>
                  </span>
                  <Badge variant="secondary">{offer.candidatures_count}</Badge>
                </li>
              ))}
            </ul>
          )}
        </Panel>

        <Panel title="Dernières candidatures reçues">
          {data.recent_candidatures.length === 0 ? (
            <Empty>Les candidatures arriveront ici dès la publication d'une offre.</Empty>
          ) : (
            <ul className="flex flex-col divide-y divide-border">
              {data.recent_candidatures.map((candidature) => (
                <li key={candidature.id} className="flex items-center gap-3 py-2 first:pt-0 last:pb-0">
                  <span
                    className="flex size-8 shrink-0 items-center justify-center rounded-full border border-border bg-muted text-xs font-semibold"
                    aria-hidden
                  >
                    {initialsOf(candidature.profil.name)}
                  </span>
                  <span className="flex min-w-0 flex-1 flex-col">
                    <Link
                      to={`/marketplace/my-offers/${candidature.offer.id}`}
                      className="truncate text-sm font-medium text-foreground hover:underline"
                    >
                      {candidature.profil.name}
                    </Link>
                    <span className="truncate text-xs text-muted-foreground">
                      {candidature.offer.title} · {formatDate(candidature.created_at)}
                    </span>
                  </span>
                  <Badge variant={candidature.status === "accepted" ? "default" : "secondary"}>
                    {CANDIDATURE_STATUS_LABELS[candidature.status]}
                  </Badge>
                  {candidature.score !== undefined ? (
                    <ScoreBadge score={candidature.score} caption="score" />
                  ) : null}
                </li>
              ))}
            </ul>
          )}
        </Panel>
      </div>
    </Section>
  );
}

function CandidateSection({ data }: { data: Dashboard["candidate"] }) {
  return (
    <Section
      title="Mes candidatures"
      action={
        <Button asChild size="sm" variant="outline">
          <Link to="/marketplace/applications">Tout voir</Link>
        </Button>
      }
    >
      <div className="grid gap-3 lg:grid-cols-[minmax(0,2fr)_minmax(0,3fr)]">
        <Panel title="Suivi">
          {data.counts.total === 0 ? (
            <Empty>
              Vous n'avez pas encore postulé.{" "}
              <Link to="/marketplace/offers" className="underline">
                Voir les offres pour moi
              </Link>
            </Empty>
          ) : (
            <StatusBars counts={data.counts} />
          )}
        </Panel>
        <Panel title="Missions à venir">
          {data.upcoming_missions.length === 0 ? (
            <Empty>Aucune mission planifiée : elles apparaissent quand une candidature est acceptée.</Empty>
          ) : (
            <ul className="flex flex-col divide-y divide-border">
              {data.upcoming_missions.map((mission) => (
                <li key={mission.id} className="flex flex-col gap-0.5 py-2 first:pt-0 last:pb-0">
                  <span className="text-sm font-medium text-foreground">
                    {mission.note.replace(/^Mission : /, "")}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    Du {formatDate(mission.start_date)} au {formatDate(mission.end_date)}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Panel>
      </div>

      {data.recommended_offers.length > 0 ? (
        <div className="flex flex-col gap-3">
          <h3 className="text-sm font-semibold text-foreground">Offres recommandées pour vous</h3>
          {data.recommended_offers.map((offer) => (
            <OfferCard key={offer.id} offer={offer} to={`/marketplace/offers/${offer.id}`} />
          ))}
        </div>
      ) : null}
    </Section>
  );
}

function ProfileSidebar({ data }: { data: Dashboard }) {
  const { completeness, availability, reputation } = data;
  const current = availability.current;
  return (
    <aside className="flex flex-col gap-3">
      <Card>
        <CardHeader className="flex-row items-center justify-between space-y-0 pb-3">
          <CardTitle className="text-sm">Complétude du profil</CardTitle>
          <span className="text-lg font-semibold text-foreground">{completeness.percent} %</span>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <ProgressBar value={completeness.percent} label="Complétude du profil" />
          {completeness.missing.length === 0 ? (
            <Empty>Votre profil est complet.</Empty>
          ) : (
            <>
              <ul className="flex list-disc flex-col gap-1 pl-4 text-xs text-muted-foreground">
                {completeness.missing.slice(0, 4).map((item) => (
                  <li key={item.key}>{item.label}</li>
                ))}
              </ul>
              {completeness.missing.length > 4 ? (
                <span className="text-xs text-muted-foreground">
                  et {completeness.missing.length - 4} autre(s)
                </span>
              ) : null}
              <Button asChild size="sm">
                <Link to="/marketplace/profile">Compléter mon profil</Link>
              </Button>
            </>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-sm">
            <CalendarDays className="size-4" aria-hidden />
            Disponibilité
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-2 text-sm">
          {current ? (
            <>
              <Badge className="w-fit" variant={current.status === "busy" ? "default" : "secondary"}>
                {AVAILABILITY_LABELS[current.status]}
              </Badge>
              <span className="text-xs text-muted-foreground">
                Jusqu'au {formatDate(current.end_date)}
                {current.source === "mission" ? " (mission)" : ""}
              </span>
            </>
          ) : (
            <Empty>Aucune période en cours aujourd'hui.</Empty>
          )}
          {availability.next_available_start ? (
            <span className="text-xs text-muted-foreground">
              Prochaine disponibilité : {formatDate(availability.next_available_start)}
            </span>
          ) : null}
          <Button asChild size="sm" variant="outline">
            <Link to="/marketplace/availability">Gérer mon calendrier</Link>
          </Button>
        </CardContent>
      </Card>

      <div className="grid grid-cols-2 gap-3">
        <StatCard
          label="Réputation"
          value={reputation.rating_avg !== null ? `${reputation.rating_avg} / 5` : "—"}
          hint={`${reputation.reviews_count} avis`}
          icon={<Star className="size-5" />}
        />
        <StatCard
          label="Connexions"
          value={data.connections_count}
          hint={<Link to="/marketplace/network" className="underline">Réseau</Link>}
          icon={<Handshake className="size-5" />}
        />
      </div>
    </aside>
  );
}

function DashboardContent() {
  const user = useAuthSlice((state) => state.user);
  const { data, isLoading, isError } = useGetDashboardQuery();

  if (isLoading) {
    return (
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-4">
        <Skeleton className="h-16 w-full" />
        <Skeleton className="h-28 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }
  if (isError || !data) {
    return (
      <p className="mx-auto w-full max-w-6xl rounded-lg border border-destructive/40 bg-card p-6 text-sm text-destructive">
        Impossible de charger le tableau de bord. Réessayez dans un instant.
      </p>
    );
  }

  const firstName = (user?.full_name || data.profil.name).split(" ")[0];
  const candidateStats = data.candidate;

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-col gap-1">
          <h1 className="text-xl font-semibold text-foreground">Bonjour {firstName}</h1>
          <p className="text-sm text-muted-foreground">
            {data.profil.headline || "Voici l'activité de votre espace marketplace."}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button asChild variant="outline">
            <Link to="/marketplace/offers">
              <Send className="size-4" />
              Offres pour moi
            </Link>
          </Button>
        </div>
      </div>

      <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_300px]">
        <div className="flex min-w-0 flex-col gap-8">
          {data.recruiter ? <RecruiterSection data={data.recruiter} /> : null}
          <CandidateSection data={candidateStats} />
        </div>
        <ProfileSidebar data={data} />
      </div>
    </div>
  );
}

/** Tableau de bord marketplace : activité de recrutement (si l'utilisateur recrute), candidatures, profil et disponibilité. */
export default function DashboardPage() {
  return (
    <RequireProfil>
      <DashboardContent />
    </RequireProfil>
  );
}
