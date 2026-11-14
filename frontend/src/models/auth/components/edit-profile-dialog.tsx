import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useTranslation } from "react-i18next";
import { KeyRound } from "lucide-react";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { CreationErrorSonner, CreationSuccessSonner } from "@/helpers/api/feed-backs";
import { ConnectedComputersSection } from "@/models/devstreet-hub/components/connected-computers-section";
import { Skeleton } from "@/components/ui/skeleton";
import { useGetMyProfileQuery, useUpdateMyProfileMutation } from "../api";
import type { User } from "../schema";
import { useAuthSlice, useChangePasswordDialogStore } from "../slice";
import ChangePasswordDialog from "./change-password/change-password-dialog";

const schema = z.object({
  first_name: z.string().trim().min(1, "Le prénom est obligatoire").max(150),
  last_name: z.string().trim().min(1, "Le nom est obligatoire").max(150),
  username: z.string().trim().min(3, "Au moins 3 caractères").max(150),
});

type Values = z.infer<typeof schema>;

type EditProfileDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** Appelé après l'enregistrement de l'identité. */
  onUpdated?: () => void;
  /** Appelé quand le nom d'utilisateur change : l'adresse du profil change avec lui. */
  onUsernameChanged?: (username: string) => void;
};

/**
 * Boîte de dialogue « Modifier le profil » : tout ce qui se modifie sur son compte, sans quitter la page.
 * Identité (prénom, nom, nom d'utilisateur), mot de passe et ordinateurs connectés.
 * La photo et la bannière se changent directement sur la page de profil, avec leurs petits boutons.
 */
export function EditProfileDialog({
  open,
  onOpenChange,
  onUpdated,
  onUsernameChanged,
}: EditProfileDialogProps) {
  const { t } = useTranslation();
  const user = useAuthSlice((state) => state.user);
  const loadSession = useAuthSlice((state) => state.loadSession);
  const { openChangePasswordDialog } = useChangePasswordDialogStore();
  const [updateProfile, { isLoading }] = useUpdateMyProfileMutation();
  // Le profil est relu à chaque ouverture : prénom et nom ne sont pas dans la session, et la session peut être ancienne
  const { data: fresh, isFetching } = useGetMyProfileQuery(undefined, {
    skip: !open,
    refetchOnMountOrArgChange: true,
  });
  const [formKey, setFormKey] = useState(0);

  // Le contenu est remonté à chaque ouverture pour repartir des valeurs enregistrées
  const handleOpenChange = (next: boolean) => {
    if (next) setFormKey((key) => key + 1);
    onOpenChange(next);
  };

  if (!user) return null;

  return (
    <>
      <Dialog open={open} onOpenChange={handleOpenChange}>
        <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>Modifier le profil</DialogTitle>
            <DialogDescription>
              Vos informations, votre mot de passe et vos ordinateurs connectés. La photo et la bannière se changent
              directement sur la page de profil.
            </DialogDescription>
          </DialogHeader>

          {isFetching && !fresh ? (
            <Skeleton className="h-52 w-full" />
          ) : (
          <IdentityForm
            key={formKey}
            user={fresh ?? user}
            busy={isLoading}
            onSubmit={async (values, setFieldError) => {
              try {
                await updateProfile(values).unwrap();
                await loadSession();
                CreationSuccessSonner("Profil mis à jour");
                onOpenChange(false);
                if (values.username !== user.username) onUsernameChanged?.(values.username);
                else onUpdated?.();
              } catch (err) {
                const data = (err as { data?: Record<string, unknown> }).data;
                let matched = false;
                if (data && typeof data === "object") {
                  (Object.keys(values) as (keyof Values)[]).forEach((field) => {
                    const messages = data[field];
                    if (Array.isArray(messages) && messages.length > 0) {
                      setFieldError(field, String(messages[0]));
                      matched = true;
                    }
                  });
                }
                if (!matched) CreationErrorSonner(t("common.error", "Impossible d'enregistrer le profil"));
              }
            }}
          />
          )}

          <Separator />

          <section className="flex flex-col gap-3">
            <div>
              <h3 className="text-sm font-semibold text-foreground">Sécurité</h3>
              <p className="text-xs text-muted-foreground">{t("my_account.password_description")}</p>
            </div>
            <Button type="button" variant="outline" className="w-fit" onClick={openChangePasswordDialog}>
              <KeyRound className="mr-2 size-4" aria-hidden />
              {t("change_password.button")}
            </Button>
          </section>

          <Separator />

          <ConnectedComputersSection />
        </DialogContent>
      </Dialog>

      {/* Boîte de dialogue du changement de mot de passe, ouverte depuis la section Sécurité */}
      <ChangePasswordDialog />
    </>
  );
}

function IdentityForm({
  user,
  busy,
  onSubmit,
}: {
  user: User;
  busy: boolean;
  onSubmit: (
    values: Values,
    setFieldError: (field: keyof Values, message: string) => void
  ) => Promise<void>;
}) {
  const { t } = useTranslation();
  const form = useForm<Values>({
    resolver: zodResolver(schema),
    defaultValues: {
      first_name: user.first_name ?? "",
      last_name: user.last_name ?? "",
      username: user.username ?? "",
    },
  });
  const username = form.watch("username");

  return (
    <Form {...form}>
      <form
        className="flex flex-col gap-4"
        noValidate
        onSubmit={form.handleSubmit((values) =>
          onSubmit(values, (field, message) => form.setError(field, { message }))
        )}
      >
        <h3 className="text-sm font-semibold text-foreground">Informations</h3>
        <div className="grid gap-4 sm:grid-cols-2">
          <FormField
            control={form.control}
            name="first_name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{t("first_name", "Prénom")}</FormLabel>
                <FormControl>
                  <Input {...field} autoComplete="given-name" />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="last_name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{t("last_name", "Nom")}</FormLabel>
                <FormControl>
                  <Input {...field} autoComplete="family-name" />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="username"
            render={({ field }) => (
              <FormItem className="sm:col-span-2">
                <FormLabel>{t("username", "Nom d'utilisateur")}</FormLabel>
                <FormControl>
                  <Input {...field} autoComplete="username" />
                </FormControl>
                {username.trim() !== user.username ? (
                  <FormDescription className="text-destructive">
                    {t("username_change_warning")}
                  </FormDescription>
                ) : null}
                <FormMessage />
              </FormItem>
            )}
          />
          <div className="flex flex-col gap-2 sm:col-span-2">
            <Label htmlFor="profile-email">{t("email", "E-mail")}</Label>
            <Input id="profile-email" value={user.email ?? ""} readOnly disabled aria-describedby="profile-email-hint" />
            <p id="profile-email-hint" className="text-[0.8rem] text-muted-foreground">
              L'adresse e-mail n'est pas modifiable.
            </p>
          </div>
        </div>
        <div className="flex justify-end">
          <Button type="submit" disabled={busy}>
            Enregistrer
          </Button>
        </div>
      </form>
    </Form>
  );
}
