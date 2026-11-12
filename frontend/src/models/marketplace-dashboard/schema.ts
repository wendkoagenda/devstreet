import type { Candidature, Offer, TalentCard } from "@/models/marketplace-offers/schema";
import type { AvailabilityStatus } from "@/models/marketplace-profile/schema";

/** Nombre de candidatures par statut, avec le total. */
export type StatusCounts = {
  sent: number;
  shortlisted: number;
  accepted: number;
  rejected: number;
  total: number;
};

export type DashboardCompleteness = {
  percent: number;
  missing: { key: string; label: string }[];
};

export type DashboardAvailability = {
  current: {
    status: AvailabilityStatus;
    end_date: string;
    source: "manual" | "mission";
    note: string;
  } | null;
  next_available_start: string | null;
  periods_count: number;
};

export type DashboardCandidate = {
  counts: StatusCounts;
  recent: Candidature[];
  recommended_offers: Offer[];
  upcoming_missions: { id: number; note: string; start_date: string; end_date: string }[];
};

export type DashboardRecruiter = {
  company: { id: number; name: string; is_verified: boolean };
  offers: { open: number; draft: number; closed: number; total: number };
  views_total: number;
  candidatures: StatusCounts;
  pool_size: number;
  top_offers: {
    id: number;
    title: string;
    status: "draft" | "open" | "closed";
    candidatures_count: number;
    candidatures_new: number;
  }[];
  recent_candidatures: (Candidature & { profil: TalentCard; offer: { id: number; title: string } })[];
  weekly: { week_start: string; count: number }[];
};

export type Dashboard = {
  profil: { id: number; name: string; headline: string };
  completeness: DashboardCompleteness;
  reputation: { rating_avg: number | null; reviews_count: number };
  availability: DashboardAvailability;
  connections_count: number;
  candidate: DashboardCandidate;
  recruiter: DashboardRecruiter | null;
};
