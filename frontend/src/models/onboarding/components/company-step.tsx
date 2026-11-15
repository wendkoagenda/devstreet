import { useState, type ReactNode } from "react";
import { CountryField } from "@/components/geo/geo-form-fields";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { Form } from "@/components/ui/form";
import { CreationSuccessSonner } from "@/helpers/api/feed-backs";
import { useCreateMyCompanyMutation } from "@/models/marketplace-space/api";
import { SelectField, TextField } from "@/models/marketplace-space/components/form-fields";
import { applySubmitError } from "@/models/marketplace-space/components/submit-error";
import { COMPANY_SIZES, SECTORS } from "@/models/marketplace-space/options";
import { companyStepSchema, type CompanyStepValues } from "../schema";
import { OnboardingShell } from "./onboarding-shell";


/** Étape entreprise : l'essentiel (nom, secteur, taille, pays) sur un seul écran. */
export function CompanyStep({
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
  const [createCompany, { isLoading }] = useCreateMyCompanyMutation();
  const [globalError, setGlobalError] = useState<ReactNode>(null);

  const form = useForm<CompanyStepValues>({
    resolver: zodResolver(companyStepSchema),
    defaultValues: { name: "", sector: "other", size: "", country: "" },
  });

  const submit = async (values: CompanyStepValues) => {
    setGlobalError(null);
    try {
      await createCompany({ ...values, country: values.country.toUpperCase() }).unwrap();
      CreationSuccessSonner("Entreprise créée");
      onDone();
    } catch (err) {
      // Ex. nom déjà pris : l'erreur s'affiche sous le champ concerné, la saisie est conservée
      setGlobalError(applySubmitError(err, form, t));
    }
  };

  return (
    <OnboardingShell
      title="Votre entreprise"
      description="L'essentiel pour publier des offres. Vous complétez le reste (description, contact, logo) plus tard."
      stepIndex={stepIndex}
      stepCount={stepCount}
    >
      <Form {...form}>
        <form onSubmit={form.handleSubmit(submit)} className="flex flex-col gap-4" noValidate>
          <TextField control={form.control} name="name" label="Nom de l'entreprise" />
          <div className="grid gap-4 sm:grid-cols-2">
            <SelectField control={form.control} name="sector" label="Secteur" options={SECTORS} />
            <SelectField control={form.control} name="size" label="Taille" options={COMPANY_SIZES} />
          </div>
          <CountryField control={form.control} name="country" label="Pays" />

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
              {isLoading ? "Création…" : "Créer mon entreprise"}
            </Button>
          </div>
        </form>
      </Form>
    </OnboardingShell>
  );
}
