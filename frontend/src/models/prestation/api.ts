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
  CreatePrestationSchema,
  GetPrestationSchema,
  UpdatePrestationSchema,
} from "./schema";

const FILE_FIELDS = [{"name": "cover_image", "uploadFolder": "prestations/cover_image"}] as const;

export type CreatePrestationMutationArg = CreatePrestationSchema & {
  _files?: Record<string, File | undefined>;
};

export type UpdatePrestationMutationArg = UpdatePrestationSchema & {
  _files?: Record<string, File | undefined>;
};

export const prestationApi = createApi({
  reducerPath: "prestationApi",
  baseQuery,
  tagTypes: ["Prestations"],
  endpoints: (builder) => ({
    createPrestation: builder.mutation<void, CreatePrestationMutationArg>({
      query: (payload) => {
        const { _files, ...body } = payload;
        if (hasFilePayload([...FILE_FIELDS], _files)) {
          return {
            url: "/prestations",
            method: "POST",
            body: buildModelFormData(body, {
              fileFields: [...FILE_FIELDS],
              fileValues: _files,
            }),
          };
        }
        return {
          url: "/prestations",
          method: "POST",
          body,
        };
      },
      invalidatesTags: ["Prestations"],
    }),
    getPrestations: builder.query<Paginated<GetPrestationSchema>, ListParams | void>({
      query: (params) => `/prestations${toQueryString(params)}`,
      providesTags: ["Prestations"],
    }),
    getPrestation: builder.query<GetPrestationSchema, number>({
      query: (id) => `/prestations/${id}`,
      providesTags: ["Prestations"],
    }),
    updatePrestation: builder.mutation<void, UpdatePrestationMutationArg>({
      query: (payload) => {
        const { _files, ...body } = payload;
        if (hasFilePayload([...FILE_FIELDS], _files)) {
          return {
            url: `/prestations/${payload.id}`,
            method: "PUT",
            body: buildModelFormData(body, {
              fileFields: [...FILE_FIELDS],
              fileValues: _files,
            }),
          };
        }
        return {
          url: `/prestations/${payload.id}`,
          method: "PUT",
          body,
        };
      },
      invalidatesTags: ["Prestations"],
    }),
    deletePrestation: builder.mutation<void, number>({
      query: (id) => ({
        url: `/prestations/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Prestations"],
    }),
  }),
});

export const {
  useCreatePrestationMutation,
  useGetPrestationsQuery,
  useGetPrestationQuery,
  useUpdatePrestationMutation,
  useDeletePrestationMutation,
} = prestationApi;