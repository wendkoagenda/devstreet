import { CountrySelect } from "@/components/geo/country-select";
import { CitySelect } from "@/components/geo/city-select";
import { PhoneInput } from "@/components/geo/phone-input";
import { UserSelect } from "@/models/user/components/user-select";
import { CompanySelect } from "@/models/company/components/company-select";
import { buildMediaUrl } from "@/helpers/displayers/media-url-builder";
import { Checkbox } from "@/components/ui/checkbox";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
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
import { zodResolver } from "@hookform/resolvers/zod";
import type { FetchBaseQueryError } from "@reduxjs/toolkit/query";
import { useForm, type Resolver } from "react-hook-form";
import { useTranslation } from "react-i18next";
import { useState } from "react";
import { useUpdateProfilMutation } from "../../api";
import {
  updateProfilSchema,
  type UpdateProfilFormValues,
  type UpdateProfilSchema,
} from "../../schema";
import { useProfilStore } from "../../slice";
import { renderFetchBaseQueryError } from "@/helpers/api/global-error-catcher";

export default function EditProfilDialogContent() {
  const { t } = useTranslation();
  const { selectedProfil, closeShowDialog, disableEditMode } = useProfilStore();
  const [updateItem, { isLoading: isSubmitting }] = useUpdateProfilMutation();
  const [globalError, setGlobalError] = useState<React.ReactNode>(null);
  const [files, setFiles] = useState<Record<string, File | undefined>>({});

  const form = useForm<UpdateProfilFormValues, unknown, UpdateProfilSchema>({
    resolver: zodResolver(updateProfilSchema(t)) as Resolver<
      UpdateProfilFormValues,
      unknown,
      UpdateProfilSchema
    >,
    defaultValues: selectedProfil
      ? {
          id: selectedProfil.id,
          company_id: selectedProfil.company?.id,
          user_id: selectedProfil.user_id,
          is_company_owner: selectedProfil.is_company_owner,
          slug: selectedProfil.slug,
          headline: selectedProfil.headline,
          bio: selectedProfil.bio,
          phone: selectedProfil.phone,
          country: selectedProfil.country,
          city: selectedProfil.city,
          remote: selectedProfil.remote,
          timezone: selectedProfil.timezone,
          default_hours_per_week: selectedProfil.default_hours_per_week,
          is_open_to_work: selectedProfil.is_open_to_work,
          daily_rate:
            selectedProfil.daily_rate != null
              ? Number(selectedProfil.daily_rate)
              : undefined,
          currency: selectedProfil.currency,
          years_of_experience: selectedProfil.years_of_experience,
          languages: selectedProfil.languages,
          github_url: selectedProfil.github_url,
          linkedin_url: selectedProfil.linkedin_url,
          portfolio_url: selectedProfil.portfolio_url,
          cv_visibility: selectedProfil.cv_visibility,
          embedding: selectedProfil.embedding,
        }
      : {},
  });

  const onSubmit = form.handleSubmit(async (data) => {
    try {
      setGlobalError(null);
      await updateItem({ ...data, _files: files }).unwrap();
      closeShowDialog();
      CreationSuccessSonner("Element mis a jour avec succes");
    } catch (err) {
      const error = err as FetchBaseQueryError;
      if (error.status === 400 && error.data) {
        const errorData = error.data as Record<string, string[]>;
        Object.entries(errorData).forEach(([field, messages]) => {
          if (Array.isArray(messages) && messages.length > 0) {
            form.setError(field as keyof UpdateProfilSchema, {
              message: messages[0],
            });
          }
        });
      } else {
        setGlobalError(renderFetchBaseQueryError(error, t));
      }
    }
  });

  if (!selectedProfil) return null;

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
                      selectedItem={selectedProfil.company}
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
              {selectedProfil.photo && (
                <a
                  href={buildMediaUrl(selectedProfil.photo!)}
                  target="_blank"
                  rel="noreferrer"
                  className="text-sm text-primary underline block mb-2"
                >
                  Fichier actuel
                </a>
              )}
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
                    <PhoneInput value={formField.value ?? ""} onChange={formField.onChange} defaultCountry={form.watch("country")} />
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
                    <CountrySelect value={formField.value ?? ""} onChange={(code) => { if (code !== formField.value) form.setValue("city", ""); formField.onChange(code); }} />
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
                    <CitySelect country={form.watch("country")} value={formField.value ?? ""} onChange={formField.onChange} />
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