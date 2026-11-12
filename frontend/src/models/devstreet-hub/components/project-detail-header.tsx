import { Code2, ExternalLink, MoreHorizontal, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { Project, Technology } from "../schema";
import type { ProjectStarView } from "../hooks/use-project-star";
import { ProjectStatusBadge } from "./project-status-badge";
import { StarButton } from "./star-button";
import { TechnologyTag } from "./technology-tag";

interface ProjectDetailHeaderProps {
  project: Project;
  technologies: Technology[];
  star: ProjectStarView;
  isOwner: boolean;
  canPublish: boolean;
  canArchive: boolean;
  canCreateTask: boolean;
  canAnalyze: boolean;
  canReview: boolean;
  canOpenCode: boolean;
  isBusy: boolean;
  onToggleStar: () => void;
  onPublish: () => void;
  onArchive: () => void;
  onCreateTask: () => void;
  onOpenCode: () => void;
}

export function ProjectDetailHeader({
  project,
  technologies,
  star,
  isOwner,
  canPublish,
  canArchive,
  canCreateTask,
  canAnalyze,
  canReview,
  canOpenCode,
  isBusy,
  onToggleStar,
  onPublish,
  onArchive,
  onCreateTask,
  onOpenCode,
}: ProjectDetailHeaderProps) {
  const { t } = useTranslation();
  const demoUrl = project.demo_url?.trim() || null;

  return (
    <header className="flex flex-col gap-5 border-b border-border pb-6">
      <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-start">
        <div className="min-w-0 flex-1">
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
              {project.title}
            </h1>
            <ProjectStatusBadge status={project.status} />
            <span className="rounded bg-brand-soft px-2 py-1 text-[10px] font-semibold leading-none text-brand-strong">
              {project.declared_license}
            </span>
          </div>
          <p className="max-w-3xl text-sm leading-relaxed text-muted-foreground">
            {project.problem || t("hub.detail.no_problem")}
          </p>
          {technologies.length > 0 ? (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {technologies.map((tech) => (
                <TechnologyTag key={tech.id} id={tech.id} label={tech.label} />
              ))}
            </div>
          ) : null}
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <StarButton
            projectTitle={project.title}
            view={star}
            onToggle={onToggleStar}
          />
          {demoUrl ? (
            <Button asChild variant="outline" className="h-9 gap-1.5 rounded-lg text-xs font-semibold">
              <a href={demoUrl} target="_blank" rel="noopener noreferrer">
                <ExternalLink aria-hidden className="size-3.5" />
                {t("hub.detail.actions.demo")}
              </a>
            </Button>
          ) : null}
          {canOpenCode ? (
            <Button
              type="button"
              variant="outline"
              className="h-9 gap-1.5 rounded-lg text-xs font-semibold"
              onClick={onOpenCode}
            >
              <Code2 aria-hidden className="size-3.5" />
              {t("hub.detail.actions.open_code")}
            </Button>
          ) : null}
          {canAnalyze ? (
            <Button asChild className="h-9 gap-1.5 rounded-lg text-xs font-semibold">
              <Link to={`/hub/projects/${project.id}/ai`}>
                <Sparkles aria-hidden className="size-3.5 text-brand-foreground" />
                {t("hub.detail.actions.ai")}
              </Link>
            </Button>
          ) : null}
          {canReview ? (
            <Button
              asChild
              variant="secondary"
              className="h-9 rounded-lg text-xs font-semibold"
            >
              <Link to={`/hub/projects/${project.id}/reviews`}>
                {t("hub.detail.actions.reviews")}
              </Link>
            </Button>
          ) : null}
          {isOwner && project.status === "draft" ? (
            <Button
              asChild
              variant="default"
              className="h-9 rounded-lg text-xs font-semibold"
            >
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
              className="h-9 rounded-lg text-xs font-semibold"
            >
              {t("hub.detail.actions.create_task")}
            </Button>
          ) : null}
          {isOwner ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-9 w-9 rounded-lg"
                  aria-label={t("hub.detail.actions.manage")}
                >
                  <MoreHorizontal aria-hidden className="size-4" />
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
        </div>
      </div>
    </header>
  );
}
