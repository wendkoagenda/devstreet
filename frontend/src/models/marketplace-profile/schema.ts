import i18n from "i18next";
import { z } from "zod";

export type AvailabilityStatus = "available" | "partial" | "busy" | "leave";

const AVAILABILITY_STATUSES = [
  "available",
  "partial",
  "busy",
  "leave",
] as const satisfies readonly AvailabilityStatus[];

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

/** Libellés résolus à la lecture (suivent la langue i18n courante). */
export const AVAILABILITY_LABELS: Record<AvailabilityStatus, string> = new Proxy(
  {} as Record<AvailabilityStatus, string>,
  {
    get: (_target, prop: string) =>
      i18n.t(`marketplace.labels.availability_status.${prop}`),
    ownKeys: () => [...AVAILABILITY_STATUSES],
    getOwnPropertyDescriptor: () => ({ enumerable: true, configurable: true }),
  }
);

export function availabilityToForm(row: Availability | null): AvailabilityFormValues {
  return {
    start_date: row?.start_date ?? "",
    end_date: row?.end_date ?? "",
    // Sans période on est disponible : une nouvelle période est une plage occupée
    status: row?.status ?? "busy",
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

export type PrestationCategory = "web" | "mobile" | "design" | "devops" | "data" | "other";

export type Prestation = {
  id: number;
  title: string;
  slug: string;
  description: string;
  category: PrestationCategory;
  price: string;
  currency: string;
  delivery_days: number;
  revisions: number;
  cover_image: string;
  is_active: boolean;
};

export const PRESTATION_CATEGORY_LABELS: Record<PrestationCategory, string> = {
  web: "Web",
  mobile: "Mobile",
  design: "Design",
  devops: "DevOps",
  data: "Data",
  other: "Autre",
};

export const prestationFormSchema = z.object({
  title: z.string().trim().min(1, "Le titre est obligatoire").max(150),
  description: z.string().trim().min(1, "La description est obligatoire"),
  category: z.enum(["web", "mobile", "design", "devops", "data", "other"]),
  price: z
    .string()
    .trim()
    .refine((value) => /^\d+([.,]\d{1,2})?$/.test(value), "Prix invalide"),
  currency: z.string().regex(/^[A-Za-z]{3}$/, "Devise à 3 lettres"),
  delivery_days: z
    .string()
    .trim()
    .refine((value) => /^\d{1,3}$/.test(value) && Number(value) >= 1 && Number(value) <= 365, "Délai 1–365 jours"),
  revisions: z
    .string()
    .trim()
    .refine((value) => value === "" || (/^\d{1,2}$/.test(value) && Number(value) <= 50), "0–50 retouches"),
  is_active: z.boolean(),
});

export type PrestationFormValues = z.infer<typeof prestationFormSchema>;

export function prestationToForm(row: Prestation | null): PrestationFormValues {
  return {
    title: row?.title ?? "",
    description: row?.description ?? "",
    category: row?.category ?? "web",
    price: row?.price ? String(Number(row.price)) : "",
    currency: row?.currency ?? "XOF",
    delivery_days: row?.delivery_days != null ? String(row.delivery_days) : "5",
    revisions: row?.revisions != null ? String(row.revisions) : "1",
    is_active: row?.is_active ?? true,
  };
}

export function prestationToPayload(values: PrestationFormValues) {
  return {
    title: values.title,
    description: values.description,
    category: values.category,
    price: values.price.replace(",", "."),
    currency: values.currency.toUpperCase(),
    delivery_days: Number(values.delivery_days),
    revisions: values.revisions === "" ? 1 : Number(values.revisions),
    is_active: values.is_active,
  };
}

/** Mission acceptée en attente d'avis (UC-12). */
export type PendingReview = {
  candidature_id: number;
  role: "candidate" | "recruiter";
  offer: { id: number; title: string };
  target: { id: number; name: string; headline?: string };
  decided_at: string | null;
};

export const reviewFormSchema = z.object({
  rating: z.enum(["1", "2", "3", "4", "5"]),
  comment: z.string().trim().max(2000),
  is_public: z.boolean(),
});

export type ReviewFormValues = z.infer<typeof reviewFormSchema>;
