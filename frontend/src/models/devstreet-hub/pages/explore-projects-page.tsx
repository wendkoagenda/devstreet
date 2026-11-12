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
    <div className="flex flex-col items-end">
      <span className="text-[11px] text-muted-foreground">{label}</span>
      <span className="text-sm font-semibold tabular-nums text-foreground">
        {value ?? "—"}
      </span>
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
          <header className="mb-6 flex flex-col justify-between gap-4 border-b border-border pb-5 md:mb-7 md:flex-row md:items-end">
            <div className="max-w-2xl">
              <h1 className="mb-1.5 text-xl font-semibold tracking-tight text-foreground sm:text-2xl">
                <span className="md:hidden">{t("hub.explorer.mobile_title")}</span>
                <span className="hidden md:inline">{t("hub.explorer.title")}</span>
              </h1>
              <p className="text-sm leading-relaxed text-muted-foreground">
                {t("hub.explorer.description")}
              </p>
            </div>
            <div className="hidden shrink-0 items-center gap-4 md:flex">
              <Metric label={t("hub.explorer.metric_projects")} value={projectCount} />
              <div aria-hidden className="h-7 w-px bg-border" />
              <Metric
                label={t("hub.explorer.metric_technologies")}
                value={technologyCount}
              />
            </div>
          </header>
        )}
      />
    </div>
  );
}
