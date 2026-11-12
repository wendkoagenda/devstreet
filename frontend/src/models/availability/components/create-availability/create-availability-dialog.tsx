import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useAvailabilityStore } from "../../slice";
import CreateAvailabilityDialogContent from "./create-availability-dialog-content";

export default function CreateAvailabilityDialog() {
  const { isCreateDialogOpen, closeCreateDialog } = useAvailabilityStore();

  return (
    <Dialog
      open={isCreateDialogOpen}
      onOpenChange={(open) => {
        if (!open) closeCreateDialog();
      }}
    >
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Creer Availability</DialogTitle>
          <DialogDescription>
            Formulaire de creation de availability
          </DialogDescription>
        </DialogHeader>
        <CreateAvailabilityDialogContent />
      </DialogContent>
    </Dialog>
  );
}