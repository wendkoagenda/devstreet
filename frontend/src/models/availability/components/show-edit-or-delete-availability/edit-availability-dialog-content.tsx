import { ProfilSelect } from "@/models/profil/components/profil-select";
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
import { useUpdateAvailabilityMutation } from "../../api";
import {
  updateAvailabilitySchema,
  type UpdateAvailabilityFormValues,
  type UpdateAvailabilitySchema,
} from "../../schema";
import { useAvailabilityStore } from "../../slice";
import { renderFetchBaseQueryError } from "@/helpers/api/global-error-catcher";

export default function EditAvailabilityDialogContent() {
  const { t } = useTranslation();
  const { selectedAvailability, closeShowDialog, disableEditMode } = useAvailabilityStore();
  const [updateItem, { isLoading: isSubmitting }] = useUpdateAvailabilityMutation();
  const [globalError, setGlobalError] = useState<React.ReactNode>(null);

  const form = useForm<UpdateAvailabilityFormValues, unknown, UpdateAvailabilitySchema>({
    resolver: zodResolver(updateAvailabilitySchema()) as Resolver<
      UpdateAvailabilityFormValues,
      unknown,
      UpdateAvailabilitySchema
    >,
    defaultValues: selectedAvailability
      ? {
          id: selectedAvailability.id,
          profil_id: selectedAvailability.profil?.id,
          start_date: selectedAvailability.start_date,
          end_date: selectedAvailability.end_date,
          status: selectedAvailability.status,
          hours_per_week: selectedAvailability.hours_per_week,
          source: selectedAvailability.source,
          note: selectedAvailability.note,
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
            form.setError(field as keyof UpdateAvailabilitySchema, {
              message: messages[0],
            });
          }
        });
      } else {
        setGlobalError(renderFetchBaseQueryError(error, t));
      }
    }
  });

  if (!selectedAvailability) return null;

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
                      selectedItem={selectedAvailability.profil}
                    />
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
                    <Input type="date" {...formField} value={formField.value ?? ""} className="h-10" />
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
                    End date *                  </FormLabel>
                  <FormControl>
                    <Input type="date" {...formField} value={formField.value ?? ""} className="h-10" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="status"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Status *                  </FormLabel>
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
                        <SelectItem value="available">Disponible</SelectItem>
                        <SelectItem value="partial">Partiel</SelectItem>
                        <SelectItem value="busy">Occupé</SelectItem>
                        <SelectItem value="leave">Congé</SelectItem>
                      </SelectContent>
                    </Select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="hours_per_week"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Hours per week                  </FormLabel>
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
            <FormField
              control={form.control}
              name="source"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Source *                  </FormLabel>
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
                        <SelectItem value="manual">Saisie manuelle</SelectItem>
                        <SelectItem value="mission">Mission</SelectItem>
                      </SelectContent>
                    </Select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="note"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Note                  </FormLabel>
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