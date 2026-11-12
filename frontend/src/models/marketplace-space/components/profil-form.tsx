import { useState, type ReactNode } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { Form } from "@/components/ui/form";
import { CreationSuccessSonner } from "@/helpers/api/feed-backs";
import { useCreateMyProfilMutation, useUpdateMyProfilMutation } from "../api";
import {
  COUNTRIES,
  CURRENCIES,
  CV_VISIBILITIES,
  TIMEZONES,
} from "../options";
import {
  profilFormSchema,
  profilToForm,
  profilToPayload,
  type MyProfil,
  type ProfilFormValues,
} from "../schema";
import {
  CheckboxField,
  SelectField,
  TextareaField,
  TextField,
} from "./form-fields";
import { applySubmitError } from "./submit-error";

type ProfilFormProps = {
  /** Profil à modifier ; null pour créer le profil de l'utilisateur. */
  profil: MyProfil | null;
};

const countryOptions = COUNTRIES.map((country) => ({
  value: country.code,
  label: country.name,
}));
const timezoneOptions = TIMEZONES.map((zone) => ({ value: zone, label: zone }));
const currencyOptions = CURRENCIES.map((currency) => ({
  value: currency.code,
  label: `${currency.code} — ${currency.name}`,
}));

/** Formulaire du profil marketplace (création et modification). */
export function ProfilForm({ profil }: ProfilFormProps) {
  const { t } = useTranslation();
  const [createProfil, { isLoading: isCreating }] = useCreateMyProfilMutation();
  const [updateProfil, { isLoading: isUpdating }] = useUpdateMyProfilMutation();
  const [globalError, setGlobalError] = useState<ReactNode>(null);
  const isEdit = profil !== null;

  const form = useForm<ProfilFormValues>({
    resolver: zodResolver(profilFormSchema),
    defaultValues: profilToForm(profil),
  });

  const onSubmit = async (values: ProfilFormValues) => {
    setGlobalError(null);
    const payload = profilToPayload(values);
    try {
      if (isEdit) {
        await updateProfil(payload).unwrap();
        CreationSuccessSonner("Profil enregistré");
      } else {
        await createProfil(payload).unwrap();
        CreationSuccessSonner("Profil créé");
      }
    } catch (err) {
      setGlobalError(applySubmitError(err, form, t));
    }
  };

  /** Propose le fuseau horaire du pays choisi tant que l'utilisateur n'a pas choisi le sien. */
  const suggestTimezone = (code: string) => {
    if (form.formState.dirtyFields.timezone && form.getValues("timezone")) {
      return;
    }
    const zone = COUNTRIES.find((country) => country.code === code)?.timezone;
    if (zone) form.setValue("timezone", zone, { shouldValidate: true });
  };

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="flex flex-col gap-6"
        noValidate
      >
        {globalError}

        <div className="grid gap-4 sm:grid-cols-2">
          <TextField
            control={form.control}
            name="headline"
            label="Accroche"
            placeholder="Ex. Développeur web junior, Django et React"
            className="sm:col-span-2"
          />
          <TextareaField
            control={form.control}
            name="bio"
            label="Présentation"
            description="Résumé affiché en tête de votre CV."
            className="sm:col-span-2"
          />
          <SelectField
            control={form.control}
            name="country"
            label="Pays"
            options={countryOptions}
            onValueChange={suggestTimezone}
          />
          <TextField control={form.control} name="city" label="Ville" />
          <SelectField
            control={form.control}
            name="timezone"
            label="Fuseau horaire"
            options={timezoneOptions}
          />
          <TextField control={form.control} name="phone" label="Téléphone" />
          <TextField
            control={form.control}
            name="languages"
            label="Langues"
            description="Séparées par des virgules."
            placeholder="Français, anglais"
            className="sm:col-span-2"
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <TextField
            control={form.control}
            name="years_of_experience"
            label="Années d'expérience"
            type="number"
          />
          <TextField
            control={form.control}
            name="default_hours_per_week"
            label="Heures par semaine"
            description="Capacité par défaut, hors périodes du calendrier."
            type="number"
          />
          <TextField
            control={form.control}
            name="daily_rate"
            label="Tarif journalier"
            description="Indicatif, facultatif."
          />
          <SelectField
            control={form.control}
            name="currency"
            label="Devise"
            options={currencyOptions}
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <CheckboxField
            control={form.control}
            name="is_open_to_work"
            label="Ouvert aux opportunités"
            description="Votre profil apparaît dans les recommandations."
          />
          <CheckboxField
            control={form.control}
            name="remote"
            label="Télétravail possible"
          />
          <SelectField
            control={form.control}
            name="cv_visibility"
            label="CV visible par"
            options={CV_VISIBILITIES}
            className="sm:col-span-2"
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-3">
          <TextField
            control={form.control}
            name="github_url"
            label="GitHub"
            placeholder="https://github.com/…"
          />
          <TextField
            control={form.control}
            name="linkedin_url"
            label="LinkedIn"
            placeholder="https://linkedin.com/in/…"
          />
          <TextField
            control={form.control}
            name="portfolio_url"
            label="Portfolio"
            placeholder="https://…"
          />
        </div>

        <div className="flex justify-end">
          <Button type="submit" disabled={isCreating || isUpdating}>
            {isEdit ? "Enregistrer" : "Créer mon profil"}
          </Button>
        </div>
      </form>
    </Form>
  );
}
