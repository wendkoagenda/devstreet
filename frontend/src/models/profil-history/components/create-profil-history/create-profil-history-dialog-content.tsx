import { ProfilSelect } from "@/models/profil/components/profil-select";
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
  createProfilHistorySchema,
  type CreateProfilHistoryFormValues,
  type CreateProfilHistorySchema,
} from "../../schema";
import { useCreateProfilHistoryMutation } from "../../api";
import { useProfilHistoryStore } from "../../slice";

export default function CreateProfilHistoryDialogContent() {
  const { t } = useTranslation();
  const [createItem, { isLoading: isSubmitting }] = useCreateProfilHistoryMutation();
  const { closeCreateDialog } = useProfilHistoryStore();
  const [globalError, setGlobalError] = useState<React.ReactNode>(null);

  const form = useForm<CreateProfilHistoryFormValues, unknown, CreateProfilHistorySchema>({
    resolver: zodResolver(createProfilHistorySchema(t)) as Resolver<
      CreateProfilHistoryFormValues,
      unknown,
      CreateProfilHistorySchema
    >,
    defaultValues: {
      field: '',
      old_value: '',
      new_value: '',
      source: "manual",
    },
  });

  const onSubmit = async (payload: CreateProfilHistorySchema) => {
    try {
      setGlobalError(null);
      await createItem({ ...payload }).unwrap();
      form.reset();
      closeCreateDialog();
      CreationSuccessSonner("Element cree avec succes");
    } catch (err) {
      const error = err as FetchBaseQueryError;
      if (error.status === 400 && error.data) {
        const errorData = error.data as Record<string, string[]>;
        Object.entries(errorData).forEach(([field, messages]) => {
          if (Array.isArray(messages) && messages.length > 0) {
            form.setError(field as keyof CreateProfilHistorySchema, {
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
              name="field"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Field *                  </FormLabel>
                  <FormControl>
                    <Input {...formField} className="h-10" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="old_value"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Old value                  </FormLabel>
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
              name="new_value"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    New value                  </FormLabel>
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
                        <SelectItem value="ai">IA</SelectItem>
                        <SelectItem value="system">Système</SelectItem>
                      </SelectContent>
                    </Select>
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