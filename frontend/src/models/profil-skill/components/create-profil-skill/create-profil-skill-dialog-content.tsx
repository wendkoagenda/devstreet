import { SkillSelect } from "@/models/skill/components/skill-select";
import { ProfilSelect } from "@/models/profil/components/profil-select";
import ActionsLayout from "@/components/layouts/actions-layout";
import { Input } from "@/components/ui/input";
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
  createProfilSkillSchema,
  type CreateProfilSkillFormValues,
  type CreateProfilSkillSchema,
} from "../../schema";
import { useCreateProfilSkillMutation } from "../../api";
import { useProfilSkillStore } from "../../slice";

export default function CreateProfilSkillDialogContent() {
  const { t } = useTranslation();
  const [createItem, { isLoading: isSubmitting }] = useCreateProfilSkillMutation();
  const { closeCreateDialog } = useProfilSkillStore();
  const [globalError, setGlobalError] = useState<React.ReactNode>(null);

  const form = useForm<CreateProfilSkillFormValues, unknown, CreateProfilSkillSchema>({
    resolver: zodResolver(createProfilSkillSchema()) as Resolver<
      CreateProfilSkillFormValues,
      unknown,
      CreateProfilSkillSchema
    >,
    defaultValues: {
      level: '',
      years: '',
    },
  });

  const onSubmit = async (payload: CreateProfilSkillSchema) => {
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
            form.setError(field as keyof CreateProfilSkillSchema, {
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
              name="skill_id"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Compétence *
                  </FormLabel>
                  <FormControl>
                    <SkillSelect
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
              name="level"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Level *                  </FormLabel>
                  <FormControl>
                    <Input {...formField} className="h-10" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="years"
              render={({ field: formField }) => (
                <FormItem className="">
                  <FormLabel className="text-sm font-medium">
                    Years *                  </FormLabel>
                  <FormControl>
                    <Input {...formField} className="h-10" />
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