import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useSkillStore } from "../../slice";
import CreateSkillDialogContent from "./create-skill-dialog-content";

export default function CreateSkillDialog() {
  const { isCreateDialogOpen, closeCreateDialog } = useSkillStore();

  return (
    <Dialog
      open={isCreateDialogOpen}
      onOpenChange={(open) => {
        if (!open) closeCreateDialog();
      }}
    >
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Creer Skill</DialogTitle>
          <DialogDescription>
            Formulaire de creation de skill
          </DialogDescription>
        </DialogHeader>
        <CreateSkillDialogContent />
      </DialogContent>
    </Dialog>
  );
}