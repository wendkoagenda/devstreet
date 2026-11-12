import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useGadoStore } from "../../slice";
import ShowGadoDialogContent from "./show-gado-dialog-content";
import EditGadoDialogContent from "./edit-gado-dialog-content";
import IconAndButtonDisplayer from "@/helpers/displayers/icon-and-button-displayer";
import { useState, useEffect } from "react";
import DeleteGadoAlertDialog from "./delete-gado-alert-dialog";
import { usePermissions } from "@/hooks/use-permissions";

function resetBodyScrollLock() {
  document.body.style.pointerEvents = "";
  document.body.style.overflow = "";
}

export default function ShowGadoDialog() {
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const {
    isShowDialogOpen,
    closeShowDialog,
    isEditMode,
    enableEditMode,
    selectedGado,
  } = useGadoStore();
  const { canUpdateGados, canDeleteGados } = usePermissions();

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
                {isEditMode ? "Modifier Gado" : "Details Gado"}
              </DialogTitle>
              <DialogDescription>
                {isEditMode ? "Edition de l'element" : "Consultation de l'element"}
              </DialogDescription>
            </div>
          </DialogHeader>
          {!isEditMode && (
            <div className="flex gap-2">
              { canUpdateGados && (
                <IconAndButtonDisplayer
                  type="edit"
                  text="Modifier"
                  onClick={enableEditMode}
                  variant="outline"
                />
              )}
              { canDeleteGados && (
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
          <EditGadoDialogContent />
        ) : (
          <ShowGadoDialogContent />
        )}
        {isDeleteDialogOpen && selectedGado && (
          <DeleteGadoAlertDialog
            gadoId={selectedGado.id}
            onCancel={() => setIsDeleteDialogOpen(false)}
            onDeleted={handleCloseShowDialog}
          />
        )}
      </DialogContent>
    </Dialog>
  );
}