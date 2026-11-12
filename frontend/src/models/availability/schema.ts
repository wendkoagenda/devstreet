import type { RelationRef } from "@/helpers/api/relations";
import { z } from "zod";

export const availabilitySchema = z.object({
  start_date: z.string(),
  end_date: z.string(),
  status: z.enum(["available", "partial", "busy", "leave"]),
  hours_per_week: z.string().nullable().optional(),
  source: z.enum(["manual", "mission"]),
  note: z.string().optional(),
});

export type AvailabilitySchema = z.infer<typeof availabilitySchema>;

export const createAvailabilitySchema = () =>
  z.object({
    profil_id: z.number({ error: "Sélection obligatoire" }),
    start_date: z.string(),
    end_date: z.string(),
    status: z.enum(["available", "partial", "busy", "leave"]),
    hours_per_week: z.string().nullable().optional(),
    source: z.enum(["manual", "mission"]),
    note: z.string().nullable().optional(),
  });

export type CreateAvailabilityFormValues = {
  profil_id?: number;
  start_date: string;
  end_date: string;
  status: string;
  hours_per_week?: string | null;
  source: string;
  note?: string;
};

export type CreateAvailabilitySchema = {
  profil_id: number;
  start_date: string;
  end_date: string;
  status: string;
  hours_per_week?: string | null;
  source: string;
  note?: string;
};

export type GetAvailabilitySchema = {
  profil?: RelationRef | null;
  id: number;
  start_date: string;
  end_date: string;
  status: string;
  hours_per_week?: string | null;
  source: string;
  note?: string;
};

export const updateAvailabilitySchema = () =>
  z.object({
    profil_id: z.number({ error: "Sélection obligatoire" }),
    id: z.number(),
    start_date: z.string(),
    end_date: z.string(),
    status: z.enum(["available", "partial", "busy", "leave"]),
    hours_per_week: z.string().nullable().optional(),
    source: z.enum(["manual", "mission"]),
    note: z.string().nullable().optional(),
  });

export type UpdateAvailabilityFormValues = {
  profil_id?: number;
  id: number;
  start_date: string;
  end_date: string;
  status: string;
  hours_per_week?: string | null;
  source: string;
  note?: string;
};

export type UpdateAvailabilitySchema = {
  profil_id: number;
  id: number;
  start_date: string;
  end_date: string;
  status: string;
  hours_per_week?: string | null;
  source: string;
  note?: string;
};