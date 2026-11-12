import type { RelationRef } from "@/helpers/api/relations";
import { z } from "zod";
import type { TFunction } from "i18next";

export const prestationSchema = z.object({
  title: z.string(),
  slug: z.string(),
  description: z.string(),
  category: z.enum(["web", "mobile", "design", "devops", "data", "other"]),
  price: z.coerce.number(),
  currency: z.string(),
  delivery_days: z.string(),
  revisions: z.string(),
  cover_image: z.string().optional(),
  is_active: z.boolean(),
  cover_image_url: z.string().optional(),
});

export type PrestationSchema = z.infer<typeof prestationSchema>;

export const createPrestationSchema = (t: TFunction) =>
  z.object({
    profil_id: z.number({ error: "Sélection obligatoire" }),
    title: z.string(t("validation.required")).min(1, t("validation.required")),
    slug: z.string(),
    description: z.string(t("validation.required")).min(1, t("validation.required")),
    category: z.enum(["web", "mobile", "design", "devops", "data", "other"]),
    price: z.preprocess(
      (val) =>
        val === undefined || val === null || val === ""
          ? undefined
          : Number(val),
      z
        .union([z.number(), z.undefined()])
        .refine(
          (val): val is number => typeof val === "number" && !Number.isNaN(val),
          { message: t("validation.number.required") },
        ),
    ),
    currency: z.string(t("validation.required")).min(1, t("validation.required")),
    delivery_days: z.string(),
    revisions: z.string(),
    is_active: z.boolean(),
  });

export type CreatePrestationFormValues = {
  profil_id?: number;
  title: string;
  slug: string;
  description: string;
  category: string;
  price?: number;
  currency: string;
  delivery_days: string;
  revisions: string;
  is_active: boolean;
};

export type CreatePrestationSchema = {
  profil_id: number;
  title: string;
  slug: string;
  description: string;
  category: string;
  price: number;
  currency: string;
  delivery_days: string;
  revisions: string;
  is_active: boolean;
};

export type GetPrestationSchema = {
  profil?: RelationRef | null;
  id: number;
  title: string;
  slug: string;
  description: string;
  category: string;
  price: number;
  currency: string;
  delivery_days: string;
  revisions: string;
  cover_image?: string;
  is_active: boolean;
  cover_image_url?: string;
};

export const updatePrestationSchema = (t: TFunction) =>
  z.object({
    profil_id: z.number({ error: "Sélection obligatoire" }),
    id: z.number(),
    title: z.string(t("validation.required")).min(1, t("validation.required")),
    slug: z.string(),
    description: z.string(t("validation.required")).min(1, t("validation.required")),
    category: z.enum(["web", "mobile", "design", "devops", "data", "other"]),
    price: z.preprocess(
      (val) =>
        val === undefined || val === null || val === ""
          ? undefined
          : Number(val),
      z
        .union([z.number(), z.undefined()])
        .refine(
          (val): val is number => typeof val === "number" && !Number.isNaN(val),
          { message: t("validation.number.required") },
        ),
    ),
    currency: z.string(t("validation.required")).min(1, t("validation.required")),
    delivery_days: z.string(),
    revisions: z.string(),
    is_active: z.boolean(),
  });

export type UpdatePrestationFormValues = {
  profil_id?: number;
  id: number;
  title: string;
  slug: string;
  description: string;
  category: string;
  price?: number;
  currency: string;
  delivery_days: string;
  revisions: string;
  is_active: boolean;
};

export type UpdatePrestationSchema = {
  profil_id: number;
  id: number;
  title: string;
  slug: string;
  description: string;
  category: string;
  price: number;
  currency: string;
  delivery_days: string;
  revisions: string;
  is_active: boolean;
};