import { z } from "zod";
import type { TFunction } from "i18next";

export const skillSchema = z.object({
  name: z.string(),
  slug: z.string(),
  type: z.enum(["hard", "soft"]),
  category: z.enum(["frontend", "backend", "mobile", "devops", "data", "design", "management", "soft"]).optional(),
});

export type SkillSchema = z.infer<typeof skillSchema>;

export const createSkillSchema = (t: TFunction) =>
  z.object({
    name: z.string(t("validation.required")).min(1, t("validation.required")),
    slug: z.string(),
    type: z.enum(["hard", "soft"]),
    category: z.enum(["frontend", "backend", "mobile", "devops", "data", "design", "management", "soft"]).optional(),
  });

export type CreateSkillFormValues = {
  name: string;
  slug: string;
  type: string;
  category?: string;
};

export type CreateSkillSchema = {
  name: string;
  slug: string;
  type: string;
  category?: string;
};

export type GetSkillSchema = {
  id: number;
  name: string;
  slug: string;
  type: string;
  category?: string;
};

export const updateSkillSchema = (t: TFunction) =>
  z.object({
    id: z.number(),
    name: z.string(t("validation.required")).min(1, t("validation.required")),
    slug: z.string(),
    type: z.enum(["hard", "soft"]),
    category: z.enum(["frontend", "backend", "mobile", "devops", "data", "design", "management", "soft"]).optional(),
  });

export type UpdateSkillFormValues = {
  id: number;
  name: string;
  slug: string;
  type: string;
  category?: string;
};

export type UpdateSkillSchema = {
  id: number;
  name: string;
  slug: string;
  type: string;
  category?: string;
};