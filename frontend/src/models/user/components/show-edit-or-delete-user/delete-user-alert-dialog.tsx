import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { useTranslation } from "react-i18next";
import { useUserStore } from "../../slice";
import { useDeleteUserMutation } from "../../api";
import { CreationSuccessSonner } from "@/helpers/api/feed-backs";

interface DeleteUserAlertDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function DeleteUserAlertDialog({
  isOpen,
  onOpenChange,
}: DeleteUserAlertDialogProps) {
  const { t } = useTranslation();
  const { selectedUser, closeShowUserDialog } = useUserStore();
  const [deleteUser] = useDeleteUserMutation();

  const handleDelete = async () => {
    if (!selectedUser) return;
    try {
      await deleteUser(selectedUser.id).unwrap();
      closeShowUserDialog();
      CreationSuccessSonner(t("user_deleted_successfully"));
    } catch (error) {
      console.error("Failed to delete user:", error);
    }
  };

  return (
    <AlertDialog open={isOpen} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>
            {t("delete_user_confirmation_title")}
          </AlertDialogTitle>
          <AlertDialogDescription>
            {t("delete_user_confirmation_description")}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>{t("cancel")}</AlertDialogCancel>
          <AlertDialogAction
            onClick={handleDelete}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
          >
            {t("delete")}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
