import { useCallback, useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import {
  useGetProjectCodeBlobQuery,
  useGetProjectCodeBranchesQuery,
  useGetProjectCodeSummaryQuery,
  useGetProjectCodeTreeQuery,
  useInitializeRepositoryMutation,
} from "../api";
import { httpStatusOf } from "../functions/api-error";
import type { CodeViewMode } from "../schema";
import { useHubAccess } from "./use-hub-access";

function parseMode(value: string | null): CodeViewMode {
  return value === "blob" ? "blob" : "tree";
}

/**
 * État d'exploration Code synchronisé dans l'URL (`ref`, `path`, `mode`).
 * Les slashs de branche restent dans le query param `ref` (pas dans le path route).
 */
export function useProjectCode(
  projectId: number,
  options: { enabled: boolean; isOwner: boolean }
) {
  const { enabled, isOwner } = options;
  const [searchParams, setSearchParams] = useSearchParams();
  const access = useHubAccess();

  const ref = searchParams.get("ref") || "";
  const path = searchParams.get("path") || "";
  const mode = parseMode(searchParams.get("mode"));

  const summaryQuery = useGetProjectCodeSummaryQuery(projectId, {
    skip: !enabled || projectId <= 0,
  });
  const defaultBranch = summaryQuery.data?.default_branch || "main";
  const activeRef = ref || defaultBranch;

  const branchesQuery = useGetProjectCodeBranchesQuery(projectId, {
    skip: !enabled || projectId <= 0 || Boolean(summaryQuery.data?.is_empty),
  });

  const treeQuery = useGetProjectCodeTreeQuery(
    { projectId, ref: activeRef, path },
    {
      skip:
        !enabled ||
        projectId <= 0 ||
        mode !== "tree" ||
        Boolean(summaryQuery.data?.is_empty),
    }
  );

  const blobQuery = useGetProjectCodeBlobQuery(
    { projectId, ref: activeRef, path },
    {
      skip:
        !enabled ||
        projectId <= 0 ||
        mode !== "blob" ||
        !path ||
        Boolean(summaryQuery.data?.is_empty),
    }
  );

  const [initializeRepository, initState] = useInitializeRepositoryMutation();

  const patchCodeParams = useCallback(
    (patch: {
      ref?: string;
      path?: string;
      mode?: CodeViewMode;
      clearPath?: boolean;
    }) => {
      const params = new URLSearchParams(searchParams);
      params.set("tab", "code");
      if (patch.ref !== undefined) {
        if (patch.ref) params.set("ref", patch.ref);
        else params.delete("ref");
      }
      if (patch.clearPath) {
        params.delete("path");
      } else if (patch.path !== undefined) {
        if (patch.path) params.set("path", patch.path);
        else params.delete("path");
      }
      if (patch.mode) {
        if (patch.mode === "tree") params.delete("mode");
        else params.set("mode", patch.mode);
      }
      setSearchParams(params, { replace: false });
    },
    [searchParams, setSearchParams]
  );

  const setBranch = useCallback(
    (nextRef: string) => {
      patchCodeParams({
        ref: nextRef === defaultBranch ? "" : nextRef,
        clearPath: true,
        mode: "tree",
      });
    },
    [defaultBranch, patchCodeParams]
  );

  const openPath = useCallback(
    (nextPath: string, nextMode: CodeViewMode) => {
      patchCodeParams({ path: nextPath, mode: nextMode });
    },
    [patchCodeParams]
  );

  const breadcrumbs = useMemo(() => {
    const parts = path ? path.split("/").filter(Boolean) : [];
    const crumbs: { label: string; path: string }[] = [
      { label: "", path: "" },
    ];
    let acc = "";
    for (const part of parts) {
      acc = acc ? `${acc}/${part}` : part;
      crumbs.push({ label: part, path: acc });
    }
    return crumbs;
  }, [path]);

  const retry = useCallback(() => {
    void summaryQuery.refetch();
    void branchesQuery.refetch();
    if (mode === "blob") void blobQuery.refetch();
    else void treeQuery.refetch();
  }, [blobQuery, branchesQuery, mode, summaryQuery, treeQuery]);

  const initReadme = useCallback(async () => {
    if (!isOwner) return false;
    try {
      await initializeRepository({
        projectId,
        body: { mode: "readme" },
      }).unwrap();
      await summaryQuery.refetch();
      await treeQuery.refetch();
      return true;
    } catch {
      return false;
    }
  }, [initializeRepository, isOwner, projectId, summaryQuery, treeQuery]);

  const errorStatus =
    httpStatusOf(summaryQuery.error) ??
    httpStatusOf(treeQuery.error) ??
    httpStatusOf(blobQuery.error);

  return {
    access,
    ref: activeRef,
    path,
    mode,
    breadcrumbs,
    summary: summaryQuery.data,
    branches: branchesQuery.data ?? [],
    tree: treeQuery.currentData,
    blob: blobQuery.currentData,
    isEmpty: Boolean(summaryQuery.data?.is_empty || treeQuery.currentData?.is_empty),
    isLoading:
      (mode === "tree" && treeQuery.isFetching && !treeQuery.currentData) ||
      (mode === "blob" && blobQuery.isFetching && !blobQuery.currentData),
    isFetching:
      summaryQuery.isFetching ||
      treeQuery.isFetching ||
      blobQuery.isFetching ||
      branchesQuery.isFetching,
    isError: Boolean(
      (mode === "tree" && treeQuery.isError) ||
        (mode === "blob" && blobQuery.isError)
    ),
    metadataError: summaryQuery.isError,
    errorStatus,
    setBranch,
    openPath,
    goRoot: () => patchCodeParams({ clearPath: true, mode: "tree" }),
    retry,
    initReadme,
    isInitializing: initState.isLoading,
    canInitialize: isOwner,
  };
}
