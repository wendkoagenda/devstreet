import { ExternalLink, MoreHorizontal, Sparkles, FolderGit2, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import type { Project, Technology } from "../schema";
import type { ProjectStarView } from "../hooks/use-project-star";
import { ProjectStatusBadge } from "./project-status-badge";
import { StarButton } from "./star-button";

const headerActionClass =
  "h-7 gap-1.5 rounded-md px-2.5 text-xs font-medium shadow-none";

interface ProjectDetailHeaderProps {
  project: Project;
  technologies?: Technology[];
  star: ProjectStarView;
  isOwner: boolean;
  canPublish: boolean;
  canArchive: boolean;
  canCreateTask: boolean;
  canAnalyze: boolean;
  canReview: boolean;
  isBusy: boolean;
  onToggleStar: () => void;
  onPublish: () => void;
  onArchive: () => void;
  onCreateTask: () => void;
}

export function ProjectDetailHeader({
  project,
  technologies = [],
  star,
  isOwner,
  canPublish,
  canArchive,
  canCreateTask,
  canAnalyze,
  canReview,
  isBusy,
  onToggleStar,
  onPublish,
  onArchive,
  onCreateTask,
}: ProjectDetailHeaderProps) {
  const { t } = useTranslation();
  const demoUrl = project.demo_url?.trim() || null;

  const managementActions = <>
          {canAnalyze ? (
            <Button asChild variant="outline" className={cn(headerActionClass)}>
              <Link to={`/hub/projects/${project.id}/ai`}>
                <Sparkles aria-hidden className="size-3.5" />
                {t("hub.detail.actions.ai")}
              </Link>
            </Button>
          ) : null}
          {canReview ? (
            <Button asChild variant="outline" className={cn(headerActionClass)}>
              <Link to={`/hub/projects/${project.id}/reviews`}>
                {t("hub.detail.actions.reviews")}
              </Link>
            </Button>
          ) : null}
          {isOwner && project.status === "draft" ? (
            <Button asChild variant="outline" className={cn(headerActionClass)}>
              <Link to={`/hub/projects/new?draft=${project.id}`}>
                {t("hub.detail.actions.continue_setup")}
              </Link>
            </Button>
          ) : null}
          {canCreateTask ? (
            <Button
              type="button"
              variant="outline"
              disabled={isBusy}
              onClick={onCreateTask}
              className={cn(headerActionClass)}
            >
              {t("hub.detail.actions.create_task")}
            </Button>
          ) : null}
          {isOwner ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  className="h-7 w-7 rounded-md shadow-none"
                  aria-label={t("hub.detail.actions.manage")}
                >
                  <MoreHorizontal aria-hidden className="size-3.5" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="min-w-[12rem]">
                {canPublish && project.status === "draft" ? (
                  <DropdownMenuItem
                    disabled={isBusy || project.repository?.status !== "ready"}
                    onClick={onPublish}
                  >
                    {t("hub.detail.actions.publish")}
                  </DropdownMenuItem>
                ) : null}
                {canArchive && project.status !== "archived" ? (
                  <DropdownMenuItem
                    disabled={isBusy}
                    onClick={onArchive}
                    className="text-destructive focus:text-destructive"
                  >
                    {t("hub.detail.actions.archive")}
                  </DropdownMenuItem>
                ) : null}
              </DropdownMenuContent>
            </DropdownMenu>
          ) : null}
  </>;

  return (
    <header className="flex flex-col gap-4 border-b border-border pb-5">
      <div className="flex flex-col justify-between gap-3 lg:flex-row lg:items-center">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="flex size-10 items-center justify-center rounded-xl border border-brand-soft-border bg-brand-soft text-brand"><FolderGit2 aria-hidden className="size-5" /></span>
            <h1 className="text-xl font-semibold tracking-tight text-foreground sm:text-2xl">
              {project.title}
            </h1>
            <ProjectStatusBadge status={project.status} />
            <span className="rounded-md border border-border bg-secondary px-1.5 py-0.5 text-[10px] font-medium leading-none text-muted-foreground">
              {project.declared_license}
            </span>
          </div>
          {project.problem.trim() ? <p className="mt-3 max-w-2xl whitespace-pre-line text-sm leading-6 text-muted-foreground line-clamp-2">{project.problem}</p> : null}
          {technologies.length ? <div className="mt-3 flex flex-wrap gap-1.5">{technologies.map(tech => <span key={tech.id} className="rounded-md border border-border bg-muted px-2 py-1 text-[11px] text-muted-foreground">{tech.label}</span>)}</div> : null}
        </div>

        <div className="flex flex-wrap items-center gap-1.5">
          <StarButton
            projectTitle={project.title}
            view={star}
            onToggle={onToggleStar}
            showLabel
          />
          {demoUrl ? (
            <Button
              asChild
              variant="outline"
              className={cn(headerActionClass)}
            >
              <a href={demoUrl} target="_blank" rel="noopener noreferrer">
                <ExternalLink aria-hidden className="size-3.5" />
                {t("hub.detail.actions.demo")}
              </a>
            </Button>
          ) : null}
        </div>
      </div>
      {isOwner || canAnalyze || canReview || canCreateTask ? <div className="flex flex-col gap-3 rounded-xl border border-border bg-muted/50 p-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="flex items-center gap-2 text-xs font-medium text-muted-foreground"><ShieldCheck aria-hidden className="size-4 text-brand" />{t("hub.presentation.management")}</p>
        <div className="flex flex-wrap items-center gap-2">{managementActions}</div>
      </div> : null}
    </header>
  );
}
