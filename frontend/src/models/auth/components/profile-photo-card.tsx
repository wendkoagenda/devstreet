import { useRef } from "react";
import { Camera, ImageIcon, Trash2, UserRound } from "lucide-react";
import { toast } from "sonner";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { buildMediaUrl } from "@/helpers/displayers/media-url-builder";
import {
  useDeleteProfileBannerMutation,
  useDeleteProfilePhotoMutation,
  useUploadProfileBannerMutation,
  useUploadProfilePhotoMutation,
} from "../api";
import { useAuthSlice } from "../slice";
import type { User } from "../schema";

const ACCEPTED_TYPES = "image/jpeg,image/png,image/gif,image/webp";
const PHOTO_MAX_MB = 5;
const BANNER_MAX_MB = 8;

type ProfilePhotoCardProps = {
  user: User;
  onUserUpdated: (user: User) => void;
};

export function ProfilePhotoCard({ user, onUserUpdated }: ProfilePhotoCardProps) {
  const { t } = useTranslation();
  const photoInputRef = useRef<HTMLInputElement>(null);
  const bannerInputRef = useRef<HTMLInputElement>(null);
  const loadSession = useAuthSlice((state) => state.loadSession);

  const [uploadPhoto, { isLoading: isUploadingPhoto }] =
    useUploadProfilePhotoMutation();
  const [deletePhoto, { isLoading: isDeletingPhoto }] =
    useDeleteProfilePhotoMutation();
  const [uploadBanner, { isLoading: isUploadingBanner }] =
    useUploadProfileBannerMutation();
  const [deleteBanner, { isLoading: isDeletingBanner }] =
    useDeleteProfileBannerMutation();

  const photoBusy = isUploadingPhoto || isDeletingPhoto;
  const bannerBusy = isUploadingBanner || isDeletingBanner;
  const photoUrl = user.photo ? buildMediaUrl(user.photo) : null;
  const bannerUrl = user.banner ? buildMediaUrl(user.banner) : null;

  const applyUpdatedUser = async (updated: User) => {
    onUserUpdated(updated);
    await loadSession();
  };

  const validateImage = (file: File, maxMb: number): boolean => {
    if (!file.type.startsWith("image/")) {
      toast.error(t("my_account.photo_invalid_type"));
      return false;
    }
    if (file.size > maxMb * 1024 * 1024) {
      toast.error(t("my_account.photo_too_large", { size: maxMb }));
      return false;
    }
    return true;
  };

  const handlePhotoChange = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file || !validateImage(file, PHOTO_MAX_MB)) return;

    try {
      const updated = await uploadPhoto(file).unwrap();
      await applyUpdatedUser(updated);
      toast.success(t("my_account.photo_updated"));
    } catch {
      toast.error(t("my_account.photo_update_error"));
    }
  };

  const handleBannerChange = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file || !validateImage(file, BANNER_MAX_MB)) return;

    try {
      const updated = await uploadBanner(file).unwrap();
      await applyUpdatedUser(updated);
      toast.success(t("my_account.banner_updated"));
    } catch {
      toast.error(t("my_account.banner_update_error"));
    }
  };

  const handleDeletePhoto = async () => {
    try {
      const updated = await deletePhoto().unwrap();
      await applyUpdatedUser(updated);
      toast.success(t("my_account.photo_removed"));
    } catch {
      toast.error(t("my_account.photo_remove_error"));
    }
  };

  const handleDeleteBanner = async () => {
    try {
      const updated = await deleteBanner().unwrap();
      await applyUpdatedUser(updated);
      toast.success(t("my_account.banner_removed"));
    } catch {
      toast.error(t("my_account.banner_remove_error"));
    }
  };

  return (
    <Card className="overflow-hidden">
      <CardHeader className="flex flex-row items-center gap-2">
        <ImageIcon className="h-5 w-5" />
        <h2 className="text-lg font-semibold">{t("my_account.profile_media_title")}</h2>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="overflow-hidden rounded-lg border border-border">
          <div className="relative h-36 w-full bg-muted sm:h-44">
            {bannerUrl ? (
              <img
                src={bannerUrl}
                alt={t("my_account.banner_alt")}
                className="h-full w-full object-cover"
              />
            ) : (
              <div className="flex h-full w-full items-center justify-center text-muted-foreground">
                <ImageIcon className="h-10 w-10" aria-hidden />
              </div>
            )}
          </div>

          <div className="relative px-4 pb-4 pt-0">
            <div className="-mt-10 mb-4 flex items-end gap-4">
              <div className="relative h-20 w-20 shrink-0 overflow-hidden rounded-full border-4 border-background bg-muted sm:h-24 sm:w-24">
                {photoUrl ? (
                  <img
                    src={photoUrl}
                    alt={t("my_account.photo_alt")}
                    className="h-full w-full object-cover"
                  />
                ) : (
                  <div className="flex h-full w-full items-center justify-center text-muted-foreground">
                    <UserRound className="h-10 w-10" aria-hidden />
                  </div>
                )}
              </div>
              <div className="min-w-0 pb-1">
                <p className="truncate font-medium">{user.full_name || "—"}</p>
                <p className="truncate text-sm text-muted-foreground">
                  @{user.username || "—"}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <h3 className="font-medium">{t("my_account.photo_title")}</h3>
            <p className="text-sm text-muted-foreground">
              {t("my_account.photo_description")}
            </p>
            <div className="flex flex-wrap gap-2">
              <Button
                type="button"
                disabled={photoBusy}
                onClick={() => photoInputRef.current?.click()}
              >
                <Camera className="mr-2 h-4 w-4" />
                {photoUrl
                  ? t("my_account.photo_change")
                  : t("my_account.photo_add")}
              </Button>
              {photoUrl ? (
                <Button
                  type="button"
                  variant="outline"
                  disabled={photoBusy}
                  onClick={handleDeletePhoto}
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  {t("my_account.photo_remove")}
                </Button>
              ) : null}
            </div>
            <input
              ref={photoInputRef}
              type="file"
              accept={ACCEPTED_TYPES}
              className="hidden"
              onChange={handlePhotoChange}
            />
          </div>

          <div className="space-y-2">
            <h3 className="font-medium">{t("my_account.banner_title")}</h3>
            <p className="text-sm text-muted-foreground">
              {t("my_account.banner_description")}
            </p>
            <div className="flex flex-wrap gap-2">
              <Button
                type="button"
                disabled={bannerBusy}
                onClick={() => bannerInputRef.current?.click()}
              >
                <ImageIcon className="mr-2 h-4 w-4" />
                {bannerUrl
                  ? t("my_account.banner_change")
                  : t("my_account.banner_add")}
              </Button>
              {bannerUrl ? (
                <Button
                  type="button"
                  variant="outline"
                  disabled={bannerBusy}
                  onClick={handleDeleteBanner}
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  {t("my_account.banner_remove")}
                </Button>
              ) : null}
            </div>
            <input
              ref={bannerInputRef}
              type="file"
              accept={ACCEPTED_TYPES}
              className="hidden"
              onChange={handleBannerChange}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
