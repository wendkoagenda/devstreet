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
  CreateCandidatureSchema,
  GetCandidatureSchema,
  UpdateCandidatureSchema,
} from "./schema";

const FILE_FIELDS = [{"name": "cv_snapshot", "uploadFolder": "candidatures/cv_snapshot"}] as const;

export type CreateCandidatureMutationArg = CreateCandidatureSchema & {
  _files?: Record<string, File | undefined>;
};

export type UpdateCandidatureMutationArg = UpdateCandidatureSchema & {
  _files?: Record<string, File | undefined>;
};

export const candidatureApi = createApi({
  reducerPath: "candidatureApi",
  baseQuery,
  tagTypes: ["Candidatures"],
  endpoints: (builder) => ({
    createCandidature: builder.mutation<void, CreateCandidatureMutationArg>({
      query: (payload) => {
        const { _files, ...body } = payload;
        if (hasFilePayload([...FILE_FIELDS], _files)) {
          return {
            url: "/candidatures",
            method: "POST",
            body: buildModelFormData(body, {
              fileFields: [...FILE_FIELDS],
              fileValues: _files,
            }),
          };
        }
        return {
          url: "/candidatures",
          method: "POST",
          body,
        };
      },
      invalidatesTags: ["Candidatures"],
    }),
    getCandidatures: builder.query<Paginated<GetCandidatureSchema>, ListParams | void>({
      query: (params) => `/candidatures${toQueryString(params)}`,
      providesTags: ["Candidatures"],
    }),
    getCandidature: builder.query<GetCandidatureSchema, number>({
      query: (id) => `/candidatures/${id}`,
      providesTags: ["Candidatures"],
    }),
    updateCandidature: builder.mutation<void, UpdateCandidatureMutationArg>({
      query: (payload) => {
        const { _files, ...body } = payload;
        if (hasFilePayload([...FILE_FIELDS], _files)) {
          return {
            url: `/candidatures/${payload.id}`,
            method: "PUT",
            body: buildModelFormData(body, {
              fileFields: [...FILE_FIELDS],
              fileValues: _files,
            }),
          };
        }
        return {
          url: `/candidatures/${payload.id}`,
          method: "PUT",
          body,
        };
      },
      invalidatesTags: ["Candidatures"],
    }),
    deleteCandidature: builder.mutation<void, number>({
      query: (id) => ({
        url: `/candidatures/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Candidatures"],
    }),
  }),
});

export const {
  useCreateCandidatureMutation,
  useGetCandidaturesQuery,
  useGetCandidatureQuery,
  useUpdateCandidatureMutation,
  useDeleteCandidatureMutation,
} = candidatureApi;