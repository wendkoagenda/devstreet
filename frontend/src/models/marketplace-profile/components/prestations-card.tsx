import { useState, type ReactNode } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Package, Pencil, Trash2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form } from "@/components/ui/form";
import { Skeleton } from "@/components/ui/skeleton";
import { CreationErrorSonner, CreationSuccessSonner } from "@/helpers/api/feed-backs";
import {
  CheckboxField,
  SelectField,
  TextareaField,
  TextField,
} from "@/models/marketplace-space/components/form-fields";
import { applySubmitError } from "@/models/marketplace-space/components/submit-error";
import { CURRENCIES } from "@/models/marketplace-space/options";
import {
  useCreatePrestationMutation,
  useDeletePrestationMutation,
  useGetMyPrestationsQuery,
  useUpdatePrestationMutation,
} from "../api";
import {
  PRESTATION_CATEGORY_LABELS,
  prestationFormSchema,
  prestationToForm,
  prestationToPayload,
  type Prestation,
  type PrestationFormValues,
} from "../schema";

const categoryOptions = Object.entries(PRESTATION_CATEGORY_LABELS).map(([value, label]) => ({
  value,
  label,
}));
const currencyOptions = CURRENCIES.map((currency) => ({
  value: currency.code,
  label: currency.code,
}));

function PrestationForm({ prestation, onDone }: { prestation: Prestation | null; onDone: () => void }) {
  const { t } = useTranslation();
  const [create, { isLoading: isCreating }] = useCreatePrestationMutation();
  const [update, { isLoading: isUpdating }] = useUpdatePrestationMutation();
  const [globalError, setGlobalError] = useState<ReactNode>(null);

  const form = useForm<PrestationFormValues>({
    resolver: zodResolver(prestationFormSchema),
    defaultValues: prestationToForm(prestation),
  });

  const onSubmit = async (values: PrestationFormValues) => {
    setGlobalError(null);
    const payload = prestationToPayload(values);
    try {
      if (prestation) {
        await update({ id: prestation.id, ...payload }).unwrap();
      } else {
        await create(payload).unwrap();
      }
      CreationSuccessSonner("Prestation enregistrée");
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
          <TextField control={form.control} name="title" label="Titre" className="sm:col-span-2" />
          <TextareaField
            control={form.control}
            name="description"
            label="Description"
            rows={3}
            className="sm:col-span-2"
          />
          <SelectField control={form.control} name="category" label="Catégorie" options={categoryOptions} />
          <TextField control={form.control} name="delivery_days" label="Délai (jours)" type="number" />
          <TextField control={form.control} name="price" label="Prix" />
          <SelectField control={form.control} name="currency" label="Devise" options={currencyOptions} />
          <TextField control={form.control} name="revisions" label="Retouches incluses" type="number" />
          <CheckboxField
            control={form.control}
            name="is_active"
            label="Visible sur mon profil"
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

/** Prestations packagées du profil : liste, ajout, modification et suppression (UC-14). */
export function PrestationsCard({ className }: { className?: string }) {
  const { data, isLoading } = useGetMyPrestationsQuery();
  const [remove] = useDeletePrestationMutation();
  const [editing, setEditing] = useState<Prestation | "new" | null>(null);

  const onDelete = async (prestation: Prestation) => {
    try {
      await remove(prestation.id).unwrap();
      CreationSuccessSonner("Prestation supprimée");
    } catch {
      CreationErrorSonner("Impossible de supprimer cette prestation");
    }
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Package className="size-4" />
          Mes prestations
        </CardTitle>
        <CardDescription>
          Services à prix fixe visibles sur votre profil et repris dans le CV.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        {editing ? (
          <PrestationForm
            key={editing === "new" ? "new" : editing.id}
            prestation={editing === "new" ? null : editing}
            onDone={() => setEditing(null)}
          />
        ) : (
          <>
            {isLoading ? <Skeleton className="h-16 w-full" /> : null}
            {data && data.length === 0 ? (
              <p className="text-sm text-muted-foreground">Aucune prestation pour l'instant.</p>
            ) : null}
            {(data ?? []).map((prestation) => (
              <div
                key={prestation.id}
                className="flex items-start justify-between gap-2 rounded-lg border border-border p-3"
              >
                <div className="flex min-w-0 flex-col gap-0.5">
                  <span className="flex flex-wrap items-center gap-2 text-sm font-medium text-foreground">
                    {prestation.title}
                    <Badge variant={prestation.is_active ? "default" : "secondary"}>
                      {prestation.is_active ? "Visible" : "Masquée"}
                    </Badge>
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {PRESTATION_CATEGORY_LABELS[prestation.category]} ·{" "}
                    {Number(prestation.price).toLocaleString("fr-FR")} {prestation.currency} ·{" "}
                    {prestation.delivery_days} j
                  </span>
                </div>
                <div className="flex shrink-0 gap-1">
                  <Button
                    type="button"
                    size="icon"
                    variant="ghost"
                    aria-label={`Modifier ${prestation.title}`}
                    onClick={() => setEditing(prestation)}
                  >
                    <Pencil className="size-4" />
                  </Button>
                  <Button
                    type="button"
                    size="icon"
                    variant="ghost"
                    aria-label={`Supprimer ${prestation.title}`}
                    onClick={() => onDelete(prestation)}
                  >
                    <Trash2 className="size-4" />
                  </Button>
                </div>
              </div>
            ))}
            <Button type="button" variant="outline" onClick={() => setEditing("new")}>
              Ajouter une prestation
            </Button>
          </>
        )}
      </CardContent>
    </Card>
  );
}
