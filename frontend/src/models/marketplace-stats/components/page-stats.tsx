import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { formatDate } from "@/models/marketplace-offers/labels";
import { AVAILABILITY_LABELS } from "@/models/marketplace-profile/schema";
import { useStats } from "../api";
import { StatsStrip, type StatItem } from "./stats-strip";

/** Mes offres (entreprise) : offres ouvertes, brouillons et clôturées, candidatures à traiter, vues. */
export function OffersStatsStrip() {
  const { t } = useTranslation();
  const { data, isLoading } = useStats("offers");
  const items: StatItem[] = data
    ? [
        { label: t("marketplace.offer_manage.stats_open"), value: data.open },
        {
          label: t("marketplace.offer_manage.stats_draft_closed"),
          value: `${data.draft} / ${data.closed}`,
        },
        {
          label: t("marketplace.offer_manage.stats_to_process"),
          value: data.to_process,
          hint:
            data.to_process > 0
              ? t("marketplace.offer_manage.stats_to_process_hint")
              : undefined,
          highlight: data.to_process > 0,
        },
        {
          label: t("marketplace.offer_manage.stats_views"),
          value: data.views_total,
        },
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
  const { t } = useTranslation();
  const { data, isLoading } = useStats("applications");
  const items: StatItem[] = data
    ? [
        { label: t("marketplace.stats_sent"), value: data.sent },
        { label: t("marketplace.stats_shortlisted"), value: data.shortlisted },
        {
          label: t("marketplace.stats_accepted"),
          value: data.accepted,
          hint:
            data.upcoming_missions > 0
              ? t("marketplace.stats_upcoming_missions", {
                  count: data.upcoming_missions,
                })
              : undefined,
          highlight: data.accepted > 0,
        },
        { label: t("marketplace.stats_rejected"), value: data.rejected },
      ]
    : [];
  return <StatsStrip items={items} isLoading={isLoading} />;
}

/** Mes disponibilités (dev) : statut du jour, prochaine disponibilité, missions à venir. */
export function AvailabilityStatsStrip() {
  const { t } = useTranslation();
  const { data, isLoading } = useStats("availability");
  const items: StatItem[] = data
    ? [
        {
          label: t("marketplace.availability.stats_today"),
          // Sans période, le membre est disponible
          value: data.current
            ? AVAILABILITY_LABELS[data.current.status]
            : t("marketplace.labels.availability_status.available"),
          hint: data.current
            ? t("marketplace.availability.stats_until", {
                date: formatDate(data.current.end_date),
              })
            : t("marketplace.availability.stats_no_busy"),
        },
        {
          label: t("marketplace.availability.stats_next"),
          value: data.next_available_start
            ? formatDate(data.next_available_start)
            : data.current
              ? "—"
              : t("marketplace.availability.stats_now"),
        },
        {
          label: t("marketplace.availability.stats_upcoming"),
          value: data.upcoming_missions,
        },
      ]
    : [];
  return <StatsStrip items={items} isLoading={isLoading} />;
}

/** Mon CV (dev) : complétude du profil et ce qui manque. */
export function CvStatsStrip() {
  const { t } = useTranslation();
  const { data, isLoading } = useStats("cv");
  const missing = data?.completeness.missing ?? [];
  const missingLabels = missing
    .slice(0, 2)
    .map((item) => t(`marketplace.cv.missing.${item.key}`, { defaultValue: item.label }))
    .join(", ");
  const items: StatItem[] = data
    ? [
        {
          label: t("marketplace.cv.stats_completeness"),
          value: `${data.completeness.percent} %`,
        },
        {
          label: t("marketplace.cv.stats_todo"),
          value: missing.length,
          hint:
            missing.length > 0 ? (
              <>
                {missingLabels}
                {missing.length > 2 ? "…" : ""}{" "}
                <Link to="/profil/me?section=dev" className="underline">
                  {t("marketplace.cv.stats_complete_action")}
                </Link>
              </>
            ) : (
              t("marketplace.cv.stats_complete")
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
          ? [{ label: "Bien adaptées (≥ 70)", value: data.well_matched, highlight: data.well_matched > 0 }]
          : []),
        ...(data.well_matched !== null
          ? [{ label: "Candidatures envoyées", value: data.applications_sent }]
          : []),
      ]
    : [];
  return <StatsStrip items={items} isLoading={isLoading} />;
}
