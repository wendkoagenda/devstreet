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
import { useUpdateConnectionMutation } from "../../api";
import {
  updateConnectionSchema,
  type UpdateConnectionFormValues,
  type UpdateConnectionSchema,
} from "../../schema";
import { useConnectionStore } from "../../slice";
import { renderFetchBaseQueryError } from "@/helpers/api/global-error-catcher";

export default function EditConnectionDialogContent() {
  const { t } = useTranslation();
  const { selectedConnection, closeShowDialog, disableEditMode } = useConnectionStore();
  const [updateItem, { isLoading: isSubmitting }] = useUpdateConnectionMutation();
  const [globalError, setGlobalError] = useState<React.ReactNode>(null);

  const form = useForm<UpdateConnectionFormValues, unknown, UpdateConnectionSchema>({
    resolver: zodResolver(updateConnectionSchema()) as Resolver<
      UpdateConnectionFormValues,
      unknown,
      UpdateConnectionSchema
    >,
    defaultValues: selectedConnection
      ? {
          id: selectedConnection.id,
          profil_a_id: selectedConnection.profil_a?.id,
          profil_b_id: selectedConnection.profil_b?.id,
          status: selectedConnection.status,
          matched_at: selectedConnection.matched_at,
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
            form.setError(field as keyof UpdateConnectionSchema, {
              message: messages[0],
            });
          }
        });
      } else {
        setGlobalError(renderFetchBaseQueryError(error, t));
      }
    }
  });

  if (!selectedConnection) return null;

  return (
    <div className="flex flex-col gap-4 mx-4">
      {globalError && <div className="mb-4">{globalError}</div>}
      <Form {...form}>
        <div className="max-h-[60vh] overflow-y-auto px-2 py-1">
          <div className="space-y-4">
            <FormField
              control={form.control}
              name="profil_a_id"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Profil A *
                  </FormLabel>
                  <FormControl>
                    <ProfilSelect
                      value={formField.value}
                      onChange={formField.onChange}
                      selectedItem={selectedConnection.profil_a}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="profil_b_id"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Profil B *
                  </FormLabel>
                  <FormControl>
                    <ProfilSelect
                      value={formField.value}
                      onChange={formField.onChange}
                      selectedItem={selectedConnection.profil_b}
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
                        <SelectItem value="matched">Connectés</SelectItem>
                        <SelectItem value="blocked">Bloquée</SelectItem>
                      </SelectContent>
                    </Select>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="matched_at"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Matched at *                  </FormLabel>
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