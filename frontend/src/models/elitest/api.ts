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
  CreateElitestSchema,
  GetElitestSchema,
  UpdateElitestSchema,
} from "./schema";

const FILE_FIELDS = [{"name": "document", "uploadFolder": "elitest_documents"}] as const;

export type CreateElitestMutationArg = CreateElitestSchema & {
  _files?: Record<string, File | undefined>;
};

export type UpdateElitestMutationArg = UpdateElitestSchema & {
  _files?: Record<string, File | undefined>;
};

export const elitestApi = createApi({
  reducerPath: "elitestApi",
  baseQuery,
  tagTypes: ["Elitests"],
  endpoints: (builder) => ({
    createElitest: builder.mutation<void, CreateElitestMutationArg>({
      query: (payload) => {
        const { _files, ...body } = payload;
        if (hasFilePayload([...FILE_FIELDS], _files)) {
          return {
            url: "/elitests",
            method: "POST",
            body: buildModelFormData(body, {
              fileFields: [...FILE_FIELDS],
              fileValues: _files,
            }),
          };
        }
        return {
          url: "/elitests",
          method: "POST",
          body,
        };
      },
      invalidatesTags: ["Elitests"],
    }),
    getElitests: builder.query<Paginated<GetElitestSchema>, ListParams | void>({
      query: (params) => `/elitests${toQueryString(params)}`,
      providesTags: ["Elitests"],
    }),
    getElitest: builder.query<GetElitestSchema, number>({
      query: (id) => `/elitests/${id}`,
      providesTags: ["Elitests"],
    }),
    updateElitest: builder.mutation<void, UpdateElitestMutationArg>({
      query: (payload) => {
        const { _files, ...body } = payload;
        if (hasFilePayload([...FILE_FIELDS], _files)) {
          return {
            url: `/elitests/${payload.id}`,
            method: "PUT",
            body: buildModelFormData(body, {
              fileFields: [...FILE_FIELDS],
              fileValues: _files,
            }),
          };
        }
        return {
          url: `/elitests/${payload.id}`,
          method: "PUT",
          body,
        };
      },
      invalidatesTags: ["Elitests"],
    }),
    deleteElitest: builder.mutation<void, number>({
      query: (id) => ({
        url: `/elitests/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Elitests"],
    }),
  }),
});

export const {
  useCreateElitestMutation,
  useGetElitestsQuery,
  useGetElitestQuery,
  useUpdateElitestMutation,
  useDeleteElitestMutation,
} = elitestApi;