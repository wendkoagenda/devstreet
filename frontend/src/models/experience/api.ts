import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQuery } from "@/helpers/api/base-query";
import {
  toQueryString,
  type ListParams,
  type Paginated,
} from "@/helpers/api/pagination";
import type {
  CreateExperienceSchema,
  GetExperienceSchema,
  UpdateExperienceSchema,
} from "./schema";

export type CreateExperienceMutationArg = CreateExperienceSchema;
export type UpdateExperienceMutationArg = UpdateExperienceSchema;

export const experienceApi = createApi({
  reducerPath: "experienceApi",
  baseQuery,
  tagTypes: ["Experiences"],
  endpoints: (builder) => ({
    createExperience: builder.mutation<void, CreateExperienceMutationArg>({
      query: (payload) => {
        return {
          url: "/experiences",
          method: "POST",
          body: payload,
        };
      },
      invalidatesTags: ["Experiences"],
    }),
    getExperiences: builder.query<Paginated<GetExperienceSchema>, ListParams | void>({
      query: (params) => `/experiences${toQueryString(params)}`,
      providesTags: ["Experiences"],
    }),
    getExperience: builder.query<GetExperienceSchema, number>({
      query: (id) => `/experiences/${id}`,
      providesTags: ["Experiences"],
    }),
    updateExperience: builder.mutation<void, UpdateExperienceMutationArg>({
      query: (payload) => {
        return {
          url: `/experiences/${payload.id}`,
          method: "PUT",
          body: payload,
        };
      },
      invalidatesTags: ["Experiences"],
    }),
    deleteExperience: builder.mutation<void, number>({
      query: (id) => ({
        url: `/experiences/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Experiences"],
    }),
  }),
});

export const {
  useCreateExperienceMutation,
  useGetExperiencesQuery,
  useGetExperienceQuery,
  useUpdateExperienceMutation,
  useDeleteExperienceMutation,
} = experienceApi;