import { useState, type ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { CreationSuccessSonner } from "@/helpers/api/feed-backs";
import {
  SelectField,
  TextareaField,
  TextField,
} from "@/models/marketplace-space/components/form-fields";
import { applySubmitError } from "@/models/marketplace-space/components/submit-error";
import { COUNTRIES, CURRENCIES } from "@/models/marketplace-space/options";
import { useCreateMyOfferMutation, useUpdateMyOfferMutation } from "../api";
import {
  LEVEL_LABELS,
  OFFER_TYPE_LABELS,
  WORK_MODE_LABELS,
} from "../labels";
import {
  offerFormSchema,
  offerToForm,
  offerToPayload,
  type Offer,
  type OfferFormValues,
} from "../schema";
import { SkillPicker } from "./skill-picker";

type OfferFormProps = {
  /** Offre à modifier ; null pour en créer une. */
  offer: Offer | null;
  /** Pays et ville de l'entreprise, proposés pour une nouvelle offre. */
  defaults?: { country?: string; city?: string };
};

const toOptions = (labels: Record<string, string>) =>
  Object.entries(labels).map(([value, label]) => ({ value, label }));

const typeOptions = toOptions(OFFER_TYPE_LABELS);
const levelOptions = toOptions(LEVEL_LABELS);
const workModeOptions = toOptions(WORK_MODE_LABELS);
const periodOptions = [
  { value: "month", label: "Par mois" },
  { value: "day", label: "Par jour" },
  { value: "fixed", label: "Forfait" },
];
const countryOptions = COUNTRIES.map((country) => ({
  value: country.code,
  label: country.name,
}));
const currencyOptions = CURRENCIES.map((currency) => ({
  value: currency.code,
  label: currency.code,
}));

/** Formulaire d'offre : brouillon ou publication à la création, enregistrement à la modification. */
export function OfferForm({ offer, defaults }: OfferFormProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [createOffer, { isLoading: isCreating }] = useCreateMyOfferMutation();
  const [updateOffer, { isLoading: isUpdating }] = useUpdateMyOfferMutation();
  const [globalError, setGlobalError] = useState<ReactNode>(null);
  const isEdit = offer !== null;

  const form = useForm<OfferFormValues>({
    resolver: zodResolver(offerFormSchema),
    defaultValues: offerToForm(offer, defaults),
  });

  const save = (publish: boolean) =>
    form.handleSubmit(async (values) => {
      setGlobalError(null);
      const payload = offerToPayload(values);
      try {
        const saved = offer
          ? await updateOffer({ id: offer.id, ...payload }).unwrap()
          : await createOffer({ ...payload, publish }).unwrap();
        CreationSuccessSonner(
          isEdit ? "Offre enregistrée" : publish ? "Offre publiée" : "Brouillon enregistré"
        );
        navigate(`/marketplace/my-offers/${saved.id}`);
      } catch (err) {
        setGlobalError(applySubmitError(err, form, t));
      }
    });

  const busy = isCreating || isUpdating;

  return (
    <Form {...form}>
      <form className="flex flex-col gap-6" noValidate onSubmit={(event) => event.preventDefault()}>
        {globalError}

        <div className="grid gap-4 sm:grid-cols-2">
          <TextField
            control={form.control}
            name="title"
            label="Titre"
            placeholder="Ex. Développeur mobile React Native"
            className="sm:col-span-2"
          />
          <TextareaField
            control={form.control}
            name="description"
            label="Description"
            rows={5}
            className="sm:col-span-2"
          />
          <SelectField control={form.control} name="type" label="Type de contrat" options={typeOptions} />
          <TextField
            control={form.control}
            name="contract_duration"
            label="Durée (mois)"
            type="number"
          />
          <SelectField control={form.control} name="experience_level" label="Niveau" options={levelOptions} />
          <SelectField control={form.control} name="work_mode" label="Mode de travail" options={workModeOptions} />
          <SelectField control={form.control} name="country" label="Pays" options={countryOptions} />
          <TextField control={form.control} name="city" label="Ville" />
          <TextField control={form.control} name="start_date" label="Démarrage" type="date" />
          <TextField control={form.control} name="deadline" label="Date limite de candidature" type="date" />
        </div>

        <div className="grid gap-4 sm:grid-cols-4">
          <TextField control={form.control} name="budget_min" label="Budget minimum" />
          <TextField control={form.control} name="budget_max" label="Budget maximum" />
          <SelectField control={form.control} name="currency" label="Devise" options={currencyOptions} />
          <SelectField control={form.control} name="budget_period" label="Période" options={periodOptions} />
        </div>

        <FormField
          control={form.control}
          name="required_skill_ids"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Compétences requises</FormLabel>
              <FormControl>
                <SkillPicker value={field.value} onChange={field.onChange} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex flex-wrap justify-end gap-2">
          {isEdit ? (
            <Button type="button" disabled={busy} onClick={save(false)}>
              Enregistrer
            </Button>
          ) : (
            <>
              <Button type="button" variant="outline" disabled={busy} onClick={save(false)}>
                Enregistrer le brouillon
              </Button>
              <Button type="button" disabled={busy} onClick={save(true)}>
                Publier l'offre
              </Button>
            </>
          )}
        </div>
      </form>
    </Form>
  );
}
