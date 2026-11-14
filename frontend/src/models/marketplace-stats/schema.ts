import type { AvailabilityStatus } from "@/models/marketplace-profile/schema";

/** Page dont on veut les petites statistiques (une ligne de pastilles en haut). */
export type StatsScope =
  | "offers"
  | "pool"
  | "applications"
  | "availability"
  | "cv"
  | "profile"
  | "explore"
  | "network";

/** Mes offres (entreprise). */
export type OffersStats = {
  open: number;
  draft: number;
  closed: number;
  total: number;
  to_process: number;
  views_total: number;
};

/** Vivier (entreprise). */
export type PoolStats = { total: number; this_week: number; open_to_work: number };

/** Mes candidatures (dev). */
export type ApplicationsStats = {
  sent: number;
  shortlisted: number;
  accepted: number;
  rejected: number;
  total: number;
  upcoming_missions: number;
};

/** Mes disponibilités (dev). */
export type AvailabilityStats = {
  current: {
    status: AvailabilityStatus;
    end_date: string;
    source: "manual" | "mission";
    note: string;
  } | null;
  next_available_start: string | null;
  periods_count: number;
  upcoming_missions: number;
};

/** Mon CV (dev). */
export type CvStats = {
  completeness: { percent: number; missing: { key: string; label: string }[] };
};

/** Résumé du profil pro (orbite). */
export type ProfileStats = {
  availability: AvailabilityStats;
  reputation: { rating_avg: number | null; reviews_count: number };
  connections_count: number;
};

/** Explorer les offres. `well_matched` est null sans profil dev (pas de score). */
export type ExploreStats = {
  open_offers: number;
  well_matched: number | null;
  applications_sent: number;
};

/** Réseau : connexions, demandes envoyées en attente de réponse, demandes reçues auxquelles je n'ai pas répondu. */
export type NetworkStats = { connections: number; pending_sent: number; pending_received: number };

export type StatsByScope = {
  offers: OffersStats;
  pool: PoolStats;
  applications: ApplicationsStats;
  availability: AvailabilityStats;
  cv: CvStats;
  profile: ProfileStats;
  explore: ExploreStats;
  network: NetworkStats;
};
