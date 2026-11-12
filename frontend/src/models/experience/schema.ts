import type { RelationRef } from "@/helpers/api/relations";
import { z } from "zod";
import type { TFunction } from "i18next";

export const experienceSchema = z.object({
  title: z.string(),
  company_name: z.string(),
  location: z.string().optional(),
  contract_type: z.enum(["cdi", "cdd", "freelance", "stage"]).optional(),
  start_date: z.string(),
  end_date: z.string().nullable().optional(),
  is_current: z.boolean(),
  description: z.string().optional(),
  technologies: z.string().optional(),
});

export type ExperienceSchema = z.infer<typeof experienceSchema>;

export const createExperienceSchema = (t: TFunction) =>
  z.object({
    profil_id: z.number({ error: "Sélection obligatoire" }),
    title: z.string(t("validation.required")).min(1, t("validation.required")),
    company_name: z.string(t("validation.required")).min(1, t("validation.required")),
    location: z.string().nullable().optional(),
    contract_type: z.enum(["cdi", "cdd", "freelance", "stage"]).optional(),
    start_date: z.string(),
    end_date: z.string().nullable().optional(),
    is_current: z.boolean(),
    description: z.string().nullable().optional(),
    technologies: z.string().nullable().optional(),
  });

export type CreateExperienceFormValues = {
  profil_id?: number;
  title: string;
  company_name: string;
  location?: string;
  contract_type?: string;
  start_date: string;
  end_date?: string | null;
  is_current: boolean;
  description?: string;
  technologies?: string;
};

export type CreateExperienceSchema = {
  profil_id: number;
  title: string;
  company_name: string;
  location?: string;
  contract_type?: string;
  start_date: string;
  end_date?: string | null;
  is_current: boolean;
  description?: string;
  technologies?: string;
};

export type GetExperienceSchema = {
  profil?: RelationRef | null;
  id: number;
  title: string;
  company_name: string;
  location?: string;
  contract_type?: string;
  start_date: string;
  end_date?: string | null;
  is_current: boolean;
  description?: string;
  technologies?: string;
};

export const updateExperienceSchema = (t: TFunction) =>
  z.object({
    profil_id: z.number({ error: "Sélection obligatoire" }),
    id: z.number(),
    title: z.string(t("validation.required")).min(1, t("validation.required")),
    company_name: z.string(t("validation.required")).min(1, t("validation.required")),
    location: z.string().nullable().optional(),
    contract_type: z.enum(["cdi", "cdd", "freelance", "stage"]).optional(),
    start_date: z.string(),
    end_date: z.string().nullable().optional(),
    is_current: z.boolean(),
    description: z.string().nullable().optional(),
    technologies: z.string().nullable().optional(),
  });

export type UpdateExperienceFormValues = {
  profil_id?: number;
  id: number;
  title: string;
  company_name: string;
  location?: string;
  contract_type?: string;
  start_date: string;
  end_date?: string | null;
  is_current: boolean;
  description?: string;
  technologies?: string;
};

export type UpdateExperienceSchema = {
  profil_id: number;
  id: number;
  title: string;
  company_name: string;
  location?: string;
  contract_type?: string;
  start_date: string;
  end_date?: string | null;
  is_current: boolean;
  description?: string;
  technologies?: string;
};