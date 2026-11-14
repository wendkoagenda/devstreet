import type { TalentCard } from "@/models/marketplace-offers/schema";

export type SwipeContext = "recruit" | "network";
/** Profil avec lequel on agit dans le réseau, pour un membre qui a un profil dev et un profil entreprise. */
export type ActingAs = "dev" | "entreprise";
export type SwipeDirection = "like" | "pass";

/** Carte du paquet de découverte (recruit : score pour l'offre la plus proche ; network : compétences en commun). */
export type DeckCard = TalentCard & {
  available_from: string | null;
  score: number | null;
  common_skills?: string[];
};

export type SwipeResult = {
  matched: boolean;
  profil: TalentCard;
};

export type PoolEntry = TalentCard & {
  liked_at: string;
  liked_by: string;
};

/** Carte de l'annuaire talents (UC-08). */
export type TalentDirectoryCard = TalentCard & {
  available_from: string | null;
};

export type TalentDirectoryFilters = {
  search?: string;
  skill?: string;
  country?: string;
  remote?: string;
  available?: string;
};

export type ConnectionEntry = TalentCard & {
  matched_at: string;
};

/** Demande de connexion (envoyée en attente, ou reçue) : l'autre profil, la date, et mon profil concerné. */
export type NetworkRequest = TalentCard & {
  requested_at: string;
  /** Celui de mes profils concerné : à utiliser pour répondre à une demande reçue. */
  acting: ActingAs;
};

export type NetworkRequests = { sent: NetworkRequest[]; received: NetworkRequest[] };

export type PublicProfile = TalentCard & {
  is_self: boolean;
  username: string;
  bio: string;
  languages: string[];
  github_url: string;
  linkedin_url: string;
  portfolio_url: string;
  cv_visibility: "public" | "companies" | "private";
  can_download_cv: boolean;
  member_since: string;
  skills_detail: { name: string; level: number; years: number }[];
  experiences: {
    id: number;
    title: string;
    company_name: string;
    location: string;
    start_date: string;
    end_date: string | null;
    is_current: boolean;
    description: string;
    technologies: string;
  }[];
  prestations: {
    id: number;
    title: string;
    slug: string;
    description: string;
    category: string;
    price: string;
    currency: string;
    delivery_days: number;
    revisions: number;
  }[];
  reviews: { rating: number; comment: string; author: string; created_at: string }[];
};
