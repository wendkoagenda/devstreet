import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
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

export type WorkshopView = "compose" | "results";

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

function adoptedStorageKey(analysisId: number): string {
  return `hub-ai-adopted-${analysisId}`;
}

function readAdopted(analysisId: number): Record<number, number> {
  try {
    const raw = sessionStorage.getItem(adoptedStorageKey(analysisId));
    if (!raw) return {};
    const parsed = JSON.parse(raw) as Record<string, number>;
    return Object.fromEntries(
      Object.entries(parsed).map(([key, value]) => [Number(key), value])
    );
  } catch {
    return {};
  }
}

function writeAdopted(analysisId: number, map: Record<number, number>): void {
  try {
    sessionStorage.setItem(adoptedStorageKey(analysisId), JSON.stringify(map));
  } catch {
    // sessionStorage indisponible : les badges adoptés ne survivent pas au refresh
  }
}

/**
 * Écran 06 : atelier contribution (manuel + IA optionnelle).
 * Suit docs/devstreet_hub/interfaces/06-atelier-ia.md.
 */
export function useAiWorkshop(projectId: number) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const access = useHubAccess();

  const [objective, setObjective] = useState("");
  const [language, setLanguage] = useState<"fr" | "en">("fr");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [view, setView] = useState<WorkshopView>("compose");
  const [selectedSuggestion, setSelectedSuggestion] = useState(0);
  const [adoptedByIndex, setAdoptedByIndex] = useState<Record<number, number>>(
    {}
  );
  const [polling, setPolling] = useState(false);
  const pollAttempt = useRef(0);
  const pollTimer = useRef<number | null>(null);
  const stopped = useRef(false);
  const hydratedFromUrl = useRef(false);

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
  const suggestions = result?.suggested_tasks ?? [];
  const currentSha = repository?.current_sha ?? null;
  const isSourcesStale = Boolean(
    analysis?.commit_sha &&
      currentSha &&
      analysis.commit_sha !== currentSha
  );

  const clearPoll = useCallback(() => {
    if (pollTimer.current != null) {
      window.clearTimeout(pollTimer.current);
    }
    pollTimer.current = null;
  }, []);

  useEffect(() => {
    stopped.current = false;
    return () => {
      stopped.current = true;
      clearPoll();
    };
  }, [clearPoll]);

  const syncAnalysisUrl = useCallback(
    (analysisId: number | null) => {
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          if (analysisId == null) {
            next.delete("analysis");
          } else {
            next.set("analysis", String(analysisId));
          }
          return next;
        },
        { replace: true }
      );
    },
    [setSearchParams]
  );

  const applyAnalysis = useCallback(
    (next: Analysis, options?: { switchToResults?: boolean }) => {
      setAnalysis(next);
      syncAnalysisUrl(next.id);
      if (
        options?.switchToResults !== false &&
        (next.status === "succeeded" || next.status === "failed")
      ) {
        setView("results");
      }
    },
    [syncAnalysisUrl]
  );

  useEffect(() => {
    if (!analysis) return;
    setSelectedSuggestion(0);
    setAdoptedByIndex(readAdopted(analysis.id));
  }, [analysis?.id]);

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

  const openTask = useCallback(
    (taskId: number) => {
      if (!project) return;
      navigate(`/hub/projects/${project.id}/tasks/${taskId}`);
    },
    [navigate, project]
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
          applyAnalysis(next);
          if (next.status === "succeeded" || next.status === "failed") {
            setPolling(false);
            if (next.status === "failed") {
              toast.error(t("hub.ai.errors.failed"));
            } else {
              toast.success(t("hub.ai.toasts.ready"));
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
    [applyAnalysis, clearPoll, fetchAnalysis, mapError, t]
  );

  useEffect(() => {
    if (hydratedFromUrl.current) return;
    const raw = searchParams.get("analysis");
    const analysisId = raw ? Number(raw) : NaN;
    if (!Number.isFinite(analysisId) || analysisId <= 0) {
      hydratedFromUrl.current = true;
      return;
    }
    hydratedFromUrl.current = true;
    void (async () => {
      try {
        const next = await fetchAnalysis(analysisId).unwrap();
        if (next.project_id !== projectId) return;
        applyAnalysis(next);
        if (next.status === "queued" || next.status === "running") {
          pollAttempt.current = 0;
          setPolling(true);
          schedulePoll(next.id);
        }
      } catch {
        syncAnalysisUrl(null);
      }
    })();
  }, [
    applyAnalysis,
    fetchAnalysis,
    projectId,
    schedulePoll,
    searchParams,
    syncAnalysisUrl,
  ]);

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
      pollAttempt.current = 0;
      applyAnalysis(created);
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
    applyAnalysis,
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
      if (adoptedByIndex[suggestionIndex] != null) {
        openTask(adoptedByIndex[suggestionIndex]);
        return;
      }
      try {
        const task = await adoptSuggestion({
          projectId: project.id,
          body: { analysis_id: analysis.id, suggestion_index: suggestionIndex },
        }).unwrap();
        const nextMap = { ...adoptedByIndex, [suggestionIndex]: task.id };
        setAdoptedByIndex(nextMap);
        writeAdopted(analysis.id, nextMap);
        toast.success(t("hub.ai.toasts.task_draft"), {
          action: {
            label: t("hub.ai.toasts.open_task"),
            onClick: () => openTask(task.id),
          },
        });
      } catch (error) {
        toast.error(mapError(error, "hub.ai.errors.adopt"));
      }
    },
    [
      adoptSuggestion,
      adoptedByIndex,
      analysis,
      canCreateTask,
      mapError,
      openTask,
      project,
      t,
    ]
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
        toast.success(t("hub.ai.toasts.manual_task"), {
          action: {
            label: t("hub.ai.toasts.open_task"),
            onClick: () => openTask(task.id),
          },
        });
        return true;
      } catch (error) {
        toast.error(mapError(error, "hub.ai.errors.manual"));
        return false;
      }
    },
    [canCreateTask, createTask, mapError, openTask, project, t]
  );

  const clearResults = useCallback(() => {
    clearPoll();
    setPolling(false);
    setAnalysis(null);
    setAdoptedByIndex({});
    setSelectedSuggestion(0);
    setView("compose");
    syncAnalysisUrl(null);
  }, [clearPoll, syncAnalysisUrl]);

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
    suggestions,
    currentSha,
    isSourcesStale,
    progressLabel,
    polling,
    view,
    setView,
    selectedSuggestion,
    setSelectedSuggestion,
    adoptedByIndex,
    openTask,
    clearResults,
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
