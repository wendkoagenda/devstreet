import { AlertTriangle, LogIn, Sparkles, X } from "lucide-react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { CreateProjectFormSection } from "../components/create-project-form-section";
import { CreateProjectPreview } from "../components/create-project-preview";
import { CreateProjectPublishSection } from "../components/create-project-publish-section";
import { CreateProjectRepoSection } from "../components/create-project-repo-section";
import { CreateProjectStepper } from "../components/create-project-stepper";
import { useCreateProject } from "../hooks/use-create-project";

function initialsOf(name: string | undefined | null): string {
  if (!name) return "?";
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");
}

export default function CreateProjectPage() {
  const { t } = useTranslation();
  const wizard = useCreateProject();

  if (!wizard.isInitialized || wizard.isHydratingDraft) {
    return (
      <div className="mx-auto w-full max-w-3xl py-16 text-center text-sm text-muted-foreground">
        {t("common.loading")}
      </div>
    );
  }

  if (!wizard.isAuthenticated || !wizard.canCreateProject) {
    return (
      <div className="mx-auto w-full max-w-lg">
        <section className="flex flex-col items-center rounded-xl border border-dashed border-input bg-card px-6 py-14 text-center shadow-sm">
          <h1 className="mb-2 text-xl font-bold text-foreground">
            {t("hub.create.gate.title")}
          </h1>
          <p className="mb-6 max-w-md text-sm text-muted-foreground">
            {!wizard.isAuthenticated
              ? t("hub.create.gate.login_text")
              : t("hub.create.gate.forbidden_text")}
          </p>
          {!wizard.isAuthenticated ? (
            <Button
              type="button"
              onClick={wizard.requestLogin}
              className="h-9 gap-1.5 rounded-lg text-xs font-semibold"
            >
              <LogIn aria-hidden className="size-4" />
              {t("hub.common.login")}
            </Button>
          ) : null}
        </section>
      </div>
    );
  }

  if (wizard.draftLoadError) {
    return (
      <div className="mx-auto flex max-w-lg flex-col items-center gap-4 py-16 text-center">
        <AlertTriangle aria-hidden className="size-8 text-destructive" />
        <p className="text-sm text-muted-foreground">{wizard.draftLoadError}</p>
        <Button asChild variant="outline" className="h-9 text-xs">
          <Link to="/hub/projects/new">{t("hub.create.actions.new_draft")}</Link>
        </Button>
      </div>
    );
  }

  const ownerLabel = wizard.user?.username
    ? `@${wizard.user.username}`
    : wizard.user?.full_name || t("hub.create.preview.you");
  const ownerInitials = initialsOf(wizard.user?.full_name || wizard.user?.username);
  const formLocked = Boolean(wizard.project);
  const savedLabel = wizard.lastSavedAt
    ? wizard.lastSavedAt.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      })
    : null;

  return (
    <div className="mx-auto flex w-full max-w-[1360px] flex-col gap-8">
      <header className="flex flex-col justify-between gap-4 border-b border-border pb-6 md:flex-row md:items-end">
        <div className="flex max-w-2xl flex-col gap-2">
          <h1 className="flex flex-wrap items-center gap-3 text-2xl font-bold tracking-tight text-foreground lg:text-3xl">
            {wizard.project
              ? t("hub.create.title_resume")
              : t("hub.create.title")}
            <span className="rounded-full border border-border bg-secondary px-3 py-1 text-xs font-medium leading-none tracking-wide text-muted-foreground">
              {t("hub.create.badge")}
            </span>
          </h1>
          <p className="text-sm text-muted-foreground">
            {wizard.project
              ? t("hub.create.description_resume")
              : t("hub.create.description")}
          </p>
        </div>
        <div className="flex items-center gap-3 self-start rounded-xl border border-border bg-card px-3.5 py-2 shadow-card md:self-auto">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2.5 w-2.5">
              {wizard.project ? (
                <>
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-75" />
                  <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-success" />
                </>
              ) : (
                <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-muted-foreground/40" />
              )}
            </span>
            <span className="text-xs font-medium text-foreground">
              {wizard.project
                ? t("hub.create.autosave.on")
                : t("hub.create.autosave.off")}
            </span>
          </div>
          {savedLabel ? (
            <>
              <span className="text-border">|</span>
              <span className="text-[11px] text-muted-foreground">{savedLabel}</span>
            </>
          ) : null}
        </div>
      </header>

      {wizard.project ? (
        <CreateProjectStepper
          progressStep={wizard.progressStep}
          setupFailed={wizard.setupFailed}
        />
      ) : null}

      {wizard.actionError ? (
        <div
          role="alert"
          className="flex items-start gap-3 rounded-xl border border-destructive/30 bg-destructive/10 p-4"
        >
          <AlertTriangle aria-hidden className="mt-0.5 size-5 shrink-0 text-destructive" />
          <div className="min-w-0 flex-1">
            <p className="text-sm font-semibold text-destructive">
              {t("hub.create.errors.title")}
            </p>
            <p className="text-xs leading-relaxed text-destructive/90">
              {wizard.actionError}
            </p>
            {wizard.setupFailed && wizard.project ? (
              <Button
                type="button"
                variant="outline"
                disabled={wizard.isBusy}
                className="mt-3 h-8 text-xs"
                onClick={() => {
                  void wizard.createMyProject();
                }}
              >
                {t("hub.create.repo.retry")}
              </Button>
            ) : null}
          </div>
          <button
            type="button"
            onClick={wizard.dismissError}
            className="rounded p-1 text-destructive hover:bg-destructive/10"
            aria-label={t("common.cancel")}
          >
            <X aria-hidden className="size-4" />
          </button>
        </div>
      ) : null}

      <div className="grid grid-cols-1 items-start gap-8 lg:grid-cols-12">
        <div className="flex flex-col gap-8 lg:col-span-8">
          <CreateProjectFormSection
            form={wizard.form}
            technologies={wizard.technologies}
            isLoadingTechs={wizard.isLoadingTechs}
            locked={formLocked}
            onPatch={wizard.patchForm}
            onToggleTechnology={wizard.toggleTechnology}
          />

          {!wizard.project ? (
            <div className="flex flex-col items-stretch gap-3 rounded-2xl border border-border bg-card p-5 shadow-card sm:flex-row sm:items-center sm:justify-between">
              <p className="text-xs leading-relaxed text-muted-foreground">
                {t("hub.create.actions.create_help")}
              </p>
              <Button
                type="button"
                disabled={!wizard.formReady || wizard.isBusy}
                onClick={() => {
                  void wizard.createMyProject();
                }}
                className="h-11 gap-2 rounded-lg text-sm font-semibold"
              >
                <Sparkles aria-hidden className="size-4" />
                {wizard.isBusy
                  ? t("hub.create.actions.creating")
                  : t("hub.create.actions.create")}
              </Button>
            </div>
          ) : null}

          {wizard.project ? (
            <CreateProjectRepoSection
              progressStep={wizard.progressStep}
              repoReady={wizard.repoReady}
              repoEmpty={wizard.repoEmpty}
              cloneUrl={wizard.cloneUrl}
              gitCommands={wizard.gitCommands}
              forgeAccess={wizard.forgeAccess}
              forgeLogin={wizard.forgeLogin}
              hasInitialPassword={wizard.hasInitialPassword}
              isBusy={wizard.isBusy}
              isResettingPassword={wizard.isResettingPassword}
              setupFailed={wizard.setupFailed}
              initMode={wizard.initMode}
              onRetrySetup={() => {
                void wizard.createMyProject();
              }}
              onInitReadme={() => {
                void wizard.initializeWithReadme();
              }}
              onInitPush={() => {
                void wizard.choosePushExisting();
              }}
              onDismissPassword={wizard.dismissInitialPassword}
              onResetPassword={() => {
                void wizard.resetGitPassword();
              }}
            />
          ) : null}

          <CreateProjectPublishSection
            integrityConfirmed={wizard.form.integrityConfirmed}
            canPublish={wizard.canPublish}
            repoReady={wizard.repoReady}
            isBusy={wizard.isBusy}
            projectSlug={wizard.project?.slug || wizard.form.slug}
            onIntegrityChange={(value) =>
              wizard.patchForm({ integrityConfirmed: value })
            }
            onPublish={() => {
              void wizard.publish();
            }}
          />
        </div>

        <CreateProjectPreview
          form={wizard.form}
          selectedTechnologies={wizard.selectedTechnologies}
          ownerLabel={ownerLabel}
          ownerInitials={ownerInitials}
          repoReady={wizard.repoReady}
          defaultBranch={wizard.defaultBranch}
        />
      </div>
    </div>
  );
}
