import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQuery } from "@/helpers/api/base-query";
import type {
  CreateUserSchema,
  GetUserSchema,
  UpdateUserSchema,
} from "./schema";

export const userApi = createApi({
  reducerPath: "userApi",
  baseQuery,
  tagTypes: ["Users"],
  endpoints: (builder) => ({
    createUser: builder.mutation<void, CreateUserSchema>({
      query: (newUser) => ({
        url: "/users",
        method: "POST",
        body: newUser,
      }),
      invalidatesTags: ["Users"],
    }),

    getUsers: builder.query<GetUserSchema[], void>({
      query: () => "/users",
      providesTags: ["Users"],
    }),

    getUser: builder.query<GetUserSchema, number>({
      query: (id) => `/users/${id}`,
      providesTags: ["Users"],
    }),

    

    updateUser: builder.mutation<void, UpdateUserSchema>({
      query: (updatedUser) => ({
        url: `/users/${updatedUser.id}`,
        method: "PUT",
        body: updatedUser,
      }),
      invalidatesTags: ["Users"],
    }),

    deleteUser: builder.mutation<void, number>({
      query: (id) => ({
        url: `/users/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Users"],
    }),
  }),
});

export const {
  useCreateUserMutation,
  useGetUsersQuery,
  useGetUserQuery,
  useUpdateUserMutation,
  useDeleteUserMutation,
} = userApi;
