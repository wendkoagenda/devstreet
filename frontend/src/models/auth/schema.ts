import { TFunction } from "i18next";
import { z } from "zod";

export const loginSchema = (t: TFunction) =>
  z.object({
    email: z.string().email(t("validation.email.invalid")),
    password: z.string().min(8, t("validation.password.min_length")),
  });

export type LoginSchema = {
  email: string;
  password: string;
};

export const registerSchema = (t: TFunction) =>
  z
    .object({
      first_name: z.string().min(1, t("validation.first_name.required")),
      last_name: z.string().min(1, t("validation.last_name.required")),
      username: z
        .string()
        .trim()
        .min(3, t("validation.username.min_length"))
        .max(150),
      email: z.string().email(t("validation.email.invalid")),
      password: z.string().min(8, t("validation.password.min_length")),
      password_confirm: z
        .string()
        .min(1, t("validation.password_confirm.required")),
    })
    .refine((data) => data.password === data.password_confirm, {
      message: t("validation.password.not_match"),
      path: ["password_confirm"],
    });

export type RegisterSchema = {
  first_name: string;
  last_name: string;
  username: string;
  email: string;
  password: string;
  password_confirm: string;
};

/** Réponse de connexion : les jetons sont dans des cookies HttpOnly, jamais dans le corps. */
export type LoginResponse = {
  user: {
    id: number;
    email: string;
    username: string;
    full_name: string;
    photo?: string;
    banner?: string;
    roles: string[];
  };
};

export interface Auth {
  username: string;
  password: string;
}
/** Type de compte choisi à l'onboarding ("" tant que le membre n'a pas choisi). */
export type AccountType = "" | "dev" | "entreprise" | "both";

export interface User {
  id: number;
  first_name?: string;
  last_name?: string;
  full_name: string;
  username: string;
  email: string;
  photo?: string;
  banner?: string;
  roles?: string[];
  permissions?: string[];
  /** Type de compte (dev, entreprise, les deux) ; vide tant que le choix n'est pas fait. */
  account_type?: AccountType;
  /** Compte d'administration de la plateforme : pas d'onboarding, menu Administration conservé. */
  is_admin?: boolean;
  /** Vrai tant que le membre (hors administrateur) n'a pas choisi son type de compte. */
  onboarding_required?: boolean;
}

export interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: User | null;
  permissions: string[];

  // États des dialogues
  isChangePasswordDialogOpen: boolean;

  // Méthodes de gestion des permissions
  setPermissions: (permissions: string[]) => void;
  hasPermission: (permission: string) => boolean;

  // Méthodes d'authentification
  loadSession: () => Promise<boolean>;
  logout: () => Promise<void>;
  initializeAuth: () => Promise<void>;
  reinitializeAuth: () => void;

  // Méthodes de gestion des dialogues
  openChangePasswordDialog: () => void;
  closeChangePasswordDialog: () => void;

  // Méthodes utilitaires
  getCurrentUserId: () => number | string | null;

  // État d'initialisation
  isInitialized: boolean;
}

export const changePasswordSchema = (t: TFunction) =>
  z.object({
    old_password: z.string().min(1, t("validation.password.required")),
    new_password: z.string().min(12, t("validation.password.min_length_new")),
    new_password_confirm: z
      .string()
      .min(1, t("validation.password_confirm.required")),
  });

export type ChangePasswordSchema = {
  old_password: string;
  new_password: string;
  new_password_confirm: string;
};

export type ChangePasswordResponse = {
  message: string;
};

// ======================== MOT DE PASSE OUBLIÉ ========================
export const forgotPasswordEmailSchema = (t: TFunction) =>
  z.object({
    email: z.string().email(t("validation.email.invalid")),
  });

export type ForgotPasswordEmailSchema = {
  email: string;
};

export const verifyResetCodeSchema = (t: TFunction) =>
  z.object({
    code: z.string().regex(/^\d{6}$/, t("forgot_password.code_invalid")),
  });

export type VerifyResetCodeSchema = {
  code: string;
};

export const resetPasswordSchema = (t: TFunction) =>
  z
    .object({
      new_password: z.string().min(12, t("validation.password.min_length_new")),
      new_password_confirm: z
        .string()
        .min(1, t("validation.password_confirm.required")),
    })
    .refine((data) => data.new_password === data.new_password_confirm, {
      message: t("validation.password.not_match"),
      path: ["new_password_confirm"],
    });

export type ResetPasswordSchema = {
  new_password: string;
  new_password_confirm: string;
};

export type ForgotPasswordRequest = {
  email: string;
};

export type ForgotPasswordResponse = {
  message: string;
};

export type VerifyResetCodeRequest = {
  email: string;
  code: string;
};

export type VerifyResetCodeResponse = {
  message: string;
  reset_token: string;
};

export type ConfirmPasswordResetRequest = {
  reset_token: string;
  new_password: string;
  new_password_confirm: string;
};

export type ConfirmPasswordResetResponse = {
  message: string;
};
