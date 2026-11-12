import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useGadoStore } from "../../slice";
import CreateGadoDialogContent from "./create-gado-dialog-content";

export default function CreateGadoDialog() {
  const { isCreateDialogOpen, closeCreateDialog } = useGadoStore();

  return (
    <Dialog
      open={isCreateDialogOpen}
      onOpenChange={(open) => {
        if (!open) closeCreateDialog();
      }}
    >
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Creer Gado</DialogTitle>
          <DialogDescription>
            Formulaire de creation de gado
          </DialogDescription>
        </DialogHeader>
        <CreateGadoDialogContent />
      </DialogContent>
    </Dialog>
  );
}