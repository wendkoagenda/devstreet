import { ArrowRight, Hourglass } from "lucide-react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { cn } from "@/lib/utils";
import type { Project, Technology } from "../schema";
import type { ProjectStarView } from "../hooks/use-project-star";
import { ProjectStatusBadge } from "./project-status-badge";
import { StarButton } from "./star-button";
import { TechnologyTag } from "./technology-tag";

interface ProjectCardProps {
  project: Project;
  technologiesById: Map<number, Technology>;
  href: string;
  star: ProjectStarView;
  onToggleStar: () => void;
}

export function ProjectCard({
  project,
  technologiesById,
  href,
  star,
  onToggleStar,
}: ProjectCardProps) {
  const { t } = useTranslation();
  const isDraft = project.status === "draft";
  const techLabels = project.technologies
    .map((id) => technologiesById.get(id))
    .filter((item): item is Technology => Boolean(item));

  const footerHint = isDraft
    ? project.repository?.status === "ready"
      ? t("hub.card.draft_ready")
      : t("hub.card.draft_git")
    : t("hub.card.discover_hint");

  return (
    <article
      className={cn(
        "group relative flex h-full flex-col justify-between rounded-xl border border-border bg-card p-5 shadow-card transition-all",
        "hover:border-input hover:shadow-card-hover"
      )}
    >
      <Link
        to={href}
        className="absolute inset-0 z-0 rounded-xl focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        aria-label={t("hub.card.open", { title: project.title })}
      />

      <div className="relative z-10 pointer-events-none">
        <div className="mb-2.5 flex items-start justify-between gap-3">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-base font-bold tracking-tight text-foreground transition-colors group-hover:text-brand">
              {project.title}
            </h2>
            <ProjectStatusBadge status={project.status} />
            {project.declared_license ? (
              <span className="rounded bg-brand-soft px-1.5 py-0.5 text-[10px] font-semibold text-brand-strong">
                {project.declared_license}
              </span>
            ) : null}
          </div>
          <div className="pointer-events-auto">
            <StarButton
              projectTitle={project.title}
              view={star}
              onToggle={onToggleStar}
            />
          </div>
        </div>

        <p className="mb-4 line-clamp-3 text-xs leading-relaxed text-muted-foreground sm:text-[13px]">
          {project.problem}
        </p>
      </div>

      <div className="relative z-10 pointer-events-none">
        {techLabels.length > 0 ? (
          <div className="mb-3.5 flex flex-wrap items-center gap-1.5">
            {techLabels.map((tech) => (
              <TechnologyTag key={tech.id} id={tech.id} label={tech.label} />
            ))}
          </div>
        ) : null}

        <div className="flex items-center justify-between gap-2 border-t border-border pt-3">
          <div
            className={cn(
              "flex min-w-0 items-center gap-1.5 text-[11px]",
              isDraft ? "text-warning" : "text-muted-foreground"
            )}
          >
            {isDraft ? (
              <Hourglass className="size-3.5 shrink-0" aria-hidden />
            ) : null}
            <span className="truncate">{footerHint}</span>
          </div>
          <span className="inline-flex shrink-0 items-center gap-1 text-xs font-semibold text-foreground transition-all group-hover:translate-x-0.5 group-hover:text-brand">
            {isDraft ? t("hub.card.open_draft") : t("hub.card.discover")}
            <ArrowRight className="size-3.5 text-brand" aria-hidden />
          </span>
        </div>
      </div>
    </article>
  );
}
