import { z } from "zod";
import type { TFunction } from "i18next";

export const companySchema = z.object({
  name: z.string(),
  slug: z.string(),
  logo: z.string().optional(),
  description: z.string().optional(),
  sector: z.enum(["fintech", "ecommerce", "agritech", "edtech", "health", "ngo", "public", "other"]),
  size: z.enum(["1-10", "11-50", "51-200", "200+"]).optional(),
  website: z.string().optional(),
  contact_email: z.string().optional(),
  phone: z.string().optional(),
  country: z.string(),
  city: z.string().optional(),
  address: z.string().optional(),
  is_verified: z.boolean(),
  verified_at: z.string().nullable().optional(),
  logo_url: z.string().optional(),
});

export type CompanySchema = z.infer<typeof companySchema>;

export const createCompanySchema = (t: TFunction) =>
  z.object({
    name: z.string(t("validation.required")).min(1, t("validation.required")),
    slug: z.string(),
    description: z.string().nullable().optional(),
    sector: z.enum(["fintech", "ecommerce", "agritech", "edtech", "health", "ngo", "public", "other"]),
    size: z.enum(["1-10", "11-50", "51-200", "200+"]).optional(),
    website: z.string().optional(),
    contact_email: z.string().optional(),
    phone: z.string().nullable().optional(),
    country: z.string(t("validation.required")).min(1, t("validation.required")),
    city: z.string().nullable().optional(),
    address: z.string().nullable().optional(),
    is_verified: z.boolean(),
    verified_at: z.string().nullable().optional(),
  });

export type CreateCompanyFormValues = {
  name: string;
  slug: string;
  description?: string;
  sector: string;
  size?: string;
  website?: string;
  contact_email?: string;
  phone?: string;
  country: string;
  city?: string;
  address?: string;
  is_verified: boolean;
  verified_at?: string | null;
};

export type CreateCompanySchema = {
  name: string;
  slug: string;
  description?: string;
  sector: string;
  size?: string;
  website?: string;
  contact_email?: string;
  phone?: string;
  country: string;
  city?: string;
  address?: string;
  is_verified: boolean;
  verified_at?: string | null;
};

export type GetCompanySchema = {
  id: number;
  name: string;
  slug: string;
  logo?: string;
  description?: string;
  sector: string;
  size?: string;
  website?: string;
  contact_email?: string;
  phone?: string;
  country: string;
  city?: string;
  address?: string;
  is_verified: boolean;
  verified_at?: string | null;
  logo_url?: string;
};

export const updateCompanySchema = (t: TFunction) =>
  z.object({
    id: z.number(),
    name: z.string(t("validation.required")).min(1, t("validation.required")),
    slug: z.string(),
    description: z.string().nullable().optional(),
    sector: z.enum(["fintech", "ecommerce", "agritech", "edtech", "health", "ngo", "public", "other"]),
    size: z.enum(["1-10", "11-50", "51-200", "200+"]).optional(),
    website: z.string().optional(),
    contact_email: z.string().optional(),
    phone: z.string().nullable().optional(),
    country: z.string(t("validation.required")).min(1, t("validation.required")),
    city: z.string().nullable().optional(),
    address: z.string().nullable().optional(),
    is_verified: z.boolean(),
    verified_at: z.string().nullable().optional(),
  });

export type UpdateCompanyFormValues = {
  id: number;
  name: string;
  slug: string;
  description?: string;
  sector: string;
  size?: string;
  website?: string;
  contact_email?: string;
  phone?: string;
  country: string;
  city?: string;
  address?: string;
  is_verified: boolean;
  verified_at?: string | null;
};

export type UpdateCompanySchema = {
  id: number;
  name: string;
  slug: string;
  description?: string;
  sector: string;
  size?: string;
  website?: string;
  contact_email?: string;
  phone?: string;
  country: string;
  city?: string;
  address?: string;
  is_verified: boolean;
  verified_at?: string | null;
};