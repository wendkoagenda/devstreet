import { ArrowLeft, LogIn } from "lucide-react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { ConnectedComputersSection } from "../components/connected-computers-section";
import { GitSetupCommandsPanel } from "../components/git-setup-commands-panel";
import { useGitComputerSetup } from "../hooks/use-git-computer-setup";
import { useHubAccess } from "../hooks/use-hub-access";

/**
 * Interface dédiée : config GCM une fois + liste des ordinateurs autorisés.
 */
export default function GitSetupPage() {
  const { t } = useTranslation();
  const { isAuthenticated, requestLogin } = useHubAccess();
  const setup = useGitComputerSetup({ skip: !isAuthenticated });

  if (!isAuthenticated) {
    return (
      <div className="mx-auto w-full max-w-lg py-10">
        <section className="flex flex-col items-center rounded-xl border border-dashed border-input bg-card px-6 py-14 text-center shadow-sm">
          <h1 className="mb-2 text-xl font-bold text-foreground">
            {t("hub.git_setup.page_title")}
          </h1>
          <p className="mb-6 max-w-md text-sm text-muted-foreground">
            {t("hub.git_setup.login_required")}
          </p>
          <Button
            type="button"
            onClick={requestLogin}
            className="h-9 gap-1.5 rounded-lg text-xs font-semibold"
          >
            <LogIn aria-hidden className="size-4" />
            {t("hub.common.login")}
          </Button>
        </section>
      </div>
    );
  }

  return (
    <div className="mx-auto flex w-full max-w-2xl flex-col gap-8 py-6 sm:py-8">
      <div className="flex flex-col gap-3">
        <Button
          asChild
          type="button"
          variant="ghost"
          className="h-8 w-fit gap-1.5 px-2 text-xs text-muted-foreground"
        >
          <Link to="/hub/projects">
            <ArrowLeft aria-hidden className="size-3.5" />
            {t("hub.git_setup.back_hub")}
          </Link>
        </Button>
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            {t("hub.git_setup.page_title")}
          </h1>
          <p className="mt-1.5 max-w-xl text-sm text-muted-foreground">
            {t("hub.git_setup.page_subtitle")}
          </p>
        </div>
      </div>

      <section className="rounded-2xl border border-border bg-card p-5 sm:p-6">
        <GitSetupCommandsPanel
          commands={setup.commands}
          isLoadingConfig={setup.isLoadingConfig}
          isErrorConfig={setup.isErrorConfig}
          copied={setup.copied}
          onCopy={() => {
            void setup.copyCommands();
          }}
          onRetryConfig={() => {
            void setup.refetchConfig();
          }}
          showPageLink={false}
        />
        {setup.needsLink ? (
          <p className="mt-4 rounded-lg border border-dashed border-brand/40 bg-brand/5 px-3 py-2 text-xs text-muted-foreground">
            {t("hub.git_setup.no_computer_yet")}
          </p>
        ) : (
          <p className="mt-4 text-xs text-muted-foreground">
            {t("hub.git_setup.has_computers", { count: setup.activeCount })}
          </p>
        )}
      </section>

      <ConnectedComputersSection showSetupLink={false} />
    </div>
  );
}
