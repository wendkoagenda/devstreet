import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useConnectionStore } from "../../slice";
import CreateConnectionDialogContent from "./create-connection-dialog-content";

export default function CreateConnectionDialog() {
  const { isCreateDialogOpen, closeCreateDialog } = useConnectionStore();

  return (
    <Dialog
      open={isCreateDialogOpen}
      onOpenChange={(open) => {
        if (!open) closeCreateDialog();
      }}
    >
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Creer Connection</DialogTitle>
          <DialogDescription>
            Formulaire de creation de connection
          </DialogDescription>
        </DialogHeader>
        <CreateConnectionDialogContent />
      </DialogContent>
    </Dialog>
  );
}