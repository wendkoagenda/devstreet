import { CircleDot, Lock, Plus, Search } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { pageCountOf } from "@/helpers/api/pagination";
import type { ProjectTasksPage, TaskStatus } from "../schema";

type TaskFilter = "open" | "closed" | "draft";

interface ContributeTasksPanelProps {
  projectId: number;
  tasks: ProjectTasksPage | undefined;
  loading: boolean;
  page: number;
  status: TaskFilter;
  search: string;
  canCreateTask: boolean;
  canSeeDrafts: boolean;
  onPageChange: (page: number) => void;
  onStatusChange: (status: TaskFilter) => void;
  onSearchChange: (search: string) => void;
  onOpenCreateTask: () => void;
}

function formatRelative(iso: string, justNow: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  const diff = Date.now() - date.getTime();
  const minutes = Math.round(diff / 60000);
  if (minutes < 1) return justNow;
  if (minutes < 60) return `${minutes} min`;
  const hours = Math.round(minutes / 60);
  if (hours < 48) return `${hours} h`;
  const days = Math.round(hours / 24);
  return `${days} j`;
}

function StatusIcon({ status }: { status: TaskStatus }) {
  if (status === "closed") {
    return <Lock aria-hidden className="size-4 text-muted-foreground" />;
  }
  if (status === "draft") {
    return (
      <CircleDot aria-hidden className="size-4 text-warning" />
    );
  }
  return <CircleDot aria-hidden className="size-4 text-success" />;
}

/**
 * Liste des tâches de contribution — présentation forge (recherche, onglets
 * Ouvertes/Fermées, lignes denses), métier DevStreet (pas les Issues Gitea).
 */
export function ContributeTasksPanel({
  projectId,
  tasks,
  loading,
  page,
  status,
  search,
  canCreateTask,
  canSeeDrafts,
  onPageChange,
  onStatusChange,
  onSearchChange,
  onOpenCreateTask,
}: ContributeTasksPanelProps) {
  const { t } = useTranslation();
  const [draftSearch, setDraftSearch] = useState(search);

  useEffect(() => {
    setDraftSearch(search);
  }, [search]);

  useEffect(() => {
    const handle = window.setTimeout(() => {
      if (draftSearch !== search) onSearchChange(draftSearch);
    }, 300);
    return () => window.clearTimeout(handle);
  }, [draftSearch, onSearchChange, search]);

  const counts = tasks?.status_counts;
  const openCount = counts?.open ?? 0;
  const closedCount = counts?.closed ?? 0;
  const draftCount = counts?.draft ?? 0;
  const pageCount = pageCountOf(tasks?.count ?? 0);
  const results = tasks?.results ?? [];

  const tabs: { id: TaskFilter; label: string; count: number; show: boolean }[] = [
    {
      id: "open",
      label: t("hub.detail.contribute.filter_open", { count: openCount }),
      count: openCount,
      show: true,
    },
    {
      id: "closed",
      label: t("hub.detail.contribute.filter_closed", { count: closedCount }),
      count: closedCount,
      show: true,
    },
    {
      id: "draft",
      label: t("hub.detail.contribute.filter_draft", { count: draftCount }),
      count: draftCount,
      show: canSeeDrafts,
    },
  ];

  return (
    <section className="flex flex-col gap-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative min-w-0 flex-1">
          <Search
            aria-hidden
            className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
          />
          <Input
            value={draftSearch}
            onChange={(event) => setDraftSearch(event.target.value)}
            placeholder={t("hub.detail.contribute.search_placeholder")}
            aria-label={t("hub.detail.contribute.search_placeholder")}
            className="h-10 rounded-lg border-border bg-card pl-9 text-sm"
          />
        </div>
        {canCreateTask ? (
          <Button
            type="button"
            onClick={onOpenCreateTask}
            className="h-10 shrink-0 gap-1.5 rounded-lg text-xs font-semibold"
          >
            <Plus aria-hidden className="size-4" />
            {t("hub.detail.contribute.new_task")}
          </Button>
        ) : null}
      </div>

      <div className="flex flex-wrap items-center gap-1 border-b border-border">
        {tabs
          .filter((tab) => tab.show)
          .map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => onStatusChange(tab.id)}
              className={cn(
                "relative px-3 py-2 text-xs font-semibold transition-colors",
                status === tab.id
                  ? "text-foreground"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              {tab.label}
              {status === tab.id ? (
                <span className="absolute inset-x-2 bottom-0 h-0.5 rounded-full bg-brand" />
              ) : null}
            </button>
          ))}
      </div>

      <div className="overflow-hidden rounded-xl border border-border bg-card shadow-card">
        {loading ? (
          <p className="px-4 py-10 text-center text-sm text-muted-foreground">
            {t("common.loading")}
          </p>
        ) : results.length === 0 ? (
          <div className="flex flex-col items-center gap-2 px-4 py-14 text-center">
            <CircleDot aria-hidden className="size-8 text-muted-foreground/50" />
            <p className="text-sm font-semibold text-foreground">
              {t("hub.detail.contribute.empty_title")}
            </p>
            <p className="max-w-sm text-xs text-muted-foreground">
              {search
                ? t("hub.detail.contribute.empty_search")
                : t("hub.detail.contribute.empty")}
            </p>
            {canCreateTask && !search && status === "open" ? (
              <Button
                type="button"
                variant="outline"
                className="mt-2 h-8 gap-1.5 text-xs"
                onClick={onOpenCreateTask}
              >
                <Plus aria-hidden className="size-3.5" />
                {t("hub.detail.contribute.new_task")}
              </Button>
            ) : null}
          </div>
        ) : (
          <ul className="divide-y divide-border">
            {results.map((task) => (
              <li key={task.id}>
                <Link
                  to={`/hub/projects/${projectId}/tasks/${task.id}`}
                  className="flex items-start gap-3 px-4 py-3.5 transition-colors hover:bg-secondary/60"
                >
                  <span className="mt-0.5 shrink-0">
                    <StatusIcon status={task.status} />
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
                      <span className="text-sm font-semibold text-foreground">
                        {task.title}
                      </span>
                      <span className="text-xs text-muted-foreground">#{task.id}</span>
                    </div>
                    <p className="mt-0.5 line-clamp-1 text-xs text-muted-foreground">
                      {task.description ||
                        t("hub.detail.contribute.no_description")}
                    </p>
                    <p className="mt-1.5 text-[11px] text-muted-foreground">
                      {t("hub.detail.contribute.row_meta", {
                        status: t(`hub.detail.task_status.${task.status}`),
                        when: formatRelative(
                          task.updated_at || task.created_at,
                          t("hub.detail.code.just_now")
                        ),
                      })}
                    </p>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>

      {pageCount > 1 ? (
        <div className="flex items-center justify-between gap-2 text-xs">
          <Button
            type="button"
            variant="outline"
            disabled={page <= 1}
            onClick={() => onPageChange(page - 1)}
            className="h-8 rounded-lg"
          >
            {t("pagination.previous")}
          </Button>
          <span className="text-muted-foreground">
            {t("hub.detail.page_of", { page, pageCount })}
          </span>
          <Button
            type="button"
            variant="outline"
            disabled={page >= pageCount}
            onClick={() => onPageChange(page + 1)}
            className="h-8 rounded-lg"
          >
            {t("pagination.next")}
          </Button>
        </div>
      ) : null}
    </section>
  );
}
