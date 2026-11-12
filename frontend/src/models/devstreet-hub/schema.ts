import { z } from "zod";

export const repositorySchema = z.object({
  id: z.number(),
  status: z.enum(["pending", "ready", "failed"]),
  namespace: z.string().nullable().optional(),
  name: z.string().nullable().optional(),
  default_branch: z.string().nullable().optional(),
  current_sha: z.string().nullable().optional(),
  clone_url: z.string().nullable().optional(),
  browse_url: z.string().nullable().optional(),
});

export const projectStatusSchema = z.enum(["draft", "published", "archived"]);

export const projectSchema = z.object({
  id: z.number(),
  owner_id: z.number(),
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

export type Repository = z.infer<typeof repositorySchema>;
export type ProjectStatus = z.infer<typeof projectStatusSchema>;
export type Project = z.infer<typeof projectSchema>;
export type Technology = z.infer<typeof technologySchema>;
export type StarResult = z.infer<typeof starResultSchema>;
export type StarResponse = StarResult;

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
