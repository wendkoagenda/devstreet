import { ProfilSelect } from "@/models/profil/components/profil-select";
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
import { useUpdatePrestationMutation } from "../../api";
import {
  updatePrestationSchema,
  type UpdatePrestationFormValues,
  type UpdatePrestationSchema,
} from "../../schema";
import { usePrestationStore } from "../../slice";
import { renderFetchBaseQueryError } from "@/helpers/api/global-error-catcher";

export default function EditPrestationDialogContent() {
  const { t } = useTranslation();
  const { selectedPrestation, closeShowDialog, disableEditMode } = usePrestationStore();
  const [updateItem, { isLoading: isSubmitting }] = useUpdatePrestationMutation();
  const [globalError, setGlobalError] = useState<React.ReactNode>(null);
  const [files, setFiles] = useState<Record<string, File | undefined>>({});

  const form = useForm<UpdatePrestationFormValues, unknown, UpdatePrestationSchema>({
    resolver: zodResolver(updatePrestationSchema(t)) as Resolver<
      UpdatePrestationFormValues,
      unknown,
      UpdatePrestationSchema
    >,
    defaultValues: selectedPrestation
      ? {
          id: selectedPrestation.id,
          profil_id: selectedPrestation.profil?.id,
          title: selectedPrestation.title,
          slug: selectedPrestation.slug,
          description: selectedPrestation.description,
          category: selectedPrestation.category,
          price:
            selectedPrestation.price != null
              ? Number(selectedPrestation.price)
              : undefined,
          currency: selectedPrestation.currency,
          delivery_days: selectedPrestation.delivery_days,
          revisions: selectedPrestation.revisions,
          is_active: selectedPrestation.is_active,
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
            form.setError(field as keyof UpdatePrestationSchema, {
              message: messages[0],
            });
          }
        });
      } else {
        setGlobalError(renderFetchBaseQueryError(error, t));
      }
    }
  });

  if (!selectedPrestation) return null;

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
                      selectedItem={selectedPrestation.profil}
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
            <FormField
              control={form.control}
              name="description"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Description *                  </FormLabel>
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
              name="category"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Category *                  </FormLabel>
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
                        <SelectItem value="web">Web</SelectItem>
                        <SelectItem value="mobile">Mobile</SelectItem>
                        <SelectItem value="design">Design</SelectItem>
                        <SelectItem value="devops">DevOps</SelectItem>
                        <SelectItem value="data">Data</SelectItem>
                        <SelectItem value="other">Autre</SelectItem>
                      </SelectContent>
                    </Select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="price"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Price *                  </FormLabel>
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
              name="delivery_days"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Delivery days *                  </FormLabel>
                  <FormControl>
                    <Input {...formField} className="h-10" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="revisions"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Revisions *                  </FormLabel>
                  <FormControl>
                    <Input {...formField} className="h-10" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormItem>
              <FormLabel className="text-sm font-medium">
                Cover image              </FormLabel>
              {selectedPrestation.cover_image && (
                <a
                  href={buildMediaUrl(selectedPrestation.cover_image!)}
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
                    setFiles((prev) => ({ ...prev, cover_image: file }));
                  }}
                />
              </FormControl>
              {files.cover_image && (
                <p className="text-sm text-muted-foreground">{files.cover_image?.name}</p>
              )}
            </FormItem>
            <FormField
              control={form.control}
              name="is_active"
              render={({ field: formField }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4 bg-muted/50">
                  <FormLabel className="text-sm font-medium">
                    Is active *                  </FormLabel>
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