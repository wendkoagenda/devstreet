import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useExperienceStore } from "../../slice";
import CreateExperienceDialogContent from "./create-experience-dialog-content";

export default function CreateExperienceDialog() {
  const { isCreateDialogOpen, closeCreateDialog } = useExperienceStore();

  return (
    <Dialog
      open={isCreateDialogOpen}
      onOpenChange={(open) => {
        if (!open) closeCreateDialog();
      }}
    >
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Creer Experience</DialogTitle>
          <DialogDescription>
            Formulaire de creation de experience
          </DialogDescription>
        </DialogHeader>
        <CreateExperienceDialogContent />
      </DialogContent>
    </Dialog>
  );
}