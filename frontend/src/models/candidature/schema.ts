import type { RelationRef } from "@/helpers/api/relations";
import { z } from "zod";
import type { TFunction } from "i18next";

export const candidatureSchema = z.object({
  message: z.string().optional(),
  status: z.enum(["sent", "shortlisted", "rejected", "accepted"]),
  ai_match_score: z.coerce.number().nullable().optional(),
  cv_snapshot: z.string().optional(),
  decided_at: z.string().nullable().optional(),
  cv_snapshot_url: z.string().optional(),
});

export type CandidatureSchema = z.infer<typeof candidatureSchema>;

export const createCandidatureSchema = (t: TFunction) =>
  z.object({
    offer_id: z.number({ error: "Sélection obligatoire" }),
    profil_id: z.number({ error: "Sélection obligatoire" }),
    message: z.string().nullable().optional(),
    status: z.enum(["sent", "shortlisted", "rejected", "accepted"]),
    ai_match_score: z.preprocess(
      (val) =>
        val === undefined || val === null || val === ""
          ? undefined
          : Number(val),
      z
        .number({ message: t("validation.number.required") })
        .optional(),
    ),
    decided_at: z.string().nullable().optional(),
  });

export type CreateCandidatureFormValues = {
  offer_id?: number;
  profil_id?: number;
  message?: string;
  status: string;
  ai_match_score?: number | null;
  decided_at?: string | null;
};

export type CreateCandidatureSchema = {
  offer_id: number;
  profil_id: number;
  message?: string;
  status: string;
  ai_match_score?: number | null;
  decided_at?: string | null;
};

export type GetCandidatureSchema = {
  offer?: RelationRef | null;
  profil?: RelationRef | null;
  id: number;
  message?: string;
  status: string;
  ai_match_score?: number | null;
  cv_snapshot?: string;
  decided_at?: string | null;
  cv_snapshot_url?: string;
};

export const updateCandidatureSchema = (t: TFunction) =>
  z.object({
    offer_id: z.number({ error: "Sélection obligatoire" }),
    profil_id: z.number({ error: "Sélection obligatoire" }),
    id: z.number(),
    message: z.string().nullable().optional(),
    status: z.enum(["sent", "shortlisted", "rejected", "accepted"]),
    ai_match_score: z.preprocess(
      (val) =>
        val === undefined || val === null || val === ""
          ? undefined
          : Number(val),
      z
        .number({ message: t("validation.number.required") })
        .optional(),
    ),
    decided_at: z.string().nullable().optional(),
  });

export type UpdateCandidatureFormValues = {
  offer_id?: number;
  profil_id?: number;
  id: number;
  message?: string;
  status: string;
  ai_match_score?: number | null;
  decided_at?: string | null;
};

export type UpdateCandidatureSchema = {
  offer_id: number;
  profil_id: number;
  id: number;
  message?: string;
  status: string;
  ai_match_score?: number | null;
  decided_at?: string | null;
};