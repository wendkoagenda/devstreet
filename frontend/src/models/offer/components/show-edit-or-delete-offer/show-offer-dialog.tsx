import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useOfferStore } from "../../slice";
import ShowOfferDialogContent from "./show-offer-dialog-content";
import EditOfferDialogContent from "./edit-offer-dialog-content";
import IconAndButtonDisplayer from "@/helpers/displayers/icon-and-button-displayer";
import { useState, useEffect } from "react";
import DeleteOfferAlertDialog from "./delete-offer-alert-dialog";
import { usePermissions } from "@/hooks/use-permissions";

function resetBodyScrollLock() {
  document.body.style.pointerEvents = "";
  document.body.style.overflow = "";
}

export default function ShowOfferDialog() {
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const {
    isShowDialogOpen,
    closeShowDialog,
    isEditMode,
    enableEditMode,
    selectedOffer,
  } = useOfferStore();
  const { canUpdateOffers, canDeleteOffers } = usePermissions();

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
                {isEditMode ? "Modifier Offer" : "Details Offer"}
              </DialogTitle>
              <DialogDescription>
                {isEditMode ? "Edition de l'element" : "Consultation de l'element"}
              </DialogDescription>
            </div>
          </DialogHeader>
          {!isEditMode && (
            <div className="flex gap-2">
              { canUpdateOffers && (
                <IconAndButtonDisplayer
                  type="edit"
                  text="Modifier"
                  onClick={enableEditMode}
                  variant="outline"
                />
              )}
              { canDeleteOffers && (
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
          <EditOfferDialogContent />
        ) : (
          <ShowOfferDialogContent />
        )}
        {isDeleteDialogOpen && selectedOffer && (
          <DeleteOfferAlertDialog
            offerId={selectedOffer.id}
            onCancel={() => setIsDeleteDialogOpen(false)}
            onDeleted={handleCloseShowDialog}
          />
        )}
      </DialogContent>
    </Dialog>
  );
}