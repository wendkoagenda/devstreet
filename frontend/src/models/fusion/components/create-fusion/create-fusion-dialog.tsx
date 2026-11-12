import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useFusionStore } from "../../slice";
import CreateFusionDialogContent from "./create-fusion-dialog-content";

export default function CreateFusionDialog() {
  const { isCreateDialogOpen, closeCreateDialog } = useFusionStore();

  return (
    <Dialog
      open={isCreateDialogOpen}
      onOpenChange={(open) => {
        if (!open) closeCreateDialog();
      }}
    >
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Creer Fusion</DialogTitle>
          <DialogDescription>
            Formulaire de creation de fusion
          </DialogDescription>
        </DialogHeader>
        <CreateFusionDialogContent />
      </DialogContent>
    </Dialog>
  );
}