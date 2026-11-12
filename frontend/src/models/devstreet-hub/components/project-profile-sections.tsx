import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { FolderGit2, GitPullRequestArrow } from "lucide-react";
import { Button } from "@/components/ui/button";
import { pageCountOf } from "@/helpers/api/pagination";
import type { Contribution, Project, ProjectProfileSection } from "../schema";

interface ProjectProfileSectionsProps {
  userId: number;
  displayName: string | null;
  section: ProjectProfileSection;
  page: number;
  pageSize: number;
  limit: number;
  projects: Project[];
  contributions: Contribution[];
  projectsCount?: number;
  contributionsCount?: number;
  projectById: Map<number, Project>;
  onSectionChange: (section: ProjectProfileSection) => void;
  onPageChange: (page: number) => void;
}

function personLabel(
  t: (key: string, options?: Record<string, unknown>) => string,
  displayName: string | null,
  userId: number
): string {
  return displayName || t("hub.profile.user_fallback", { id: userId });
}

function ProjectCard({ project }: { project: Project }) {
  const { t } = useTranslation();
  return (
    <article className="rounded-xl border border-border bg-secondary/30 p-4">
      <div className="mb-2 flex flex-wrap items-start justify-between gap-2">
        <h3 className="text-sm font-bold text-foreground">{project.title}</h3>
        <span className="rounded-md bg-secondary px-2 py-0.5 text-[11px] font-medium text-muted-foreground">
          {t("hub.profile.role_owner")}
        </span>
      </div>
      <p className="mb-3 line-clamp-3 text-xs leading-relaxed text-muted-foreground">
        {project.problem}
      </p>
      <div className="flex flex-wrap items-center justify-between gap-2 text-[11px] text-muted-foreground">
        <span>
          {t("hub.profile.stars", { count: project.star_count })}
        </span>
        <Button asChild variant="ghost" className="h-7 px-2 text-xs">
          <Link to={`/hub/projects/${project.id}`}>
            {t("hub.profile.open_project")}
          </Link>
        </Button>
      </div>
    </article>
  );
}

function ContributionCard({
  contribution,
  project,
  authorLabel,
}: {
  contribution: Contribution;
  project: Project | undefined;
  authorLabel: string;
}) {
  const { t, i18n } = useTranslation();
  const unavailable = !project || project.status === "archived";
  const dateLabel = contribution.reviewed_at
    ? new Date(contribution.reviewed_at).toLocaleDateString(i18n.language)
    : null;

  if (unavailable) {
    return (
      <article className="rounded-xl border border-border bg-secondary/20 p-4">
        <p className="text-sm text-muted-foreground">
          {t("hub.profile.unavailable")}
        </p>
      </article>
    );
  }

  const statusLabel =
    contribution.status === "accepted"
      ? t("hub.profile.status.accepted")
      : contribution.status === "submitted"
        ? t("hub.profile.status.submitted")
        : t("hub.profile.status.rejected");

  const story =
    contribution.status === "accepted"
      ? t("hub.profile.story", {
          author: authorLabel,
          summary: contribution.summary,
          project: project.title,
          reviewer: contribution.reviewed_by_id
            ? t("hub.profile.user_fallback", {
                id: contribution.reviewed_by_id,
              })
            : t("hub.profile.reviewer_unknown"),
        })
      : t("hub.profile.story_pending", {
          author: authorLabel,
          summary: contribution.summary,
          project: project.title,
        });

  return (
    <article className="rounded-xl border border-border bg-secondary/30 p-4">
      <p className="mb-2 text-sm leading-relaxed text-foreground">{story}</p>
      <div className="mb-3 flex flex-wrap gap-2 text-[11px]">
        <span className="rounded-md bg-secondary px-2 py-0.5 font-medium text-foreground">
          {statusLabel}
        </span>
        {dateLabel ? (
          <span className="rounded-md bg-secondary px-2 py-0.5 text-muted-foreground">
            {dateLabel}
          </span>
        ) : null}
      </div>
      <div className="flex flex-wrap gap-2">
        <Button asChild variant="outline" className="h-7 rounded-lg px-2 text-xs">
          <Link to={`/hub/projects/${contribution.project_id}/tasks/${contribution.task_id}`}>
            {t("hub.profile.open_task")}
          </Link>
        </Button>
        <Button asChild variant="ghost" className="h-7 px-2 text-xs">
          <Link to={`/hub/projects/${contribution.project_id}/reviews`}>
            {t("hub.profile.open_contribution")}
          </Link>
        </Button>
      </div>
    </article>
  );
}

function PaginationBar({
  page,
  pageCount,
  onPageChange,
}: {
  page: number;
  pageCount: number;
  onPageChange: (page: number) => void;
}) {
  const { t } = useTranslation();
  if (pageCount <= 1) return null;
  return (
    <div className="flex items-center justify-between gap-2">
      <Button
        type="button"
        variant="outline"
        className="h-8 text-xs"
        disabled={page <= 1}
        onClick={() => onPageChange(page - 1)}
      >
        {t("hub.profile.prev")}
      </Button>
      <span className="text-xs text-muted-foreground">
        {t("hub.profile.page", { page, pageCount })}
      </span>
      <Button
        type="button"
        variant="outline"
        className="h-8 text-xs"
        disabled={page >= pageCount}
        onClick={() => onPageChange(page + 1)}
      >
        {t("hub.profile.next")}
      </Button>
    </div>
  );
}

export function ProjectProfileSections({
  userId,
  displayName,
  section,
  page,
  pageSize,
  limit,
  projects,
  contributions,
  projectsCount,
  contributionsCount,
  projectById,
  onSectionChange,
  onPageChange,
}: ProjectProfileSectionsProps) {
  const { t } = useTranslation();
  const authorLabel = personLabel(t, displayName, userId);
  const projectsPageCount = pageCountOf(projectsCount ?? 0, pageSize);
  const contributionsPageCount = pageCountOf(contributionsCount ?? 0, pageSize);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap gap-2">
        <Button
          type="button"
          variant={section === "overview" ? "default" : "outline"}
          className="h-8 rounded-lg text-xs"
          onClick={() => onSectionChange("overview")}
        >
          {t("hub.profile.tabs.overview")}
        </Button>
        <Button
          type="button"
          variant={section === "projects" ? "default" : "outline"}
          className="h-8 rounded-lg text-xs"
          onClick={() => onSectionChange("projects")}
        >
          {t("hub.profile.tabs.projects")}
        </Button>
        <Button
          type="button"
          variant={section === "contributions" ? "default" : "outline"}
          className="h-8 rounded-lg text-xs"
          onClick={() => onSectionChange("contributions")}
        >
          {t("hub.profile.tabs.contributions")}
        </Button>
      </div>

      {section === "overview" || section === "projects" ? (
        <section className="rounded-2xl border border-border bg-card p-5 shadow-card">
          <div className="mb-4 flex items-center gap-2">
            <FolderGit2 aria-hidden className="size-4 text-brand" />
            <h2 className="text-sm font-bold text-foreground">
              {t("hub.profile.projects_title")}
            </h2>
          </div>
          {section === "overview" ? (
            <p className="mb-4 text-xs text-muted-foreground">
              {t("hub.profile.preview_limit", { limit })}
            </p>
          ) : null}
          {projects.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              {t("hub.profile.projects_empty")}
            </p>
          ) : (
            <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
              {projects.map((project) => (
                <ProjectCard key={project.id} project={project} />
              ))}
            </div>
          )}
          {section === "overview" && projects.length >= limit ? (
            <div className="mt-4">
              <Button
                type="button"
                variant="outline"
                className="h-8 text-xs"
                onClick={() => onSectionChange("projects")}
              >
                {t("hub.profile.see_all_projects")}
              </Button>
            </div>
          ) : null}
          {section === "projects" ? (
            <div className="mt-4">
              <PaginationBar
                page={page}
                pageCount={projectsPageCount}
                onPageChange={onPageChange}
              />
            </div>
          ) : null}
        </section>
      ) : null}

      {section === "overview" || section === "contributions" ? (
        <section className="rounded-2xl border border-border bg-card p-5 shadow-card">
          <div className="mb-4 flex items-center gap-2">
            <GitPullRequestArrow aria-hidden className="size-4 text-brand" />
            <h2 className="text-sm font-bold text-foreground">
              {t("hub.profile.contributions_title")}
            </h2>
          </div>
          {section === "overview" ? (
            <p className="mb-4 text-xs text-muted-foreground">
              {t("hub.profile.accepted_only_hint")}
            </p>
          ) : (
            <p className="mb-4 text-xs text-muted-foreground">
              {t("hub.profile.list_visibility_hint")}
            </p>
          )}
          {contributions.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              {t("hub.profile.contributions_empty")}
            </p>
          ) : (
            <div className="flex flex-col gap-3">
              {contributions.map((contribution) => (
                <ContributionCard
                  key={contribution.id}
                  contribution={contribution}
                  project={projectById.get(contribution.project_id)}
                  authorLabel={authorLabel}
                />
              ))}
            </div>
          )}
          {section === "overview" && contributions.length >= limit ? (
            <div className="mt-4">
              <Button
                type="button"
                variant="outline"
                className="h-8 text-xs"
                onClick={() => onSectionChange("contributions")}
              >
                {t("hub.profile.see_all_contributions")}
              </Button>
            </div>
          ) : null}
          {section === "contributions" ? (
            <div className="mt-4">
              <PaginationBar
                page={page}
                pageCount={contributionsPageCount}
                onPageChange={onPageChange}
              />
            </div>
          ) : null}
        </section>
      ) : null}
    </div>
  );
}
