import { useCallback, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import {
  useCreateProjectDiscussionMutation,
  useGetContributionTaskQuery,
  useGetContributionsQuery,
  useGetProjectQuery,
  useSubmitContributionMutation,
  useUpdateContributionTaskMutation,
} from "../api";
import { apiDetailOf, httpStatusOf } from "../functions/api-error";
import type {
  ContributionWrite,
  DiscussionWrite,
  TaskUpdate,
} from "../schema";
import { useHubAccess } from "./use-hub-access";
import { PAGE_SIZE } from "@/helpers/api/pagination";

function newRequestKey(): string {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (char) => {
    const random = (Math.random() * 16) | 0;
    const value = char === "x" ? random : (random & 0x3) | 0x8;
    return value.toString(16);
  });
}

/**
 * Écran 04 : comprendre une tâche, demander de l'aide, proposer une contribution.
 * Suit docs/devstreet_hub/interfaces/04-tache-contribution.md.
 */
export function useTaskContribution(projectId: number, taskId: number) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const access = useHubAccess();
  const helpRequestKey = useRef(newRequestKey());
  const [helpDraft, setHelpDraft] = useState<{ title: string; body: string } | null>(
    null
  );
  const [forumUnavailable, setForumUnavailable] = useState(false);

  const taskQuery = useGetContributionTaskQuery(taskId, {
    skip: !Number.isFinite(taskId) || taskId <= 0,
  });
  const task = taskQuery.data;

  const projectQuery = useGetProjectQuery(projectId, {
    skip: !Number.isFinite(projectId) || projectId <= 0,
  });
  const project = projectQuery.data;

  const contributionsQuery = useGetContributionsQuery(
    { task_id: taskId, page_size: PAGE_SIZE },
    { skip: !task }
  );

  const [submitContribution, submitState] = useSubmitContributionMutation();
  const [createDiscussion, discussionState] = useCreateProjectDiscussionMutation();
  const [updateTask, updateState] = useUpdateContributionTaskMutation();

  const isOwner = Boolean(
    project && access.userId != null && project.owner_id === access.userId
  );
  const canMaintain = isOwner || access.canUpdateTask;
  /** Droit API de soumettre une contribution (tâche ouverte + projet publié). */
  const canSubmit =
    access.canSubmitContribution &&
    task?.status === "open" &&
    project?.status === "published";
  /**
   * CTA « Proposer mon travail » : réservé au contributeur.
   * Le propriétaire / mainteneur qui a ouvert la tâche gère (fermer, revue),
   * il ne doit pas voir ce bouton en action principale.
   */
  const showProposeCta = canSubmit && !canMaintain;

  const firstStep = useMemo(() => {
    if (!task) return null;
    const criteria = task.acceptance_criteria ?? [];
    if (criteria.length > 0) return criteria[0];
    const lines = task.description
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean);
    return lines[0] ?? null;
  }, [task]);

  const mapError = useCallback(
    (error: unknown, fallbackKey: string) => {
      const status = httpStatusOf(error);
      const detail = apiDetailOf(error);
      if (detail) return detail;
      if (status === 401) return t("hub.task.errors.login_required");
      if (status === 403) return t("hub.task.errors.forbidden");
      if (status === 404) return t("hub.task.errors.not_found");
      if (status === 409) return t("hub.task.errors.conflict");
      if (status === 429) return t("hub.common.rate_limited");
      if (status === 503) return t("hub.task.errors.forum_unavailable");
      if (status === null) return t("hub.task.errors.network");
      return t(fallbackKey);
    },
    [t]
  );

  const openHelpDraft = useCallback(() => {
    if (!task) return;
    setForumUnavailable(false);
    setHelpDraft({
      title: t("hub.task.help.default_title", { title: task.title }),
      body: t("hub.task.help.default_body", { title: task.title }),
    });
  }, [t, task]);

  const publishHelp = useCallback(async () => {
    if (!task || !helpDraft || !project) return false;
    if (!access.isAuthenticated) {
      access.requestLogin();
      return false;
    }
    if (!access.canDiscuss) {
      toast.error(t("hub.task.errors.forbidden"));
      return false;
    }

    const body: DiscussionWrite = {
      request_key: helpRequestKey.current,
      task_id: task.id,
      title: helpDraft.title.trim(),
      body: helpDraft.body.trim(),
    };

    try {
      const created = await createDiscussion({
        projectId: project.id,
        body,
      }).unwrap();
      const topicId = Number(created.forum_topic_id);
      toast.success(t("hub.task.toasts.help_sent"), {
        action:
          Number.isFinite(topicId) && topicId > 0
            ? {
                label: t("hub.task.toasts.open_forum"),
                onClick: () => navigate(`/forum/publications/${topicId}`),
              }
            : undefined,
      });
      setHelpDraft(null);
      setForumUnavailable(false);
      helpRequestKey.current = newRequestKey();
      return true;
    } catch (error) {
      const status = httpStatusOf(error);
      if (status === 503) {
        setForumUnavailable(true);
        toast.error(t("hub.task.errors.forum_unavailable"));
        return false;
      }
      toast.error(mapError(error, "hub.task.errors.help"));
      return false;
    }
  }, [
    access,
    createDiscussion,
    helpDraft,
    mapError,
    navigate,
    project,
    t,
    task,
  ]);

  const proposeWork = useCallback(
    async (payload: ContributionWrite) => {
      if (!task) return false;
      if (!access.isAuthenticated) {
        access.requestLogin();
        return false;
      }
      if (!canSubmit) {
        toast.error(
          task.status !== "open"
            ? t("hub.task.errors.task_closed")
            : t("hub.task.errors.forbidden")
        );
        return false;
      }

      const body: ContributionWrite = {
        summary: payload.summary.trim(),
        pull_request_number: payload.pull_request_number || null,
        artifact_sha: payload.artifact_sha?.trim() || null,
      };

      try {
        await submitContribution({ taskId: task.id, body }).unwrap();
        toast.success(t("hub.task.toasts.submitted"));
        return true;
      } catch (error) {
        toast.error(mapError(error, "hub.task.errors.submit"));
        return false;
      }
    },
    [access, canSubmit, mapError, submitContribution, t, task]
  );

  const patchTask = useCallback(
    async (body: TaskUpdate) => {
      if (!task) return false;
      try {
        await updateTask({ taskId: task.id, body }).unwrap();
        toast.success(t("hub.task.toasts.updated"));
        return true;
      } catch (error) {
        toast.error(mapError(error, "hub.task.errors.update"));
        return false;
      }
    },
    [mapError, t, task, updateTask]
  );

  const refetch = useCallback(() => {
    void taskQuery.refetch();
    void projectQuery.refetch();
    void contributionsQuery.refetch();
  }, [contributionsQuery, projectQuery, taskQuery]);

  return {
    access,
    task,
    project,
    firstStep,
    contributions: contributionsQuery.data,
    contributionsLoading: contributionsQuery.isLoading,
    isLoading: taskQuery.isLoading || projectQuery.isLoading,
    isError: taskQuery.isError || projectQuery.isError,
    errorStatus: httpStatusOf(taskQuery.error) ?? httpStatusOf(projectQuery.error),
    refetch,
    canMaintain,
    canSubmit,
    showProposeCta,
    helpDraft,
    setHelpDraft,
    forumUnavailable,
    openHelpDraft,
    closeHelpDraft: () => setHelpDraft(null),
    publishHelp,
    proposeWork,
    patchTask,
    isBusy:
      submitState.isLoading ||
      discussionState.isLoading ||
      updateState.isLoading,
  };
}
