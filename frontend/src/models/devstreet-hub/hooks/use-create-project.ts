import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import {
  useCreateProjectMutation,
  useGetProjectQuery,
  useGetProjectRepositoryQuery,
  useGetTechnologiesQuery,
  useInitializeRepositoryMutation,
  usePublishProjectMutation,
  useResetForgePasswordMutation,
  useResumeProjectSetupMutation,
} from "../api";
import { apiDetailOf, httpStatusOf } from "../functions/api-error";
import { slugifyProjectTitle } from "../functions/project-slug";
import {
  PROJECT_LICENSES,
  type ForgeAccess,
  type Project,
  type ProjectLicense,
  type ProjectSetup,
  type ProjectWritePayload,
  type Technology,
} from "../schema";
import { useHubAccess } from "./use-hub-access";
import { useAuthSlice } from "@/models/auth/slice";

/** Étapes de progression visibles après le clic principal. */
export type ProgressStep = "form" | "draft" | "identity" | "repository" | "init" | "done";

export interface CreateProjectFormState {
  title: string;
  slug: string;
  problem: string;
  description: string;
  demo_url: string;
  declared_license: ProjectLicense;
  technologies: number[];
  slugTouched: boolean;
  integrityConfirmed: boolean;
  showAdvanced: boolean;
}

const INITIAL_FORM: CreateProjectFormState = {
  title: "",
  slug: "",
  problem: "",
  description: "",
  demo_url: "",
  declared_license: "MIT",
  technologies: [],
  slugTouched: false,
  integrityConfirmed: false,
  showAdvanced: false,
};

function toPayload(form: CreateProjectFormState): ProjectWritePayload {
  const demo = form.demo_url.trim();
  const payload: ProjectWritePayload = {
    title: form.title.trim(),
    declared_license: form.declared_license,
    // Langues détectées automatiquement après le premier push (via Gitea).
    technologies: [],
    problem: form.problem.trim(),
    description: form.description.trim(),
    demo_url: demo ? demo : null,
  };
  if (form.slugTouched && form.slug.trim()) {
    payload.slug = form.slug.trim();
  }
  return payload;
}

function isFormReady(form: CreateProjectFormState): boolean {
  if (!form.title.trim()) return false;
  if (form.slugTouched && form.slug.trim()) {
    return /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(form.slug.trim());
  }
  return true;
}

function licenseOf(value: string | undefined): ProjectLicense {
  if (value && (PROJECT_LICENSES as readonly string[]).includes(value)) {
    return value as ProjectLicense;
  }
  return "MIT";
}

function formFromProject(project: Project): CreateProjectFormState {
  return {
    title: project.title ?? "",
    slug: project.slug ?? "",
    problem: project.problem ?? "",
    description: project.description ?? "",
    demo_url: project.demo_url ?? "",
    declared_license: licenseOf(project.declared_license),
    technologies: project.technologies ?? [],
    slugTouched: true,
    integrityConfirmed: false,
    showAdvanced: false,
  };
}

function stripCreateExtras(result: Project & {
  forge_access?: ForgeAccess | null;
  setup?: ProjectSetup;
}): Project {
  const { forge_access: _fa, setup: _setup, ...project } = result as Project & {
    forge_access?: ForgeAccess | null;
    setup?: ProjectSetup;
  };
  return project;
}

/**
 * Création simplifiée : un bouton orchestre brouillon + identité + dépôt.
 * Reprise via `?draft=:id` et `POST .../setup` ; init README/push dans le Hub.
 */
export function useCreateProject() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { isAuthenticated, isInitialized, canCreateProject, requestLogin } =
    useHubAccess();
  const user = useAuthSlice((state) => state.user);

  const draftParam = searchParams.get("draft");
  const draftId = Number(draftParam);
  const hasDraftId = Number.isFinite(draftId) && draftId > 0;

  const [form, setForm] = useState<CreateProjectFormState>(INITIAL_FORM);
  const [project, setProject] = useState<Project | null>(null);
  const [forgeAccess, setForgeAccess] = useState<ForgeAccess | null>(null);
  const [setup, setSetup] = useState<ProjectSetup | null>(null);
  const [lastSavedAt, setLastSavedAt] = useState<Date | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [setupFailed, setSetupFailed] = useState(false);
  const [initMode, setInitMode] = useState<"readme" | "push_existing" | null>(null);
  const hydratedDraftId = useRef<number | null>(null);
  const createLock = useRef(false);

  const draftQuery = useGetProjectQuery(draftId, { skip: !hasDraftId });
  const repositoryQuery = useGetProjectRepositoryQuery(draftId, {
    skip: !hasDraftId || draftQuery.data?.repository?.status !== "ready",
  });

  const { data: techPage, isLoading: isLoadingTechs } = useGetTechnologiesQuery({
    page_size: 100,
    ordering: "label",
  });
  const technologies: Technology[] = techPage?.results ?? [];

  const [createProject, createState] = useCreateProjectMutation();
  const [resumeSetup, resumeState] = useResumeProjectSetupMutation();
  const [initializeRepository, initState] = useInitializeRepositoryMutation();
  const [publishProject, publishState] = usePublishProjectMutation();
  const [resetForgePassword, resetPasswordState] = useResetForgePasswordMutation();

  const isBusy =
    createState.isLoading ||
    resumeState.isLoading ||
    initState.isLoading ||
    publishState.isLoading ||
    resetPasswordState.isLoading ||
    createLock.current;

  const isHydratingDraft =
    hasDraftId && draftQuery.isLoading && hydratedDraftId.current !== draftId;

  useEffect(() => {
    if (hasDraftId) return;
    if (hydratedDraftId.current == null) return;
    hydratedDraftId.current = null;
    setProject(null);
    setForm(INITIAL_FORM);
    setForgeAccess(null);
    setSetup(null);
    setLastSavedAt(null);
    setActionError(null);
    setSetupFailed(false);
    setInitMode(null);
  }, [hasDraftId]);

  useEffect(() => {
    if (!hasDraftId || !draftQuery.data) return;
    if (hydratedDraftId.current === draftId) return;

    const loaded = draftQuery.data;
    const repository = repositoryQuery.data ?? loaded.repository ?? null;
    const merged: Project = repository
      ? { ...loaded, repository }
      : loaded;

    setProject(merged);
    setForm(formFromProject(merged));
    setLastSavedAt(new Date(merged.updated_at));
    setActionError(null);
    setSetupFailed(merged.repository?.status !== "ready");
    setInitMode(
      merged.repository?.status === "ready" &&
        (merged.repository.is_empty === false || Boolean(merged.repository.current_sha))
        ? "readme"
        : null
    );
    hydratedDraftId.current = draftId;
  }, [draftId, draftQuery.data, hasDraftId, repositoryQuery.data]);

  useEffect(() => {
    const repository = repositoryQuery.data;
    if (!repository) return;
    setProject((prev) => {
      if (!prev) return prev;
      if (
        prev.repository?.id === repository.id &&
        prev.repository?.status === repository.status &&
        prev.repository?.clone_url === repository.clone_url &&
        prev.repository?.current_sha === repository.current_sha
      ) {
        return prev;
      }
      return { ...prev, repository };
    });
  }, [repositoryQuery.data]);

  const repoReady = project?.repository?.status === "ready";
  const repoEmpty =
    repoReady &&
    (project?.repository?.is_empty ?? !project?.repository?.current_sha);
  const cloneUrl = project?.repository?.clone_url ?? null;
  const defaultBranch = project?.repository?.default_branch || "main";
  const forgeLogin = forgeAccess?.login ?? project?.repository?.namespace ?? null;
  const hasInitialPassword = Boolean(forgeAccess?.initial_password);

  const progressStep: ProgressStep = useMemo(() => {
    if (!project) return "form";
    if (!setup && !repoReady) {
      return setupFailed ? "identity" : "draft";
    }
    if (setup?.identity === "failed" || setup?.identity === "conflict") {
      return "identity";
    }
    if (setup?.repository === "failed" || (!repoReady && setup?.identity === "ok")) {
      return "repository";
    }
    if (repoReady && repoEmpty && !initMode) return "init";
    if (repoReady) return "done";
    return "draft";
  }, [initMode, project, repoEmpty, repoReady, setup, setupFailed]);

  const formReady = isFormReady(form);
  const canPublish = Boolean(
    project && repoReady && form.integrityConfirmed && project.status === "draft"
  );

  const mapError = useCallback(
    (error: unknown, fallbackKey: string) => {
      const status = httpStatusOf(error);
      const detail = apiDetailOf(error);
      if (status === 503) return t("hub.create.errors.forge_unavailable");
      if (detail) return detail;
      if (status === 401) return t("hub.create.errors.login_required");
      if (status === 403) return t("hub.create.errors.forbidden");
      if (status === 404) return t("hub.create.errors.draft_not_found");
      if (status === 409) return t("hub.create.errors.conflict");
      if (status === 429) return t("hub.common.rate_limited");
      if (status === null) return t("hub.create.errors.network");
      return t(fallbackKey);
    },
    [t]
  );

  const applySetupResult = useCallback(
    (result: Project & { forge_access?: ForgeAccess | null; setup?: ProjectSetup }) => {
      const nextProject = stripCreateExtras(result);
      setProject(nextProject);
      if (result.forge_access) {
        setForgeAccess(result.forge_access);
        if (result.forge_access.initial_password) {
          toast.message(
            result.forge_access.password_recovery_required
              ? t("hub.create.toasts.forge_password_recovered")
              : t("hub.create.toasts.forge_password_once"),
            {
              description: result.forge_access.password_recovery_required
                ? t("hub.create.toasts.forge_password_recovered_hint")
                : t("hub.create.toasts.forge_password_hint"),
            }
          );
        }
      }
      if (result.setup) {
        setSetup(result.setup);
        const failed =
          result.setup.identity !== "ok" || result.setup.repository !== "ok";
        setSetupFailed(failed);
        if (!failed) {
          toast.success(t("hub.create.toasts.repo_ready"));
        }
      }
      setLastSavedAt(new Date());
      setActionError(null);
      return nextProject;
    },
    [t]
  );

  const patchForm = useCallback((patch: Partial<CreateProjectFormState>) => {
    setForm((prev) => {
      const next = { ...prev, ...patch };
      if (patch.title !== undefined && !prev.slugTouched) {
        next.slug = slugifyProjectTitle(patch.title);
      }
      if (patch.slug !== undefined && patch.slugTouched === undefined) {
        next.slugTouched = true;
      }
      return next;
    });
    setActionError(null);
  }, []);

  const toggleTechnology = useCallback((id: number) => {
    setForm((prev) => {
      const has = prev.technologies.includes(id);
      return {
        ...prev,
        technologies: has
          ? prev.technologies.filter((techId) => techId !== id)
          : [...prev.technologies, id],
      };
    });
    setActionError(null);
  }, []);

  const createMyProject = useCallback(async () => {
    if (!canCreateProject) {
      requestLogin();
      return;
    }
    if (!isFormReady(form)) {
      setActionError(t("hub.create.errors.form_incomplete"));
      return;
    }
    if (createLock.current || createState.isLoading) return;
    createLock.current = true;

    try {
      if (project) {
        const result = await resumeSetup(project.id).unwrap();
        applySetupResult(result);
        return;
      }

      const result = await createProject(toPayload(form)).unwrap();
      const saved = applySetupResult(result);
      navigate(`/hub/projects/new?draft=${saved.id}`, { replace: true });
      hydratedDraftId.current = saved.id;

      if (result.setup && (result.setup.identity !== "ok" || result.setup.repository !== "ok")) {
        const message =
          result.setup.identity === "conflict"
            ? t("hub.create.errors.identity_conflict")
            : t("hub.create.errors.forge_unavailable");
        setActionError(message);
        toast.error(message);
      }
    } catch (error) {
      const message = mapError(error, "hub.create.errors.create");
      setActionError(message);
      setSetupFailed(true);
      toast.error(message);
    } finally {
      createLock.current = false;
    }
  }, [
    applySetupResult,
    canCreateProject,
    createProject,
    createState.isLoading,
    form,
    mapError,
    navigate,
    project,
    requestLogin,
    resumeSetup,
    t,
  ]);

  const initializeWithReadme = useCallback(async () => {
    if (!project || !repoReady) return;
    try {
      const result = await initializeRepository({
        projectId: project.id,
        body: { mode: "readme" },
      }).unwrap();
      setProject((prev) =>
        prev ? { ...prev, repository: result.repository } : prev
      );
      setInitMode("readme");
      setActionError(null);
      toast.success(t("hub.create.toasts.initialized"));
    } catch (error) {
      const message = mapError(error, "hub.create.errors.initialize");
      setActionError(message);
      toast.error(message);
    }
  }, [initializeRepository, mapError, project, repoReady, t]);

  const choosePushExisting = useCallback(async () => {
    if (!project || !repoReady) return;
    try {
      const result = await initializeRepository({
        projectId: project.id,
        body: { mode: "push_existing" },
      }).unwrap();
      setProject((prev) =>
        prev ? { ...prev, repository: result.repository } : prev
      );
      setInitMode("push_existing");
      setActionError(null);
      toast.message(t("hub.create.toasts.push_mode"));
    } catch (error) {
      const message = mapError(error, "hub.create.errors.initialize");
      setActionError(message);
      toast.error(message);
    }
  }, [initializeRepository, mapError, project, repoReady, t]);

  const publish = useCallback(async () => {
    if (!project) return;
    if (!canPublish) {
      setActionError(
        !repoReady
          ? t("hub.create.errors.repo_not_ready")
          : t("hub.create.errors.integrity_required")
      );
      return;
    }

    try {
      const published = await publishProject(project.id).unwrap();
      toast.success(t("hub.create.toasts.published"));
      navigate(`/hub/projects/${published.id}`);
    } catch (error) {
      const message = mapError(error, "hub.create.errors.publish");
      setActionError(message);
      toast.error(message);
    }
  }, [
    canPublish,
    mapError,
    navigate,
    project,
    publishProject,
    repoReady,
    t,
  ]);

  const dismissError = useCallback(() => setActionError(null), []);

  const dismissInitialPassword = useCallback(() => {
    // Purge mémoire uniquement — jamais de persistance navigateur du secret.
    setForgeAccess((prev) =>
      prev
        ? {
            ...prev,
            initial_password: undefined,
            created: false,
            reset: false,
            change_password_required: false,
            password_recovery_required: false,
          }
        : prev
    );
  }, []);

  const resetGitPassword = useCallback(async () => {
    if (!canCreateProject) {
      requestLogin();
      return;
    }
    try {
      const access = await resetForgePassword().unwrap();
      setForgeAccess(access);
      setActionError(null);
      toast.message(t("hub.create.toasts.password_reset"), {
        description: t("hub.create.toasts.password_reset_hint"),
      });
    } catch (error) {
      const message = mapError(error, "hub.create.errors.password_reset");
      setActionError(message);
      toast.error(message);
    }
  }, [canCreateProject, mapError, requestLogin, resetForgePassword, t]);

  const gitCommands = useMemo(() => {
    if (!cloneUrl) return null;
    const commitMsg = `feat: initial commit - ${form.title.trim() || "project"}`;
    return [
      "# 1. Se placer à la racine de ton projet",
      "git init",
      `git remote add origin ${cloneUrl}`,
      "# 2. Indexer et commiter les fichiers sources",
      "git add .",
      `git commit -m "${commitMsg}"`,
      "# 3. Publier la branche principale",
      `git branch -M ${defaultBranch}`,
      `git push -u origin ${defaultBranch}`,
    ].join("\n");
  }, [cloneUrl, defaultBranch, form.title]);

  const selectedTechnologies = useMemo(
    () => technologies.filter((tech) => form.technologies.includes(tech.id)),
    [form.technologies, technologies]
  );

  const draftLoadError =
    hasDraftId && draftQuery.isError
      ? mapError(draftQuery.error, "hub.create.errors.draft_not_found")
      : null;

  return {
    form,
    project,
    forgeAccess,
    forgeLogin,
    hasInitialPassword,
    setup,
    progressStep,
    technologies,
    selectedTechnologies,
    isLoadingTechs,
    isHydratingDraft,
    draftLoadError,
    formReady,
    canPublish,
    repoReady,
    repoEmpty,
    cloneUrl,
    defaultBranch,
    gitCommands,
    initMode,
    lastSavedAt,
    actionError,
    setupFailed,
    isBusy,
    isAuthenticated,
    isInitialized,
    canCreateProject,
    user,
    patchForm,
    toggleTechnology,
    createMyProject,
    initializeWithReadme,
    choosePushExisting,
    publish,
    dismissError,
    dismissInitialPassword,
    resetGitPassword,
    isResettingPassword: resetPasswordState.isLoading,
    requestLogin,
  };
}
