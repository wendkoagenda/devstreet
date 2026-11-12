import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useCompanyStore } from "../../slice";
import CreateCompanyDialogContent from "./create-company-dialog-content";

export default function CreateCompanyDialog() {
  const { isCreateDialogOpen, closeCreateDialog } = useCompanyStore();

  return (
    <Dialog
      open={isCreateDialogOpen}
      onOpenChange={(open) => {
        if (!open) closeCreateDialog();
      }}
    >
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Creer Company</DialogTitle>
          <DialogDescription>
            Formulaire de creation de company
          </DialogDescription>
        </DialogHeader>
        <CreateCompanyDialogContent />
      </DialogContent>
    </Dialog>
  );
}