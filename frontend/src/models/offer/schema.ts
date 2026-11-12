import type { RelationRef } from "@/helpers/api/relations";
import { z } from "zod";
import type { TFunction } from "i18next";

export const offerSchema = z.object({
  title: z.string(),
  slug: z.string(),
  description: z.string(),
  type: z.enum(["mission", "cdd", "cdi", "stage"]),
  contract_duration: z.string().nullable().optional(),
  experience_level: z.enum(["junior", "mid", "senior"]),
  budget_min: z.coerce.number().nullable().optional(),
  budget_max: z.coerce.number().nullable().optional(),
  currency: z.string(),
  budget_period: z.enum(["day", "month", "fixed"]),
  country: z.string(),
  city: z.string().optional(),
  work_mode: z.enum(["on_site", "hybrid", "remote"]),
  start_date: z.string().nullable().optional(),
  deadline: z.string().nullable().optional(),
  status: z.enum(["draft", "open", "closed"]),
  published_at: z.string().nullable().optional(),
  views_count: z.coerce.number(),
  embedding: z.string().nullable().optional(),
});

export type OfferSchema = z.infer<typeof offerSchema>;

export const createOfferSchema = (t: TFunction) =>
  z.object({
    company_id: z.number({ error: "Sélection obligatoire" }),
    recruiter_id: z.number({ error: "Sélection obligatoire" }),
    required_skills: z.array(z.number()).optional(),
    title: z.string(t("validation.required")).min(1, t("validation.required")),
    slug: z.string(),
    description: z.string(t("validation.required")).min(1, t("validation.required")),
    type: z.enum(["mission", "cdd", "cdi", "stage"]),
    contract_duration: z.string().nullable().optional(),
    experience_level: z.enum(["junior", "mid", "senior"]),
    budget_min: z.preprocess(
      (val) =>
        val === undefined || val === null || val === ""
          ? undefined
          : Number(val),
      z
        .number({ message: t("validation.number.required") })
        .optional(),
    ),
    budget_max: z.preprocess(
      (val) =>
        val === undefined || val === null || val === ""
          ? undefined
          : Number(val),
      z
        .number({ message: t("validation.number.required") })
        .optional(),
    ),
    currency: z.string(t("validation.required")).min(1, t("validation.required")),
    budget_period: z.enum(["day", "month", "fixed"]),
    country: z.string(t("validation.required")).min(1, t("validation.required")),
    city: z.string().nullable().optional(),
    work_mode: z.enum(["on_site", "hybrid", "remote"]),
    start_date: z.string().nullable().optional(),
    deadline: z.string().nullable().optional(),
    status: z.enum(["draft", "open", "closed"]),
    published_at: z.string().nullable().optional(),
    views_count: z.coerce.number(),
    embedding: z.string().nullable().optional(),
  });

export type CreateOfferFormValues = {
  company_id?: number;
  recruiter_id?: number;
  required_skills?: number[];
  title: string;
  slug: string;
  description: string;
  type: string;
  contract_duration?: string | null;
  experience_level: string;
  budget_min?: number | null;
  budget_max?: number | null;
  currency: string;
  budget_period: string;
  country: string;
  city?: string;
  work_mode: string;
  start_date?: string | null;
  deadline?: string | null;
  status: string;
  published_at?: string | null;
  views_count: number;
  embedding?: string | null;
};

export type CreateOfferSchema = {
  company_id: number;
  recruiter_id: number;
  required_skills?: number[];
  title: string;
  slug: string;
  description: string;
  type: string;
  contract_duration?: string | null;
  experience_level: string;
  budget_min?: number | null;
  budget_max?: number | null;
  currency: string;
  budget_period: string;
  country: string;
  city?: string;
  work_mode: string;
  start_date?: string | null;
  deadline?: string | null;
  status: string;
  published_at?: string | null;
  views_count: number;
  embedding?: string | null;
};

export type GetOfferSchema = {
  company?: RelationRef | null;
  recruiter?: RelationRef | null;
  required_skills?: RelationRef[];
  id: number;
  title: string;
  slug: string;
  description: string;
  type: string;
  contract_duration?: string | null;
  experience_level: string;
  budget_min?: number | null;
  budget_max?: number | null;
  currency: string;
  budget_period: string;
  country: string;
  city?: string;
  work_mode: string;
  start_date?: string | null;
  deadline?: string | null;
  status: string;
  published_at?: string | null;
  views_count: number;
  embedding?: string | null;
};

export const updateOfferSchema = (t: TFunction) =>
  z.object({
    company_id: z.number({ error: "Sélection obligatoire" }),
    recruiter_id: z.number({ error: "Sélection obligatoire" }),
    required_skills: z.array(z.number()).optional(),
    id: z.number(),
    title: z.string(t("validation.required")).min(1, t("validation.required")),
    slug: z.string(),
    description: z.string(t("validation.required")).min(1, t("validation.required")),
    type: z.enum(["mission", "cdd", "cdi", "stage"]),
    contract_duration: z.string().nullable().optional(),
    experience_level: z.enum(["junior", "mid", "senior"]),
    budget_min: z.preprocess(
      (val) =>
        val === undefined || val === null || val === ""
          ? undefined
          : Number(val),
      z
        .number({ message: t("validation.number.required") })
        .optional(),
    ),
    budget_max: z.preprocess(
      (val) =>
        val === undefined || val === null || val === ""
          ? undefined
          : Number(val),
      z
        .number({ message: t("validation.number.required") })
        .optional(),
    ),
    currency: z.string(t("validation.required")).min(1, t("validation.required")),
    budget_period: z.enum(["day", "month", "fixed"]),
    country: z.string(t("validation.required")).min(1, t("validation.required")),
    city: z.string().nullable().optional(),
    work_mode: z.enum(["on_site", "hybrid", "remote"]),
    start_date: z.string().nullable().optional(),
    deadline: z.string().nullable().optional(),
    status: z.enum(["draft", "open", "closed"]),
    published_at: z.string().nullable().optional(),
    views_count: z.coerce.number(),
    embedding: z.string().nullable().optional(),
  });

export type UpdateOfferFormValues = {
  company_id?: number;
  recruiter_id?: number;
  required_skills?: number[];
  id: number;
  title: string;
  slug: string;
  description: string;
  type: string;
  contract_duration?: string | null;
  experience_level: string;
  budget_min?: number | null;
  budget_max?: number | null;
  currency: string;
  budget_period: string;
  country: string;
  city?: string;
  work_mode: string;
  start_date?: string | null;
  deadline?: string | null;
  status: string;
  published_at?: string | null;
  views_count: number;
  embedding?: string | null;
};

export type UpdateOfferSchema = {
  company_id: number;
  recruiter_id: number;
  required_skills?: number[];
  id: number;
  title: string;
  slug: string;
  description: string;
  type: string;
  contract_duration?: string | null;
  experience_level: string;
  budget_min?: number | null;
  budget_max?: number | null;
  currency: string;
  budget_period: string;
  country: string;
  city?: string;
  work_mode: string;
  start_date?: string | null;
  deadline?: string | null;
  status: string;
  published_at?: string | null;
  views_count: number;
  embedding?: string | null;
};