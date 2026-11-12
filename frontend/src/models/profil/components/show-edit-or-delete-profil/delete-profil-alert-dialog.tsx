import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { useDeleteProfilMutation } from "../../api";
import {
  CreationErrorSonner,
  CreationSuccessSonner,
} from "@/helpers/api/feed-backs";

interface DeleteProfilAlertDialogProps {
  profilId: number;
  onCancel: () => void;
  onDeleted: () => void;
}

export default function DeleteProfilAlertDialog({
  profilId,
  onCancel,
  onDeleted,
}: DeleteProfilAlertDialogProps) {
  const [deleteItem, { isLoading }] = useDeleteProfilMutation();

  const handleDelete = async () => {
    try {
      await deleteItem(profilId).unwrap();
      onDeleted();
      CreationSuccessSonner("Element supprime avec succes");
    } catch (error) {
      console.error("Failed to delete item:", error);
      CreationErrorSonner("Impossible de supprimer l'element");
    }
  };

  return (
    <AlertDialog
      open
      onOpenChange={(open) => {
        if (!open && !isLoading) {
          onCancel();
        }
      }}
    >
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Confirmer la suppression</AlertDialogTitle>
          <AlertDialogDescription>
            Cette action est irreversible.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isLoading}>Annuler</AlertDialogCancel>
          <Button
            type="button"
            variant="destructive"
            disabled={isLoading}
            onClick={() => void handleDelete()}
          >
            {isLoading ? "Suppression..." : "Supprimer"}
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}