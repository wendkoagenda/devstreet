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
import { Check, Eye, EyeOff, X } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useTranslation } from "react-i18next";
import { useChangePasswordMutation } from "../../api";
import { ChangePasswordSchema, changePasswordSchema } from "../../schema";
import { useChangePasswordDialogStore } from "../../slice";
import PasswordStrengthIndicator from "@/helpers/displayers/password-strength-indicator";
import { useAuth } from "../../hooks/useAuth";

export default function ChangePasswordDialogContent() {
  const { t } = useTranslation();
  const [changePassword, { isLoading }] = useChangePasswordMutation();
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const { closeChangePasswordDialog } = useChangePasswordDialogStore();
  const form = useForm<ChangePasswordSchema>({
    resolver: zodResolver(changePasswordSchema(t)),
    defaultValues: {
      old_password: "",
      new_password: "",
      new_password_confirm: "",
    },
  });
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
      CreationErrorSonner(t("change_password.error"));
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
