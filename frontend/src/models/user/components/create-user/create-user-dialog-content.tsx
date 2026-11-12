import { Button } from "@/components/ui/button";
import ActionsLayout from "@/components/layouts/actions-layout";
import { Input } from "@/components/ui/input";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { createUserSchema, type CreateUserSchema } from "../../schema";
import { useTranslation } from "react-i18next";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from "@/components/ui/form";
import { User, X, Check } from "lucide-react";
import { Mail } from "lucide-react";
import { useState } from "react";
import { Eye } from "lucide-react";
import { EyeOff } from "lucide-react";
import { Icons } from "@/lib/constants/icons";
import IconAndTextDisplayerAsTitle from "@/helpers/displayers/icon-and-text-displayer-as-title";
import { useCreateUserMutation } from "../../api";
import { CreationSuccessSonner } from "@/helpers/api/feed-backs";
import { renderFetchBaseQueryError } from "@/helpers/api/global-error-catcher";
import type { FetchBaseQueryError } from "@reduxjs/toolkit/query";
import RoleSelector from "./role-selector";
import PasswordStrengthIndicator from "@/helpers/displayers/password-strength-indicator";
import { useUserStore } from "../../slice";

export default function CreateUserDialogContent() {
  const { t } = useTranslation();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [createUser, { isLoading: isSubmitting }] = useCreateUserMutation();
  const { closeCreateUserDialog } = useUserStore();
  const [globalError, setGlobalError] = useState<React.ReactNode>(null);
  const form = useForm<CreateUserSchema>({
    resolver: zodResolver(createUserSchema(t)),
    defaultValues: {
      is_active: true,
    },
  });

  const watchedPassword = form.watch("password");
  const watchedConfirmPassword = form.watch("password_confirm");

  const onSubmit = async (newUser: CreateUserSchema) => {
    try {
      setGlobalError(null);
      await createUser(newUser).unwrap();
      form.reset();
      closeCreateUserDialog();
      CreationSuccessSonner(t("user_created_successfully"));
    } catch (err) {
      const error = err as FetchBaseQueryError;

      if (error.status === 400 && error.data) {
        const errorData = error.data as Record<string, string[]>;
        Object.entries(errorData).forEach(([field, messages]) => {
          if (Array.isArray(messages) && messages.length > 0) {
            form.setError(field as keyof CreateUserSchema, {
              message: messages[0],
            });
          }
        });
      } else {
        setGlobalError(renderFetchBaseQueryError(error, t));
      }
    }
  };

  return (
    <div className="flex flex-col gap-4 mx-4">
      {globalError && <div className="mb-4">{globalError}</div>}
      <Form {...form}>
        <div className="max-h-[60vh] overflow-y-auto pr-2">
          <div className="space-y-6">
            <div className="space-y-4">
              <IconAndTextDisplayerAsTitle
                Icon={Icons.User}
                text={t("personal_information")}
              />
              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="first_name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-sm font-medium">
                        {t("first_name")} *
                      </FormLabel>
                      <FormControl>
                        <Input {...field} placeholder="Jean" className="h-10" />
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
                      <FormLabel className="text-sm font-medium">
                        {t("last_name")} *
                      </FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          placeholder="Dupont"
                          className="h-10"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>
            <div className="space-y-4">
              <IconAndTextDisplayerAsTitle
                Icon={Icons.PersonalInformation}
                text={t("account_information")}
              />
              <FormField
                control={form.control}
                name="username"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium">
                      {t("username")} *
                    </FormLabel>
                    <FormControl>
                      <div className="relative">
                        <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                        <Input
                          {...field}
                          placeholder="nom_utilisateur"
                          className="pl-10 h-10"
                        />
                      </div>
                    </FormControl>
                    <FormDescription className="text-xs">
                      Le nom d'utilisateur doit être unique
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium">
                      {t("email")} *
                    </FormLabel>
                    <FormControl>
                      <div className="relative">
                        <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                        <Input
                          type="email"
                          {...field}
                          placeholder="utilisateur@exemple.com"
                          className="pl-10 h-10"
                        />
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="space-y-4">
              <IconAndTextDisplayerAsTitle
                Icon={Icons.Security}
                text={t("security")}
              />

              <div className="grid grid-cols-1 gap-4">
                <FormField
                  control={form.control}
                  name="password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-sm font-medium">
                        {t("password")} *
                      </FormLabel>
                      <FormControl>
                        <div className="relative">
                          <Input
                            type={showPassword ? "text" : "password"}
                            {...field}
                            placeholder="••••••••"
                            className="pr-10 h-10"
                          />
                          <Button
                            type="button"
                            onClick={() => setShowPassword(!showPassword)}
                            variant="ghost"
                            size="icon"
                            className="absolute right-1 top-1 h-8 w-8 text-muted-foreground hover:text-foreground"
                          >
                            {showPassword ? (
                              <EyeOff className="h-4 w-4" />
                            ) : (
                              <Eye className="h-4 w-4" />
                            )}
                          </Button>
                        </div>
                      </FormControl>
                      {watchedPassword && (
                        <PasswordStrengthIndicator password={watchedPassword} />
                      )}
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="password_confirm"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-sm font-medium">
                        {t("password_confirm")} *
                      </FormLabel>
                      <FormControl>
                        <div className="relative">
                          <Input
                            type={showConfirmPassword ? "text" : "password"}
                            {...field}
                            placeholder="••••••••"
                            className="pr-10 h-10"
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
                      {watchedPassword && watchedConfirmPassword && (
                        <div className="flex items-center gap-2 text-xs mt-1">
                          {watchedPassword === watchedConfirmPassword ? (
                            <>
                              <Check className="h-3 w-3 text-green-600 dark:text-green-400" />
                              <span className="text-green-700 dark:text-green-400">
                                Les mots de passe correspondent
                              </span>
                            </>
                          ) : (
                            <>
                              <X className="h-3 w-3 text-destructive" />
                              <span className="text-destructive">
                                Les mots de passe ne correspondent pas
                              </span>
                            </>
                          )}
                        </div>
                      )}
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            <div className="space-y-4">
              <IconAndTextDisplayerAsTitle
                Icon={Icons.Roles}
                text={t("roles_and_permissions")}
              />
              <FormField
                control={form.control}
                name="role_names"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-sm font-medium">
                      {t("role_names")} *
                    </FormLabel>
                    <FormControl>
                      <RoleSelector
                        value={field.value || []}
                        onChange={(roles) => {
                          field.onChange(roles);
                          form.setValue("role_names", roles);
                        }}
                      />
                    </FormControl>
                    <FormDescription className="text-xs">
                      Sélectionnez un ou plusieurs rôles pour cet utilisateur
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="is_active"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4 bg-muted/50 col-span-1">
                      <div className="space-y-0.5">
                        <FormLabel className="text-sm font-medium">
                          {t("is_active")}
                        </FormLabel>
                        <FormDescription className="text-xs">
                          L'utilisateur pourra se connecter immédiatement
                        </FormDescription>
                      </div>
                      <FormControl>
                        <Checkbox
                          checked={field.value}
                          onCheckedChange={(checked) => {
                            field.onChange(checked as boolean);
                            form.setValue("is_active", checked as boolean);
                          }}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
              </div>
            </div>
          </div>
          <ActionsLayout
            type="create"
            onSubmit={form.handleSubmit(onSubmit)}
            onCancel={closeCreateUserDialog}
            isSubmitting={isSubmitting}
          />
        </div>
      </Form>
    </div>
  );
}
