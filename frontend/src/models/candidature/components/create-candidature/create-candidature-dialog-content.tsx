import { ProfilSelect } from "@/models/profil/components/profil-select";
import { OfferSelect } from "@/models/offer/components/offer-select";
import ActionsLayout from "@/components/layouts/actions-layout";
import { Input } from "@/components/ui/input";
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
  createCandidatureSchema,
  type CreateCandidatureFormValues,
  type CreateCandidatureSchema,
} from "../../schema";
import { useCreateCandidatureMutation } from "../../api";
import { useCandidatureStore } from "../../slice";

export default function CreateCandidatureDialogContent() {
  const { t } = useTranslation();
  const [createItem, { isLoading: isSubmitting }] = useCreateCandidatureMutation();
  const { closeCreateDialog } = useCandidatureStore();
  const [globalError, setGlobalError] = useState<React.ReactNode>(null);
  const [files, setFiles] = useState<Record<string, File | undefined>>({});

  const form = useForm<CreateCandidatureFormValues, unknown, CreateCandidatureSchema>({
    resolver: zodResolver(createCandidatureSchema(t)) as Resolver<
      CreateCandidatureFormValues,
      unknown,
      CreateCandidatureSchema
    >,
    defaultValues: {
      message: '',
      status: "sent",
      ai_match_score: undefined,
      decided_at: '',
    },
  });

  const onSubmit = async (payload: CreateCandidatureSchema) => {
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
            form.setError(field as keyof CreateCandidatureSchema, {
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