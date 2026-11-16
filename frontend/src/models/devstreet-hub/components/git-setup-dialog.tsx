import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { GitSetupCommandsPanel } from "./git-setup-commands-panel";
import type { useGitComputerSetup } from "../hooks/use-git-computer-setup";

type GitSetupState = ReturnType<typeof useGitComputerSetup>;

interface GitSetupDialogProps {
  open: boolean;
  setup: GitSetupState;
  onOpenChange: (open: boolean) => void;
  /** Soft gate : l'utilisateur confirme avoir collé la config. */
  onContinue: () => void;
}

/**
 * Modal « Relier cet ordinateur » affichée à la création de dépôt si aucun PAT actif.
 */
export function GitSetupDialog({
  open,
  setup,
  onOpenChange,
  onContinue,
}: GitSetupDialogProps) {
  const { t } = useTranslation();

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] max-w-lg overflow-y-auto sm:max-w-xl">
        <DialogHeader>
          <DialogTitle>{t("hub.git_setup.dialog_title")}</DialogTitle>
          <DialogDescription>
            {t("hub.git_setup.dialog_description")}
          </DialogDescription>
        </DialogHeader>

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
          showPageLink
          compact
        />

        <DialogFooter className="flex-col gap-2 sm:flex-row sm:justify-between">
          <Button asChild type="button" variant="outline" className="h-9 text-xs">
            <Link to="/hub/git-setup">{t("hub.git_setup.open_page")}</Link>
          </Button>
          <Button
            type="button"
            className="h-9 text-xs font-semibold"
            onClick={onContinue}
          >
            {t("hub.git_setup.continue")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
