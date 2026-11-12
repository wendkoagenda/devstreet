import { z } from "zod";

// =============================================
// Schémas de base
// =============================================
export const roleSchema = z.object({
  name: z.string().min(1, "Le nom est obligatoire"),
  description: z.string().optional(),
  permission_codes: z.array(z.string()).optional(),
});

export const updateRoleSchema = z.object({
  id: z.number().positive("ID invalide"),
  name: z.string().min(1, "Le nom est obligatoire"),
  description: z.string().optional(),
  permission_codes: z.array(z.string()).optional(),
});

export const assignPermissionSchema = z.object({
  id: z.number().positive("ID invalide"),
  permission_codes: z
    .array(z.string())
    .min(1, "Au moins une permission est requise"),
});

export const permissionSchema = z.object({
  code: z.string().min(1, "Le code est obligatoire"),
  description: z.string().min(1, "La description est obligatoire"),
});

// =============================================
// Types Zod
// =============================================
export type RoleSchema = z.infer<typeof roleSchema>;
export type CreateRoleSchema = z.infer<typeof roleSchema>;
export type UpdateRoleSchema = z.infer<typeof updateRoleSchema>;
export type AssignPermissionToRoleSchema = z.infer<
  typeof assignPermissionSchema
>;
export type PermissionSchema = z.infer<typeof permissionSchema>;

// =============================================
// Interfaces et types (basées sur les sérialiseurs backend)
// =============================================
export interface Role {
  id: number;
  name: string;
  description: string;
  permissions: Permission[];
  user_count: number;
  permission_count: number;
  created_at: string;
  updated_at: string;
}

export interface Permission {
  id: number;
  code: string;
  description: string;
  role_count: number;
  created_at: string;
  updated_at: string;
}

export type CreateRolePayload = Omit<Role, "id" | "permissions">;
export type UpdateRolePayload = Pick<Role, "id" | "name" | "description">;
export type AssignPermissionsPayload = AssignPermissionToRoleSchema;

// =============================================
// Types de réponse API
// =============================================
export interface UserPermissionsResponse {
  permissions: string[];
}

export interface PermissionCheckResponse {
  has_permission: boolean;
}
