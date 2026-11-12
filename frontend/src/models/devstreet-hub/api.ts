import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQuery } from "@/helpers/api/base-query";
import { toQueryString, type Paginated } from "@/helpers/api/pagination";
import type {
  Project,
  ProjectListParams,
  StarResult,
  Technology,
  TechnologyListParams,
} from "./schema";

export const devstreetHubApi = createApi({
  reducerPath: "devstreetHubApi",
  baseQuery,
  tagTypes: ["Projects", "Technologies", "Project"],
  endpoints: (builder) => ({
    getProjects: builder.query<Paginated<Project>, ProjectListParams | void>({
      query: (params) => `/projects${toQueryString(params)}`,
      providesTags: (result) =>
        result
          ? [
              ...result.results.map(({ id }) => ({
                type: "Projects" as const,
                id,
              })),
              { type: "Projects", id: "LIST" },
            ]
          : [{ type: "Projects", id: "LIST" }],
    }),

    getProject: builder.query<Project, number>({
      query: (id) => `/projects/${id}`,
      providesTags: (_result, _error, id) => [{ type: "Project", id }],
    }),

    getTechnologies: builder.query<
      Paginated<Technology>,
      TechnologyListParams | void
    >({
      query: (params) => `/technologies${toQueryString(params)}`,
      providesTags: [{ type: "Technologies", id: "LIST" }],
    }),

    setProjectStar: builder.mutation<
      StarResult,
      { projectId: number; starred: boolean }
    >({
      query: ({ projectId, starred }) => ({
        url: `/projects/${projectId}/star`,
        method: starred ? "PUT" : "DELETE",
      }),
      invalidatesTags: (_result, _error, { projectId }) => [
        { type: "Projects", id: projectId },
        { type: "Projects", id: "LIST" },
        { type: "Project", id: projectId },
      ],
    }),
  }),
});

export const {
  useGetProjectsQuery,
  useGetProjectQuery,
  useGetTechnologiesQuery,
  useSetProjectStarMutation,
} = devstreetHubApi;
