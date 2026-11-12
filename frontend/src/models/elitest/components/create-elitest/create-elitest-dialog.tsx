import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useElitestStore } from "../../slice";
import CreateElitestDialogContent from "./create-elitest-dialog-content";

export default function CreateElitestDialog() {
  const { isCreateDialogOpen, closeCreateDialog } = useElitestStore();

  return (
    <Dialog
      open={isCreateDialogOpen}
      onOpenChange={(open) => {
        if (!open) closeCreateDialog();
      }}
    >
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Creer Elitest</DialogTitle>
          <DialogDescription>
            Formulaire de creation de elitest
          </DialogDescription>
        </DialogHeader>
        <CreateElitestDialogContent />
      </DialogContent>
    </Dialog>
  );
}