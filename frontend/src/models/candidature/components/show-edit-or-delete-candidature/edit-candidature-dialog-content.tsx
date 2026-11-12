import { ProfilSelect } from "@/models/profil/components/profil-select";
import { OfferSelect } from "@/models/offer/components/offer-select";
import { buildMediaUrl } from "@/helpers/displayers/media-url-builder";
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
import { useUpdateCandidatureMutation } from "../../api";
import {
  updateCandidatureSchema,
  type UpdateCandidatureFormValues,
  type UpdateCandidatureSchema,
} from "../../schema";
import { useCandidatureStore } from "../../slice";
import { renderFetchBaseQueryError } from "@/helpers/api/global-error-catcher";

export default function EditCandidatureDialogContent() {
  const { t } = useTranslation();
  const { selectedCandidature, closeShowDialog, disableEditMode } = useCandidatureStore();
  const [updateItem, { isLoading: isSubmitting }] = useUpdateCandidatureMutation();
  const [globalError, setGlobalError] = useState<React.ReactNode>(null);
  const [files, setFiles] = useState<Record<string, File | undefined>>({});

  const form = useForm<UpdateCandidatureFormValues, unknown, UpdateCandidatureSchema>({
    resolver: zodResolver(updateCandidatureSchema(t)) as Resolver<
      UpdateCandidatureFormValues,
      unknown,
      UpdateCandidatureSchema
    >,
    defaultValues: selectedCandidature
      ? {
          id: selectedCandidature.id,
          offer_id: selectedCandidature.offer?.id,
          profil_id: selectedCandidature.profil?.id,
          message: selectedCandidature.message,
          status: selectedCandidature.status,
          ai_match_score:
            selectedCandidature.ai_match_score != null
              ? Number(selectedCandidature.ai_match_score)
              : undefined,
          decided_at: selectedCandidature.decided_at,
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
            form.setError(field as keyof UpdateCandidatureSchema, {
              message: messages[0],
            });
          }
        });
      } else {
        setGlobalError(renderFetchBaseQueryError(error, t));
      }
    }
  });

  if (!selectedCandidature) return null;

  return (
    <div className="flex flex-col gap-4 mx-4">
      {globalError && <div className="mb-4">{globalError}</div>}
      <Form {...form}>
        <div className="max-h-[60vh] overflow-y-auto px-2 py-1">
          <div className="space-y-4">
            <FormField
              control={form.control}
              name="offer_id"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Offre *
                  </FormLabel>
                  <FormControl>
                    <OfferSelect
                      value={formField.value}
                      onChange={formField.onChange}
                      selectedItem={selectedCandidature.offer}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
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
                      selectedItem={selectedCandidature.profil}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="message"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Message                  </FormLabel>
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
                        <SelectItem value="sent">Envoyée</SelectItem>
                        <SelectItem value="shortlisted">Présélectionnée</SelectItem>
                        <SelectItem value="rejected">Refusée</SelectItem>
                        <SelectItem value="accepted">Acceptée</SelectItem>
                      </SelectContent>
                    </Select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="ai_match_score"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Ai match score                  </FormLabel>
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
            <FormItem>
              <FormLabel className="text-sm font-medium">
                Cv snapshot              </FormLabel>
              {selectedCandidature.cv_snapshot && (
                <a
                  href={buildMediaUrl(selectedCandidature.cv_snapshot!)}
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
                  accept=".pdf"
                  className="h-10"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    setFiles((prev) => ({ ...prev, cv_snapshot: file }));
                  }}
                />
              </FormControl>
              {files.cv_snapshot && (
                <p className="text-sm text-muted-foreground">{files.cv_snapshot?.name}</p>
              )}
            </FormItem>
            <FormField
              control={form.control}
              name="decided_at"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Decided at                  </FormLabel>
                  <FormControl>
                    <Input type="date" {...formField} className="h-10" />
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