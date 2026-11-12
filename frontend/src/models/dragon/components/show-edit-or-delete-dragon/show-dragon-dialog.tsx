import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useDragonStore } from "../../slice";
import ShowDragonDialogContent from "./show-dragon-dialog-content";
import EditDragonDialogContent from "./edit-dragon-dialog-content";
import IconAndButtonDisplayer from "@/helpers/displayers/icon-and-button-displayer";
import { useState, useEffect } from "react";
import DeleteDragonAlertDialog from "./delete-dragon-alert-dialog";
import { usePermissions } from "@/hooks/use-permissions";

function resetBodyScrollLock() {
  document.body.style.pointerEvents = "";
  document.body.style.overflow = "";
}

export default function ShowDragonDialog() {
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const {
    isShowDialogOpen,
    closeShowDialog,
    isEditMode,
    enableEditMode,
    selectedDragon,
  } = useDragonStore();
  const { canUpdateDragons, canDeleteDragons } = usePermissions();

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
                {isEditMode ? "Modifier Dragon" : "Details Dragon"}
              </DialogTitle>
              <DialogDescription>
                {isEditMode ? "Edition de l'element" : "Consultation de l'element"}
              </DialogDescription>
            </div>
          </DialogHeader>
          {!isEditMode && (
            <div className="flex gap-2">
              { canUpdateDragons && (
                <IconAndButtonDisplayer
                  type="edit"
                  text="Modifier"
                  onClick={enableEditMode}
                  variant="outline"
                />
              )}
              { canDeleteDragons && (
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
          <EditDragonDialogContent />
        ) : (
          <ShowDragonDialogContent />
        )}
        {isDeleteDialogOpen && selectedDragon && (
          <DeleteDragonAlertDialog
            dragonId={selectedDragon.id}
            onCancel={() => setIsDeleteDialogOpen(false)}
            onDeleted={handleCloseShowDialog}
          />
        )}
      </DialogContent>
    </Dialog>
  );
}