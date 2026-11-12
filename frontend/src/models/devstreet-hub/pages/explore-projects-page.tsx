import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { ProjectExplorer } from "../components/project-explorer";
import type { Project } from "../schema";

interface MetricProps {
  label: string;
  value: number | null;
}

function Metric({ label, value }: MetricProps) {
  return (
    <div className="flex flex-col">
      <span className="mb-0.5 font-mono text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
        {label}
      </span>
      <span className="font-mono text-lg font-bold text-foreground">{value ?? "—"}</span>
    </div>
  );
}

export default function ExploreProjectsPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const handleCreateProject = () => navigate("/hub/projects/new");
  const getProjectHref = (project: Project) => `/hub/projects/${project.id}`;

  return (
    <div className="mx-auto w-full max-w-7xl">
      <ProjectExplorer
        getProjectHref={getProjectHref}
        onCreateProject={handleCreateProject}
        renderIntro={({ projectCount, technologyCount }) => (
          <header className="mb-6 flex flex-col justify-between gap-5 md:mb-8 md:flex-row md:items-end">
            <div className="max-w-2xl">
              <span className="mb-3 hidden items-center gap-1.5 rounded-md border border-brand-soft-border bg-brand-soft px-2 py-1 font-mono text-[11px] font-medium text-brand-strong md:inline-flex">
                <span aria-hidden className="h-1.5 w-1.5 rounded-full bg-brand" />
                {t("hub.explorer.eyebrow")}
              </span>
              <h1 className="mb-2 text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
                <span className="md:hidden">{t("hub.explorer.mobile_title")}</span>
                <span className="hidden md:inline">{t("hub.explorer.title")}</span>
              </h1>
              <p className="text-sm leading-relaxed text-muted-foreground">
                {t("hub.explorer.description")}
              </p>
            </div>
            <div className="hidden shrink-0 items-center gap-4 rounded-xl border border-border bg-card p-3 shadow-sm md:flex">
              <Metric label={t("hub.explorer.metric_projects")} value={projectCount} />
              <div aria-hidden className="h-8 w-px bg-border" />
              <Metric label={t("hub.explorer.metric_technologies")} value={technologyCount} />
            </div>
          </header>
        )}
      />
    </div>
  );
}
