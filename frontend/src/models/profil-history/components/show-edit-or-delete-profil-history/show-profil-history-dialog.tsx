import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useProfilHistoryStore } from "../../slice";
import ShowProfilHistoryDialogContent from "./show-profil-history-dialog-content";
import EditProfilHistoryDialogContent from "./edit-profil-history-dialog-content";
import IconAndButtonDisplayer from "@/helpers/displayers/icon-and-button-displayer";
import { useState, useEffect } from "react";
import DeleteProfilHistoryAlertDialog from "./delete-profil-history-alert-dialog";
import { usePermissions } from "@/hooks/use-permissions";

function resetBodyScrollLock() {
  document.body.style.pointerEvents = "";
  document.body.style.overflow = "";
}

export default function ShowProfilHistoryDialog() {
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const {
    isShowDialogOpen,
    closeShowDialog,
    isEditMode,
    enableEditMode,
    selectedProfilHistory,
  } = useProfilHistoryStore();
  const { canUpdateProfilHistories, canDeleteProfilHistories } = usePermissions();

  useEffect(() => {
    if (!isShowDialogOpen) {
      setIsDeleteDialogOpen(false);
    }
  }, [isShowDialogOpen]);

  useEffect(() => {
    if (!isShowDialogOpen && !isDeleteDialogOpen) {
      resetBodyScrollLock();
    }
  }, [isShowDialogOpen, isDeleteDialogOpen]);

  useEffect(() => {
    return () => {
      resetBodyScrollLock();
    };
  }, []);

  const handleCloseShowDialog = () => {
    setIsDeleteDialogOpen(false);
    closeShowDialog();
    resetBodyScrollLock();
  };

  return (
    <Dialog
      open={isShowDialogOpen}
      onOpenChange={(open) => {
        if (!open && !isDeleteDialogOpen) {
          handleCloseShowDialog();
        }
      }}
    >
      <DialogContent
        className="max-w-4xl"
        onInteractOutside={(event) => {
          if (isDeleteDialogOpen) {
            event.preventDefault();
          }
        }}
        onEscapeKeyDown={(event) => {
          if (isDeleteDialogOpen) {
            event.preventDefault();
          }
        }}
      >
        <div className="flex justify-between items-start">
          <DialogHeader>
            <div>
              <DialogTitle>
                {isEditMode ? "Modifier ProfilHistory" : "Details ProfilHistory"}
              </DialogTitle>
              <DialogDescription>
                {isEditMode ? "Edition de l'element" : "Consultation de l'element"}
              </DialogDescription>
            </div>
          </DialogHeader>
          {!isEditMode && (
            <div className="flex gap-2">
              { canUpdateProfilHistories && (
                <IconAndButtonDisplayer
                  type="edit"
                  text="Modifier"
                  onClick={enableEditMode}
                  variant="outline"
                />
              )}
              { canDeleteProfilHistories && (
                <IconAndButtonDisplayer
                  type="delete"
                  text="Supprimer"
                  onClick={() => setIsDeleteDialogOpen(true)}
                  variant="destructive"
                />
              )}
            </div>
          )}
        </div>
        {isEditMode ? (
          <EditProfilHistoryDialogContent />
        ) : (
          <ShowProfilHistoryDialogContent />
        )}
        {isDeleteDialogOpen && selectedProfilHistory && (
          <DeleteProfilHistoryAlertDialog
            profilHistoryId={selectedProfilHistory.id}
            onCancel={() => setIsDeleteDialogOpen(false)}
            onDeleted={handleCloseShowDialog}
          />
        )}
      </DialogContent>
    </Dialog>
  );
}