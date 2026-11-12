import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useReviewStore } from "../../slice";
import CreateReviewDialogContent from "./create-review-dialog-content";

export default function CreateReviewDialog() {
  const { isCreateDialogOpen, closeCreateDialog } = useReviewStore();

  return (
    <Dialog
      open={isCreateDialogOpen}
      onOpenChange={(open) => {
        if (!open) closeCreateDialog();
      }}
    >
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Creer Review</DialogTitle>
          <DialogDescription>
            Formulaire de creation de review
          </DialogDescription>
        </DialogHeader>
        <CreateReviewDialogContent />
      </DialogContent>
    </Dialog>
  );
}