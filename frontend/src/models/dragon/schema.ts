import { z } from "zod";
import type { TFunction } from "i18next";

export const dragonSchema = z.object({
  id: z.number(),
  uuid: z.string().uuid(),
  titre: z.string(),
  statut: z.enum(["draft", "published", "archived"]),
  description: z.string().nullable().optional(),
  prix: z.coerce.number(),
  document: z.string().nullable().optional(),
  document_url: z.string().optional(),
});

export type DragonSchema = z.infer<typeof dragonSchema>;

export const createDragonSchema = (t: TFunction) =>
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

export type CreateDragonFormValues = {
  titre: string;
  statut: string;
  description?: string | null;
  prix?: number;
};

export type CreateDragonSchema = {
  titre: string;
  statut: string;
  description?: string | null;
  prix: number;
};

export type GetDragonSchema = {
  id: number;
  uuid: string;
  titre: string;
  statut: string;
  description?: string | null;
  prix: number;
  document?: string | null;
  document_url?: string;
};

export const updateDragonSchema = (t: TFunction) =>
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

export type UpdateDragonFormValues = {
  id: number;
  titre: string;
  statut: string;
  description?: string | null;
  prix?: number;
};

export type UpdateDragonSchema = {
  id: number;
  titre: string;
  statut: string;
  description?: string | null;
  prix: number;
};