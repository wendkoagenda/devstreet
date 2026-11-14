import { z } from "zod";

export type OfferType = "mission" | "cdd" | "cdi" | "stage";
export type ExperienceLevel = "junior" | "mid" | "senior" | "expert";
/** Unité de la durée d'une offre. */
export type DurationUnit = "hour" | "day" | "month" | "year";
export type WorkMode = "on_site" | "hybrid" | "remote";
export type OfferStatus = "draft" | "open" | "closed";
export type CandidatureStatus = "sent" | "shortlisted" | "rejected" | "accepted";

/** Un critère du score de recommandation (par règles, sur 100 au total). */
export type ScoreItem = {
  key: string;
  label: string;
  score: number;
  max: number;
  detail: string;
};

export type OfferCompany = {
  id: number;
  name: string;
  slug: string;
  sector: string;
  city: string;
  country: string;
  is_verified: boolean;
};

export type Offer = {
  id: number;
  slug: string;
  title: string;
  type: OfferType;
  contract_duration: number | null;
  contract_duration_unit: DurationUnit;
  experience_level: ExperienceLevel;
  budget_min: string | null;
  budget_max: string | null;
  currency: string;
  budget_period: "day" | "month" | "fixed";
  country: string;
  city: string;
  work_mode: WorkMode;
  start_date: string | null;
  deadline: string | null;
  status: OfferStatus;
  published_at: string | null;
  company: OfferCompany;
  skills: { id: number; name: string }[];
  description?: string;
  views_count?: number;
  is_own?: boolean;
  score?: number;
  breakdown?: ScoreItem[];
  matched_skill_ids?: number[];
  my_candidature?: { id: number; status: CandidatureStatus; created_at: string };
  candidatures_count?: number;
  candidatures_new?: number;
};

/** Carte d'un profil (talent recommandé, candidat). */
export type TalentCard = {
  id: number;
  name: string;
  headline: string;
  city: string;
  country: string;
  remote: boolean;
  years_of_experience: number;
  is_open_to_work: boolean;
  skills: string[];
  rating_avg: number | null;
  reviews_count: number;
  /** Profil dev ou profil entreprise (l'accroche d'un profil entreprise est le nom de sa société). */
  type?: "dev" | "entreprise";
  /** Nom d'utilisateur du membre : sert à ouvrir sa page de profil. */
  username?: string;
  company?: { id: number; name: string; is_verified: boolean } | null;
  email?: string;
  score?: number;
  breakdown?: ScoreItem[];
  applied?: boolean;
};

export type Candidature = {
  id: number;
  status: CandidatureStatus;
  message: string;
  created_at: string;
  decided_at: string | null;
  offer?: Offer;
  score?: number;
  profil?: TalentCard;
};

export type SkillOption = {
  id: number;
  name: string;
  type: "hard" | "soft";
  category: string;
};

export type MySkill = {
  skill_id: number;
  name: string;
  type: "hard" | "soft";
  level: number;
  years: number;
};

export type OfferFilters = {
  search?: string;
  type?: string;
  work_mode?: string;
};

/** Brouillon renvoyé par POST /marketplace/me/offers/generate (UC-09). */
export type OfferAiDraft = {
  title: string;
  description: string;
  type: OfferType;
  experience_level: ExperienceLevel;
  work_mode: WorkMode;
  contract_duration: number | null;
  budget_min: number | null;
  budget_max: number | null;
  currency: string;
  budget_period: "day" | "month" | "fixed";
  country: string;
  city: string;
  required_skill_ids: number[];
  skills: SkillOption[];
};

export type OfferAiGenerateResult = {
  draft: OfferAiDraft;
  suggested_profils: TalentCard[];
  provider: string;
  model: string;
};

const optionalDate = z
  .string()
  .refine((value) => value === "" || /^\d{4}-\d{2}-\d{2}$/.test(value), "Date invalide");
const optionalNumber = z
  .string()
  .trim()
  .refine((value) => value === "" || /^\d+([.,]\d{1,2})?$/.test(value), "Nombre invalide");

export const offerFormSchema = z.object({
  title: z.string().trim().min(1, "Le titre est obligatoire").max(200),
  description: z.string().trim().min(1, "La description est obligatoire"),
  type: z.enum(["mission", "cdd", "cdi", "stage"]),
  experience_level: z.enum(["junior", "mid", "senior", "expert"]),
  work_mode: z.enum(["on_site", "hybrid", "remote"]),
  contract_duration: z
    .string()
    .trim()
    .refine((value) => value === "" || /^\d{1,5}$/.test(value), "Durée : nombre entier"),
  contract_duration_unit: z.enum(["hour", "day", "month", "year"]),
  budget_min: optionalNumber,
  budget_max: optionalNumber,
  currency: z.string().regex(/^[A-Za-z]{3}$/, "Devise à 3 lettres"),
  budget_period: z.enum(["day", "month", "fixed"]),
  country: z.string().regex(/^[A-Za-z]{2}$/, "Choisissez un pays"),
  city: z.string().trim().max(100),
  start_date: optionalDate,
  deadline: optionalDate,
  required_skill_ids: z.array(z.number()),
});

export type OfferFormValues = z.infer<typeof offerFormSchema>;

export function offerToForm(offer: Offer | null, defaults?: { country?: string; city?: string }): OfferFormValues {
  return {
    title: offer?.title ?? "",
    description: offer?.description ?? "",
    type: offer?.type ?? "mission",
    experience_level: offer?.experience_level ?? "mid",
    work_mode: offer?.work_mode ?? "hybrid",
    contract_duration: offer?.contract_duration ? String(offer.contract_duration) : "",
    contract_duration_unit: offer?.contract_duration_unit ?? "month",
    budget_min: offer?.budget_min ? String(Number(offer.budget_min)) : "",
    budget_max: offer?.budget_max ? String(Number(offer.budget_max)) : "",
    currency: offer?.currency ?? "XOF",
    budget_period: offer?.budget_period ?? "month",
    country: offer?.country ?? defaults?.country ?? "",
    city: offer?.city ?? defaults?.city ?? "",
    start_date: offer?.start_date ?? "",
    deadline: offer?.deadline ?? "",
    required_skill_ids: offer?.skills.map((skill) => skill.id) ?? [],
  };
}

/** Convertit le brouillon IA en valeurs de formulaire (dates laissées vides). */
export function draftToForm(draft: OfferAiDraft): OfferFormValues {
  return {
    title: draft.title,
    description: draft.description,
    type: draft.type,
    experience_level: draft.experience_level,
    work_mode: draft.work_mode,
    contract_duration: draft.contract_duration != null ? String(draft.contract_duration) : "",
    budget_min: draft.budget_min != null ? String(draft.budget_min) : "",
    budget_max: draft.budget_max != null ? String(draft.budget_max) : "",
    currency: draft.currency || "XOF",
    budget_period: draft.budget_period,
    country: draft.country || "",
    city: draft.city || "",
    start_date: "",
    deadline: "",
    required_skill_ids: draft.required_skill_ids ?? [],
  };
}

const toNumberOrNull = (value: string) =>
  value === "" ? null : value.replace(",", ".");

export function offerToPayload(values: OfferFormValues) {
  return {
    ...values,
    country: values.country.toUpperCase(),
    currency: values.currency.toUpperCase(),
    contract_duration: values.contract_duration === "" ? null : Number(values.contract_duration),
    budget_min: toNumberOrNull(values.budget_min),
    budget_max: toNumberOrNull(values.budget_max),
    start_date: values.start_date === "" ? null : values.start_date,
    deadline: values.deadline === "" ? null : values.deadline,
  };
}
