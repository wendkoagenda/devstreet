import type { RelationRef } from "@/helpers/api/relations";
import { z } from "zod";

export const connectionSchema = z.object({
  status: z.enum(["matched", "blocked"]),
  matched_at: z.string(),
});

export type ConnectionSchema = z.infer<typeof connectionSchema>;

export const createConnectionSchema = () =>
  z.object({
    profil_a_id: z.number({ error: "Sélection obligatoire" }),
    profil_b_id: z.number({ error: "Sélection obligatoire" }),
    status: z.enum(["matched", "blocked"]),
    matched_at: z.string(),
  });

export type CreateConnectionFormValues = {
  profil_a_id?: number;
  profil_b_id?: number;
  status: string;
  matched_at: string;
};

export type CreateConnectionSchema = {
  profil_a_id: number;
  profil_b_id: number;
  status: string;
  matched_at: string;
};

export type GetConnectionSchema = {
  profil_a?: RelationRef | null;
  profil_b?: RelationRef | null;
  id: number;
  status: string;
  matched_at: string;
};

export const updateConnectionSchema = () =>
  z.object({
    profil_a_id: z.number({ error: "Sélection obligatoire" }),
    profil_b_id: z.number({ error: "Sélection obligatoire" }),
    id: z.number(),
    status: z.enum(["matched", "blocked"]),
    matched_at: z.string(),
  });

export type UpdateConnectionFormValues = {
  profil_a_id?: number;
  profil_b_id?: number;
  id: number;
  status: string;
  matched_at: string;
};

export type UpdateConnectionSchema = {
  profil_a_id: number;
  profil_b_id: number;
  id: number;
  status: string;
  matched_at: string;
};