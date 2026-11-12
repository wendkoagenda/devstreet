import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQuery } from "@/helpers/api/base-query";
import {
  toQueryString,
  type ListParams,
  type Paginated,
} from "@/helpers/api/pagination";
import {
  buildModelFormData,
  hasFilePayload,
} from "@/helpers/api/form-data-builder";
import type {
  CreateProfilSchema,
  GetProfilSchema,
  UpdateProfilSchema,
} from "./schema";

const FILE_FIELDS = [{"name": "photo", "uploadFolder": "profils/photo"}] as const;

export type CreateProfilMutationArg = CreateProfilSchema & {
  _files?: Record<string, File | undefined>;
};

export type UpdateProfilMutationArg = UpdateProfilSchema & {
  _files?: Record<string, File | undefined>;
};

export const profilApi = createApi({
  reducerPath: "profilApi",
  baseQuery,
  tagTypes: ["Profils"],
  endpoints: (builder) => ({
    createProfil: builder.mutation<void, CreateProfilMutationArg>({
      query: (payload) => {
        const { _files, ...body } = payload;
        if (hasFilePayload([...FILE_FIELDS], _files)) {
          return {
            url: "/profils",
            method: "POST",
            body: buildModelFormData(body, {
              fileFields: [...FILE_FIELDS],
              fileValues: _files,
            }),
          };
        }
        return {
          url: "/profils",
          method: "POST",
          body,
        };
      },
      invalidatesTags: ["Profils"],
    }),
    getProfils: builder.query<Paginated<GetProfilSchema>, ListParams | void>({
      query: (params) => `/profils${toQueryString(params)}`,
      providesTags: ["Profils"],
    }),
    getProfil: builder.query<GetProfilSchema, number>({
      query: (id) => `/profils/${id}`,
      providesTags: ["Profils"],
    }),
    updateProfil: builder.mutation<void, UpdateProfilMutationArg>({
      query: (payload) => {
        const { _files, ...body } = payload;
        if (hasFilePayload([...FILE_FIELDS], _files)) {
          return {
            url: `/profils/${payload.id}`,
            method: "PUT",
            body: buildModelFormData(body, {
              fileFields: [...FILE_FIELDS],
              fileValues: _files,
            }),
          };
        }
        return {
          url: `/profils/${payload.id}`,
          method: "PUT",
          body,
        };
      },
      invalidatesTags: ["Profils"],
    }),
    deleteProfil: builder.mutation<void, number>({
      query: (id) => ({
        url: `/profils/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Profils"],
    }),
  }),
});

export const {
  useCreateProfilMutation,
  useGetProfilsQuery,
  useGetProfilQuery,
  useUpdateProfilMutation,
  useDeleteProfilMutation,
} = profilApi;