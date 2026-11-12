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
  CreateFusionSchema,
  GetFusionSchema,
  UpdateFusionSchema,
} from "./schema";

const FILE_FIELDS = [{"name": "document", "uploadFolder": "fusion_documents"}] as const;

export type CreateFusionMutationArg = CreateFusionSchema & {
  _files?: Record<string, File | undefined>;
};

export type UpdateFusionMutationArg = UpdateFusionSchema & {
  _files?: Record<string, File | undefined>;
};

export const fusionApi = createApi({
  reducerPath: "fusionApi",
  baseQuery,
  tagTypes: ["Fusions"],
  endpoints: (builder) => ({
    createFusion: builder.mutation<void, CreateFusionMutationArg>({
      query: (payload) => {
        const { _files, ...body } = payload;
        if (hasFilePayload([...FILE_FIELDS], _files)) {
          return {
            url: "/fusions",
            method: "POST",
            body: buildModelFormData(body, {
              fileFields: [...FILE_FIELDS],
              fileValues: _files,
            }),
          };
        }
        return {
          url: "/fusions",
          method: "POST",
          body,
        };
      },
      invalidatesTags: ["Fusions"],
    }),
    getFusions: builder.query<Paginated<GetFusionSchema>, ListParams | void>({
      query: (params) => `/fusions${toQueryString(params)}`,
      providesTags: ["Fusions"],
    }),
    getFusion: builder.query<GetFusionSchema, number>({
      query: (id) => `/fusions/${id}`,
      providesTags: ["Fusions"],
    }),
    updateFusion: builder.mutation<void, UpdateFusionMutationArg>({
      query: (payload) => {
        const { _files, ...body } = payload;
        if (hasFilePayload([...FILE_FIELDS], _files)) {
          return {
            url: `/fusions/${payload.id}`,
            method: "PUT",
            body: buildModelFormData(body, {
              fileFields: [...FILE_FIELDS],
              fileValues: _files,
            }),
          };
        }
        return {
          url: `/fusions/${payload.id}`,
          method: "PUT",
          body,
        };
      },
      invalidatesTags: ["Fusions"],
    }),
    deleteFusion: builder.mutation<void, number>({
      query: (id) => ({
        url: `/fusions/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Fusions"],
    }),
  }),
});

export const {
  useCreateFusionMutation,
  useGetFusionsQuery,
  useGetFusionQuery,
  useUpdateFusionMutation,
  useDeleteFusionMutation,
} = fusionApi;