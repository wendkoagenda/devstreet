import { useState, type ReactNode } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { Form } from "@/components/ui/form";
import { CreationSuccessSonner } from "@/helpers/api/feed-backs";
import { useCreateMyProfilMutation } from "@/models/marketplace-space/api";
import { SelectField, TextField } from "@/models/marketplace-space/components/form-fields";
import { applySubmitError } from "@/models/marketplace-space/components/submit-error";
import { COUNTRIES } from "@/models/marketplace-space/options";
import { devProfilStepSchema, type DevProfilStepValues } from "../schema";
import { OnboardingShell } from "./onboarding-shell";

const countryOptions = COUNTRIES.map((country) => ({
  value: country.code,
  label: country.name,
}));

/** Étape dev 1/2 : l'essentiel du profil (titre, pays, ville). */
export function DevProfilStep({
  stepIndex,
  stepCount,
  onDone,
  onSkip,
}: {
  stepIndex: number;
  stepCount: number;
  onDone: () => void;
  onSkip: () => void;
}) {
  const { t } = useTranslation();
  const [createProfil, { isLoading }] = useCreateMyProfilMutation();
  const [globalError, setGlobalError] = useState<ReactNode>(null);

  const form = useForm<DevProfilStepValues>({
    resolver: zodResolver(devProfilStepSchema),
    defaultValues: { headline: "", country: "", city: "" },
  });

  const submit = async (values: DevProfilStepValues) => {
    setGlobalError(null);
    const country = values.country.toUpperCase();
    const timezone = COUNTRIES.find((item) => item.code === country)?.timezone;
    try {
      await createProfil({
        headline: values.headline,
        country,
        city: values.city,
        ...(timezone ? { timezone } : {}),
      }).unwrap();
      CreationSuccessSonner("Profil dev créé");
      onDone();
    } catch (err) {
      // Les erreurs de champ s'affichent sous le champ, la saisie est conservée
      setGlobalError(applySubmitError(err, form, t));
    }
  };

  return (
    <OnboardingShell
      title="Votre profil développeur"
      description="L'essentiel pour être visible. Vous complétez le reste (CV, expériences, liens) quand vous voulez."
      stepIndex={stepIndex}
      stepCount={stepCount}
    >
      <Form {...form}>
        <form onSubmit={form.handleSubmit(submit)} className="flex flex-col gap-4" noValidate>
          <TextField
            control={form.control}
            name="headline"
            label="Titre"
            placeholder="Ex. Développeur full-stack React / Django"
          />
          <SelectField control={form.control} name="country" label="Pays" options={countryOptions} />
          <TextField control={form.control} name="city" label="Ville" />

          {globalError ? (
            <div role="alert" className="text-sm text-destructive">
              {globalError}
            </div>
          ) : null}

          <div className="mt-2 flex items-center justify-between gap-3">
            <Button type="button" variant="ghost" onClick={onSkip} disabled={isLoading}>
              Terminer plus tard
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? "Création…" : "Continuer"}
            </Button>
          </div>
        </form>
      </Form>
    </OnboardingShell>
  );
}
