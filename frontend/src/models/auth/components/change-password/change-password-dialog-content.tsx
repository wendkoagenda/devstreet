import { Button } from "@/components/ui/button";
import ActionsLayout from "@/components/layouts/actions-layout";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  CreationErrorSonner,
  CreationSuccessSonner,
} from "@/helpers/api/feed-backs";
import { zodResolver } from "@hookform/resolvers/zod";
import { Check, Eye, EyeOff, Mail, X } from "lucide-react";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { useTranslation } from "react-i18next";
import {
  useChangePasswordMutation,
  useRequestChangePasswordCodeMutation,
} from "../../api";
import { ChangePasswordSchema, changePasswordSchema } from "../../schema";
import { useChangePasswordDialogStore } from "../../slice";
import PasswordStrengthIndicator from "@/helpers/displayers/password-strength-indicator";
import { useAuth } from "../../hooks/useAuth";

const RESEND_DELAY_SECONDS = 60;

/** Message d'erreur renvoyé par l'API ({ error: "..." }), s'il y en a un. */
function apiErrorMessage(error: unknown): string | undefined {
  const data = (error as { data?: { error?: unknown } }).data;
  return typeof data?.error === "string" ? data.error : undefined;
}

export default function ChangePasswordDialogContent() {
  const { t } = useTranslation();
  const [changePassword, { isLoading }] = useChangePasswordMutation();
  const [requestCode, { isLoading: isSendingCode }] =
    useRequestChangePasswordCodeMutation();
  // Délai avant de pouvoir redemander un code (aligné sur la limite du serveur)
  const [resendIn, setResendIn] = useState(0);
  const [codeSent, setCodeSent] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const { closeChangePasswordDialog } = useChangePasswordDialogStore();
  const form = useForm<ChangePasswordSchema>({
    resolver: zodResolver(changePasswordSchema(t)),
    defaultValues: {
      old_password: "",
      new_password: "",
      new_password_confirm: "",
      code: "",
    },
  });

  useEffect(() => {
    if (resendIn <= 0) return;
    const timer = window.setTimeout(() => setResendIn((value) => value - 1), 1000);
    return () => window.clearTimeout(timer);
  }, [resendIn]);

  /** Envoie le code de confirmation à l'adresse du compte. */
  const handleSendCode = async () => {
    try {
      const result = await requestCode().unwrap();
      setCodeSent(true);
      setResendIn(RESEND_DELAY_SECONDS);
      CreationSuccessSonner(result.message);
    } catch (error) {
      console.error("Envoi du code de changement de mot de passe impossible :", error);
      CreationErrorSonner(
        apiErrorMessage(error) ?? "Le code n'a pas pu être envoyé. Réessayez dans quelques instants."
      );
    }
  };
  const { logout } = useAuth();
  const watchedNewPassword = form.watch("new_password");
  const watchedConfirmPassword = form.watch("new_password_confirm");

  const handleSubmit = async (data: ChangePasswordSchema) => {
    try {
      await changePassword(data).unwrap();
      CreationSuccessSonner(t("change_password.success"));
      closeChangePasswordDialog();
      form.reset();
      logout();
    } catch (error) {
      console.error("Change password failed:", error);
      // Erreurs de champ du serveur (code invalide, ancien mot de passe faux) : affichées sous le champ
      const fieldErrors = (error as { data?: Record<string, unknown> }).data;
      let matched = false;
      for (const field of ["code", "old_password", "new_password"] as const) {
        const messages = fieldErrors?.[field];
        if (Array.isArray(messages) && messages.length > 0) {
          form.setError(field, { message: String(messages[0]) });
          matched = true;
        }
      }
      if (!matched) CreationErrorSonner(t("change_password.error"));
    }
  };

  return (
    <div className="flex flex-col gap-4 mx-4">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="old_password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{t("change_password.old_password")}</FormLabel>
                <FormControl>
                  <Input
                    {...field}
                    type="password"
                    placeholder={t("change_password.old_password_placeholder")}
                    autoComplete="current-password"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="new_password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{t("change_password.new_password")}</FormLabel>
                <FormControl>
                  <div className="relative">
                    <Input
                      {...field}
                      type={showNewPassword ? "text" : "password"}
                      placeholder={t(
                        "change_password.new_password_placeholder"
                      )}
                      autoComplete="new-password"
                    />
                    <Button
                      type="button"
                      onClick={() => setShowNewPassword(!showNewPassword)}
                      variant="ghost"
                      size="icon"
                      className="absolute right-1 top-1 h-8 w-8 text-muted-foreground hover:text-foreground"
                    >
                      {showNewPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </FormControl>
                {watchedNewPassword && (
                  <PasswordStrengthIndicator password={watchedNewPassword} />
                )}
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="new_password_confirm"
            render={({ field }) => (
              <FormItem>
                <FormLabel>
                  {t("change_password.new_password_confirm")}
                </FormLabel>
                <FormControl>
                  <div className="relative">
                    <Input
                      {...field}
                      type={showConfirmPassword ? "text" : "password"}
                      placeholder={t(
                        "change_password.new_password_confirm_placeholder"
                      )}
                      autoComplete="new-password"
                    />
                    <Button
                      type="button"
                      onClick={() =>
                        setShowConfirmPassword(!showConfirmPassword)
                      }
                      variant="ghost"
                      size="icon"
                      className="absolute right-1 top-1 h-8 w-8 text-muted-foreground hover:text-foreground"
                    >
                      {showConfirmPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </FormControl>
                {watchedNewPassword && watchedConfirmPassword && (
                  <div className="flex items-center gap-2 text-xs mt-1">
                    {watchedNewPassword === watchedConfirmPassword ? (
                      <>
                        <Check className="h-3 w-3 text-success" />
                        <span className="text-success">
                          {t("validation.password.match")}
                        </span>
                      </>
                    ) : (
                      <>
                        <X className="h-3 w-3 text-destructive" />
                        <span className="text-destructive">
                          {t("validation.password.not_match")}
                        </span>
                      </>
                    )}
                  </div>
                )}
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="code"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Code de confirmation</FormLabel>
                <div className="flex gap-2">
                  <FormControl>
                    <Input
                      {...field}
                      inputMode="numeric"
                      autoComplete="one-time-code"
                      maxLength={6}
                      placeholder="6 chiffres"
                      className="font-mono tracking-[0.3em]"
                    />
                  </FormControl>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => void handleSendCode()}
                    disabled={isSendingCode || resendIn > 0}
                    className="shrink-0 gap-1.5"
                  >
                    <Mail className="h-4 w-4" aria-hidden />
                    {isSendingCode
                      ? "Envoi…"
                      : resendIn > 0
                        ? `Renvoyer (${resendIn} s)`
                        : codeSent
                          ? "Renvoyer"
                          : "Recevoir le code"}
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground">
                  {codeSent
                    ? "Le code a été envoyé à votre adresse e-mail. Il est valable 15 minutes."
                    : "Pour votre sécurité, un code envoyé par e-mail confirme le changement."}
                </p>
                <FormMessage />
              </FormItem>
            )}
          />

          <ActionsLayout
            type="save"
            onSubmit={form.handleSubmit(handleSubmit)}
            onCancel={closeChangePasswordDialog}
            isSubmitting={isLoading}
          />
        </form>
      </Form>
    </div>
  );
}
