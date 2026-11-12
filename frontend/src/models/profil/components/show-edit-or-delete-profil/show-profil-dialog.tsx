import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useProfilStore } from "../../slice";
import ShowProfilDialogContent from "./show-profil-dialog-content";
import EditProfilDialogContent from "./edit-profil-dialog-content";
import IconAndButtonDisplayer from "@/helpers/displayers/icon-and-button-displayer";
import { useState, useEffect } from "react";
import DeleteProfilAlertDialog from "./delete-profil-alert-dialog";
import { usePermissions } from "@/hooks/use-permissions";

function resetBodyScrollLock() {
  document.body.style.pointerEvents = "";
  document.body.style.overflow = "";
}

export default function ShowProfilDialog() {
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const {
    isShowDialogOpen,
    closeShowDialog,
    isEditMode,
    enableEditMode,
    selectedProfil,
  } = useProfilStore();
  const { canUpdateProfils, canDeleteProfils } = usePermissions();

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
                {isEditMode ? "Modifier Profil" : "Details Profil"}
              </DialogTitle>
              <DialogDescription>
                {isEditMode ? "Edition de l'element" : "Consultation de l'element"}
              </DialogDescription>
            </div>
          </DialogHeader>
          {!isEditMode && (
            <div className="flex gap-2">
              { canUpdateProfils && (
                <IconAndButtonDisplayer
                  type="edit"
                  text="Modifier"
                  onClick={enableEditMode}
                  variant="outline"
                />
              )}
              { canDeleteProfils && (
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
          <EditProfilDialogContent />
        ) : (
          <ShowProfilDialogContent />
        )}
        {isDeleteDialogOpen && selectedProfil && (
          <DeleteProfilAlertDialog
            profilId={selectedProfil.id}
            onCancel={() => setIsDeleteDialogOpen(false)}
            onDeleted={handleCloseShowDialog}
          />
        )}
      </DialogContent>
    </Dialog>
  );
}