import { useCallback, useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import {
  useAddProjectMemberMutation,
  useArchiveProjectMutation,
  useCreateProjectTaskMutation,
  useGetProjectMembersQuery,
  useGetProjectQuery,
  useGetProjectRepositoryQuery,
  useGetProjectTasksQuery,
  useGetTechnologiesQuery,
  usePublishProjectMutation,
  useRemoveProjectMemberMutation,
} from "../api";
import { apiDetailOf, httpStatusOf } from "../functions/api-error";
import type {
  ProjectDetailTab,
  ProjectMemberWrite,
  TaskStatus,
  TaskWrite,
  Technology,
} from "../schema";
import { useHubAccess } from "./use-hub-access";
import { useProjectStar } from "./use-project-star";
import { PAGE_SIZE } from "@/helpers/api/pagination";

const TABS: ProjectDetailTab[] = [
  "presentation",
  "code",
  "contribute",
  "team",
];

type TaskFilter = Extract<TaskStatus, "open" | "closed" | "draft">;

function parseTab(value: string | null): ProjectDetailTab {
  if (value && TABS.includes(value as ProjectDetailTab)) {
    return value as ProjectDetailTab;
  }
  return "presentation";
}

function parseTaskStatus(value: string | null): TaskFilter {
  if (value === "closed" || value === "draft" || value === "open") return value;
  return "open";
}

/**
 * Fiche projet (écran 03) : charge le projet, les listes paginées et expose les mutations
 * documentées dans docs/devstreet_hub/interfaces/03-fiche-projet.md.
 */
export function useProjectDetail(projectId: number) {
  const { t } = useTranslation();
  const [searchParams, setSearchParams] = useSearchParams();
  const access = useHubAccess();

  const tab = parseTab(searchParams.get("tab"));
  const tasksPage = Math.max(1, Number(searchParams.get("tasks_page") || "1"));
  const tasksStatus = parseTaskStatus(searchParams.get("tasks_status"));
  const tasksSearch = (searchParams.get("tasks_q") || "").trim();
  const membersPage = Math.max(
    1,
    Number(searchParams.get("members_page") || "1")
  );

  const projectQuery = useGetProjectQuery(projectId, {
    skip: !Number.isFinite(projectId) || projectId <= 0,
  });
  const project = projectQuery.data;

  const repositoryQuery = useGetProjectRepositoryQuery(projectId, {
    skip: !project || project.repository?.status !== "ready",
  });

  const tasksQuery = useGetProjectTasksQuery(
    {
      projectId,
      page: tasksPage,
      page_size: PAGE_SIZE,
      status: tasksStatus,
      search: tasksSearch || undefined,
    },
    { skip: !project || tab !== "contribute" }
  );

  const membersQuery = useGetProjectMembersQuery(
    { projectId, page: membersPage, page_size: PAGE_SIZE },
    { skip: !project || tab !== "team" }
  );

  const { data: techPage } = useGetTechnologiesQuery({
    page_size: 100,
    ordering: "label",
  });
  const technologiesById = useMemo(() => {
    const map = new Map<number, Technology>();
    for (const tech of techPage?.results ?? []) map.set(tech.id, tech);
    return map;
  }, [techPage?.results]);

  const { viewOf, toggle: toggleStarAction } = useProjectStar();
  const [publishProject, publishState] = usePublishProjectMutation();
  const [archiveProject, archiveState] = useArchiveProjectMutation();
  const [createTask, createTaskState] = useCreateProjectTaskMutation();
  const [addMember, addMemberState] = useAddProjectMemberMutation();
  const [removeMember, removeMemberState] = useRemoveProjectMemberMutation();

  const isOwner = Boolean(
    project && access.userId != null && project.owner_id === access.userId
  );
  const star = project ? viewOf(project) : null;

  const mapError = useCallback(
    (error: unknown, fallbackKey: string) => {
      const status = httpStatusOf(error);
      const detail = apiDetailOf(error);
      if (detail) return detail;
      if (status === 401) return t("hub.detail.errors.login_required");
      if (status === 403) return t("hub.detail.errors.forbidden");
      if (status === 404) return t("hub.detail.errors.not_found");
      if (status === 409) return t("hub.detail.errors.conflict");
      if (status === 429) return t("hub.common.rate_limited");
      if (status === null) return t("hub.detail.errors.network");
      return t(fallbackKey);
    },
    [t]
  );

  const setTab = useCallback(
    (next: ProjectDetailTab) => {
      const params = new URLSearchParams(searchParams);
      params.set("tab", next);
      if (next !== "contribute") {
        params.delete("tasks_page");
        params.delete("tasks_status");
        params.delete("tasks_q");
      }
      if (next !== "team") params.delete("members_page");
      setSearchParams(params, { replace: true });
    },
    [searchParams, setSearchParams]
  );

  const setTasksPage = useCallback(
    (page: number) => {
      const params = new URLSearchParams(searchParams);
      params.set("tab", "contribute");
      params.set("tasks_page", String(page));
      setSearchParams(params, { replace: true });
    },
    [searchParams, setSearchParams]
  );

  const setTasksStatus = useCallback(
    (status: TaskFilter) => {
      const params = new URLSearchParams(searchParams);
      params.set("tab", "contribute");
      params.set("tasks_status", status);
      params.set("tasks_page", "1");
      setSearchParams(params, { replace: true });
    },
    [searchParams, setSearchParams]
  );

  const setTasksSearch = useCallback(
    (value: string) => {
      const params = new URLSearchParams(searchParams);
      params.set("tab", "contribute");
      const trimmed = value.trim();
      if (trimmed) params.set("tasks_q", trimmed);
      else params.delete("tasks_q");
      params.set("tasks_page", "1");
      setSearchParams(params, { replace: true });
    },
    [searchParams, setSearchParams]
  );

  const setMembersPage = useCallback(
    (page: number) => {
      const params = new URLSearchParams(searchParams);
      params.set("tab", "team");
      params.set("members_page", String(page));
      setSearchParams(params, { replace: true });
    },
    [searchParams, setSearchParams]
  );

  const toggleStar = useCallback(async () => {
    if (!project) return;
    await toggleStarAction(project);
  }, [project, toggleStarAction]);

  const publish = useCallback(async () => {
    if (!project) return;
    try {
      await publishProject(project.id).unwrap();
      toast.success(t("hub.detail.toasts.published"));
    } catch (error) {
      toast.error(mapError(error, "hub.detail.errors.publish"));
    }
  }, [mapError, project, publishProject, t]);

  const archive = useCallback(async () => {
    if (!project) return;
    try {
      await archiveProject(project.id).unwrap();
      toast.success(t("hub.detail.toasts.archived"));
    } catch (error) {
      toast.error(mapError(error, "hub.detail.errors.archive"));
    }
  }, [archiveProject, mapError, project, t]);

  const createManualTask = useCallback(
    async (body: TaskWrite) => {
      if (!project) return false;
      try {
        await createTask({ projectId: project.id, body }).unwrap();
        toast.success(t("hub.detail.toasts.task_created"));
        setTab("contribute");
        return true;
      } catch (error) {
        toast.error(mapError(error, "hub.detail.errors.task_create"));
        return false;
      }
    },
    [createTask, mapError, project, setTab, t]
  );

  const inviteMember = useCallback(
    async (body: ProjectMemberWrite) => {
      if (!project) return false;
      try {
        await addMember({ projectId: project.id, body }).unwrap();
        toast.success(t("hub.detail.toasts.member_added"));
        return true;
      } catch (error) {
        toast.error(mapError(error, "hub.detail.errors.member_add"));
        return false;
      }
    },
    [addMember, mapError, project, t]
  );

  const updateMemberRole = useCallback(
    async (body: ProjectMemberWrite) => {
      if (!project) return false;
      try {
        await addMember({ projectId: project.id, body }).unwrap();
        toast.success(t("hub.detail.toasts.member_updated"));
        return true;
      } catch (error) {
        toast.error(mapError(error, "hub.detail.errors.member_update"));
        return false;
      }
    },
    [addMember, mapError, project, t]
  );

  const ejectMember = useCallback(
    async (userId: number) => {
      if (!project) return;
      try {
        await removeMember({ projectId: project.id, userId }).unwrap();
        toast.success(t("hub.detail.toasts.member_removed"));
      } catch (error) {
        toast.error(mapError(error, "hub.detail.errors.member_remove"));
      }
    },
    [mapError, project, removeMember, t]
  );

  const repository = repositoryQuery.data ?? project?.repository ?? null;

  return {
    access,
    tab,
    setTab,
    project,
    repository,
    technologiesById,
    star,
    isOwner,
    isLoading: projectQuery.isLoading || projectQuery.isFetching,
    isError: projectQuery.isError,
    errorStatus: httpStatusOf(projectQuery.error),
    refetch: projectQuery.refetch,
    tasks: tasksQuery.data,
    tasksLoading: tasksQuery.isLoading || tasksQuery.isFetching,
    tasksPage,
    setTasksPage,
    tasksStatus,
    setTasksStatus,
    tasksSearch,
    setTasksSearch,
    members: membersQuery.data,
    membersLoading: membersQuery.isLoading || membersQuery.isFetching,
    membersPage,
    setMembersPage,
    toggleStar,
    publish,
    archive,
    createManualTask,
    inviteMember,
    updateMemberRole,
    ejectMember,
    isBusy:
      publishState.isLoading ||
      archiveState.isLoading ||
      createTaskState.isLoading ||
      addMemberState.isLoading ||
      removeMemberState.isLoading,
  };
}
