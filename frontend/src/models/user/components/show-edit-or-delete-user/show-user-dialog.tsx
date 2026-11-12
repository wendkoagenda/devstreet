import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useUserStore } from "../../slice";
import ShowUserDialogContent from "./show-user-dialog-content";
import EditUserDialogContent from "./edit-user-dialog-content";
import { useTranslation } from "react-i18next";
import IconAndButtonDisplayer from "@/helpers/displayers/icon-and-button-displayer";
import { useState } from "react";
import DeleteUserAlertDialog from "./delete-user-alert-dialog";
import { usePermissions } from "@/hooks/use-permissions";

export default function ShowUserDialog() {
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const {
    isShowUserDialogOpen,
    closeShowUserDialog,
    isEditMode,
    enableEditMode,
  } = useUserStore();
  const { t } = useTranslation();

  const { canUpdateUsers, canDeleteUsers } = usePermissions();

  return (
    <>
      <Dialog
        open={isShowUserDialogOpen}
        onOpenChange={(open) => {
          if (!open) closeShowUserDialog();
        }}
      >
        <DialogContent className="max-w-4xl">
          <div className="flex justify-between items-start">
            <DialogHeader className="">
              <div>
                <DialogTitle>
                  {isEditMode
                    ? t("edit_user_form_title")
                    : t("show_user_form_title")}
                </DialogTitle>
                <DialogDescription>
                  {isEditMode
                    ? t("edit_user_form_description")
                    : t("show_user_form_description")}
                </DialogDescription>
              </div>
            </DialogHeader>
            <div className="flex justify-end items-end">
              {!isEditMode && (
                <div className="flex gap-2">
                  {canUpdateUsers && (
                    <IconAndButtonDisplayer
                      type="edit"
                      text={t("edit")}
                      onClick={enableEditMode}
                      variant="outline"
                    />
                  )}

                  {canDeleteUsers && (
                    <IconAndButtonDisplayer
                      type="delete"
                      text={t("delete")}
                      onClick={() => setIsDeleteDialogOpen(true)}
                      variant="destructive"
                    />
                  )}
                </div>
              )}
            </div>
          </div>
          {isEditMode ? <EditUserDialogContent /> : <ShowUserDialogContent />}
        </DialogContent>
      </Dialog>
      <DeleteUserAlertDialog
        isOpen={isDeleteDialogOpen}
        onOpenChange={setIsDeleteDialogOpen}
      />
    </>
  );
}
