import type { RelationRef } from "@/helpers/api/relations";
import { z } from "zod";

export const swipeSchema = z.object({
  direction: z.enum(["like", "pass"]),
  context: z.enum(["recruit", "network"]),
});

export type SwipeSchema = z.infer<typeof swipeSchema>;

export const createSwipeSchema = () =>
  z.object({
    author_id: z.number({ error: "Sélection obligatoire" }),
    target_id: z.number({ error: "Sélection obligatoire" }),
    direction: z.enum(["like", "pass"]),
    context: z.enum(["recruit", "network"]),
  });

export type CreateSwipeFormValues = {
  author_id?: number;
  target_id?: number;
  direction: string;
  context: string;
};

export type CreateSwipeSchema = {
  author_id: number;
  target_id: number;
  direction: string;
  context: string;
};

export type GetSwipeSchema = {
  author?: RelationRef | null;
  target?: RelationRef | null;
  id: number;
  direction: string;
  context: string;
};

export const updateSwipeSchema = () =>
  z.object({
    author_id: z.number({ error: "Sélection obligatoire" }),
    target_id: z.number({ error: "Sélection obligatoire" }),
    id: z.number(),
    direction: z.enum(["like", "pass"]),
    context: z.enum(["recruit", "network"]),
  });

export type UpdateSwipeFormValues = {
  author_id?: number;
  target_id?: number;
  id: number;
  direction: string;
  context: string;
};

export type UpdateSwipeSchema = {
  author_id: number;
  target_id: number;
  id: number;
  direction: string;
  context: string;
};