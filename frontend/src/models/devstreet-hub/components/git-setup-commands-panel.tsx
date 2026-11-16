import { Check, Copy, Laptop, RefreshCw } from "lucide-react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface GitSetupCommandsPanelProps {
  commands: string[];
  isLoadingConfig: boolean;
  isErrorConfig: boolean;
  copied: boolean;
  onCopy: () => void;
  onRetryConfig?: () => void;
  /** Affiche le lien vers la page dédiée (masqué si on y est déjà). */
  showPageLink?: boolean;
  compact?: boolean;
  className?: string;
}

/**
 * Bloc réutilisable : étapes + commandes git config + bouton copier.
 */
export function GitSetupCommandsPanel({
  commands,
  isLoadingConfig,
  isErrorConfig,
  copied,
  onCopy,
  onRetryConfig,
  showPageLink = true,
  compact = false,
  className,
}: GitSetupCommandsPanelProps) {
  const { t } = useTranslation();
  const steps = [
    t("hub.create.repo.git_setup_step_git"),
    t("hub.create.repo.git_setup_step_config"),
    t("hub.create.repo.git_setup_step_push"),
  ];

  return (
    <div className={cn("flex flex-col gap-4", className)}>
      <div className="flex items-start gap-3">
        <span className="mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-lg bg-brand/10 text-brand">
          <Laptop aria-hidden className="size-4" />
        </span>
        <div className="min-w-0">
          <p className="text-sm font-semibold text-foreground">
            {compact
              ? t("hub.create.repo.git_setup_title_short")
              : t("hub.create.repo.git_setup_title")}
          </p>
          <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
            {compact
              ? t("hub.create.repo.git_setup_text_short")
              : t("hub.create.repo.git_setup_text")}
          </p>
        </div>
      </div>

      <ol className="flex list-decimal flex-col gap-1.5 pl-5 text-xs text-muted-foreground">
        {steps.map((step) => (
          <li key={step}>{step}</li>
        ))}
      </ol>

      {isLoadingConfig ? (
        <p className="text-xs text-muted-foreground">
          {t("hub.create.repo.git_setup_loading")}
        </p>
      ) : isErrorConfig ? (
        <div className="flex flex-col gap-2">
          <p className="text-xs text-destructive">
            {t("hub.git_setup.config_error")}
          </p>
          {onRetryConfig ? (
            <Button
              type="button"
              variant="outline"
              className="h-8 w-fit gap-1.5 text-xs"
              onClick={onRetryConfig}
            >
              <RefreshCw aria-hidden className="size-3.5" />
              {t("common.retry", "Réessayer")}
            </Button>
          ) : null}
        </div>
      ) : (
        <>
          <pre className="max-h-48 overflow-auto rounded-lg border border-border bg-muted/40 p-3 font-mono text-[11px] leading-relaxed text-foreground whitespace-pre-wrap break-all">
            {commands.length > 0
              ? commands.join("\n")
              : t("hub.git_setup.config_empty")}
          </pre>
          <div className="flex flex-wrap items-center gap-2">
            <Button
              type="button"
              className="h-9 gap-1.5 text-xs font-semibold"
              disabled={commands.length === 0}
              onClick={onCopy}
            >
              {copied ? (
                <Check aria-hidden className="size-3.5" />
              ) : (
                <Copy aria-hidden className="size-3.5" />
              )}
              {copied
                ? t("hub.create.repo.copied")
                : t("hub.create.repo.copy_git_config")}
            </Button>
            {showPageLink ? (
              <Button asChild type="button" variant="ghost" className="h-9 text-xs">
                <Link to="/hub/git-setup">{t("hub.git_setup.open_page")}</Link>
              </Button>
            ) : null}
          </div>
        </>
      )}
    </div>
  );
}
