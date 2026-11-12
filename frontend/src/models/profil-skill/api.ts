import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQuery } from "@/helpers/api/base-query";
import {
  toQueryString,
  type ListParams,
  type Paginated,
} from "@/helpers/api/pagination";
import type {
  CreateProfilSkillSchema,
  GetProfilSkillSchema,
  UpdateProfilSkillSchema,
} from "./schema";

export type CreateProfilSkillMutationArg = CreateProfilSkillSchema;
export type UpdateProfilSkillMutationArg = UpdateProfilSkillSchema;

export const profilSkillApi = createApi({
  reducerPath: "profilSkillApi",
  baseQuery,
  tagTypes: ["ProfilSkills"],
  endpoints: (builder) => ({
    createProfilSkill: builder.mutation<void, CreateProfilSkillMutationArg>({
      query: (payload) => {
        return {
          url: "/profil-skills",
          method: "POST",
          body: payload,
        };
      },
      invalidatesTags: ["ProfilSkills"],
    }),
    getProfilSkills: builder.query<Paginated<GetProfilSkillSchema>, ListParams | void>({
      query: (params) => `/profil-skills${toQueryString(params)}`,
      providesTags: ["ProfilSkills"],
    }),
    getProfilSkill: builder.query<GetProfilSkillSchema, number>({
      query: (id) => `/profil-skills/${id}`,
      providesTags: ["ProfilSkills"],
    }),
    updateProfilSkill: builder.mutation<void, UpdateProfilSkillMutationArg>({
      query: (payload) => {
        return {
          url: `/profil-skills/${payload.id}`,
          method: "PUT",
          body: payload,
        };
      },
      invalidatesTags: ["ProfilSkills"],
    }),
    deleteProfilSkill: builder.mutation<void, number>({
      query: (id) => ({
        url: `/profil-skills/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["ProfilSkills"],
    }),
  }),
});

export const {
  useCreateProfilSkillMutation,
  useGetProfilSkillsQuery,
  useGetProfilSkillQuery,
  useUpdateProfilSkillMutation,
  useDeleteProfilSkillMutation,
} = profilSkillApi;