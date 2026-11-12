import { z } from "zod";
import type { TFunction } from "i18next";

export const userSchema = z.object({
  username: z.string(),
  email: z.string(),
  first_name: z.string(),
  last_name: z.string(),
  password: z.string(),
  password_confirm: z.string(),
  role_names: z.array(z.string()).optional(),
  is_active: z.boolean().optional(),
});

export type UserSchema = z.infer<typeof userSchema>;

export const createUserSchema = (t: TFunction) =>
  z
    .object({
      username: z
        .string(t("validation.username.required"))
        .min(3, t("validation.username.min_length")),
      email: z
        .string(t("validation.email.required"))
        .email(t("validation.email.invalid")),
      first_name: z
        .string(t("validation.first_name.required"))
        .min(2, t("validation.first_name.min_length")),
      last_name: z
        .string(t("validation.last_name.required"))
        .min(2, t("validation.last_name.min_length")),
      password: z
        .string(t("validation.password.required"))
        .min(12, t("validation.password.min_length_new")),
      password_confirm: z
        .string(t("validation.password_confirm.required"))
        .min(12, t("validation.password.min_length_new")),
      role_names: z.array(z.string()).optional(),
      is_active: z.boolean(),
    })
    .refine((data) => data.password === data.password_confirm, {
      message: t("validation.password.not_match"),
      path: ["password_confirm"],
    });

export type CreateUserSchema = {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  password_confirm: string;
  role_names?: string[];
  is_active: boolean;
};

export type GetUserSchema = {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role_names: string[];
  is_active: boolean;
};

export const updateUserSchema = (t: TFunction) =>
  z.object({
    id: z.number(),
    username: z.string(),
    email: z.string().email(t("validation.email.invalid")),
    first_name: z.string().min(2, t("validation.first_name.min_length")),
    last_name: z.string().min(2, t("validation.last_name.min_length")),
    role_names: z.array(z.string()),
    is_active: z.boolean(),
  });

export type UpdateUserSchema = {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role_names: string[];
  is_active: boolean;
};

export interface User {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  password: string;
  password_confirm: string;
  roles?: string[];
  is_active?: boolean;
}
