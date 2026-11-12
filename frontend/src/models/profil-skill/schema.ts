import type { RelationRef } from "@/helpers/api/relations";
import { z } from "zod";

export const profilSkillSchema = z.object({
  level: z.string(),
  years: z.string(),
});

export type ProfilSkillSchema = z.infer<typeof profilSkillSchema>;

export const createProfilSkillSchema = () =>
  z.object({
    profil_id: z.number({ error: "Sélection obligatoire" }),
    skill_id: z.number({ error: "Sélection obligatoire" }),
    level: z.string(),
    years: z.string(),
  });

export type CreateProfilSkillFormValues = {
  profil_id?: number;
  skill_id?: number;
  level: string;
  years: string;
};

export type CreateProfilSkillSchema = {
  profil_id: number;
  skill_id: number;
  level: string;
  years: string;
};

export type GetProfilSkillSchema = {
  profil?: RelationRef | null;
  skill?: RelationRef | null;
  id: number;
  level: string;
  years: string;
};

export const updateProfilSkillSchema = () =>
  z.object({
    profil_id: z.number({ error: "Sélection obligatoire" }),
    skill_id: z.number({ error: "Sélection obligatoire" }),
    id: z.number(),
    level: z.string(),
    years: z.string(),
  });

export type UpdateProfilSkillFormValues = {
  profil_id?: number;
  skill_id?: number;
  id: number;
  level: string;
  years: string;
};

export type UpdateProfilSkillSchema = {
  profil_id: number;
  skill_id: number;
  id: number;
  level: string;
  years: string;
};