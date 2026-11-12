import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQuery } from "@/helpers/api/base-query";
import {
  toQueryString,
  type ListParams,
  type Paginated,
} from "@/helpers/api/pagination";
import type {
  CreateSkillSchema,
  GetSkillSchema,
  UpdateSkillSchema,
} from "./schema";

export type CreateSkillMutationArg = CreateSkillSchema;
export type UpdateSkillMutationArg = UpdateSkillSchema;

export const skillApi = createApi({
  reducerPath: "skillApi",
  baseQuery,
  tagTypes: ["Skills"],
  endpoints: (builder) => ({
    createSkill: builder.mutation<void, CreateSkillMutationArg>({
      query: (payload) => {
        return {
          url: "/skills",
          method: "POST",
          body: payload,
        };
      },
      invalidatesTags: ["Skills"],
    }),
    getSkills: builder.query<Paginated<GetSkillSchema>, ListParams | void>({
      query: (params) => `/skills${toQueryString(params)}`,
      providesTags: ["Skills"],
    }),
    getSkill: builder.query<GetSkillSchema, number>({
      query: (id) => `/skills/${id}`,
      providesTags: ["Skills"],
    }),
    updateSkill: builder.mutation<void, UpdateSkillMutationArg>({
      query: (payload) => {
        return {
          url: `/skills/${payload.id}`,
          method: "PUT",
          body: payload,
        };
      },
      invalidatesTags: ["Skills"],
    }),
    deleteSkill: builder.mutation<void, number>({
      query: (id) => ({
        url: `/skills/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Skills"],
    }),
  }),
});

export const {
  useCreateSkillMutation,
  useGetSkillsQuery,
  useGetSkillQuery,
  useUpdateSkillMutation,
  useDeleteSkillMutation,
} = skillApi;