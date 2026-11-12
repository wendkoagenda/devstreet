import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useOfferStore } from "../../slice";
import CreateOfferDialogContent from "./create-offer-dialog-content";

export default function CreateOfferDialog() {
  const { isCreateDialogOpen, closeCreateDialog } = useOfferStore();

  return (
    <Dialog
      open={isCreateDialogOpen}
      onOpenChange={(open) => {
        if (!open) closeCreateDialog();
      }}
    >
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Creer Offer</DialogTitle>
          <DialogDescription>
            Formulaire de creation de offer
          </DialogDescription>
        </DialogHeader>
        <CreateOfferDialogContent />
      </DialogContent>
    </Dialog>
  );
}