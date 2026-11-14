import { Link } from "react-router-dom";
import { formatDate } from "@/models/marketplace-offers/labels";
import { AVAILABILITY_LABELS } from "@/models/marketplace-profile/schema";
import { useStats } from "../api";
import { StatsStrip, type StatItem } from "./stats-strip";

/** Mes offres (entreprise) : offres ouvertes, brouillons et clôturées, candidatures à traiter, vues. */
export function OffersStatsStrip() {
  const { data, isLoading } = useStats("offers");
  const items: StatItem[] = data
    ? [
        { label: "Offres ouvertes", value: data.open },
        { label: "Brouillons / clôturées", value: `${data.draft} / ${data.closed}` },
        {
          label: "Candidatures à traiter",
          value: data.to_process,
          hint: data.to_process > 0 ? "Nouvelles, pas encore examinées" : undefined,
          highlight: data.to_process > 0,
        },
        { label: "Vues des offres", value: data.views_total },
      ]
    : [];
  return <StatsStrip items={items} isLoading={isLoading} />;
}

/** Vivier (entreprise) : talents gardés, ajoutés cette semaine, ouverts aux opportunités. */
export function PoolStatsStrip() {
  const { data, isLoading } = useStats("pool");
  const items: StatItem[] = data
    ? [
        { label: "Talents gardés", value: data.total },
        { label: "Ajoutés cette semaine", value: data.this_week },
        { label: "Ouverts aux opportunités", value: data.open_to_work },
      ]
    : [];
  return <StatsStrip items={items} isLoading={isLoading} />;
}

/** Mes candidatures (dev) : par statut, avec les missions à venir. */
export function ApplicationsStatsStrip() {
  const { data, isLoading } = useStats("applications");
  const items: StatItem[] = data
    ? [
        { label: "Envoyées", value: data.sent },
        { label: "Présélectionnées", value: data.shortlisted },
        {
          label: "Acceptées",
          value: data.accepted,
          hint: data.upcoming_missions > 0 ? `${data.upcoming_missions} mission(s) à venir` : undefined,
          highlight: data.accepted > 0,
        },
        { label: "Refusées", value: data.rejected },
      ]
    : [];
  return <StatsStrip items={items} isLoading={isLoading} />;
}

/** Mes disponibilités (dev) : statut du jour, prochaine disponibilité, missions à venir. */
export function AvailabilityStatsStrip() {
  const { data, isLoading } = useStats("availability");
  const items: StatItem[] = data
    ? [
        {
          label: "Aujourd'hui",
          // Sans période, le membre est disponible
          value: data.current ? AVAILABILITY_LABELS[data.current.status] : "Disponible",
          hint: data.current ? `Jusqu'au ${formatDate(data.current.end_date)}` : "Aucune période occupée",
        },
        {
          label: "Prochaine disponibilité",
          value: data.next_available_start ? formatDate(data.next_available_start) : data.current ? "—" : "Maintenant",
        },
        { label: "Missions à venir", value: data.upcoming_missions },
      ]
    : [];
  return <StatsStrip items={items} isLoading={isLoading} />;
}

/** Mon CV (dev) : complétude du profil et ce qui manque. */
export function CvStatsStrip() {
  const { data, isLoading } = useStats("cv");
  const missing = data?.completeness.missing ?? [];
  const items: StatItem[] = data
    ? [
        { label: "Complétude du profil", value: `${data.completeness.percent} %` },
        {
          label: "À compléter",
          value: missing.length,
          hint:
            missing.length > 0 ? (
              <>
                {missing.slice(0, 2).map((item) => item.label).join(", ")}
                {missing.length > 2 ? "…" : ""}{" "}
                <Link to="/profil/me?section=dev" className="underline">Compléter</Link>
              </>
            ) : (
              "Profil complet"
            ),
          highlight: missing.length > 0,
        },
      ]
    : [];
  return <StatsStrip items={items} isLoading={isLoading} />;
}

/** Explorer les offres : offres ouvertes, bien adaptées à mon profil, candidatures envoyées. */
export function ExploreStatsStrip() {
  const { data, isLoading } = useStats("explore");
  const items: StatItem[] = data
    ? [
        { label: "Offres ouvertes", value: data.open_offers },
        ...(data.well_matched !== null
          ? [{ label: "Bien adaptées à mon profil", value: data.well_matched, highlight: data.well_matched > 0 }]
          : []),
        ...(data.well_matched !== null
          ? [{ label: "Candidatures envoyées", value: data.applications_sent }]
          : []),
      ]
    : [];
  return <StatsStrip items={items} isLoading={isLoading} />;
}
