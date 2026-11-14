import { useRef } from "react";
import { Camera, Loader2, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  useDeleteProfileBannerMutation,
  useDeleteProfilePhotoMutation,
  useUploadProfileBannerMutation,
  useUploadProfilePhotoMutation,
} from "../api";
import { useAuthSlice } from "../slice";

const ACCEPTED_TYPES = "image/jpeg,image/png,image/gif,image/webp";
const MAX_MB = { photo: 5, banner: 8 } as const;

type ProfileImageEditButtonProps = {
  /** Image modifiée : la photo de profil ou la bannière. */
  kind: "photo" | "banner";
  /** Une image est déjà enregistrée : un bouton permet alors de la supprimer. */
  hasImage?: boolean;
  /** Appelé après l'enregistrement, pour recharger la page de profil. */
  onUpdated?: () => void;
  /** Position du groupe de boutons sur l'image. */
  className?: string;
};

/**
 * Petits boutons posés sur la photo ou la bannière : changer l'image (le fichier choisi est enregistré tout de suite)
 * et, quand une image existe, la supprimer.
 */
export function ProfileImageEditButton({ kind, hasImage = false, onUpdated, className }: ProfileImageEditButtonProps) {
  const { t } = useTranslation();
  const inputRef = useRef<HTMLInputElement>(null);
  const loadSession = useAuthSlice((state) => state.loadSession);
  const [uploadPhoto, { isLoading: uploadingPhoto }] = useUploadProfilePhotoMutation();
  const [uploadBanner, { isLoading: uploadingBanner }] = useUploadProfileBannerMutation();
  const [deletePhoto, { isLoading: deletingPhoto }] = useDeleteProfilePhotoMutation();
  const [deleteBanner, { isLoading: deletingBanner }] = useDeleteProfileBannerMutation();
  const uploading = uploadingPhoto || uploadingBanner;
  const busy = uploading || deletingPhoto || deletingBanner;
  const isPhoto = kind === "photo";
  const changeLabel = isPhoto ? "Changer la photo de profil" : "Changer la bannière";
  const removeLabel = isPhoto ? "Supprimer la photo de profil" : "Supprimer la bannière";

  const handleChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      toast.error(t("my_account.photo_invalid_type"));
      return;
    }
    if (file.size > MAX_MB[kind] * 1024 * 1024) {
      toast.error(t("my_account.photo_too_large", { size: MAX_MB[kind] }));
      return;
    }
    try {
      await (isPhoto ? uploadPhoto(file) : uploadBanner(file)).unwrap();
      await loadSession();
      onUpdated?.();
      toast.success(t(isPhoto ? "my_account.photo_updated" : "my_account.banner_updated"));
    } catch {
      toast.error(t(isPhoto ? "my_account.photo_update_error" : "my_account.banner_update_error"));
    }
  };

  const handleRemove = async () => {
    try {
      await (isPhoto ? deletePhoto() : deleteBanner()).unwrap();
      await loadSession();
      onUpdated?.();
      toast.success(t(isPhoto ? "my_account.photo_removed" : "my_account.banner_removed"));
    } catch {
      toast.error(t(isPhoto ? "my_account.photo_remove_error" : "my_account.banner_remove_error"));
    }
  };

  return (
    <div className={cn("flex gap-1.5", className)}>
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED_TYPES}
        className="hidden"
        onChange={handleChange}
        aria-hidden
        tabIndex={-1}
      />
      <Button
        type="button"
        size="icon"
        variant="secondary"
        disabled={busy}
        onClick={() => inputRef.current?.click()}
        title={changeLabel}
        aria-label={changeLabel}
        className="size-8 rounded-full shadow-md"
      >
        {uploading ? <Loader2 className="size-4 animate-spin" aria-hidden /> : <Camera className="size-4" aria-hidden />}
      </Button>
      {hasImage ? (
        <Button
          type="button"
          size="icon"
          variant="secondary"
          disabled={busy}
          onClick={() => void handleRemove()}
          title={removeLabel}
          aria-label={removeLabel}
          className="size-8 rounded-full shadow-md"
        >
          <Trash2 className="size-4" aria-hidden />
        </Button>
      ) : null}
    </div>
  );
}
