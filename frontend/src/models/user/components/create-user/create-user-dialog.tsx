import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useUserStore } from "../../slice";
import CreateUserDialogContent from "./create-user-dialog-content";
import { useTranslation } from "react-i18next";

export default function CreateUserDialog() {
  const { isCreateUserDialogOpen, closeCreateUserDialog } = useUserStore();
  const { t } = useTranslation();
  return (
    <Dialog
      open={isCreateUserDialogOpen}
      onOpenChange={(open) => {
        if (!open) closeCreateUserDialog();
      }}
    >
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>{t("create_user_form_title")}</DialogTitle>
          <DialogDescription>
            {t("create_user_form_description")}
          </DialogDescription>
        </DialogHeader>
        <CreateUserDialogContent />
      </DialogContent>
    </Dialog>
  );
}
