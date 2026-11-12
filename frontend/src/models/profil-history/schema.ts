import type { RelationRef } from "@/helpers/api/relations";
import { z } from "zod";
import type { TFunction } from "i18next";

export const profilHistorySchema = z.object({
  field: z.string(),
  old_value: z.string().optional(),
  new_value: z.string().optional(),
  source: z.enum(["manual", "ai", "system"]),
});

export type ProfilHistorySchema = z.infer<typeof profilHistorySchema>;

export const createProfilHistorySchema = (t: TFunction) =>
  z.object({
    profil_id: z.number({ error: "Sélection obligatoire" }),
    field: z.string(t("validation.required")).min(1, t("validation.required")),
    old_value: z.string().nullable().optional(),
    new_value: z.string().nullable().optional(),
    source: z.enum(["manual", "ai", "system"]),
  });

export type CreateProfilHistoryFormValues = {
  profil_id?: number;
  field: string;
  old_value?: string;
  new_value?: string;
  source: string;
};

export type CreateProfilHistorySchema = {
  profil_id: number;
  field: string;
  old_value?: string;
  new_value?: string;
  source: string;
};

export type GetProfilHistorySchema = {
  profil?: RelationRef | null;
  id: number;
  field: string;
  old_value?: string;
  new_value?: string;
  source: string;
};

export const updateProfilHistorySchema = (t: TFunction) =>
  z.object({
    profil_id: z.number({ error: "Sélection obligatoire" }),
    id: z.number(),
    field: z.string(t("validation.required")).min(1, t("validation.required")),
    old_value: z.string().nullable().optional(),
    new_value: z.string().nullable().optional(),
    source: z.enum(["manual", "ai", "system"]),
  });

export type UpdateProfilHistoryFormValues = {
  profil_id?: number;
  id: number;
  field: string;
  old_value?: string;
  new_value?: string;
  source: string;
};

export type UpdateProfilHistorySchema = {
  profil_id: number;
  id: number;
  field: string;
  old_value?: string;
  new_value?: string;
  source: string;
};