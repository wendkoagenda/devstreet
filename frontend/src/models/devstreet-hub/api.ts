import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQuery } from "@/helpers/api/base-query";
import { toQueryString, type Paginated } from "@/helpers/api/pagination";
import type {
  AdoptSuggestion,
  Analysis,
  AnalysisRequest,
  Contribution,
  ContributionListParams,
  ContributionReview,
  ContributionTask,
  ContributionWrite,
  Discussion,
  DiscussionWrite,
  ForgeAccess,
  InitializeRepositoryPayload,
  InitializeRepositoryResult,
  Project,
  ProjectCreateResult,
  ProjectListParams,
  ProjectMember,
  ProjectMemberWrite,
  ProjectMembersParams,
  ProjectProfile,
  ProjectTasksParams,
  ProjectWritePayload,
  Repository,
  StarResult,
  TaskUpdate,
  TaskWrite,
  Technology,
  TechnologyListParams,
} from "./schema";

export const devstreetHubApi = createApi({
  reducerPath: "devstreetHubApi",
  baseQuery,
  tagTypes: [
    "Projects",
    "Technologies",
    "Project",
    "ProjectTasks",
    "ProjectMembers",
    "Task",
    "Contributions",
    "Analysis",
    "ProjectProfile",
  ],
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

    getProjectRepository: builder.query<Repository, number>({
      query: (projectId) => `/projects/${projectId}/repository`,
      providesTags: (_result, _error, projectId) => [
        { type: "Project", id: projectId },
      ],
    }),

    getTechnologies: builder.query<
      Paginated<Technology>,
      TechnologyListParams | void
    >({
      query: (params) => `/technologies${toQueryString(params)}`,
      providesTags: [{ type: "Technologies", id: "LIST" }],
    }),

    getProjectTasks: builder.query<
      Paginated<ContributionTask>,
      { projectId: number } & ProjectTasksParams
    >({
      query: ({ projectId, ...params }) =>
        `/projects/${projectId}/tasks${toQueryString(params)}`,
      providesTags: (_result, _error, { projectId }) => [
        { type: "ProjectTasks", id: projectId },
      ],
    }),

    getContributionTask: builder.query<ContributionTask, number>({
      query: (taskId) => `/contribution-tasks/${taskId}`,
      providesTags: (_result, _error, taskId) => [{ type: "Task", id: taskId }],
    }),

    updateContributionTask: builder.mutation<
      ContributionTask,
      { taskId: number; body: TaskUpdate }
    >({
      query: ({ taskId, body }) => ({
        url: `/contribution-tasks/${taskId}`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (result, _error, { taskId }) => [
        { type: "Task", id: taskId },
        ...(result
          ? [{ type: "ProjectTasks" as const, id: result.project_id }]
          : []),
      ],
    }),

    getContributions: builder.query<
      Paginated<Contribution>,
      ContributionListParams | void
    >({
      query: (params) => `/contributions${toQueryString(params)}`,
      providesTags: (result) =>
        result
          ? [
              ...result.results.map(({ id }) => ({
                type: "Contributions" as const,
                id,
              })),
              { type: "Contributions", id: "LIST" },
            ]
          : [{ type: "Contributions", id: "LIST" }],
    }),

    getContribution: builder.query<Contribution, number>({
      query: (contributionId) => `/contributions/${contributionId}`,
      providesTags: (_result, _error, contributionId) => [
        { type: "Contributions", id: contributionId },
      ],
    }),

    reviewContribution: builder.mutation<
      Contribution,
      { contributionId: number; body: ContributionReview }
    >({
      query: ({ contributionId, body }) => ({
        url: `/contributions/${contributionId}/review`,
        method: "POST",
        body,
      }),
      invalidatesTags: (_result, _error, { contributionId }) => [
        { type: "Contributions", id: contributionId },
        { type: "Contributions", id: "LIST" },
      ],
    }),

    submitContribution: builder.mutation<
      Contribution,
      { taskId: number; body: ContributionWrite }
    >({
      query: ({ taskId, body }) => ({
        url: `/contribution-tasks/${taskId}/contributions`,
        method: "POST",
        body,
      }),
      invalidatesTags: [{ type: "Contributions", id: "LIST" }],
    }),

    createProjectDiscussion: builder.mutation<
      Discussion,
      { projectId: number; body: DiscussionWrite }
    >({
      query: ({ projectId, body }) => ({
        url: `/projects/${projectId}/discussions`,
        method: "POST",
        body,
      }),
    }),

    getProjectMembers: builder.query<
      Paginated<ProjectMember>,
      { projectId: number } & ProjectMembersParams
    >({
      query: ({ projectId, ...params }) =>
        `/projects/${projectId}/members${toQueryString(params)}`,
      providesTags: (_result, _error, { projectId }) => [
        { type: "ProjectMembers", id: projectId },
      ],
    }),

    createProject: builder.mutation<ProjectCreateResult, ProjectWritePayload>({
      query: (body) => ({
        url: "/projects",
        method: "POST",
        body,
      }),
      invalidatesTags: [{ type: "Projects", id: "LIST" }],
    }),

    updateProject: builder.mutation<
      Project,
      { projectId: number; body: Partial<ProjectWritePayload> }
    >({
      query: ({ projectId, body }) => ({
        url: `/projects/${projectId}`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (_result, _error, { projectId }) => [
        { type: "Projects", id: projectId },
        { type: "Projects", id: "LIST" },
        { type: "Project", id: projectId },
      ],
    }),

    provisionForgeAccess: builder.mutation<ForgeAccess, void>({
      query: () => ({
        url: "/forge-access",
        method: "POST",
      }),
    }),

    provisionRepository: builder.mutation<Repository, number>({
      query: (projectId) => ({
        url: `/projects/${projectId}/provision`,
        method: "POST",
      }),
      invalidatesTags: (_result, _error, projectId) => [
        { type: "Projects", id: projectId },
        { type: "Projects", id: "LIST" },
        { type: "Project", id: projectId },
      ],
    }),

    resumeProjectSetup: builder.mutation<ProjectCreateResult, number>({
      query: (projectId) => ({
        url: `/projects/${projectId}/setup`,
        method: "POST",
      }),
      invalidatesTags: (_result, _error, projectId) => [
        { type: "Projects", id: projectId },
        { type: "Projects", id: "LIST" },
        { type: "Project", id: projectId },
      ],
    }),

    initializeRepository: builder.mutation<
      InitializeRepositoryResult,
      { projectId: number; body: InitializeRepositoryPayload }
    >({
      query: ({ projectId, body }) => ({
        url: `/projects/${projectId}/initialize`,
        method: "POST",
        body,
      }),
      invalidatesTags: (_result, _error, { projectId }) => [
        { type: "Projects", id: projectId },
        { type: "Project", id: projectId },
      ],
    }),

    publishProject: builder.mutation<Project, number>({
      query: (projectId) => ({
        url: `/projects/${projectId}/publish`,
        method: "POST",
      }),
      invalidatesTags: (_result, _error, projectId) => [
        { type: "Projects", id: projectId },
        { type: "Projects", id: "LIST" },
        { type: "Project", id: projectId },
      ],
    }),

    archiveProject: builder.mutation<Project, number>({
      query: (projectId) => ({
        url: `/projects/${projectId}/archive`,
        method: "POST",
      }),
      invalidatesTags: (_result, _error, projectId) => [
        { type: "Projects", id: projectId },
        { type: "Projects", id: "LIST" },
        { type: "Project", id: projectId },
      ],
    }),

    createProjectTask: builder.mutation<
      ContributionTask,
      { projectId: number; body: TaskWrite }
    >({
      query: ({ projectId, body }) => ({
        url: `/projects/${projectId}/tasks`,
        method: "POST",
        body,
      }),
      invalidatesTags: (_result, _error, { projectId }) => [
        { type: "ProjectTasks", id: projectId },
      ],
    }),

    addProjectMember: builder.mutation<
      ProjectMember,
      { projectId: number; body: ProjectMemberWrite }
    >({
      query: ({ projectId, body }) => ({
        url: `/projects/${projectId}/members`,
        method: "POST",
        body,
      }),
      invalidatesTags: (_result, _error, { projectId }) => [
        { type: "ProjectMembers", id: projectId },
      ],
    }),

    removeProjectMember: builder.mutation<
      void,
      { projectId: number; userId: number }
    >({
      query: ({ projectId, userId }) => ({
        url: `/projects/${projectId}/members/${userId}`,
        method: "DELETE",
      }),
      invalidatesTags: (_result, _error, { projectId }) => [
        { type: "ProjectMembers", id: projectId },
      ],
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

    setAiConsent: builder.mutation<
      Project,
      { projectId: number; enabled: boolean }
    >({
      query: ({ projectId, enabled }) => ({
        url: `/projects/${projectId}/ai-consent`,
        method: "POST",
        body: { enabled },
      }),
      invalidatesTags: (_result, _error, { projectId }) => [
        { type: "Project", id: projectId },
        { type: "Projects", id: projectId },
      ],
    }),

    createAnalysis: builder.mutation<
      Analysis,
      { projectId: number; body: AnalysisRequest }
    >({
      query: ({ projectId, body }) => ({
        url: `/projects/${projectId}/analyses`,
        method: "POST",
        body,
      }),
      invalidatesTags: (result) =>
        result ? [{ type: "Analysis", id: result.id }] : [],
    }),

    getAnalysis: builder.query<Analysis, number>({
      query: (analysisId) => `/analyses/${analysisId}`,
      providesTags: (_result, _error, analysisId) => [
        { type: "Analysis", id: analysisId },
      ],
    }),

    adoptAnalysisSuggestion: builder.mutation<
      ContributionTask,
      { projectId: number; body: AdoptSuggestion }
    >({
      query: ({ projectId, body }) => ({
        url: `/projects/${projectId}/tasks/from-analysis`,
        method: "POST",
        body,
      }),
      invalidatesTags: (_result, _error, { projectId }) => [
        { type: "ProjectTasks", id: projectId },
      ],
    }),

    getProjectProfile: builder.query<ProjectProfile, number>({
      query: (userId) => `/project-profiles/${userId}`,
      providesTags: (_result, _error, userId) => [
        { type: "ProjectProfile", id: userId },
      ],
    }),

    getProjectEvidence: builder.query<Contribution, number>({
      query: (contributionId) => `/project-evidence/${contributionId}`,
      providesTags: (_result, _error, contributionId) => [
        { type: "Contributions", id: contributionId },
      ],
    }),
  }),
});

export const {
  useGetProjectsQuery,
  useGetProjectQuery,
  useLazyGetProjectQuery,
  useGetProjectRepositoryQuery,
  useGetTechnologiesQuery,
  useGetProjectTasksQuery,
  useGetProjectMembersQuery,
  useGetContributionTaskQuery,
  useUpdateContributionTaskMutation,
  useGetContributionsQuery,
  useGetContributionQuery,
  useReviewContributionMutation,
  useSubmitContributionMutation,
  useCreateProjectDiscussionMutation,
  useCreateProjectMutation,
  useUpdateProjectMutation,
  useProvisionForgeAccessMutation,
  useProvisionRepositoryMutation,
  useResumeProjectSetupMutation,
  useInitializeRepositoryMutation,
  usePublishProjectMutation,
  useArchiveProjectMutation,
  useCreateProjectTaskMutation,
  useAddProjectMemberMutation,
  useRemoveProjectMemberMutation,
  useSetProjectStarMutation,
  useSetAiConsentMutation,
  useCreateAnalysisMutation,
  useGetAnalysisQuery,
  useLazyGetAnalysisQuery,
  useAdoptAnalysisSuggestionMutation,
  useGetProjectProfileQuery,
  useGetProjectEvidenceQuery,
  useLazyGetProjectEvidenceQuery,
} = devstreetHubApi;
