import { Check, Copy, ExternalLink, KeyRound, Shield, Terminal } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { ForgeAccess } from "../schema";
import type { WizardStep } from "../hooks/use-create-project";

interface CreateProjectRepoSectionProps {
  activeStep: WizardStep;
  repoReady: boolean;
  cloneUrl: string | null;
  browseUrl: string | null;
  gitCommands: string | null;
  forgeAccess: ForgeAccess | null;
  forgeLogin: string | null;
  hasInitialPassword: boolean;
  isBusy: boolean;
  canPrepare: boolean;
  provisionFailed: boolean;
  onPrepare: () => void;
  onDismissPassword: () => void;
}

async function copyText(value: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(value);
    return true;
  } catch {
    return false;
  }
}

export function CreateProjectRepoSection({
  activeStep,
  repoReady,
  cloneUrl,
  browseUrl,
  gitCommands,
  forgeAccess,
  forgeLogin,
  hasInitialPassword,
  isBusy,
  canPrepare,
  provisionFailed,
  onPrepare,
  onDismissPassword,
}: CreateProjectRepoSectionProps) {
  const { t } = useTranslation();
  const [copiedUrl, setCopiedUrl] = useState(false);
  const [copiedCli, setCopiedCli] = useState(false);
  const [copiedPassword, setCopiedPassword] = useState(false);
  const focused = activeStep === 2;
  const initialPassword = forgeAccess?.initial_password ?? null;

  const handleCopyUrl = async () => {
    if (!cloneUrl) return;
    const ok = await copyText(cloneUrl);
    if (ok) {
      setCopiedUrl(true);
      window.setTimeout(() => setCopiedUrl(false), 1800);
    }
  };

  const handleCopyCli = async () => {
    if (!gitCommands) return;
    const ok = await copyText(gitCommands);
    if (ok) {
      setCopiedCli(true);
      window.setTimeout(() => setCopiedCli(false), 1800);
    }
  };

  const handleCopyPassword = async () => {
    if (!initialPassword) return;
    const ok = await copyText(initialPassword);
    if (ok) {
      setCopiedPassword(true);
      window.setTimeout(() => setCopiedPassword(false), 1800);
    }
  };

  return (
    <section
      aria-labelledby="create-step-2-title"
      className={cn(
        "relative flex flex-col gap-6 overflow-hidden rounded-2xl border bg-card p-6 shadow-card sm:p-7",
        focused ? "border-2 border-brand/40 shadow-card-hover" : "border-border"
      )}
    >
      <div className="pointer-events-none absolute -right-20 -top-20 h-48 w-48 rounded-full bg-brand/10 blur-3xl" />

      <div className="flex flex-col justify-between gap-3 border-b border-border pb-4 sm:flex-row sm:items-center">
        <div className="flex items-center gap-3">
          <div
            className={cn(
              "flex h-7 w-7 items-center justify-center rounded-md text-xs font-bold",
              focused ? "bg-brand text-brand-foreground" : "bg-secondary text-foreground"
            )}
          >
            2
          </div>
          <div className="flex flex-col">
            <h2 className="text-base font-bold text-foreground" id="create-step-2-title">
              {t("hub.create.sections.repository")}
            </h2>
            <span className="text-xs text-muted-foreground">
              {t("hub.create.sections.repository_hint")}
            </span>
          </div>
        </div>
        <div
          className={cn(
            "inline-flex items-center gap-1.5 self-start rounded-full border px-3 py-1 text-xs font-medium sm:self-auto",
            repoReady
              ? "border-success/30 bg-success/10 text-success"
              : "border-border bg-secondary text-muted-foreground"
          )}
        >
          <span
            className={cn(
              "h-2 w-2 rounded-full",
              repoReady ? "animate-pulse bg-success" : "bg-muted-foreground/50"
            )}
          />
          {repoReady
            ? t("hub.create.repo.status_ready")
            : t("hub.create.repo.status_pending")}
        </div>
      </div>

      {!repoReady ? (
        <div className="flex flex-col gap-3 rounded-xl border border-dashed border-border bg-secondary/50 p-4">
          <p className="text-xs leading-relaxed text-muted-foreground">
            {provisionFailed
              ? t("hub.create.repo.retry_help")
              : t("hub.create.repo.prepare_help")}
          </p>
          <Button
            type="button"
            onClick={onPrepare}
            disabled={!canPrepare || isBusy}
            className="h-9 w-full gap-2 rounded-lg text-xs font-semibold sm:w-auto"
          >
            {isBusy
              ? t("hub.create.repo.preparing")
              : provisionFailed
                ? t("hub.create.repo.retry")
                : t("hub.create.repo.prepare")}
          </Button>
        </div>
      ) : null}

      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between gap-2">
          <span className="text-xs font-semibold text-foreground">
            {t("hub.create.repo.remote_url")}
          </span>
          <span className="text-[11px] text-muted-foreground">
            {t("hub.create.repo.https")}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex h-11 min-w-0 flex-1 items-center justify-between overflow-hidden rounded-lg border border-primary/20 bg-primary px-3.5 text-xs text-primary-foreground sm:text-sm">
            <span className="truncate select-all">
              {cloneUrl || t("hub.create.repo.url_placeholder")}
            </span>
          </div>
          <Button
            type="button"
            variant="secondary"
            disabled={!cloneUrl}
            onClick={handleCopyUrl}
            className="h-11 shrink-0 gap-2 rounded-lg text-xs font-semibold"
          >
            {copiedUrl ? <Check aria-hidden className="size-4" /> : <Copy aria-hidden className="size-4" />}
            {copiedUrl ? t("hub.create.repo.copied") : t("hub.create.repo.copy_url")}
          </Button>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between gap-2">
          <span className="flex items-center gap-1.5 text-xs font-semibold text-foreground">
            <Terminal aria-hidden className="size-4 text-muted-foreground" />
            {t("hub.create.repo.cli_title")}
          </span>
          {gitCommands ? (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleCopyCli}
              className="h-7 gap-1 text-xs text-brand"
            >
              {copiedCli ? t("hub.create.repo.copied") : t("hub.create.repo.copy_cli")}
            </Button>
          ) : null}
        </div>
        {gitCommands ? (
          <div className="flex flex-col gap-2 rounded-xl border border-primary/20 bg-primary p-4 text-xs text-primary-foreground shadow-md">
            <div className="flex items-center justify-between border-b border-primary-foreground/10 pb-2 text-[11px] text-primary-foreground/60">
              <span className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-full bg-destructive/80" />
                <span className="h-2.5 w-2.5 rounded-full bg-warning/80" />
                <span className="h-2.5 w-2.5 rounded-full bg-success/80" />
                <span className="ml-2 font-medium">{t("hub.create.repo.terminal")}</span>
              </span>
            </div>
            <pre className="overflow-x-auto whitespace-pre-wrap py-1 font-sans leading-relaxed text-primary-foreground/90">
              {gitCommands}
            </pre>
          </div>
        ) : (
          <p className="rounded-xl border border-dashed border-border bg-secondary/40 px-4 py-3 text-xs text-muted-foreground">
            {t("hub.create.repo.cli_waiting")}
          </p>
        )}
      </div>

      <div className="flex items-start gap-3 rounded-xl border border-warning/30 bg-warning-soft/80 p-4">
        <Shield aria-hidden className="mt-0.5 size-5 shrink-0 text-warning" />
        <div className="flex flex-col gap-0.5 text-xs leading-relaxed text-foreground">
          <strong className="font-semibold">{t("hub.create.repo.security_title")}</strong>
          <span className="text-muted-foreground">{t("hub.create.repo.security_text")}</span>
        </div>
      </div>

      <div className="flex items-start gap-3.5 rounded-xl border border-border bg-secondary p-4">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <KeyRound aria-hidden className="size-4" />
        </div>
        <div className="flex flex-col gap-1 text-xs">
          <span className="font-semibold text-foreground">
            {t("hub.create.repo.auth_title")}
          </span>
          <p className="leading-relaxed text-muted-foreground">
            {t("hub.create.repo.auth_text", {
              login: forgeLogin ? `@${forgeLogin}` : t("hub.create.preview.you"),
            })}
          </p>
          {browseUrl ? (
            <Button
              asChild
              variant="outline"
              className="mt-2 h-8 w-fit gap-1.5 rounded-lg text-xs"
            >
              <a href={browseUrl} target="_blank" rel="noopener noreferrer">
                <ExternalLink aria-hidden className="size-3.5" />
                {t("hub.create.repo.open_forge")}
              </a>
            </Button>
          ) : null}
        </div>
      </div>

      {hasInitialPassword && initialPassword ? (
        <div
          role="dialog"
          aria-labelledby="forge-password-title"
          className="flex flex-col gap-3 rounded-xl border border-warning/40 bg-warning-soft p-4"
        >
          <div className="flex items-start gap-3">
            <KeyRound aria-hidden className="mt-0.5 size-5 shrink-0 text-warning" />
            <div className="min-w-0 flex-1">
              <h3
                id="forge-password-title"
                className="text-sm font-bold text-foreground"
              >
                {t("hub.create.repo.password_panel_title")}
              </h3>
              <p className="mt-1 text-xs text-muted-foreground">
                {forgeAccess?.password_recovery_required
                  ? t("hub.create.repo.password_recovery_text")
                  : t("hub.create.repo.password_panel_text")}
              </p>
              <p className="mt-3 break-all rounded-md border border-border bg-card px-3 py-2 font-sans text-sm font-semibold text-foreground">
                {initialPassword}
              </p>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant="secondary"
              className="h-8 gap-1.5 text-xs"
              onClick={handleCopyPassword}
            >
              {copiedPassword ? (
                <Check aria-hidden className="size-3.5" />
              ) : (
                <Copy aria-hidden className="size-3.5" />
              )}
              {copiedPassword
                ? t("hub.create.repo.copied")
                : t("hub.create.repo.copy_password")}
            </Button>
            {browseUrl ? (
              <Button asChild variant="outline" className="h-8 gap-1.5 text-xs">
                <a href={browseUrl} target="_blank" rel="noopener noreferrer">
                  <ExternalLink aria-hidden className="size-3.5" />
                  {t("hub.create.repo.change_password")}
                </a>
              </Button>
            ) : null}
            <Button
              type="button"
              className="h-8 text-xs"
              onClick={onDismissPassword}
            >
              {t("hub.create.repo.password_dismiss")}
            </Button>
          </div>
        </div>
      ) : null}
    </section>
  );
}
