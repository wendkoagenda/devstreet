import { SkillSelect } from "@/models/skill/components/skill-select";
import { ProfilSelect } from "@/models/profil/components/profil-select";
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
import { useUpdateProfilSkillMutation } from "../../api";
import {
  updateProfilSkillSchema,
  type UpdateProfilSkillFormValues,
  type UpdateProfilSkillSchema,
} from "../../schema";
import { useProfilSkillStore } from "../../slice";
import { renderFetchBaseQueryError } from "@/helpers/api/global-error-catcher";

export default function EditProfilSkillDialogContent() {
  const { t } = useTranslation();
  const { selectedProfilSkill, closeShowDialog, disableEditMode } = useProfilSkillStore();
  const [updateItem, { isLoading: isSubmitting }] = useUpdateProfilSkillMutation();
  const [globalError, setGlobalError] = useState<React.ReactNode>(null);

  const form = useForm<UpdateProfilSkillFormValues, unknown, UpdateProfilSkillSchema>({
    resolver: zodResolver(updateProfilSkillSchema()) as Resolver<
      UpdateProfilSkillFormValues,
      unknown,
      UpdateProfilSkillSchema
    >,
    defaultValues: selectedProfilSkill
      ? {
          id: selectedProfilSkill.id,
          profil_id: selectedProfilSkill.profil?.id,
          skill_id: selectedProfilSkill.skill?.id,
          level: selectedProfilSkill.level,
          years: selectedProfilSkill.years,
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
            form.setError(field as keyof UpdateProfilSkillSchema, {
              message: messages[0],
            });
          }
        });
      } else {
        setGlobalError(renderFetchBaseQueryError(error, t));
      }
    }
  });

  if (!selectedProfilSkill) return null;

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
                      selectedItem={selectedProfilSkill.profil}
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
                      selectedItem={selectedProfilSkill.skill}
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