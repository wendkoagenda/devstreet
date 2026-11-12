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
  CreateDragonSchema,
  GetDragonSchema,
  UpdateDragonSchema,
} from "./schema";

const FILE_FIELDS = [{"name": "document", "uploadFolder": "dragon_documents"}] as const;

export type CreateDragonMutationArg = CreateDragonSchema & {
  _files?: Record<string, File | undefined>;
};

export type UpdateDragonMutationArg = UpdateDragonSchema & {
  _files?: Record<string, File | undefined>;
};

export const dragonApi = createApi({
  reducerPath: "dragonApi",
  baseQuery,
  tagTypes: ["Dragons"],
  endpoints: (builder) => ({
    createDragon: builder.mutation<void, CreateDragonMutationArg>({
      query: (payload) => {
        const { _files, ...body } = payload;
        if (hasFilePayload([...FILE_FIELDS], _files)) {
          return {
            url: "/dragons",
            method: "POST",
            body: buildModelFormData(body, {
              fileFields: [...FILE_FIELDS],
              fileValues: _files,
            }),
          };
        }
        return {
          url: "/dragons",
          method: "POST",
          body,
        };
      },
      invalidatesTags: ["Dragons"],
    }),
    getDragons: builder.query<Paginated<GetDragonSchema>, ListParams | void>({
      query: (params) => `/dragons${toQueryString(params)}`,
      providesTags: ["Dragons"],
    }),
    getDragon: builder.query<GetDragonSchema, number>({
      query: (id) => `/dragons/${id}`,
      providesTags: ["Dragons"],
    }),
    updateDragon: builder.mutation<void, UpdateDragonMutationArg>({
      query: (payload) => {
        const { _files, ...body } = payload;
        if (hasFilePayload([...FILE_FIELDS], _files)) {
          return {
            url: `/dragons/${payload.id}`,
            method: "PUT",
            body: buildModelFormData(body, {
              fileFields: [...FILE_FIELDS],
              fileValues: _files,
            }),
          };
        }
        return {
          url: `/dragons/${payload.id}`,
          method: "PUT",
          body,
        };
      },
      invalidatesTags: ["Dragons"],
    }),
    deleteDragon: builder.mutation<void, number>({
      query: (id) => ({
        url: `/dragons/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Dragons"],
    }),
  }),
});

export const {
  useCreateDragonMutation,
  useGetDragonsQuery,
  useGetDragonQuery,
  useUpdateDragonMutation,
  useDeleteDragonMutation,
} = dragonApi;