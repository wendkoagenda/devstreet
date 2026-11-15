import { useState, type ReactNode } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { Form } from "@/components/ui/form";
import { CreationSuccessSonner } from "@/helpers/api/feed-backs";
import {
  DateField,
  SelectField,
  TextField,
} from "@/models/marketplace-space/components/form-fields";
import { applySubmitError } from "@/models/marketplace-space/components/submit-error";
import { useCreateAvailabilityMutation, useUpdateAvailabilityMutation } from "../api";
import {
  AVAILABILITY_LABELS,
  availabilityFormSchema,
  availabilityToForm,
  availabilityToPayload,
  type Availability,
  type AvailabilityFormValues,
} from "../schema";

/**
 * Statuts proposés pour une période. Sans période on est disponible : on n'ajoute donc que des plages occupées
 * (occupé, partiellement occupé, congé). « Disponible » n'est proposé que pour modifier une ancienne période qui l'avait.
 */
function statusOptionsFor(period: { status: string } | null) {
  return Object.entries(AVAILABILITY_LABELS)
    .filter(([value]) => value !== "available" || period?.status === "available")
    .map(([value, label]) => ({ value, label }));
}

type AvailabilityFormProps = {
  /** Période à modifier ; null pour en ajouter une. */
  period: Availability | null;
  onDone: () => void;
};

/** Ajout ou modification d'une période de disponibilité. */
export function AvailabilityForm({ period, onDone }: AvailabilityFormProps) {
  const { t } = useTranslation();
  const [create, { isLoading: isCreating }] = useCreateAvailabilityMutation();
  const [update, { isLoading: isUpdating }] = useUpdateAvailabilityMutation();
  const [globalError, setGlobalError] = useState<ReactNode>(null);

  const form = useForm<AvailabilityFormValues>({
    resolver: zodResolver(availabilityFormSchema),
    defaultValues: availabilityToForm(period),
  });

  const onSubmit = async (values: AvailabilityFormValues) => {
    setGlobalError(null);
    const payload = availabilityToPayload(values);
    try {
      if (period) {
        await update({ id: period.id, ...payload }).unwrap();
      } else {
        await create(payload).unwrap();
      }
      CreationSuccessSonner(t("marketplace.availability.saved"));
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
          <DateField
            control={form.control}
            name="start_date"
            label={t("marketplace.availability.from")}
            placeholder={t("marketplace.availability.pick_date")}
          />
          <DateField
            control={form.control}
            name="end_date"
            label={t("marketplace.availability.to")}
            placeholder={t("marketplace.availability.pick_date")}
          />
          <SelectField
            control={form.control}
            name="status"
            label={t("marketplace.availability.status")}
            options={statusOptionsFor(period)}
          />
          <TextField
            control={form.control}
            name="hours_per_week"
            label={t("marketplace.availability.hours_per_week")}
            type="number"
          />
        </div>
        <div className="flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onDone}>
            {t("actions.cancel")}
          </Button>
          <Button type="submit" disabled={isCreating || isUpdating}>
            {t("actions.save")}
          </Button>
        </div>
      </form>
    </Form>
  );
}
