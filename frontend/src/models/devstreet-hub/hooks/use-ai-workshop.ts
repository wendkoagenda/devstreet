import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import {
  useAdoptAnalysisSuggestionMutation,
  useCreateAnalysisMutation,
  useCreateProjectTaskMutation,
  useGetProjectQuery,
  useGetProjectRepositoryQuery,
  useLazyGetAnalysisQuery,
  useSetAiConsentMutation,
} from "../api";
import { apiDetailOf, httpStatusOf } from "../functions/api-error";
import type {
  Analysis,
  AnalysisRequest,
  AnalysisResult,
  TaskWrite,
} from "../schema";
import { useHubAccess } from "./use-hub-access";

const MAX_POLLS = 24;

function nextDelayMs(attempt: number): number {
  return Math.min(10_000, 1000 * 2 ** Math.min(attempt, 3));
}

function asResult(raw: Analysis["result"]): AnalysisResult | null {
  if (!raw || typeof raw !== "object") return null;
  const data = raw as AnalysisResult;
  return {
    summary: data.summary ?? "",
    entry_points: data.entry_points ?? [],
    suggested_tasks: data.suggested_tasks ?? [],
    unknowns: data.unknowns ?? [],
  };
}

/**
 * Écran 06 : atelier IA guidé (consentement, génération, adoption).
 * Suit docs/devstreet_hub/interfaces/06-atelier-ia.md.
 */
export function useAiWorkshop(projectId: number) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const access = useHubAccess();

  const [objective, setObjective] = useState("");
  const [language, setLanguage] = useState<"fr" | "en">("fr");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [polling, setPolling] = useState(false);
  const pollAttempt = useRef(0);
  const pollTimer = useRef<number | null>(null);
  const stopped = useRef(false);

  const projectQuery = useGetProjectQuery(projectId, {
    skip: !Number.isFinite(projectId) || projectId <= 0,
  });
  const project = projectQuery.data;
  const repositoryQuery = useGetProjectRepositoryQuery(projectId, {
    skip: !project || project.repository?.status !== "ready",
  });
  const repository = repositoryQuery.data ?? project?.repository ?? null;

  const [setAiConsent, consentState] = useSetAiConsentMutation();
  const [createAnalysis, createState] = useCreateAnalysisMutation();
  const [fetchAnalysis] = useLazyGetAnalysisQuery();
  const [adoptSuggestion, adoptState] = useAdoptAnalysisSuggestionMutation();
  const [createTask, manualState] = useCreateProjectTaskMutation();

  const isOwner = Boolean(
    project && access.userId != null && project.owner_id === access.userId
  );
  const hasConsent = Boolean(project?.ai_consent_at);
  const canAnalyze = access.canAnalyze;
  const canCreateTask = access.canCreateTask;

  const result = useMemo(() => asResult(analysis?.result), [analysis?.result]);
  const currentSha = repository?.current_sha ?? null;
  const isSourcesStale = Boolean(
    analysis?.commit_sha &&
      currentSha &&
      analysis.commit_sha !== currentSha
  );

  const clearPoll = useCallback(() => {
    if (pollTimer.current != null) {
      window.clearTimeout(pollTimer.current);
      pollTimer.current = null;
    }
  }, []);

  useEffect(() => {
    stopped.current = false;
    return () => {
      stopped.current = true;
      clearPoll();
    };
  }, [clearPoll]);

  const mapError = useCallback(
    (error: unknown, fallbackKey: string) => {
      const status = httpStatusOf(error);
      const detail = apiDetailOf(error);
      if (detail) return detail;
      if (status === 401) return t("hub.ai.errors.login_required");
      if (status === 403) return t("hub.ai.errors.forbidden");
      if (status === 404) return t("hub.ai.errors.not_found");
      if (status === 409) return t("hub.ai.errors.conflict");
      if (status === 429) return t("hub.ai.errors.quota");
      if (status === 503) return t("hub.ai.errors.unavailable");
      if (status === null) return t("hub.ai.errors.network");
      return t(fallbackKey);
    },
    [t]
  );

  const schedulePoll = useCallback(
    (analysisId: number) => {
      clearPoll();
      if (stopped.current) return;
      if (pollAttempt.current >= MAX_POLLS) {
        setPolling(false);
        toast.error(t("hub.ai.errors.poll_timeout"));
        return;
      }
      const delay = nextDelayMs(pollAttempt.current);
      pollAttempt.current += 1;
      pollTimer.current = window.setTimeout(async () => {
        if (stopped.current) return;
        try {
          const next = await fetchAnalysis(analysisId).unwrap();
          setAnalysis(next);
          if (next.status === "succeeded" || next.status === "failed") {
            setPolling(false);
            if (next.status === "failed") {
              toast.error(t("hub.ai.errors.failed"));
            }
            return;
          }
          schedulePoll(analysisId);
        } catch (error) {
          setPolling(false);
          toast.error(mapError(error, "hub.ai.errors.poll"));
        }
      }, delay);
    },
    [clearPoll, fetchAnalysis, mapError, t]
  );

  const toggleConsent = useCallback(
    async (enabled: boolean) => {
      if (!project) return;
      if (!access.isAuthenticated) {
        access.requestLogin();
        return;
      }
      if (!isOwner) {
        toast.error(t("hub.ai.errors.owner_only_consent"));
        return;
      }
      try {
        await setAiConsent({ projectId: project.id, enabled }).unwrap();
        toast.success(
          enabled ? t("hub.ai.toasts.consent_on") : t("hub.ai.toasts.consent_off")
        );
      } catch (error) {
        toast.error(mapError(error, "hub.ai.errors.consent"));
      }
    },
    [access, isOwner, mapError, project, setAiConsent, t]
  );

  const startAnalysis = useCallback(async () => {
    if (!project) return;
    if (!access.isAuthenticated) {
      access.requestLogin();
      return;
    }
    if (!canAnalyze) {
      toast.error(t("hub.ai.errors.forbidden"));
      return;
    }
    if (!hasConsent) {
      toast.error(t("hub.ai.errors.need_consent"));
      return;
    }
    const body: AnalysisRequest = {
      objective: objective.trim(),
      language,
    };
    if (!body.objective) {
      toast.error(t("hub.ai.errors.objective_required"));
      return;
    }

    try {
      const created = await createAnalysis({
        projectId: project.id,
        body,
      }).unwrap();
      setAnalysis(created);
      pollAttempt.current = 0;
      if (created.status === "succeeded") {
        setPolling(false);
        toast.success(t("hub.ai.toasts.ready"));
        return;
      }
      if (created.status === "failed") {
        setPolling(false);
        toast.error(t("hub.ai.errors.failed"));
        return;
      }
      setPolling(true);
      schedulePoll(created.id);
    } catch (error) {
      const status = httpStatusOf(error);
      if (status === 429) {
        toast.error(t("hub.ai.errors.quota"));
        return;
      }
      if (status === 503) {
        toast.error(t("hub.ai.errors.unavailable"));
        return;
      }
      toast.error(mapError(error, "hub.ai.errors.start"));
    }
  }, [
    access,
    canAnalyze,
    createAnalysis,
    hasConsent,
    language,
    mapError,
    objective,
    project,
    schedulePoll,
    t,
  ]);

  const adopt = useCallback(
    async (suggestionIndex: number) => {
      if (!project || !analysis) return;
      if (!canCreateTask) {
        toast.error(t("hub.ai.errors.forbidden"));
        return;
      }
      try {
        const task = await adoptSuggestion({
          projectId: project.id,
          body: { analysis_id: analysis.id, suggestion_index: suggestionIndex },
        }).unwrap();
        toast.success(t("hub.ai.toasts.task_draft"));
        navigate(`/hub/projects/${project.id}/tasks/${task.id}`);
      } catch (error) {
        toast.error(mapError(error, "hub.ai.errors.adopt"));
      }
    },
    [adoptSuggestion, analysis, canCreateTask, mapError, navigate, project, t]
  );

  const createManual = useCallback(
    async (body: TaskWrite) => {
      if (!project) return false;
      if (!canCreateTask) {
        toast.error(t("hub.ai.errors.forbidden"));
        return false;
      }
      try {
        const task = await createTask({
          projectId: project.id,
          body,
        }).unwrap();
        toast.success(t("hub.ai.toasts.manual_task"));
        navigate(`/hub/projects/${project.id}/tasks/${task.id}`);
        return true;
      } catch (error) {
        toast.error(mapError(error, "hub.ai.errors.manual"));
        return false;
      }
    },
    [canCreateTask, createTask, mapError, navigate, project, t]
  );

  const progressLabel = useMemo(() => {
    if (!analysis) return null;
    if (analysis.status === "queued") return t("hub.ai.progress.queued");
    if (analysis.status === "running") return t("hub.ai.progress.running");
    if (analysis.status === "succeeded") return t("hub.ai.progress.succeeded");
    if (analysis.status === "failed") return t("hub.ai.progress.failed");
    return null;
  }, [analysis, t]);

  return {
    access,
    project,
    isOwner,
    hasConsent,
    canAnalyze,
    canCreateTask,
    objective,
    setObjective,
    language,
    setLanguage,
    analysis,
    result,
    currentSha,
    isSourcesStale,
    progressLabel,
    polling,
    isLoading: projectQuery.isLoading,
    isError: projectQuery.isError,
    errorStatus: httpStatusOf(projectQuery.error),
    refetch: projectQuery.refetch,
    toggleConsent,
    startAnalysis,
    adopt,
    createManual,
    isBusy:
      consentState.isLoading ||
      createState.isLoading ||
      adoptState.isLoading ||
      manualState.isLoading ||
      polling,
  };
}
