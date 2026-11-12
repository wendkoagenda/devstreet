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
  CreateGadoSchema,
  GetGadoSchema,
  UpdateGadoSchema,
} from "./schema";

const FILE_FIELDS = [{"name": "document", "uploadFolder": "fusion_documents"}] as const;

export type CreateGadoMutationArg = CreateGadoSchema & {
  _files?: Record<string, File | undefined>;
};

export type UpdateGadoMutationArg = UpdateGadoSchema & {
  _files?: Record<string, File | undefined>;
};

export const gadoApi = createApi({
  reducerPath: "gadoApi",
  baseQuery,
  tagTypes: ["Gados"],
  endpoints: (builder) => ({
    createGado: builder.mutation<void, CreateGadoMutationArg>({
      query: (payload) => {
        const { _files, ...body } = payload;
        if (hasFilePayload([...FILE_FIELDS], _files)) {
          return {
            url: "/gados",
            method: "POST",
            body: buildModelFormData(body, {
              fileFields: [...FILE_FIELDS],
              fileValues: _files,
            }),
          };
        }
        return {
          url: "/gados",
          method: "POST",
          body,
        };
      },
      invalidatesTags: ["Gados"],
    }),
    getGados: builder.query<Paginated<GetGadoSchema>, ListParams | void>({
      query: (params) => `/gados${toQueryString(params)}`,
      providesTags: ["Gados"],
    }),
    getGado: builder.query<GetGadoSchema, number>({
      query: (id) => `/gados/${id}`,
      providesTags: ["Gados"],
    }),
    updateGado: builder.mutation<void, UpdateGadoMutationArg>({
      query: (payload) => {
        const { _files, ...body } = payload;
        if (hasFilePayload([...FILE_FIELDS], _files)) {
          return {
            url: `/gados/${payload.id}`,
            method: "PUT",
            body: buildModelFormData(body, {
              fileFields: [...FILE_FIELDS],
              fileValues: _files,
            }),
          };
        }
        return {
          url: `/gados/${payload.id}`,
          method: "PUT",
          body,
        };
      },
      invalidatesTags: ["Gados"],
    }),
    deleteGado: builder.mutation<void, number>({
      query: (id) => ({
        url: `/gados/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Gados"],
    }),
  }),
});

export const {
  useCreateGadoMutation,
  useGetGadosQuery,
  useGetGadoQuery,
  useUpdateGadoMutation,
  useDeleteGadoMutation,
} = gadoApi;