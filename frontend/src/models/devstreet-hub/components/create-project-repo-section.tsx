import { Check, Copy, Sparkles } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import type { ForgeAccess } from "../schema";
import type { ProgressStep } from "../hooks/use-create-project";
import { copyText } from "@/helpers/clipboard";

interface CreateProjectRepoSectionProps {
  progressStep: ProgressStep;
  repoReady: boolean;
  repoEmpty: boolean;
  cloneUrl: string | null;
  gitCommands: string | null;
  forgeAccess: ForgeAccess | null;
  forgeLogin: string | null;
  repoName: string | null;
  projectSlug: string | null;
  hasInitialPassword: boolean;
  isBusy: boolean;
  isResettingPassword: boolean;
  setupFailed: boolean;
  initMode: "readme" | "push_existing" | null;
  onRetrySetup: () => void;
  onInitReadme: () => void;
  onInitPush: () => void;
  onDismissPassword: () => void;
  onResetPassword: () => void;
  onFinalize: (options: { publishAutomatically: boolean }) => void;
}

export function CreateProjectRepoSection({
  progressStep,
  repoReady,
  cloneUrl,
  forgeLogin,
  repoName,
  projectSlug,
  isBusy,
  setupFailed,
  onRetrySetup,
  onFinalize,
}: CreateProjectRepoSectionProps) {
  const { t } = useTranslation();
  const [copiedUrl, setCopiedUrl] = useState(false);
  const [publishAutomatically, setPublishAutomatically] = useState(false);
  const focused =
    progressStep === "identity" ||
    progressStep === "repository" ||
    progressStep === "init";
  const forgePath =
    forgeLogin && repoName ? `@${forgeLogin}/${repoName}` : null;
  const nameCollision = Boolean(
    projectSlug && repoName && projectSlug !== repoName
  );

  const handleCopyUrl = async () => {
    if (!cloneUrl) return;
    if (await copyText(cloneUrl)) {
      setCopiedUrl(true);
      window.setTimeout(() => setCopiedUrl(false), 1600);
    }
  };

  return (
    <section
      aria-labelledby="create-repo-title"
      className={cn(
        "flex flex-col gap-4 rounded-2xl border bg-card p-5 sm:p-6",
        focused ? "border-brand/40" : "border-border"
      )}
    >
      <div className="flex items-center justify-between gap-3">
        <h2
          className="text-sm font-bold text-foreground sm:text-base"
          id="create-repo-title"
        >
          {t("hub.create.sections.repository")}
        </h2>
        <span
          className={cn(
            "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[11px] font-medium",
            repoReady
              ? "bg-success/10 text-success"
              : "bg-secondary text-muted-foreground"
          )}
        >
          <span
            className={cn(
              "h-1.5 w-1.5 rounded-full",
              repoReady ? "bg-success" : "bg-muted-foreground/50"
            )}
          />
          {repoReady
            ? t("hub.create.repo.status_ready")
            : t("hub.create.repo.status_pending")}
        </span>
      </div>

      {!repoReady ? (
        <div className="flex flex-col gap-2 rounded-lg border border-dashed border-border bg-secondary/40 px-3 py-3">
          <p className="text-xs text-muted-foreground">
            {setupFailed
              ? t("hub.create.repo.retry_help")
              : t("hub.create.repo.waiting_help")}
          </p>
          {setupFailed ? (
            <Button
              type="button"
              onClick={onRetrySetup}
              disabled={isBusy}
              className="h-8 w-fit text-xs font-semibold"
            >
              {isBusy ? t("hub.create.repo.preparing") : t("hub.create.repo.retry")}
            </Button>
          ) : null}
        </div>
      ) : (
        <>
          <div className="flex flex-col gap-1.5">
            {forgePath ? (
              <code className="truncate font-sans text-xs font-semibold text-foreground">
                {forgePath}
              </code>
            ) : null}
            {nameCollision ? (
              <p className="text-[11px] text-muted-foreground">
                {t("hub.create.repo.forge_path_collision")}
              </p>
            ) : null}
            <div className="flex items-center gap-2">
              <div className="flex h-9 min-w-0 flex-1 items-center overflow-hidden rounded-md border border-border bg-muted/40 px-3 text-[11px] text-foreground sm:text-xs">
                <span className="truncate select-all">
                  {cloneUrl || t("hub.create.repo.url_placeholder")}
                </span>
              </div>
              <Button
                type="button"
                variant="secondary"
                disabled={!cloneUrl}
                onClick={handleCopyUrl}
                className="h-9 shrink-0 gap-1.5 px-3 text-xs"
              >
                {copiedUrl ? (
                  <Check aria-hidden className="size-3.5" />
                ) : (
                  <Copy aria-hidden className="size-3.5" />
                )}
                {copiedUrl
                  ? t("hub.create.repo.copied")
                  : t("hub.create.repo.copy_url")}
              </Button>
            </div>
          </div>

          <p className="text-xs text-muted-foreground">
            {t("hub.create.repo.finalize_hint")}
          </p>

          <div className="flex items-start gap-2">
            <Checkbox
              id="create-publish-automatically"
              checked={publishAutomatically}
              disabled={isBusy}
              onCheckedChange={(value) =>
                setPublishAutomatically(value === true)
              }
            />
            <Label
              htmlFor="create-publish-automatically"
              className="cursor-pointer text-xs font-normal leading-5 text-muted-foreground"
            >
              {t("hub.create.repo.publish_automatically")}
            </Label>
          </div>

          <Button
            type="button"
            disabled={isBusy}
            onClick={() => onFinalize({ publishAutomatically })}
            className="h-10 w-full gap-2 text-sm font-semibold sm:w-fit"
          >
            <Sparkles aria-hidden className="size-4" />
            {t("hub.create.actions.finalize")}
          </Button>
        </>
      )}
    </section>
  );
}
