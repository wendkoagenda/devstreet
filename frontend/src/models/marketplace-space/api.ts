import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQuery } from "@/helpers/api/base-query";
import type { MySpace } from "./schema";

/** Profil et entreprise de l'utilisateur connecté (aucune permission RBAC : chacun gère ses propres données). */
export const marketplaceSpaceApi = createApi({
  reducerPath: "marketplaceSpaceApi",
  baseQuery,
  tagTypes: ["MySpace"],
  endpoints: (builder) => ({
    getMySpace: builder.query<MySpace, void>({
      query: () => "/marketplace/me",
      providesTags: ["MySpace"],
    }),
    createMyProfil: builder.mutation<MySpace, Record<string, unknown>>({
      query: (body) => ({
        url: "/marketplace/me/profil",
        method: "POST",
        body,
      }),
      invalidatesTags: ["MySpace"],
    }),
    updateMyProfil: builder.mutation<MySpace, Record<string, unknown>>({
      query: (body) => ({
        url: "/marketplace/me/profil",
        method: "PATCH",
        body,
      }),
      invalidatesTags: ["MySpace"],
    }),
    createMyCompany: builder.mutation<MySpace, Record<string, unknown>>({
      query: (body) => ({
        url: "/marketplace/me/company",
        method: "POST",
        body,
      }),
      invalidatesTags: ["MySpace"],
    }),
    updateMyCompany: builder.mutation<MySpace, Record<string, unknown>>({
      query: (body) => ({
        url: "/marketplace/me/company",
        method: "PATCH",
        body,
      }),
      invalidatesTags: ["MySpace"],
    }),
  }),
});

export const {
  useGetMySpaceQuery,
  useCreateMyProfilMutation,
  useUpdateMyProfilMutation,
  useCreateMyCompanyMutation,
  useUpdateMyCompanyMutation,
} = marketplaceSpaceApi;
