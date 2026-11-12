import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import {
  useCreateProjectMutation,
  useGetProjectQuery,
  useGetProjectRepositoryQuery,
  useGetTechnologiesQuery,
  useProvisionForgeAccessMutation,
  useProvisionRepositoryMutation,
  usePublishProjectMutation,
  useUpdateProjectMutation,
} from "../api";
import { apiDetailOf, httpStatusOf } from "../functions/api-error";
import { slugifyProjectTitle } from "../functions/project-slug";
import {
  PROJECT_LICENSES,
  type ForgeAccess,
  type Project,
  type ProjectLicense,
  type ProjectWritePayload,
  type Technology,
} from "../schema";
import { useHubAccess } from "./use-hub-access";
import { useAuthSlice } from "@/models/auth/slice";

export type WizardStep = 1 | 2 | 3;

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
};

function toPayload(form: CreateProjectFormState): ProjectWritePayload {
  const demo = form.demo_url.trim();
  return {
    title: form.title.trim(),
    slug: form.slug.trim(),
    problem: form.problem.trim(),
    description: form.description.trim(),
    demo_url: demo ? demo : null,
    declared_license: form.declared_license,
    technologies: form.technologies,
  };
}

function isFormReady(form: CreateProjectFormState): boolean {
  return (
    form.title.trim().length > 0 &&
    form.slug.trim().length > 0 &&
    /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(form.slug.trim()) &&
    form.problem.trim().length > 0
  );
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
  };
}

/**
 * Orchestration du wizard de création : brouillon → forge/provision → publication.
 * Reprise via `?draft=:id`. Les droits restent contrôlés côté serveur.
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
  const [lastSavedAt, setLastSavedAt] = useState<Date | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [provisionFailed, setProvisionFailed] = useState(false);
  const hydratedDraftId = useRef<number | null>(null);

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
  const [updateProject, updateState] = useUpdateProjectMutation();
  const [provisionForgeAccess, forgeState] = useProvisionForgeAccessMutation();
  const [provisionRepository, provisionState] = useProvisionRepositoryMutation();
  const [publishProject, publishState] = usePublishProjectMutation();

  const isBusy =
    createState.isLoading ||
    updateState.isLoading ||
    forgeState.isLoading ||
    provisionState.isLoading ||
    publishState.isLoading;

  const isHydratingDraft =
    hasDraftId && draftQuery.isLoading && hydratedDraftId.current !== draftId;

  useEffect(() => {
    if (hasDraftId) return;
    if (hydratedDraftId.current == null) return;
    hydratedDraftId.current = null;
    setProject(null);
    setForm(INITIAL_FORM);
    setForgeAccess(null);
    setLastSavedAt(null);
    setActionError(null);
    setProvisionFailed(false);
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
    setProvisionFailed(false);
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
        prev.repository?.clone_url === repository.clone_url
      ) {
        return prev;
      }
      return { ...prev, repository };
    });
  }, [repositoryQuery.data]);

  const repoReady = project?.repository?.status === "ready";
  const cloneUrl = project?.repository?.clone_url ?? null;
  const browseUrl = project?.repository?.browse_url ?? null;
  const defaultBranch = project?.repository?.default_branch || "main";
  const forgeLogin = forgeAccess?.login ?? project?.repository?.namespace ?? null;
  const hasInitialPassword = Boolean(forgeAccess?.initial_password);

  const activeStep: WizardStep = useMemo(() => {
    if (!project) return 1;
    if (!repoReady) return 2;
    return 3;
  }, [project, repoReady]);

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

  const saveDraft = useCallback(async () => {
    if (!canCreateProject) {
      requestLogin();
      return null;
    }
    if (!isFormReady(form)) {
      setActionError(t("hub.create.errors.form_incomplete"));
      return null;
    }

    const payload = toPayload(form);
    try {
      const wasCreate = !project;
      const saved = project
        ? await updateProject({ projectId: project.id, body: payload }).unwrap()
        : await createProject(payload).unwrap();
      setProject((prev) =>
        prev?.repository
          ? { ...saved, repository: prev.repository }
          : saved
      );
      setLastSavedAt(new Date());
      setActionError(null);
      toast.success(t("hub.create.toasts.draft_saved"));
      if (wasCreate) {
        navigate(`/hub/projects/new?draft=${saved.id}`, { replace: true });
        hydratedDraftId.current = saved.id;
      }
      return saved;
    } catch (error) {
      const message = mapError(error, "hub.create.errors.save");
      setActionError(message);
      toast.error(message);
      return null;
    }
  }, [
    canCreateProject,
    createProject,
    form,
    mapError,
    navigate,
    project,
    requestLogin,
    t,
    updateProject,
  ]);

  const prepareRepository = useCallback(async () => {
    if (!canCreateProject) {
      requestLogin();
      return;
    }

    let current = project;
    if (!current) {
      current = await saveDraft();
      if (!current) return;
    } else if (isFormReady(form)) {
      const refreshed = await saveDraft();
      if (refreshed) current = refreshed;
    }

    try {
      const access = await provisionForgeAccess().unwrap();
      setForgeAccess(access);
      if (access.initial_password) {
        toast.message(
          access.password_recovery_required
            ? t("hub.create.toasts.forge_password_recovered")
            : t("hub.create.toasts.forge_password_once"),
          {
            description: access.password_recovery_required
              ? t("hub.create.toasts.forge_password_recovered_hint")
              : t("hub.create.toasts.forge_password_hint"),
          }
        );
      }

      const repository = await provisionRepository(current.id).unwrap();
      setProject((prev) =>
        prev ? { ...prev, repository } : { ...current!, repository }
      );
      setLastSavedAt(new Date());
      setActionError(null);
      setProvisionFailed(false);
      if (repository.status === "ready") {
        toast.success(t("hub.create.toasts.repo_ready"));
      } else {
        toast.message(t("hub.create.toasts.repo_pending"));
      }
    } catch (error) {
      const status = httpStatusOf(error);
      const message =
        status === 503
          ? t("hub.create.errors.forge_unavailable")
          : mapError(error, "hub.create.errors.provision");
      setActionError(message);
      setProvisionFailed(true);
      toast.error(message);
    }
  }, [
    canCreateProject,
    form,
    mapError,
    project,
    provisionForgeAccess,
    provisionRepository,
    requestLogin,
    saveDraft,
    t,
  ]);

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
    setForgeAccess((prev) =>
      prev
        ? {
            ...prev,
            initial_password: undefined,
            created: false,
            change_password_required: false,
          }
        : prev
    );
  }, []);

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
      "# 3. Publier la branche principale sur la forge",
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
    technologies,
    selectedTechnologies,
    isLoadingTechs,
    isHydratingDraft,
    draftLoadError,
    activeStep,
    formReady,
    canPublish,
    repoReady,
    cloneUrl,
    browseUrl,
    defaultBranch,
    gitCommands,
    lastSavedAt,
    actionError,
    provisionFailed,
    isBusy,
    isAuthenticated,
    isInitialized,
    canCreateProject,
    user,
    patchForm,
    toggleTechnology,
    saveDraft,
    prepareRepository,
    publish,
    dismissError,
    dismissInitialPassword,
    requestLogin,
  };
}
