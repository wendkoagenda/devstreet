import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useSwipeStore } from "../../slice";
import CreateSwipeDialogContent from "./create-swipe-dialog-content";

export default function CreateSwipeDialog() {
  const { isCreateDialogOpen, closeCreateDialog } = useSwipeStore();

  return (
    <Dialog
      open={isCreateDialogOpen}
      onOpenChange={(open) => {
        if (!open) closeCreateDialog();
      }}
    >
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Creer Swipe</DialogTitle>
          <DialogDescription>
            Formulaire de creation de swipe
          </DialogDescription>
        </DialogHeader>
        <CreateSwipeDialogContent />
      </DialogContent>
    </Dialog>
  );
}