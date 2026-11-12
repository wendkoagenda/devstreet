import { Checkbox } from "@/components/ui/checkbox";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { CreationSuccessSonner } from "@/helpers/api/feed-backs";
import IconAndButtonDisplayer from "@/helpers/displayers/icon-and-button-displayer";
import IconAndTextDisplayerAsTitle from "@/helpers/displayers/icon-and-text-displayer-as-title";
import { Icons } from "@/lib/constants/icons";
import { zodResolver } from "@hookform/resolvers/zod";
import type { FetchBaseQueryError } from "@reduxjs/toolkit/query";
import { useForm } from "react-hook-form";
import { useTranslation } from "react-i18next";
import { useUpdateUserMutation } from "../../api";
import { updateUserSchema, type UpdateUserSchema } from "../../schema";
import { useUserStore } from "../../slice";
import RoleSelector from "../create-user/role-selector";
import { useState } from "react";
import { renderFetchBaseQueryError } from "@/helpers/api/global-error-catcher";

export default function EditUserDialogContent() {
  const { t } = useTranslation();
  const { selectedUser, closeShowUserDialog, disableEditMode } = useUserStore();
  const [updateUser, { isLoading: isSubmitting }] = useUpdateUserMutation();
  const [globalError, setGlobalError] = useState<React.ReactNode>(null);
  const form = useForm<UpdateUserSchema>({
    resolver: zodResolver(updateUserSchema(t)),
    defaultValues: selectedUser
      ? {
          id: selectedUser.id,
          username: selectedUser.username,
          email: selectedUser.email,
          first_name: selectedUser.first_name,
          last_name: selectedUser.last_name,
          role_names: selectedUser.role_names,
          is_active: selectedUser.is_active,
        }
      : {},
  });

  const onSubmit = form.handleSubmit(async (data) => {
    try {
      setGlobalError(null);
      await updateUser(data).unwrap();
      closeShowUserDialog();
      CreationSuccessSonner(t("user_updated_successfully"));
    } catch (err) {
      const error = err as FetchBaseQueryError;
      if (error.status === 400 && error.data) {
        const errorData = error.data as Record<string, string[]>;
        Object.entries(errorData).forEach(([field, messages]) => {
          if (Array.isArray(messages) && messages.length > 0) {
            form.setError(field as keyof UpdateUserSchema, {
              message: messages[0],
            });
          }
        });
      } else {
        setGlobalError(renderFetchBaseQueryError(error, t));
      }
    }
  });

  if (!selectedUser) return null;

  return (
    <div className="flex flex-col gap-4 mx-4">
      {globalError && <div className="mb-4">{globalError}</div>}
      <Form {...form}>
        <div className="max-h-[60vh] overflow-y-auto pr-2">
          <div className="space-y-6">
            {/* Informations personnelles */}
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
                        <Input {...field} className="h-10" />
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
                        <Input {...field} className="h-10" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            {/* Informations du compte */}
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
                      <Input {...field} className="h-10" />
                    </FormControl>
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
                      <Input {...field} type="email" className="h-10" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            {/* Rôles et permissions */}
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
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="is_active"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4 bg-muted/50">
                    <div className="space-y-0.5">
                      <FormLabel className="text-sm font-medium">
                        {t("is_active")}
                      </FormLabel>
                    </div>
                    <FormControl>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={(checked) => {
                          field.onChange(checked);
                          form.setValue("is_active", checked as boolean);
                        }}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />
            </div>
          </div>

          <div className="flex justify-end gap-4 mt-6">
            <IconAndButtonDisplayer
              type="cancel"
              text={t("cancel")}
              onClick={disableEditMode}
              variant="outline"
            />
            <IconAndButtonDisplayer
              type="save"
              text={isSubmitting ? t("actions.submitting") : t("save")}
              onClick={onSubmit}
              variant="default"
            />
          </div>
        </div>
      </Form>
    </div>
  );
}
