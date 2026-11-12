import type { RelationRef } from "@/helpers/api/relations";
import { z } from "zod";

export const reviewSchema = z.object({
  rating: z.string(),
  comment: z.string().optional(),
  is_public: z.boolean(),
});

export type ReviewSchema = z.infer<typeof reviewSchema>;

export const createReviewSchema = () =>
  z.object({
    target_id: z.number({ error: "Sélection obligatoire" }),
    author_id: z.number({ error: "Sélection obligatoire" }),
    candidature_id: z.number().nullable().optional(),
    rating: z.string(),
    comment: z.string().nullable().optional(),
    is_public: z.boolean(),
  });

export type CreateReviewFormValues = {
  target_id?: number;
  author_id?: number;
  candidature_id?: number | null;
  rating: string;
  comment?: string;
  is_public: boolean;
};

export type CreateReviewSchema = {
  target_id: number;
  author_id: number;
  candidature_id?: number | null;
  rating: string;
  comment?: string;
  is_public: boolean;
};

export type GetReviewSchema = {
  target?: RelationRef | null;
  author?: RelationRef | null;
  candidature?: RelationRef | null;
  id: number;
  rating: string;
  comment?: string;
  is_public: boolean;
};

export const updateReviewSchema = () =>
  z.object({
    target_id: z.number({ error: "Sélection obligatoire" }),
    author_id: z.number({ error: "Sélection obligatoire" }),
    candidature_id: z.number().nullable().optional(),
    id: z.number(),
    rating: z.string(),
    comment: z.string().nullable().optional(),
    is_public: z.boolean(),
  });

export type UpdateReviewFormValues = {
  target_id?: number;
  author_id?: number;
  candidature_id?: number | null;
  id: number;
  rating: string;
  comment?: string;
  is_public: boolean;
};

export type UpdateReviewSchema = {
  target_id: number;
  author_id: number;
  candidature_id?: number | null;
  id: number;
  rating: string;
  comment?: string;
  is_public: boolean;
};