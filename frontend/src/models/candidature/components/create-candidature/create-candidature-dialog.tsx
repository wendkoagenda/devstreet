import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useCandidatureStore } from "../../slice";
import CreateCandidatureDialogContent from "./create-candidature-dialog-content";

export default function CreateCandidatureDialog() {
  const { isCreateDialogOpen, closeCreateDialog } = useCandidatureStore();

  return (
    <Dialog
      open={isCreateDialogOpen}
      onOpenChange={(open) => {
        if (!open) closeCreateDialog();
      }}
    >
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Creer Candidature</DialogTitle>
          <DialogDescription>
            Formulaire de creation de candidature
          </DialogDescription>
        </DialogHeader>
        <CreateCandidatureDialogContent />
      </DialogContent>
    </Dialog>
  );
}