import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import {
  useGetContributionsQuery,
  useGetProjectProfileQuery,
  useGetProjectsQuery,
  useLazyGetProjectQuery,
} from "../api";
import { apiDetailOf, httpStatusOf } from "../functions/api-error";
import type { Project, ProjectProfileSection } from "../schema";
import { useHubAccess } from "./use-hub-access";
import { useAuthSlice } from "@/models/auth/slice";

const PAGE_SIZE = 12;

function parseSection(raw: string | null): ProjectProfileSection {
  if (raw === "projects" || raw === "contributions") return raw;
  return "overview";
}

/**
 * Écran 07 : projets publiés et contributions acceptées du profil commun.
 * Suit docs/devstreet_hub/interfaces/07-profil-realisations.md.
 */
export function useProjectProfile(userId: number) {
  const access = useHubAccess();
  const authUser = useAuthSlice((state) => state.user);
  const [params, setSearchParams] = useSearchParams();
  const [extraProjects, setExtraProjects] = useState<Record<number, Project>>(
    {}
  );
  const [fetchProject] = useLazyGetProjectQuery();

  const section = parseSection(params.get("section"));
  const page = Math.max(1, Number(params.get("page") || "1") || 1);

  const profileQuery = useGetProjectProfileQuery(userId, {
    skip: !Number.isFinite(userId) || userId <= 0,
  });

  const projectsQuery = useGetProjectsQuery(
    { owner: userId, page, page_size: PAGE_SIZE },
    { skip: section !== "projects" || userId <= 0 }
  );

  const contributionsQuery = useGetContributionsQuery(
    { author_id: userId, page, page_size: PAGE_SIZE },
    { skip: section !== "contributions" || userId <= 0 }
  );

  const displayName = useMemo(() => {
    if (authUser?.id === userId && authUser.full_name) return authUser.full_name;
    return null;
  }, [authUser, userId]);

  const visibleContributions = useMemo(() => {
    if (section === "contributions") {
      return contributionsQuery.data?.results ?? [];
    }
    return profileQuery.data?.contributions ?? [];
  }, [
    contributionsQuery.data?.results,
    profileQuery.data?.contributions,
    section,
  ]);

  const knownProjectKey = useMemo(() => {
    const ids = new Set<number>();
    for (const project of profileQuery.data?.projects ?? []) ids.add(project.id);
    for (const project of projectsQuery.data?.results ?? []) ids.add(project.id);
    for (const id of Object.keys(extraProjects)) ids.add(Number(id));
    return [...ids].sort((a, b) => a - b).join(",");
  }, [
    extraProjects,
    profileQuery.data?.projects,
    projectsQuery.data?.results,
  ]);

  const contributionProjectKey = useMemo(
    () =>
      [...new Set(visibleContributions.map((item) => item.project_id))]
        .sort((a, b) => a - b)
        .join(","),
    [visibleContributions]
  );

  useEffect(() => {
    const known = new Set(
      knownProjectKey
        .split(",")
        .filter(Boolean)
        .map((value) => Number(value))
    );
    const missing = contributionProjectKey
      .split(",")
      .filter(Boolean)
      .map((value) => Number(value))
      .filter((id) => !known.has(id));
    if (missing.length === 0) return;

    let cancelled = false;
    void (async () => {
      const next: Record<number, Project> = {};
      await Promise.all(
        missing.map(async (id) => {
          try {
            const project = await fetchProject(id).unwrap();
            next[id] = project;
          } catch {
            // Projet inaccessible : la carte affichera « réalisation indisponible ».
          }
        })
      );
      if (!cancelled && Object.keys(next).length > 0) {
        setExtraProjects((prev) => ({ ...prev, ...next }));
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [contributionProjectKey, fetchProject, knownProjectKey]);

  const projectById = useMemo(() => {
    const map = new Map<number, Project>();
    for (const project of profileQuery.data?.projects ?? []) {
      map.set(project.id, project);
    }
    for (const project of projectsQuery.data?.results ?? []) {
      map.set(project.id, project);
    }
    for (const project of Object.values(extraProjects)) {
      map.set(project.id, project);
    }
    return map;
  }, [
    extraProjects,
    profileQuery.data?.projects,
    projectsQuery.data?.results,
  ]);

  const setSection = (next: ProjectProfileSection) => {
    const nextParams = new URLSearchParams();
    if (next !== "overview") {
      nextParams.set("section", next);
      nextParams.set("page", "1");
    }
    setSearchParams(nextParams, { replace: true });
  };

  const setPage = (nextPage: number) => {
    const nextParams = new URLSearchParams(params);
    nextParams.set("section", section);
    nextParams.set("page", String(Math.max(1, nextPage)));
    setSearchParams(nextParams, { replace: true });
  };

  const activeQuery =
    section === "projects"
      ? projectsQuery
      : section === "contributions"
        ? contributionsQuery
        : profileQuery;

  return {
    access,
    userId,
    displayName,
    isSelf: access.userId === userId,
    section,
    page,
    pageSize: PAGE_SIZE,
    setSection,
    setPage,
    profile: profileQuery.data ?? null,
    projectsPage: projectsQuery.data ?? null,
    contributionsPage: contributionsQuery.data ?? null,
    projectById,
    isLoading: activeQuery.isLoading || activeQuery.isFetching,
    isError: activeQuery.isError,
    errorStatus: httpStatusOf(activeQuery.error),
    errorDetail: apiDetailOf(activeQuery.error),
    refetch: activeQuery.refetch,
  };
}
