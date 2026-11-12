import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { cn } from "@/lib/utils";
import { useHubAccess } from "../hooks/use-hub-access";
import { useProjectExplorer } from "../hooks/use-project-explorer";
import { useProjectStar } from "../hooks/use-project-star";
import { httpStatusOf } from "../functions/api-error";
import type { Project } from "../schema";
import { ActiveFilters, type ActiveFilter } from "./active-filters";
import { ExplorerPagination } from "./explorer-pagination";
import { ExplorerEmptyState, ExplorerErrorState, ProjectGridSkeleton } from "./explorer-states";
import { ExplorerToolbar, type CreateAction } from "./explorer-toolbar";
import { ProjectCard } from "./project-card";

interface ProjectExplorerProps {
  /** En-tête de page ; reçoit les indicateurs calculés à partir des données réelles. */
  renderIntro: (metrics: { projectCount: number | null; technologyCount: number | null }) => ReactNode;
  getProjectHref: (project: Project) => string;
  onCreateProject: () => void;
}

/**
 * Écran 01 autonome : recherche, filtre technologie, cartes, étoiles et pagination serveur.
 * Les données et l'état des filtres (dans l'URL) sont gérés ici ; la page ne fournit que la navigation.
 */
export function ProjectExplorer({ renderIntro, getProjectHref, onCreateProject }: ProjectExplorerProps) {
  const { t } = useTranslation();
  const explorer = useProjectExplorer();
  const { isAuthenticated, isInitialized, userId, canCreateProject, requestLogin } = useHubAccess();
  const star = useProjectStar();

  const createAction: CreateAction = !isInitialized
    ? "hidden"
    : !isAuthenticated
      ? "login"
      : canCreateProject
        ? "allowed"
        : "hidden";
  const handleCreate = createAction === "login" ? requestLogin : onCreateProject;

  const { filters } = explorer;
  const activeFilters: ActiveFilter[] = [];
  if (filters.search) {
    activeFilters.push({
      key: "search",
      label: t("hub.explorer.filter_search", { search: filters.search }),
      onRemove: explorer.clearSearch,
    });
  }
  if (explorer.selectedTechnology) {
    activeFilters.push({
      key: "technology",
      label: explorer.selectedTechnology.label,
      onRemove: explorer.clearTechnology,
    });
  }
  if (filters.owner !== null) {
    activeFilters.push({
      key: "owner",
      label:
        filters.owner === userId
          ? t("hub.explorer.filter_mine")
          : t("hub.explorer.filter_owner", { id: filters.owner }),
      onRemove: explorer.clearOwner,
    });
  }

  const hasData = !explorer.isLoading && !explorer.error;
  const isRefreshing = explorer.isFetching && !explorer.isLoading;

  return (
    <>
      {renderIntro({
        projectCount: hasData && !explorer.hasActiveFilters ? explorer.count : null,
        technologyCount: explorer.catalogError ? null : explorer.technologies.length || null,
      })}

      <ExplorerToolbar
        searchInput={explorer.searchInput}
        onSearchChange={explorer.setSearchInput}
        onSearchClear={explorer.clearSearch}
        technology={filters.technology}
        technologies={explorer.technologies}
        isCatalogLoading={explorer.isCatalogLoading}
        hasCatalogError={Boolean(explorer.catalogError)}
        onRetryCatalog={explorer.retryCatalog}
        onTechnologyChange={explorer.setTechnology}
        createAction={createAction}
        onCreate={handleCreate}
      />

      <ActiveFilters
        filters={activeFilters}
        count={explorer.count}
        isCountKnown={hasData}
        onClearAll={explorer.clearAll}
      />

      {explorer.isLoading ? (
        <ProjectGridSkeleton />
      ) : explorer.error ? (
        <ExplorerErrorState
          status={httpStatusOf(explorer.error)}
          isRetrying={explorer.isFetching}
          onRetry={explorer.retry}
        />
      ) : explorer.projects.length === 0 ? (
        <ExplorerEmptyState
          hasActiveFilters={explorer.hasActiveFilters}
          createAction={createAction}
          onClearFilters={explorer.clearAll}
          onCreate={handleCreate}
        />
      ) : (
        <>
          <ul
            aria-busy={isRefreshing}
            aria-label={t("hub.explorer.list_label")}
            className={cn(
              "mb-6 grid grid-cols-1 gap-4 transition-opacity md:grid-cols-2",
              isRefreshing && "opacity-60"
            )}
          >
            {explorer.projects.map((project) => (
              <li key={project.id} className="flex">
                <div className="w-full [&>article]:h-full">
                  <ProjectCard
                    project={project}
                    technologiesById={explorer.technologiesById}
                    href={getProjectHref(project)}
                    star={star.viewOf(project)}
                    onToggleStar={() => void star.toggle(project)}
                  />
                </div>
              </li>
            ))}
          </ul>
          <ExplorerPagination
            page={filters.page}
            pageCount={explorer.pageCount}
            count={explorer.count}
            pageSize={explorer.pageSize}
            isBusy={explorer.isFetching}
            onPageChange={(page) => {
              explorer.setPage(page);
              window.scrollTo({ top: 0, behavior: "smooth" });
            }}
          />
        </>
      )}
    </>
  );
}
