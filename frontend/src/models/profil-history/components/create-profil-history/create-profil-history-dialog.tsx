import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useProfilHistoryStore } from "../../slice";
import CreateProfilHistoryDialogContent from "./create-profil-history-dialog-content";

export default function CreateProfilHistoryDialog() {
  const { isCreateDialogOpen, closeCreateDialog } = useProfilHistoryStore();

  return (
    <Dialog
      open={isCreateDialogOpen}
      onOpenChange={(open) => {
        if (!open) closeCreateDialog();
      }}
    >
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Creer ProfilHistory</DialogTitle>
          <DialogDescription>
            Formulaire de creation de profilhistory
          </DialogDescription>
        </DialogHeader>
        <CreateProfilHistoryDialogContent />
      </DialogContent>
    </Dialog>
  );
}