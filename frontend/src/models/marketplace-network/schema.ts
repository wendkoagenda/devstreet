import type { TalentCard } from "@/models/marketplace-offers/schema";

export type SwipeContext = "recruit" | "network";
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

export type ConnectionEntry = TalentCard & {
  matched_at: string;
};

export type PublicProfile = TalentCard & {
  is_self: boolean;
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
  reviews: { rating: number; comment: string; author: string; created_at: string }[];
};
