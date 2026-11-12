import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useProfilStore } from "../../slice";
import CreateProfilDialogContent from "./create-profil-dialog-content";

export default function CreateProfilDialog() {
  const { isCreateDialogOpen, closeCreateDialog } = useProfilStore();

  return (
    <Dialog
      open={isCreateDialogOpen}
      onOpenChange={(open) => {
        if (!open) closeCreateDialog();
      }}
    >
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Creer Profil</DialogTitle>
          <DialogDescription>
            Formulaire de creation de profil
          </DialogDescription>
        </DialogHeader>
        <CreateProfilDialogContent />
      </DialogContent>
    </Dialog>
  );
}