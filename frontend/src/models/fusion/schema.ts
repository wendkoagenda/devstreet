import { z } from "zod";
import type { TFunction } from "i18next";

export const fusionSchema = z.object({
  id: z.number(),
  uuid: z.string().uuid(),
  titre: z.string(),
  statut: z.enum(["draft", "published", "archived"]),
  description: z.string().nullable().optional(),
  prix: z.coerce.number(),
  document: z.string().nullable().optional(),
  document_url: z.string().optional(),
});

export type FusionSchema = z.infer<typeof fusionSchema>;

export const createFusionSchema = (t: TFunction) =>
  z.object({
    titre: z.string(t("validation.required")).min(1, t("validation.required")),
    statut: z.enum(["draft", "published", "archived"]),
    description: z.string().nullable().optional(),
    prix: z.preprocess(
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
  });

export type CreateFusionFormValues = {
  titre: string;
  statut: string;
  description?: string | null;
  prix?: number;
};

export type CreateFusionSchema = {
  titre: string;
  statut: string;
  description?: string | null;
  prix: number;
};

export type GetFusionSchema = {
  id: number;
  uuid: string;
  titre: string;
  statut: string;
  description?: string | null;
  prix: number;
  document?: string | null;
  document_url?: string;
};

export const updateFusionSchema = (t: TFunction) =>
  z.object({
    id: z.number(),
    titre: z.string(t("validation.required")).min(1, t("validation.required")),
    statut: z.enum(["draft", "published", "archived"]),
    description: z.string().nullable().optional(),
    prix: z.preprocess(
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
  });

export type UpdateFusionFormValues = {
  id: number;
  titre: string;
  statut: string;
  description?: string | null;
  prix?: number;
};

export type UpdateFusionSchema = {
  id: number;
  titre: string;
  statut: string;
  description?: string | null;
  prix: number;
};