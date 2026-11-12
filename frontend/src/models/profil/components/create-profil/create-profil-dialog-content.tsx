import { UserSelect } from "@/models/user/components/user-select";
import { CompanySelect } from "@/models/company/components/company-select";
import ActionsLayout from "@/components/layouts/actions-layout";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useForm, type Resolver } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useTranslation } from "react-i18next";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { CreationSuccessSonner } from "@/helpers/api/feed-backs";
import { renderFetchBaseQueryError } from "@/helpers/api/global-error-catcher";
import type { FetchBaseQueryError } from "@reduxjs/toolkit/query";
import { useState } from "react";
import {
  createProfilSchema,
  type CreateProfilFormValues,
  type CreateProfilSchema,
} from "../../schema";
import { useCreateProfilMutation } from "../../api";
import { useProfilStore } from "../../slice";

export default function CreateProfilDialogContent() {
  const { t } = useTranslation();
  const [createItem, { isLoading: isSubmitting }] = useCreateProfilMutation();
  const { closeCreateDialog } = useProfilStore();
  const [globalError, setGlobalError] = useState<React.ReactNode>(null);
  const [files, setFiles] = useState<Record<string, File | undefined>>({});

  const form = useForm<CreateProfilFormValues, unknown, CreateProfilSchema>({
    resolver: zodResolver(createProfilSchema(t)) as Resolver<
      CreateProfilFormValues,
      unknown,
      CreateProfilSchema
    >,
    defaultValues: {
      is_company_owner: false,
      slug: '',
      headline: '',
      bio: '',
      phone: '',
      country: '',
      city: '',
      remote: false,
      timezone: '',
      default_hours_per_week: '',
      is_open_to_work: false,
      daily_rate: undefined,
      currency: '',
      years_of_experience: '',
      languages: '',
      github_url: '',
      linkedin_url: '',
      portfolio_url: '',
      cv_visibility: "public",
      embedding: '',
    },
  });

  const onSubmit = async (payload: CreateProfilSchema) => {
    try {
      setGlobalError(null);
      await createItem({ ...payload, _files: files }).unwrap();
      form.reset();
      setFiles({});
      closeCreateDialog();
      CreationSuccessSonner("Element cree avec succes");
    } catch (err) {
      const error = err as FetchBaseQueryError;
      if (error.status === 400 && error.data) {
        const errorData = error.data as Record<string, string[]>;
        Object.entries(errorData).forEach(([field, messages]) => {
          if (Array.isArray(messages) && messages.length > 0) {
            form.setError(field as keyof CreateProfilSchema, {
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
        <div className="max-h-[60vh] overflow-y-auto px-2 py-1">
          <div className="space-y-4">
            <FormField
              control={form.control}
              name="company_id"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Entreprise
                  </FormLabel>
                  <FormControl>
                    <CompanySelect
                      value={formField.value}
                      onChange={formField.onChange}
                      clearable
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="user_id"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Compte utilisateur *
                  </FormLabel>
                  <FormControl>
                    <UserSelect
                      value={formField.value}
                      onChange={formField.onChange}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="is_company_owner"
              render={({ field: formField }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4 bg-muted/50">
                  <FormLabel className="text-sm font-medium">
                    Is company owner *                  </FormLabel>
                  <FormControl>
                    <Checkbox
                      checked={Boolean(formField.value)}
                      onCheckedChange={(checked) => formField.onChange(Boolean(checked))}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="slug"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Slug *                  </FormLabel>
                  <FormControl>
                    <Input {...formField} className="h-10" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormItem>
              <FormLabel className="text-sm font-medium">
                Photo              </FormLabel>
              <FormControl>
                <Input
                  type="file"
                  accept=".jpg,.jpeg,.png,.webp"
                  className="h-10"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    setFiles((prev) => ({ ...prev, photo: file }));
                  }}
                />
              </FormControl>
              {files.photo && (
                <p className="text-sm text-muted-foreground">{files.photo?.name}</p>
              )}
            </FormItem>
            <FormField
              control={form.control}
              name="headline"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Headline                  </FormLabel>
                  <FormControl>
                    <Input {...formField} className="h-10" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="bio"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Bio                  </FormLabel>
                  <FormControl>
                    <Textarea
                      {...formField}
                      value={formField.value ?? ""}
                      onChange={(e) =>
                        formField.onChange(e.target.value)
                      }
                      className="min-h-[100px] resize-y"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="phone"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Phone                  </FormLabel>
                  <FormControl>
                    <Input {...formField} className="h-10" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="country"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Country *                  </FormLabel>
                  <FormControl>
                    <Input {...formField} className="h-10" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="city"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    City                  </FormLabel>
                  <FormControl>
                    <Input {...formField} className="h-10" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="remote"
              render={({ field: formField }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4 bg-muted/50">
                  <FormLabel className="text-sm font-medium">
                    Remote *                  </FormLabel>
                  <FormControl>
                    <Checkbox
                      checked={Boolean(formField.value)}
                      onCheckedChange={(checked) => formField.onChange(Boolean(checked))}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="timezone"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Timezone *                  </FormLabel>
                  <FormControl>
                    <Input {...formField} className="h-10" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="default_hours_per_week"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Default hours per week *                  </FormLabel>
                  <FormControl>
                    <Input {...formField} className="h-10" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="is_open_to_work"
              render={({ field: formField }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4 bg-muted/50">
                  <FormLabel className="text-sm font-medium">
                    Is open to work *                  </FormLabel>
                  <FormControl>
                    <Checkbox
                      checked={Boolean(formField.value)}
                      onCheckedChange={(checked) => formField.onChange(Boolean(checked))}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="daily_rate"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Daily rate                  </FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      value={(formField.value as number | undefined) ?? ""}
                      onChange={(e) =>
                        formField.onChange(e.target.value === "" ? undefined : Number(e.target.value))
                      }
                      className="h-10"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="currency"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Currency *                  </FormLabel>
                  <FormControl>
                    <Input {...formField} className="h-10" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="years_of_experience"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Years of experience *                  </FormLabel>
                  <FormControl>
                    <Input {...formField} className="h-10" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="languages"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Languages                  </FormLabel>
                  <FormControl>
                    <Input {...formField} className="h-10" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="github_url"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Github url                  </FormLabel>
                  <FormControl>
                    <Input {...formField} className="h-10" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="linkedin_url"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Linkedin url                  </FormLabel>
                  <FormControl>
                    <Input {...formField} className="h-10" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="portfolio_url"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Portfolio url                  </FormLabel>
                  <FormControl>
                    <Input {...formField} className="h-10" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="cv_visibility"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Cv visibility *                  </FormLabel>
                  <FormControl>
                    <Select
                      value={
                        formField.value != null && formField.value !== undefined
                          ? String(formField.value)
                          : undefined
                      }
                      onValueChange={(value) =>
                        formField.onChange(
                          value
                        )
                      }
                    >
                      <SelectTrigger className="h-10">
                        <SelectValue placeholder="Selectionner..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="public">Public</SelectItem>
                        <SelectItem value="companies">Entreprises</SelectItem>
                        <SelectItem value="private">Privé</SelectItem>
                      </SelectContent>
                    </Select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="embedding"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Embedding                  </FormLabel>
                  <FormControl>
                    <Input
                      {...formField}
                      value={formField.value ?? ""}
                      onChange={(e) =>
                        formField.onChange(e.target.value === "" ? null : e.target.value)
                      }
                      className="h-10"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
          <ActionsLayout
            type="create"
            onSubmit={form.handleSubmit(onSubmit)}
            onCancel={closeCreateDialog}
            isSubmitting={isSubmitting}
          />
        </div>
      </Form>
    </div>
  );
}