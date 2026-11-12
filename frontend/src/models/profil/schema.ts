import type { RelationRef } from "@/helpers/api/relations";
import { z } from "zod";
import type { TFunction } from "i18next";

export const profilSchema = z.object({
  is_company_owner: z.boolean(),
  slug: z.string(),
  photo: z.string().optional(),
  headline: z.string().optional(),
  bio: z.string().optional(),
  phone: z.string().optional(),
  country: z.string(),
  city: z.string().optional(),
  remote: z.boolean(),
  timezone: z.string(),
  default_hours_per_week: z.string(),
  is_open_to_work: z.boolean(),
  daily_rate: z.coerce.number().nullable().optional(),
  currency: z.string(),
  years_of_experience: z.string(),
  languages: z.string().optional(),
  github_url: z.string().optional(),
  linkedin_url: z.string().optional(),
  portfolio_url: z.string().optional(),
  cv_visibility: z.enum(["public", "companies", "private"]),
  embedding: z.string().nullable().optional(),
  photo_url: z.string().optional(),
});

export type ProfilSchema = z.infer<typeof profilSchema>;

export const createProfilSchema = (t: TFunction) =>
  z.object({
    company_id: z.number().nullable().optional(),
    user_id: z.number({ error: "Sélection obligatoire" }),
    is_company_owner: z.boolean(),
    slug: z.string(),
    headline: z.string().nullable().optional(),
    bio: z.string().nullable().optional(),
    phone: z.string().nullable().optional(),
    country: z.string(t("validation.required")).min(1, t("validation.required")),
    city: z.string().nullable().optional(),
    remote: z.boolean(),
    timezone: z.string(t("validation.required")).min(1, t("validation.required")),
    default_hours_per_week: z.string(),
    is_open_to_work: z.boolean(),
    daily_rate: z.preprocess(
      (val) =>
        val === undefined || val === null || val === ""
          ? undefined
          : Number(val),
      z
        .number({ message: t("validation.number.required") })
        .optional(),
    ),
    currency: z.string(t("validation.required")).min(1, t("validation.required")),
    years_of_experience: z.string(),
    languages: z.string().optional(),
    github_url: z.string().optional(),
    linkedin_url: z.string().optional(),
    portfolio_url: z.string().optional(),
    cv_visibility: z.enum(["public", "companies", "private"]),
    embedding: z.string().nullable().optional(),
  });

export type CreateProfilFormValues = {
  company_id?: number | null;
  user_id?: number;
  is_company_owner: boolean;
  slug: string;
  headline?: string;
  bio?: string;
  phone?: string;
  country: string;
  city?: string;
  remote: boolean;
  timezone: string;
  default_hours_per_week: string;
  is_open_to_work: boolean;
  daily_rate?: number | null;
  currency: string;
  years_of_experience: string;
  languages?: string;
  github_url?: string;
  linkedin_url?: string;
  portfolio_url?: string;
  cv_visibility: string;
  embedding?: string | null;
};

export type CreateProfilSchema = {
  company_id?: number | null;
  user_id: number;
  is_company_owner: boolean;
  slug: string;
  headline?: string;
  bio?: string;
  phone?: string;
  country: string;
  city?: string;
  remote: boolean;
  timezone: string;
  default_hours_per_week: string;
  is_open_to_work: boolean;
  daily_rate?: number | null;
  currency: string;
  years_of_experience: string;
  languages?: string;
  github_url?: string;
  linkedin_url?: string;
  portfolio_url?: string;
  cv_visibility: string;
  embedding?: string | null;
};

export type GetProfilSchema = {
  company?: RelationRef | null;
  user_id?: number;
  id: number;
  is_company_owner: boolean;
  slug: string;
  photo?: string;
  headline?: string;
  bio?: string;
  phone?: string;
  country: string;
  city?: string;
  remote: boolean;
  timezone: string;
  default_hours_per_week: string;
  is_open_to_work: boolean;
  daily_rate?: number | null;
  currency: string;
  years_of_experience: string;
  languages?: string;
  github_url?: string;
  linkedin_url?: string;
  portfolio_url?: string;
  cv_visibility: string;
  embedding?: string | null;
  photo_url?: string;
};

export const updateProfilSchema = (t: TFunction) =>
  z.object({
    company_id: z.number().nullable().optional(),
    user_id: z.number({ error: "Sélection obligatoire" }),
    id: z.number(),
    is_company_owner: z.boolean(),
    slug: z.string(),
    headline: z.string().nullable().optional(),
    bio: z.string().nullable().optional(),
    phone: z.string().nullable().optional(),
    country: z.string(t("validation.required")).min(1, t("validation.required")),
    city: z.string().nullable().optional(),
    remote: z.boolean(),
    timezone: z.string(t("validation.required")).min(1, t("validation.required")),
    default_hours_per_week: z.string(),
    is_open_to_work: z.boolean(),
    daily_rate: z.preprocess(
      (val) =>
        val === undefined || val === null || val === ""
          ? undefined
          : Number(val),
      z
        .number({ message: t("validation.number.required") })
        .optional(),
    ),
    currency: z.string(t("validation.required")).min(1, t("validation.required")),
    years_of_experience: z.string(),
    languages: z.string().optional(),
    github_url: z.string().optional(),
    linkedin_url: z.string().optional(),
    portfolio_url: z.string().optional(),
    cv_visibility: z.enum(["public", "companies", "private"]),
    embedding: z.string().nullable().optional(),
  });

export type UpdateProfilFormValues = {
  company_id?: number | null;
  user_id?: number;
  id: number;
  is_company_owner: boolean;
  slug: string;
  headline?: string;
  bio?: string;
  phone?: string;
  country: string;
  city?: string;
  remote: boolean;
  timezone: string;
  default_hours_per_week: string;
  is_open_to_work: boolean;
  daily_rate?: number | null;
  currency: string;
  years_of_experience: string;
  languages?: string;
  github_url?: string;
  linkedin_url?: string;
  portfolio_url?: string;
  cv_visibility: string;
  embedding?: string | null;
};

export type UpdateProfilSchema = {
  company_id?: number | null;
  user_id: number;
  id: number;
  is_company_owner: boolean;
  slug: string;
  headline?: string;
  bio?: string;
  phone?: string;
  country: string;
  city?: string;
  remote: boolean;
  timezone: string;
  default_hours_per_week: string;
  is_open_to_work: boolean;
  daily_rate?: number | null;
  currency: string;
  years_of_experience: string;
  languages?: string;
  github_url?: string;
  linkedin_url?: string;
  portfolio_url?: string;
  cv_visibility: string;
  embedding?: string | null;
};