import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { usePrestationStore } from "../../slice";
import CreatePrestationDialogContent from "./create-prestation-dialog-content";

export default function CreatePrestationDialog() {
  const { isCreateDialogOpen, closeCreateDialog } = usePrestationStore();

  return (
    <Dialog
      open={isCreateDialogOpen}
      onOpenChange={(open) => {
        if (!open) closeCreateDialog();
      }}
    >
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Creer Prestation</DialogTitle>
          <DialogDescription>
            Formulaire de creation de prestation
          </DialogDescription>
        </DialogHeader>
        <CreatePrestationDialogContent />
      </DialogContent>
    </Dialog>
  );
}