import { useState, type ReactNode } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Briefcase, Pencil, Trash2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form } from "@/components/ui/form";
import { Skeleton } from "@/components/ui/skeleton";
import { CreationErrorSonner, CreationSuccessSonner } from "@/helpers/api/feed-backs";
import { formatDate } from "@/models/marketplace-offers/labels";
import {
  CheckboxField,
  SelectField,
  TextareaField,
  TextField,
} from "@/models/marketplace-space/components/form-fields";
import { applySubmitError } from "@/models/marketplace-space/components/submit-error";
import {
  useCreateExperienceMutation,
  useDeleteExperienceMutation,
  useGetMyExperiencesQuery,
  useUpdateExperienceMutation,
} from "../api";
import {
  experienceFormSchema,
  experienceToForm,
  experienceToPayload,
  type Experience,
  type ExperienceFormValues,
} from "../schema";

const CONTRACT_OPTIONS = [
  { value: "cdi", label: "CDI" },
  { value: "cdd", label: "CDD" },
  { value: "freelance", label: "Freelance" },
  { value: "stage", label: "Stage" },
];

function ExperienceForm({ experience, onDone }: { experience: Experience | null; onDone: () => void }) {
  const { t } = useTranslation();
  const [create, { isLoading: isCreating }] = useCreateExperienceMutation();
  const [update, { isLoading: isUpdating }] = useUpdateExperienceMutation();
  const [globalError, setGlobalError] = useState<ReactNode>(null);

  const form = useForm<ExperienceFormValues>({
    resolver: zodResolver(experienceFormSchema),
    defaultValues: experienceToForm(experience),
  });
  const isCurrent = form.watch("is_current");

  const onSubmit = async (values: ExperienceFormValues) => {
    setGlobalError(null);
    const payload = experienceToPayload(values);
    try {
      if (experience) {
        await update({ id: experience.id, ...payload }).unwrap();
      } else {
        await create(payload).unwrap();
      }
      CreationSuccessSonner("Expérience enregistrée");
      onDone();
    } catch (err) {
      setGlobalError(applySubmitError(err, form, t));
    }
  };

  return (
    <Form {...form}>
      <form className="flex flex-col gap-4" noValidate onSubmit={form.handleSubmit(onSubmit)}>
        {globalError}
        <div className="grid gap-3 sm:grid-cols-2">
          <TextField control={form.control} name="title" label="Poste" />
          <TextField control={form.control} name="company_name" label="Entreprise" />
          <TextField control={form.control} name="location" label="Lieu" />
          <SelectField
            control={form.control}
            name="contract_type"
            label="Contrat"
            options={CONTRACT_OPTIONS}
          />
          <TextField control={form.control} name="start_date" label="Début" type="date" />
          {isCurrent ? null : (
            <TextField control={form.control} name="end_date" label="Fin" type="date" />
          )}
          <CheckboxField
            control={form.control}
            name="is_current"
            label="Poste actuel"
            className="sm:col-span-2"
          />
          <TextareaField
            control={form.control}
            name="description"
            label="Description"
            rows={3}
            className="sm:col-span-2"
          />
          <TextField
            control={form.control}
            name="technologies"
            label="Technologies"
            placeholder="Django, React, PostgreSQL"
            className="sm:col-span-2"
          />
        </div>
        <div className="flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onDone}>
            Annuler
          </Button>
          <Button type="submit" disabled={isCreating || isUpdating}>
            Enregistrer
          </Button>
        </div>
      </form>
    </Form>
  );
}

/** Expériences du profil : liste, ajout, modification et suppression (elles alimentent le CV). */
export function ExperiencesCard({ className }: { className?: string }) {
  const { data, isLoading } = useGetMyExperiencesQuery();
  const [remove] = useDeleteExperienceMutation();
  const [editing, setEditing] = useState<Experience | "new" | null>(null);

  const onDelete = async (experience: Experience) => {
    try {
      await remove(experience.id).unwrap();
      CreationSuccessSonner("Expérience supprimée");
    } catch {
      CreationErrorSonner("Impossible de supprimer cette expérience");
    }
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Briefcase className="size-4" />
          Mes expériences
        </CardTitle>
        <CardDescription>Votre parcours, repris dans votre CV automatique.</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        {editing ? (
          <ExperienceForm
            key={editing === "new" ? "new" : editing.id}
            experience={editing === "new" ? null : editing}
            onDone={() => setEditing(null)}
          />
        ) : (
          <>
            {isLoading ? <Skeleton className="h-16 w-full" /> : null}
            {data && data.length === 0 ? (
              <p className="text-sm text-muted-foreground">Aucune expérience renseignée.</p>
            ) : null}
            {(data ?? []).map((experience) => (
              <div
                key={experience.id}
                className="flex items-start justify-between gap-2 rounded-lg border border-border p-3"
              >
                <div className="flex min-w-0 flex-col gap-0.5">
                  <span className="text-sm font-medium text-foreground">
                    {experience.title}, {experience.company_name}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {formatDate(experience.start_date)} –{" "}
                    {experience.is_current || !experience.end_date
                      ? "aujourd'hui"
                      : formatDate(experience.end_date)}
                    {experience.location ? ` · ${experience.location}` : ""}
                  </span>
                </div>
                <div className="flex shrink-0 gap-1">
                  <Button
                    type="button"
                    size="icon"
                    variant="ghost"
                    aria-label={`Modifier ${experience.title}`}
                    onClick={() => setEditing(experience)}
                  >
                    <Pencil className="size-4" />
                  </Button>
                  <Button
                    type="button"
                    size="icon"
                    variant="ghost"
                    aria-label={`Supprimer ${experience.title}`}
                    onClick={() => onDelete(experience)}
                  >
                    <Trash2 className="size-4" />
                  </Button>
                </div>
              </div>
            ))}
            <Button type="button" variant="outline" onClick={() => setEditing("new")}>
              Ajouter une expérience
            </Button>
          </>
        )}
      </CardContent>
    </Card>
  );
}
