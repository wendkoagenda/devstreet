import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useDragonStore } from "../../slice";
import CreateDragonDialogContent from "./create-dragon-dialog-content";

export default function CreateDragonDialog() {
  const { isCreateDialogOpen, closeCreateDialog } = useDragonStore();

  return (
    <Dialog
      open={isCreateDialogOpen}
      onOpenChange={(open) => {
        if (!open) closeCreateDialog();
      }}
    >
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Creer Dragon</DialogTitle>
          <DialogDescription>
            Formulaire de creation de dragon
          </DialogDescription>
        </DialogHeader>
        <CreateDragonDialogContent />
      </DialogContent>
    </Dialog>
  );
}