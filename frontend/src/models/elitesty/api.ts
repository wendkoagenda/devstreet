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
  CreateElitestySchema,
  GetElitestySchema,
  UpdateElitestySchema,
} from "./schema";

const FILE_FIELDS = [{"name": "document", "uploadFolder": "elitest_documents"}] as const;

export type CreateElitestyMutationArg = CreateElitestySchema & {
  _files?: Record<string, File | undefined>;
};

export type UpdateElitestyMutationArg = UpdateElitestySchema & {
  _files?: Record<string, File | undefined>;
};

export const elitestyApi = createApi({
  reducerPath: "elitestyApi",
  baseQuery,
  tagTypes: ["Elitesties"],
  endpoints: (builder) => ({
    createElitesty: builder.mutation<void, CreateElitestyMutationArg>({
      query: (payload) => {
        const { _files, ...body } = payload;
        if (hasFilePayload([...FILE_FIELDS], _files)) {
          return {
            url: "/elitesties",
            method: "POST",
            body: buildModelFormData(body, {
              fileFields: [...FILE_FIELDS],
              fileValues: _files,
            }),
          };
        }
        return {
          url: "/elitesties",
          method: "POST",
          body,
        };
      },
      invalidatesTags: ["Elitesties"],
    }),
    getElitesties: builder.query<Paginated<GetElitestySchema>, ListParams | void>({
      query: (params) => `/elitesties${toQueryString(params)}`,
      providesTags: ["Elitesties"],
    }),
    getElitesty: builder.query<GetElitestySchema, number>({
      query: (id) => `/elitesties/${id}`,
      providesTags: ["Elitesties"],
    }),
    updateElitesty: builder.mutation<void, UpdateElitestyMutationArg>({
      query: (payload) => {
        const { _files, ...body } = payload;
        if (hasFilePayload([...FILE_FIELDS], _files)) {
          return {
            url: `/elitesties/${payload.id}`,
            method: "PUT",
            body: buildModelFormData(body, {
              fileFields: [...FILE_FIELDS],
              fileValues: _files,
            }),
          };
        }
        return {
          url: `/elitesties/${payload.id}`,
          method: "PUT",
          body,
        };
      },
      invalidatesTags: ["Elitesties"],
    }),
    deleteElitesty: builder.mutation<void, number>({
      query: (id) => ({
        url: `/elitesties/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Elitesties"],
    }),
  }),
});

export const {
  useCreateElitestyMutation,
  useGetElitestiesQuery,
  useGetElitestyQuery,
  useUpdateElitestyMutation,
  useDeleteElitestyMutation,
} = elitestyApi;