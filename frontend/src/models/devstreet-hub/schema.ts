import { z } from "zod";

export const repositorySchema = z.object({
  id: z.number(),
  status: z.enum(["pending", "ready", "failed"]),
  namespace: z.string().nullable().optional(),
  name: z.string().nullable().optional(),
  default_branch: z.string().nullable().optional(),
  current_sha: z.string().nullable().optional(),
  is_empty: z.boolean().optional(),
  clone_url: z.string().nullable().optional(),
  browse_url: z.string().nullable().optional(),
});

export const projectStatusSchema = z.enum(["draft", "published", "archived"]);

export const projectSchema = z.object({
  id: z.number(),
  owner_id: z.number(),
  owner_display_name: z.string().optional(),
  images: z.array(z.object({ id: z.number(), url: z.string(), display_name: z.string() })).optional(),
  title: z.string(),
  slug: z.string(),
  problem: z.string(),
  description: z.string(),
  demo_url: z.string().nullable().optional(),
  declared_license: z.string(),
  status: projectStatusSchema,
  technologies: z.array(z.number()),
  star_count: z.number(),
  repository: repositorySchema.nullable().optional(),
  ai_consent_at: z.string().nullable().optional(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const technologySchema = z.object({
  id: z.number(),
  label: z.string(),
  slug: z.string(),
  created_by: z.number().nullable().optional(),
  updated_by: z.number().nullable().optional(),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
});

export const starResultSchema = z.object({
  starred: z.boolean(),
  star_count: z.number(),
});

/** Licences permissives acceptées par le MVP backend. */
export const PROJECT_LICENSES = [
  "MIT",
  "Apache-2.0",
  "BSD-2-Clause",
  "BSD-3-Clause",
] as const;

export const projectLicenseSchema = z.enum(PROJECT_LICENSES);

export const projectWriteSchema = z.object({
  title: z.string().trim().min(1).max(180),
  slug: z
    .string()
    .trim()
    .max(100)
    .regex(/^$|^[a-z0-9]+(?:-[a-z0-9]+)*$/)
    .optional()
    .default(""),
  problem: z.string().trim().max(2000).optional().default(""),
  description: z.string().max(10000).default(""),
  demo_url: z.string().url().nullable().optional().or(z.literal("")),
  declared_license: projectLicenseSchema,
  technologies: z.array(z.number().int().positive()).default([]),
});

export const forgeAccessSchema = z.object({
  login: z.string(),
  created: z.boolean().optional().default(false),
  initial_password: z.string().optional(),
  change_password_required: z.boolean().optional(),
  recovered: z.boolean().optional(),
  password_recovery_required: z.boolean().optional(),
  reset: z.boolean().optional(),
});

export const gitDeviceAuthRequestSchema = z.object({
  id: z.string(),
  computer_name: z.string(),
  hub_base_url: z.string().optional(),
  status: z.enum([
    "pending",
    "authorized",
    "denied",
    "expired",
    "consumed",
  ]),
  expires_at: z.string(),
  created_at: z.string(),
  decided_at: z.string().nullable().optional(),
  scopes: z.array(z.string()),
  scope_labels: z.array(z.string()),
  gitea_host: z.string(),
  client_id: z.string().optional(),
});

export const gitOAuthClientConfigSchema = z.object({
  client_id: z.string(),
  gitea_origin: z.string(),
  authorize_endpoint: z.string(),
  token_endpoint: z.string(),
  redirect_uri: z.string(),
  oauth_default_username: z.string(),
  scopes: z.string(),
  git_config_commands: z.array(z.string()),
});

export type GitOAuthClientConfig = z.infer<typeof gitOAuthClientConfigSchema>;
export type GitOAuthRequest = z.infer<typeof gitDeviceAuthRequestSchema>;

export const gitConnectedComputerSchema = z.object({
  id: z.number(),
  name: z.string(),
  forge_login: z.string(),
  token_last_eight: z.string(),
  status: z.enum(["active", "revoked"]),
  created_at: z.string(),
  revoked_at: z.string().nullable().optional(),
  last_used_at: z.string().nullable().optional(),
});

export const projectSetupSchema = z.object({
  draft: z.literal("ok"),
  identity: z.enum(["pending", "ok", "failed", "conflict"]),
  repository: z.enum(["pending", "ok", "failed"]),
});

export const projectCreateResultSchema = projectSchema.extend({
  forge_access: forgeAccessSchema.optional().nullable(),
  setup: projectSetupSchema.optional(),
});

export const initializeRepositorySchema = z.object({
  mode: z.enum(["readme", "push_existing"]),
});

export const initializeRepositoryResultSchema = z.object({
  mode: z.enum(["readme", "push_existing"]),
  initialized: z.boolean(),
  is_empty: z.boolean(),
  repository: repositorySchema,
});

export type Repository = z.infer<typeof repositorySchema>;
export type ProjectStatus = z.infer<typeof projectStatusSchema>;
export type Project = z.infer<typeof projectSchema>;
export type Technology = z.infer<typeof technologySchema>;
export type StarResult = z.infer<typeof starResultSchema>;
export type StarResponse = StarResult;
export type ProjectLicense = z.infer<typeof projectLicenseSchema>;
export type ProjectWrite = z.infer<typeof projectWriteSchema>;
export type ForgeAccess = z.infer<typeof forgeAccessSchema>;
export type GitDeviceAuthRequest = z.infer<typeof gitDeviceAuthRequestSchema>;
export type GitConnectedComputer = z.infer<typeof gitConnectedComputerSchema>;
export type ProjectSetup = z.infer<typeof projectSetupSchema>;
export type ProjectCreateResult = z.infer<typeof projectCreateResultSchema>;
export type InitializeRepositoryPayload = z.infer<typeof initializeRepositorySchema>;
export type InitializeRepositoryResult = z.infer<
  typeof initializeRepositoryResultSchema
>;

export type ProjectListParams = {
  page?: number;
  page_size?: number;
  search?: string;
  technology?: string;
  owner?: number;
};

export type TechnologyListParams = {
  page?: number;
  page_size?: number;
  search?: string;
  ordering?: string;
};

/** Payload API : slug/problem optionnels ; `demo_url` vide devient null. */
export type ProjectWritePayload = {
  title: string;
  slug?: string;
  problem?: string;
  description?: string;
  demo_url?: string | null;
  declared_license: ProjectLicense;
  technologies: number[];
};

export const taskStatusSchema = z.enum(["draft", "open", "closed"]);

export const contributionTaskSchema = z.object({
  id: z.number(),
  project_id: z.number(),
  analysis_id: z.number().nullable().optional(),
  title: z.string(),
  description: z.string(),
  acceptance_criteria: z.array(z.string()).default([]),
  status: taskStatusSchema,
  created_by: z.number(),
  created_at: z.string(),
  updated_at: z.string(),
  source_references: z
    .array(
      z.object({
        source_id: z.string().optional(),
        path: z.string(),
        commit_sha: z.string().optional(),
        url: z.string().nullable().optional(),
      })
    )
    .optional()
    .default([]),
});

export const taskWriteSchema = z.object({
  title: z.string().trim().min(1).max(180),
  description: z.string().max(5000).default(""),
  acceptance_criteria: z.array(z.string().max(500)).max(10).optional(),
});

export const projectMemberSchema = z.object({
  id: z.number(),
  user_id: z.number(),
  role: z.enum(["maintainer", "contributor"]),
  display_name: z.string().optional(),
  username: z.string().optional(),
});

export const projectMemberWriteSchema = z
  .object({
    user_id: z.number().int().positive().optional(),
    identifier: z.string().trim().min(1).optional(),
    role: z.enum(["maintainer", "contributor"]),
  })
  .refine((value) => value.user_id != null || Boolean(value.identifier), {
    message: "user_id_or_identifier_required",
  });

export type TaskStatus = z.infer<typeof taskStatusSchema>;
export type ContributionTask = z.infer<typeof contributionTaskSchema>;
export type TaskWrite = z.infer<typeof taskWriteSchema>;
export type ProjectMember = z.infer<typeof projectMemberSchema>;
export type ProjectMemberWrite = z.infer<typeof projectMemberWriteSchema>;

export type ProjectDetailTab =
  | "presentation"
  | "code"
  | "contribute"
  | "team";

export type CodeViewMode = "tree" | "blob";

export const codeCommitSchema = z.object({
  sha: z.string(),
  short_sha: z.string(),
  message: z.string(),
  author_name: z.string().nullable().optional(),
  authored_at: z.string().nullable().optional(),
});

export const codeLanguageSchema = z.object({
  name: z.string(),
  bytes: z.number(),
  percent: z.number(),
});

export const codeSummarySchema = z.object({
  default_branch: z.string(),
  is_empty: z.boolean(),
  clone_url: z.string().nullable().optional(),
  description: z.string().nullable().optional(),
  size_kib: z.number().nullable().optional(),
  stats: z.object({
    commits: z.number().nullable().optional(),
    branches: z.number().nullable().optional(),
    tags: z.number().nullable().optional(),
  }),
  languages: z.array(codeLanguageSchema).default([]),
  repository: repositorySchema.optional(),
});

export const codeBranchSchema = z.object({
  name: z.string(),
  commit: codeCommitSchema.nullable().optional(),
});

export const codeTreeEntrySchema = z.object({
  name: z.string(),
  path: z.string(),
  type: z.enum(["file", "dir"]),
  size: z.number().nullable().optional(),
  sha: z.string().nullable().optional(),
});

export const codeReadmeSchema = z.object({
  name: z.string(),
  path: z.string(),
  content: z.string(),
  truncated: z.boolean(),
});

export const codeTreeSchema = z.object({
  ref: z.string(),
  path: z.string(),
  is_empty: z.boolean(),
  entries: z.array(codeTreeEntrySchema),
  latest_commit: codeCommitSchema.nullable().optional(),
  readme: codeReadmeSchema.nullable().optional(),
});

export const codeBlobSchema = z.object({
  ref: z.string(),
  path: z.string(),
  name: z.string(),
  size: z.number(),
  sha: z.string().nullable().optional(),
  encoding: z.enum(["utf-8", "none", "base64"]),
  content: z.string().nullable().optional(),
  is_binary: z.boolean(),
  is_too_large: z.boolean(),
  language: z.string().nullable().optional(),
  latest_commit: codeCommitSchema.nullable().optional(),
});

export type CodeCommit = z.infer<typeof codeCommitSchema>;
export type CodeLanguage = z.infer<typeof codeLanguageSchema>;
export type CodeSummary = z.infer<typeof codeSummarySchema>;
export type CodeBranch = z.infer<typeof codeBranchSchema>;
export type CodeTreeEntry = z.infer<typeof codeTreeEntrySchema>;
export type CodeReadme = z.infer<typeof codeReadmeSchema>;
export type CodeTree = z.infer<typeof codeTreeSchema>;
export type CodeBlob = z.infer<typeof codeBlobSchema>;

export type ProjectTasksParams = {
  page?: number;
  page_size?: number;
  status?: TaskStatus;
  search?: string;
};

export type ProjectTasksPage = {
  count: number;
  next: string | null;
  previous: string | null;
  results: ContributionTask[];
  status_counts?: {
    open: number;
    closed: number;
    draft: number;
  };
};

export type ProjectMembersParams = {
  page?: number;
  page_size?: number;
};

export const contributionStatusSchema = z.enum([
  "submitted",
  "accepted",
  "rejected",
]);

export const contributionSchema = z.object({
  id: z.number(),
  task_id: z.number(),
  project_id: z.number(),
  author_id: z.number(),
  summary: z.string(),
  pull_request_number: z.number().nullable().optional(),
  artifact_sha: z.string().nullable().optional(),
  status: contributionStatusSchema,
  reviewed_by_id: z.number().nullable().optional(),
  review_note: z.string().nullable().optional(),
  reviewed_at: z.string().nullable().optional(),
  created_at: z.string(),
  validation_kind: z.string().nullable().optional(),
});

export const contributionWriteSchema = z.object({
  summary: z.string().trim().min(1).max(3000),
  pull_request_number: z.number().int().positive().nullable().optional(),
  artifact_sha: z.string().nullable().optional(),
});

export const taskUpdateSchema = z.object({
  title: z.string().trim().min(1).max(180).optional(),
  description: z.string().max(5000).optional(),
  acceptance_criteria: z.array(z.string().max(500)).max(10).optional(),
  status: taskStatusSchema.optional(),
});

export const discussionWriteSchema = z.object({
  request_key: z.string().uuid(),
  task_id: z.number().int().positive().optional(),
  title: z.string().trim().min(1).max(180),
  body: z.string().trim().min(1).max(5000),
});

export const discussionSchema = z.object({
  id: z.number(),
  project_id: z.number(),
  task_id: z.number().nullable().optional(),
  forum_topic_id: z.string(),
  request_key: z.string(),
  title: z.string(),
  body: z.string(),
  created_at: z.string(),
});

export type ContributionStatus = z.infer<typeof contributionStatusSchema>;
export type Contribution = z.infer<typeof contributionSchema>;
export type ContributionWrite = z.infer<typeof contributionWriteSchema>;
export type TaskUpdate = z.infer<typeof taskUpdateSchema>;
export type DiscussionWrite = z.infer<typeof discussionWriteSchema>;
export type Discussion = z.infer<typeof discussionSchema>;

export type ContributionListParams = {
  page?: number;
  page_size?: number;
  task_id?: number;
  project_id?: number;
  author_id?: number;
};

export const contributionReviewSchema = z.object({
  status: z.enum(["accepted", "rejected"]),
  note: z.string().trim().min(1).max(3000),
});

export type ContributionReview = z.infer<typeof contributionReviewSchema>;

export const analysisStatusSchema = z.enum([
  "queued",
  "running",
  "succeeded",
  "failed",
]);

export const analysisCitationSchema = z.object({
  source_id: z.string(),
  line_start: z.number().optional(),
  line_end: z.number().optional(),
  reason: z.string().optional(),
});

export const analysisSuggestedTaskSchema = z.object({
  title: z.string(),
  description: z.string(),
  source_ids: z.array(z.string()).default([]),
  steps: z.array(z.string()).default([]),
  acceptance_criteria: z.array(z.string()).default([]),
});

export const analysisResultSchema = z.object({
  summary: z.string().optional(),
  entry_points: z.array(analysisCitationSchema).optional().default([]),
  suggested_tasks: z.array(analysisSuggestedTaskSchema).optional().default([]),
  unknowns: z.array(z.string()).optional().default([]),
});

export const analysisSchema = z.object({
  id: z.number(),
  project_id: z.number(),
  commit_sha: z.string(),
  objective: z.string(),
  language: z.enum(["fr", "en"]),
  status: analysisStatusSchema,
  model: z.string(),
  prompt_version: z.string().optional(),
  result: z.object({
    description: z.string().min(1).max(10000),
    references: z.array(analysisCitationSchema),
    unknowns: z.array(z.string()),
  }).or(analysisResultSchema).or(z.record(z.string(), z.unknown())).optional(),
  error_code: z.string().optional(),
  input_tokens: z.number().optional(),
  output_tokens: z.number().optional(),
  sources: z
    .array(z.object({ source_id: z.string(), path: z.string() }))
    .optional()
    .default([]),
  created_at: z.string(),
  finished_at: z.string().nullable().optional(),
});

export const analysisRequestSchema = z.object({
  objective: z.string().trim().min(1).max(2000),
  language: z.enum(["fr", "en"]).default("fr"),
});

export const adoptSuggestionSchema = z.object({
  analysis_id: z.number().int().positive(),
  suggestion_index: z.number().int().min(0).max(2),
});

export type AnalysisStatus = z.infer<typeof analysisStatusSchema>;
export type Analysis = z.infer<typeof analysisSchema>;
export type AnalysisResult = z.infer<typeof analysisResultSchema>;
export type AnalysisRequest = z.infer<typeof analysisRequestSchema>;
export type AdoptSuggestion = z.infer<typeof adoptSuggestionSchema>;
export type AnalysisSuggestedTask = z.infer<typeof analysisSuggestedTaskSchema>;

export const projectProfileSchema = z.object({
  user_id: z.number(),
  projects: z.array(projectSchema).default([]),
  contributions: z.array(contributionSchema).default([]),
  limit: z.number().default(20),
});

export type ProjectProfile = z.infer<typeof projectProfileSchema>;

export type ProjectProfileSection = "overview" | "projects" | "contributions";
