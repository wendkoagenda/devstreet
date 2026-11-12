import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useProfilSkillStore } from "../../slice";
import CreateProfilSkillDialogContent from "./create-profil-skill-dialog-content";

export default function CreateProfilSkillDialog() {
  const { isCreateDialogOpen, closeCreateDialog } = useProfilSkillStore();

  return (
    <Dialog
      open={isCreateDialogOpen}
      onOpenChange={(open) => {
        if (!open) closeCreateDialog();
      }}
    >
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Creer ProfilSkill</DialogTitle>
          <DialogDescription>
            Formulaire de creation de profilskill
          </DialogDescription>
        </DialogHeader>
        <CreateProfilSkillDialogContent />
      </DialogContent>
    </Dialog>
  );
}