import { useCallback, useEffect, useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import {
  useGetContributionTaskQuery,
  useGetContributionsQuery,
  useGetProjectQuery,
  useGetProjectRepositoryQuery,
  useReviewContributionMutation,
} from "../api";
import { apiDetailOf, httpStatusOf } from "../functions/api-error";
import type { Contribution, ContributionReview } from "../schema";
import { useHubAccess } from "./use-hub-access";
import { PAGE_SIZE } from "@/helpers/api/pagination";

/**
 * Écran 05 : revue mainteneur des contributions d'un projet.
 * Suit docs/devstreet_hub/interfaces/05-revue-contributions.md.
 */
export function useContributionReview(projectId: number) {
  const { t } = useTranslation();
  const access = useHubAccess();
  const [searchParams, setSearchParams] = useSearchParams();

  const page = Math.max(1, Number(searchParams.get("page") || "1"));
  const selectedId = Number(searchParams.get("contribution") || "0");

  const projectQuery = useGetProjectQuery(projectId, {
    skip: !Number.isFinite(projectId) || projectId <= 0,
  });
  const project = projectQuery.data;

  const listQuery = useGetContributionsQuery(
    { project_id: projectId, page, page_size: PAGE_SIZE },
    { skip: !project }
  );

  const selectedFromList = useMemo(() => {
    if (!listQuery.data || !selectedId) return null;
    return (
      listQuery.data.results.find((item) => item.id === selectedId) ?? null
    );
  }, [listQuery.data, selectedId]);

  // Auto-sélection de la première proposition si aucune n'est choisie.
  useEffect(() => {
    if (selectedId || !listQuery.data?.results.length) return;
    const first = listQuery.data.results[0];
    const params = new URLSearchParams(searchParams);
    params.set("contribution", String(first.id));
    setSearchParams(params, { replace: true });
  }, [listQuery.data, searchParams, selectedId, setSearchParams]);

  const activeId = selectedFromList?.id ?? selectedId;
  const taskId = selectedFromList?.task_id ?? 0;

  const taskQuery = useGetContributionTaskQuery(taskId, {
    skip: !taskId,
  });

  const repositoryQuery = useGetProjectRepositoryQuery(projectId, {
    skip: !project || project.repository?.status !== "ready",
  });

  const [reviewContribution, reviewState] = useReviewContributionMutation();

  /** Affichage seulement : le serveur applique require_maintainer + contributions.review. */
  const canReview = access.canReviewContributions;

  const mapError = useCallback(
    (error: unknown, fallbackKey: string) => {
      const status = httpStatusOf(error);
      const detail = apiDetailOf(error);
      if (detail) return detail;
      if (status === 401) return t("hub.review.errors.login_required");
      if (status === 403) return t("hub.review.errors.forbidden");
      if (status === 404) return t("hub.review.errors.not_found");
      if (status === 409) return t("hub.review.errors.conflict");
      if (status === 429) return t("hub.common.rate_limited");
      if (status === null) return t("hub.review.errors.network");
      return t(fallbackKey);
    },
    [t]
  );

  const selectContribution = useCallback(
    (contribution: Contribution) => {
      const params = new URLSearchParams(searchParams);
      params.set("contribution", String(contribution.id));
      setSearchParams(params, { replace: true });
    },
    [searchParams, setSearchParams]
  );

  const setPage = useCallback(
    (nextPage: number) => {
      const params = new URLSearchParams(searchParams);
      params.set("page", String(nextPage));
      setSearchParams(params, { replace: true });
    },
    [searchParams, setSearchParams]
  );

  const decide = useCallback(
    async (body: ContributionReview) => {
      if (!selectedFromList) return false;
      if (!access.isAuthenticated) {
        access.requestLogin();
        return false;
      }
      if (!canReview) {
        toast.error(t("hub.review.errors.forbidden"));
        return false;
      }
      if (selectedFromList.author_id === access.userId) {
        toast.error(t("hub.review.errors.self_review"));
        return false;
      }
      if (selectedFromList.status !== "submitted") {
        toast.error(t("hub.review.errors.already_decided"));
        return false;
      }
      if (!body.note.trim()) {
        toast.error(t("hub.review.errors.note_required"));
        return false;
      }

      try {
        await reviewContribution({
          contributionId: selectedFromList.id,
          body: { status: body.status, note: body.note.trim() },
        }).unwrap();
        toast.success(
          body.status === "accepted"
            ? t("hub.review.toasts.accepted")
            : t("hub.review.toasts.rejected")
        );
        return true;
      } catch (error) {
        toast.error(mapError(error, "hub.review.errors.decide"));
        return false;
      }
    },
    [
      access,
      canReview,
      mapError,
      reviewContribution,
      selectedFromList,
      t,
    ]
  );

  const repository = repositoryQuery.data ?? project?.repository ?? null;
  const prUrl = useMemo(() => {
    if (!selectedFromList?.pull_request_number || !repository?.browse_url) {
      return null;
    }
    return `${repository.browse_url}/pulls/${selectedFromList.pull_request_number}`;
  }, [repository?.browse_url, selectedFromList?.pull_request_number]);

  return {
    access,
    project,
    repository,
    prUrl,
    contributions: listQuery.data,
    listLoading: listQuery.isLoading || listQuery.isFetching,
    page,
    setPage,
    selected: selectedFromList,
    selectContribution,
    activeId,
    task: taskQuery.data,
    taskLoading: taskQuery.isLoading,
    isLoading: projectQuery.isLoading,
    isError: projectQuery.isError,
    errorStatus: httpStatusOf(projectQuery.error),
    refetch: () => {
      void projectQuery.refetch();
      void listQuery.refetch();
    },
    canReview,
    decide,
    isBusy: reviewState.isLoading,
  };
}
