import { z } from "zod";

export type AvailabilityStatus = "available" | "partial" | "busy" | "leave";

export type Availability = {
  id: number;
  start_date: string;
  end_date: string;
  status: AvailabilityStatus;
  hours_per_week: number | null;
  /** « mission » : période ajoutée par une candidature acceptée (non modifiable). */
  source: "manual" | "mission";
  note: string;
};

export type Experience = {
  id: number;
  title: string;
  company_name: string;
  location: string;
  contract_type: "" | "cdi" | "cdd" | "freelance" | "stage";
  start_date: string;
  end_date: string | null;
  is_current: boolean;
  description: string;
  technologies: string;
};

const date = z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Date obligatoire");

export const availabilityFormSchema = z
  .object({
    start_date: date,
    end_date: date,
    status: z.enum(["available", "partial", "busy", "leave"]),
    hours_per_week: z
      .string()
      .trim()
      .refine((value) => value === "" || /^\d{1,2}$/.test(value), "Heures entre 0 et 80"),
    note: z.string().trim().max(255),
  })
  .refine((values) => values.end_date >= values.start_date, {
    path: ["end_date"],
    message: "La fin doit suivre le début",
  });

export type AvailabilityFormValues = z.infer<typeof availabilityFormSchema>;

export const AVAILABILITY_LABELS: Record<AvailabilityStatus, string> = {
  available: "Disponible",
  partial: "Partiel",
  busy: "Occupé",
  leave: "Congé",
};

export function availabilityToForm(row: Availability | null): AvailabilityFormValues {
  return {
    start_date: row?.start_date ?? "",
    end_date: row?.end_date ?? "",
    status: row?.status ?? "available",
    hours_per_week: row?.hours_per_week != null ? String(row.hours_per_week) : "",
    note: row?.note ?? "",
  };
}

export function availabilityToPayload(values: AvailabilityFormValues) {
  return {
    ...values,
    hours_per_week: values.hours_per_week === "" ? null : Number(values.hours_per_week),
  };
}

export const experienceFormSchema = z
  .object({
    title: z.string().trim().min(1, "Le poste est obligatoire").max(150),
    company_name: z.string().trim().min(1, "L'entreprise est obligatoire").max(150),
    location: z.string().trim().max(150),
    contract_type: z.enum(["", "cdi", "cdd", "freelance", "stage"]),
    start_date: date,
    end_date: z.string().refine((value) => value === "" || /^\d{4}-\d{2}-\d{2}$/.test(value), "Date invalide"),
    is_current: z.boolean(),
    description: z.string().trim(),
    technologies: z.string().trim().max(255),
  })
  .refine((values) => values.is_current || values.end_date === "" || values.end_date >= values.start_date, {
    path: ["end_date"],
    message: "La fin doit suivre le début",
  });

export type ExperienceFormValues = z.infer<typeof experienceFormSchema>;

export function experienceToForm(row: Experience | null): ExperienceFormValues {
  return {
    title: row?.title ?? "",
    company_name: row?.company_name ?? "",
    location: row?.location ?? "",
    contract_type: row?.contract_type ?? "",
    start_date: row?.start_date ?? "",
    end_date: row?.end_date ?? "",
    is_current: row?.is_current ?? false,
    description: row?.description ?? "",
    technologies: row?.technologies ?? "",
  };
}

export function experienceToPayload(values: ExperienceFormValues) {
  return {
    ...values,
    end_date: values.is_current || values.end_date === "" ? null : values.end_date,
  };
}
