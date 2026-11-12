import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useTranslation } from "react-i18next";
import { useChangePasswordDialogStore } from "../../slice";
import ChangePasswordDialogContent from "./change-password-dialog-content";

export default function ChangePasswordDialog() {
  const { isChangePasswordDialogOpen, closeChangePasswordDialog } =
    useChangePasswordDialogStore();
  const { t } = useTranslation();

  return (
    <Dialog
      open={isChangePasswordDialogOpen}
      onOpenChange={(open) => {
        if (!open) closeChangePasswordDialog();
      }}
    >
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>{t("change_password.title")}</DialogTitle>
        </DialogHeader>
        <DialogDescription className="text-md text-destructive">
          {t("change_password.description")}
        </DialogDescription>
        <ChangePasswordDialogContent />
      </DialogContent>
    </Dialog>
  );
}
