import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQuery } from "@/helpers/api/base-query";
import {
  toQueryString,
  type ListParams,
  type Paginated,
} from "@/helpers/api/pagination";
import type {
  CreateProfilHistorySchema,
  GetProfilHistorySchema,
  UpdateProfilHistorySchema,
} from "./schema";

export type CreateProfilHistoryMutationArg = CreateProfilHistorySchema;
export type UpdateProfilHistoryMutationArg = UpdateProfilHistorySchema;

export const profilHistoryApi = createApi({
  reducerPath: "profilHistoryApi",
  baseQuery,
  tagTypes: ["ProfilHistories"],
  endpoints: (builder) => ({
    createProfilHistory: builder.mutation<void, CreateProfilHistoryMutationArg>({
      query: (payload) => {
        return {
          url: "/profil-histories",
          method: "POST",
          body: payload,
        };
      },
      invalidatesTags: ["ProfilHistories"],
    }),
    getProfilHistories: builder.query<Paginated<GetProfilHistorySchema>, ListParams | void>({
      query: (params) => `/profil-histories${toQueryString(params)}`,
      providesTags: ["ProfilHistories"],
    }),
    getProfilHistory: builder.query<GetProfilHistorySchema, number>({
      query: (id) => `/profil-histories/${id}`,
      providesTags: ["ProfilHistories"],
    }),
    updateProfilHistory: builder.mutation<void, UpdateProfilHistoryMutationArg>({
      query: (payload) => {
        return {
          url: `/profil-histories/${payload.id}`,
          method: "PUT",
          body: payload,
        };
      },
      invalidatesTags: ["ProfilHistories"],
    }),
    deleteProfilHistory: builder.mutation<void, number>({
      query: (id) => ({
        url: `/profil-histories/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["ProfilHistories"],
    }),
  }),
});

export const {
  useCreateProfilHistoryMutation,
  useGetProfilHistoriesQuery,
  useGetProfilHistoryQuery,
  useUpdateProfilHistoryMutation,
  useDeleteProfilHistoryMutation,
} = profilHistoryApi;