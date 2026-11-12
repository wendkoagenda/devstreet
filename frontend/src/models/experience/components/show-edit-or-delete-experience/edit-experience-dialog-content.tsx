import { ProfilSelect } from "@/models/profil/components/profil-select";
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
import { useUpdateExperienceMutation } from "../../api";
import {
  updateExperienceSchema,
  type UpdateExperienceFormValues,
  type UpdateExperienceSchema,
} from "../../schema";
import { useExperienceStore } from "../../slice";
import { renderFetchBaseQueryError } from "@/helpers/api/global-error-catcher";

export default function EditExperienceDialogContent() {
  const { t } = useTranslation();
  const { selectedExperience, closeShowDialog, disableEditMode } = useExperienceStore();
  const [updateItem, { isLoading: isSubmitting }] = useUpdateExperienceMutation();
  const [globalError, setGlobalError] = useState<React.ReactNode>(null);

  const form = useForm<UpdateExperienceFormValues, unknown, UpdateExperienceSchema>({
    resolver: zodResolver(updateExperienceSchema(t)) as Resolver<
      UpdateExperienceFormValues,
      unknown,
      UpdateExperienceSchema
    >,
    defaultValues: selectedExperience
      ? {
          id: selectedExperience.id,
          profil_id: selectedExperience.profil?.id,
          title: selectedExperience.title,
          company_name: selectedExperience.company_name,
          location: selectedExperience.location,
          contract_type: selectedExperience.contract_type,
          start_date: selectedExperience.start_date,
          end_date: selectedExperience.end_date,
          is_current: selectedExperience.is_current,
          description: selectedExperience.description,
          technologies: selectedExperience.technologies,
        }
      : {},
  });

  const onSubmit = form.handleSubmit(async (data) => {
    try {
      setGlobalError(null);
      await updateItem({ ...data }).unwrap();
      closeShowDialog();
      CreationSuccessSonner("Element mis a jour avec succes");
    } catch (err) {
      const error = err as FetchBaseQueryError;
      if (error.status === 400 && error.data) {
        const errorData = error.data as Record<string, string[]>;
        Object.entries(errorData).forEach(([field, messages]) => {
          if (Array.isArray(messages) && messages.length > 0) {
            form.setError(field as keyof UpdateExperienceSchema, {
              message: messages[0],
            });
          }
        });
      } else {
        setGlobalError(renderFetchBaseQueryError(error, t));
      }
    }
  });

  if (!selectedExperience) return null;

  return (
    <div className="flex flex-col gap-4 mx-4">
      {globalError && <div className="mb-4">{globalError}</div>}
      <Form {...form}>
        <div className="max-h-[60vh] overflow-y-auto px-2 py-1">
          <div className="space-y-4">
            <FormField
              control={form.control}
              name="profil_id"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Profil *
                  </FormLabel>
                  <FormControl>
                    <ProfilSelect
                      value={formField.value}
                      onChange={formField.onChange}
                      selectedItem={selectedExperience.profil}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="title"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Title *                  </FormLabel>
                  <FormControl>
                    <Input {...formField} className="h-10" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="company_name"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Company name *                  </FormLabel>
                  <FormControl>
                    <Input {...formField} className="h-10" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="location"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Location                  </FormLabel>
                  <FormControl>
                    <Input {...formField} className="h-10" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="contract_type"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Contract type                  </FormLabel>
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
                        <SelectItem value="cdi">CDI</SelectItem>
                        <SelectItem value="cdd">CDD</SelectItem>
                        <SelectItem value="freelance">Freelance</SelectItem>
                        <SelectItem value="stage">Stage</SelectItem>
                      </SelectContent>
                    </Select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="start_date"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Start date *                  </FormLabel>
                  <FormControl>
                    <Input type="date" {...formField} className="h-10" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="end_date"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    End date                  </FormLabel>
                  <FormControl>
                    <Input type="date" {...formField} className="h-10" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="is_current"
              render={({ field: formField }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4 bg-muted/50">
                  <FormLabel className="text-sm font-medium">
                    Is current *                  </FormLabel>
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
              name="description"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Description                  </FormLabel>
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
              name="technologies"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Technologies                  </FormLabel>
                  <FormControl>
                    <Input {...formField} className="h-10" />
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