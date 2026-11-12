import { z } from "zod";

/** Profil de l'utilisateur connecté, tel que renvoyé par GET /marketplace/me. */
export type MyProfil = {
  id: number;
  user_id: number;
  is_company_owner: boolean;
  slug: string;
  headline: string;
  bio: string;
  phone: string;
  country: string;
  city: string;
  remote: boolean;
  timezone: string;
  default_hours_per_week: number;
  is_open_to_work: boolean;
  daily_rate: string | null;
  currency: string;
  years_of_experience: number;
  languages: { language: string; level?: string }[];
  github_url: string;
  linkedin_url: string;
  portfolio_url: string;
  cv_visibility: "public" | "companies" | "private";
  company: { id: number; __str__: string } | null;
};

/** Entreprise rattachée au profil de l'utilisateur. */
export type MyCompany = {
  id: number;
  name: string;
  slug: string;
  description: string;
  sector: string;
  size: string;
  website: string;
  contact_email: string;
  phone: string;
  country: string;
  city: string;
  address: string;
  is_verified: boolean;
};

export type MySpace = { profil: MyProfil | null; company: MyCompany | null };

const optionalUrl = z
  .string()
  .trim()
  .refine(
    (value) => value === "" || /^https?:\/\/\S+$/i.test(value),
    "Adresse web invalide (https://…)"
  );

const country = z.string().regex(/^[A-Za-z]{2}$/, "Choisissez un pays");

/** Formulaire du profil : les nombres restent des chaînes dans le formulaire (convertis à l'envoi). */
export const profilFormSchema = z.object({
  headline: z.string().trim().max(160, "160 caractères au maximum"),
  bio: z.string().trim(),
  phone: z.string().trim().max(20, "20 caractères au maximum"),
  country,
  city: z.string().trim().max(100),
  languages: z.string().trim(),
  timezone: z.string().min(1, "Choisissez un fuseau horaire"),
  remote: z.boolean(),
  is_open_to_work: z.boolean(),
  default_hours_per_week: z
    .string()
    .regex(/^\d{1,2}$/, "Nombre d'heures entre 0 et 99"),
  years_of_experience: z
    .string()
    .regex(/^\d{1,2}$/, "Nombre d'années entre 0 et 99"),
  daily_rate: z
    .string()
    .trim()
    .refine(
      (value) => value === "" || /^\d+([.,]\d{1,2})?$/.test(value),
      "Montant invalide"
    ),
  currency: z.string().min(1, "Choisissez une devise"),
  github_url: optionalUrl,
  linkedin_url: optionalUrl,
  portfolio_url: optionalUrl,
  cv_visibility: z.enum(["public", "companies", "private"]),
});

export type ProfilFormValues = z.infer<typeof profilFormSchema>;

export const companyFormSchema = z.object({
  name: z.string().trim().min(1, "Le nom est obligatoire").max(150),
  description: z.string().trim(),
  sector: z.enum([
    "fintech",
    "ecommerce",
    "agritech",
    "edtech",
    "health",
    "ngo",
    "public",
    "other",
  ]),
  size: z.enum(["", "1-10", "11-50", "51-200", "200+"]),
  website: optionalUrl,
  contact_email: z
    .string()
    .trim()
    .refine(
      (value) => value === "" || /^\S+@\S+\.\S+$/.test(value),
      "E-mail invalide"
    ),
  phone: z.string().trim().max(20, "20 caractères au maximum"),
  country,
  city: z.string().trim().max(100),
  address: z.string().trim().max(255),
});

export type CompanyFormValues = z.infer<typeof companyFormSchema>;

/** Valeurs initiales du formulaire de profil (création : celles par défaut du modèle). */
export function profilToForm(profil: MyProfil | null): ProfilFormValues {
  return {
    headline: profil?.headline ?? "",
    bio: profil?.bio ?? "",
    phone: profil?.phone ?? "",
    country: profil?.country ?? "",
    city: profil?.city ?? "",
    languages: (profil?.languages ?? []).map((item) => item.language).join(", "),
    timezone: profil?.timezone ?? "",
    remote: profil?.remote ?? true,
    is_open_to_work: profil?.is_open_to_work ?? true,
    default_hours_per_week: String(profil?.default_hours_per_week ?? 40),
    years_of_experience: String(profil?.years_of_experience ?? 0),
    daily_rate: profil?.daily_rate ? String(Number(profil.daily_rate)) : "",
    currency: profil?.currency ?? "XOF",
    github_url: profil?.github_url ?? "",
    linkedin_url: profil?.linkedin_url ?? "",
    portfolio_url: profil?.portfolio_url ?? "",
    cv_visibility: profil?.cv_visibility ?? "companies",
  };
}

/** Corps de la requête : nombres convertis, langues transformées en liste d'objets. */
export function profilToPayload(values: ProfilFormValues) {
  return {
    ...values,
    country: values.country.toUpperCase(),
    default_hours_per_week: Number(values.default_hours_per_week),
    years_of_experience: Number(values.years_of_experience),
    daily_rate:
      values.daily_rate === "" ? null : values.daily_rate.replace(",", "."),
    languages: values.languages
      .split(",")
      .map((name) => name.trim())
      .filter(Boolean)
      .map((language) => ({ language })),
  };
}

export function companyToForm(company: MyCompany | null): CompanyFormValues {
  return {
    name: company?.name ?? "",
    description: company?.description ?? "",
    sector: (company?.sector as CompanyFormValues["sector"]) ?? "other",
    size: (company?.size as CompanyFormValues["size"]) ?? "",
    website: company?.website ?? "",
    contact_email: company?.contact_email ?? "",
    phone: company?.phone ?? "",
    country: company?.country ?? "",
    city: company?.city ?? "",
    address: company?.address ?? "",
  };
}

export function companyToPayload(values: CompanyFormValues) {
  return { ...values, country: values.country.toUpperCase() };
}
