import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useElitestyStore } from "../../slice";
import CreateElitestyDialogContent from "./create-elitesty-dialog-content";

export default function CreateElitestyDialog() {
  const { isCreateDialogOpen, closeCreateDialog } = useElitestyStore();

  return (
    <Dialog
      open={isCreateDialogOpen}
      onOpenChange={(open) => {
        if (!open) closeCreateDialog();
      }}
    >
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Creer Elitesty</DialogTitle>
          <DialogDescription>
            Formulaire de creation de elitesty
          </DialogDescription>
        </DialogHeader>
        <CreateElitestyDialogContent />
      </DialogContent>
    </Dialog>
  );
}