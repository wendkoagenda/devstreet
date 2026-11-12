import { baseQuery } from "@/helpers/api/base-query";
import { createApi } from "@reduxjs/toolkit/query/react";
import type {
  AssignPermissionToRoleSchema,
  CreateRoleSchema,
  Permission,
  Role,
  UpdateRoleSchema,
} from "./schema";

export const rolePermissionApi = createApi({
  reducerPath: "rolePermissionApi",
  baseQuery,
  tagTypes: ["Role", "Permission", "UserPermissions"],

  endpoints: (builder) => ({
    // Endpoints pour les rôles
    getRoles: builder.query<Role[], void>({
      query: () => "/roles",
      providesTags: ["Role"],
    }),

    createRole: builder.mutation<Role, CreateRoleSchema>({
      query: (newRole) => ({
        url: "/roles",
        method: "POST",
        body: newRole,
      }),
      invalidatesTags: ["Role"],
    }),

    updateRole: builder.mutation<Role, UpdateRoleSchema>({
      query: ({ id, ...body }) => ({
        url: `/roles/${id}`,
        method: "PUT",
        body,
      }),
      invalidatesTags: (_, __, { id }) => [{ type: "Role", id }],
    }),

    assignPermissionToRole: builder.mutation<
      void,
      AssignPermissionToRoleSchema
    >({
      query: (payload) => ({
        url: `/roles/${payload.id}/bulk_assign_permissions`,
        method: "POST",
        body: {
          permission_codes: payload.permission_codes,
        },
      }),
      invalidatesTags: ["Role"],
    }),

    deleteRole: builder.mutation<void, number>({
      query: (id) => ({
        url: `/roles/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Role"],
    }),

    // Endpoints pour les permissions
    getPermissions: builder.query<Permission[], void>({
      query: () => "/permissions",
      providesTags: (result) =>
        result
          ? [
              ...result.map(({ id }) => ({ type: "Permission" as const, id })),
              { type: "Permission", id: "LIST" },
            ]
          : [{ type: "Permission", id: "LIST" }],
    }),

    getUserPermissions: builder.query<string[], number>({
      query: (userId) => `/users/${userId}/permissions`,
      providesTags: (_, __, userId) => [
        { type: "UserPermissions", id: userId },
      ],
      transformResponse: (response: { permissions: string[] }) => {
        if (response?.permissions && Array.isArray(response.permissions)) {
          return response.permissions;
        }
        // Une réponse inattendue est une erreur : on ne la masque pas par une liste vide (« aucun droit »)
        throw new Error("Format de réponse inattendu pour les permissions");
      },
    }),

    createPermission: builder.mutation<
      Permission,
      Omit<Permission, "id" | "created_at" | "updated_at" | "role_count">
    >({
      query: (newPermission) => ({
        url: "/permissions",
        method: "POST",
        body: newPermission,
      }),
      invalidatesTags: [{ type: "Permission", id: "LIST" }],
    }),

    updatePermission: builder.mutation<Permission, Permission>({
      query: (updatedPermission) => ({
        url: `/permissions/${updatedPermission.id}`,
        method: "PUT",
        body: updatedPermission,
      }),
      invalidatesTags: (_, __, arg) => [{ type: "Permission", id: arg.id }],
    }),

    deletePermission: builder.mutation<void, number>({
      query: (id) => ({
        url: `/permissions/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: (_, __, id) => [{ type: "Permission", id }],
    }),
  }),
});

export const {
  // Rôles
  useCreateRoleMutation,
  useGetRolesQuery,
  useUpdateRoleMutation,
  useDeleteRoleMutation,
  useAssignPermissionToRoleMutation,

  // Permissions
  useGetPermissionsQuery,
  useCreatePermissionMutation,
  useUpdatePermissionMutation,
  useDeletePermissionMutation,
  useGetUserPermissionsQuery,
} = rolePermissionApi;
