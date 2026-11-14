import { useState, type ReactNode } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useTranslation } from "react-i18next";
import { Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Form } from "@/components/ui/form";
import { CreationSuccessSonner } from "@/helpers/api/feed-backs";
import { cn } from "@/lib/utils";
import { useCreateMyCompanyMutation } from "../api";
import { COMPANY_SIZES, COUNTRIES, SECTORS } from "../options";
import {
  companyFormSchema,
  companyToForm,
  companyToPayload,
  type CompanyFormValues,
} from "../schema";
import { SelectField, TextareaField, TextField } from "./form-fields";
import { applySubmitError } from "./submit-error";

const countryOptions = COUNTRIES.map((country) => ({
  value: country.code,
  label: country.name,
}));

type Step = {
  title: string;
  description: string;
  /** Champs validés avant de passer à l'étape suivante. */
  fields: (keyof CompanyFormValues)[];
};

const STEPS: Step[] = [
  {
    title: "Identité",
    description: "Comment s'appelle votre entreprise et que fait-elle ?",
    fields: ["name", "sector", "size", "description"],
  },
  {
    title: "Localisation",
    description: "Où se trouve votre entreprise ?",
    fields: ["country", "city", "address"],
  },
  {
    title: "Contact",
    description: "Comment les développeurs peuvent-ils vous joindre ?",
    fields: ["contact_email", "phone", "website"],
  },
];

/** Formulaire de création d'entreprise en plusieurs étapes (identité, localisation, contact). */
export function CompanyStepsForm({ onCreated }: { onCreated?: () => void }) {
  const { t } = useTranslation();
  const [createCompany, { isLoading }] = useCreateMyCompanyMutation();
  const [stepIndex, setStepIndex] = useState(0);
  const [globalError, setGlobalError] = useState<ReactNode>(null);

  const form = useForm<CompanyFormValues>({
    resolver: zodResolver(companyFormSchema),
    defaultValues: companyToForm(null),
  });

  const step = STEPS[stepIndex];
  const isLast = stepIndex === STEPS.length - 1;

  const goNext = async () => {
    // On ne passe à l'étape suivante que si les champs de l'étape courante sont valides
    const valid = await form.trigger(step.fields);
    if (valid) setStepIndex((index) => Math.min(index + 1, STEPS.length - 1));
  };

  const goBack = () => {
    setGlobalError(null);
    setStepIndex((index) => Math.max(index - 1, 0));
  };

  const submit = async (values: CompanyFormValues) => {
    setGlobalError(null);
    try {
      await createCompany(companyToPayload(values)).unwrap();
      CreationSuccessSonner("Entreprise créée");
      onCreated?.();
    } catch (err) {
      setGlobalError(applySubmitError(err, form, t));
      // Une erreur du serveur sur un champ d'une étape précédente y ramène l'utilisateur
      const data = (err as { data?: Record<string, unknown> }).data;
      if (data && typeof data === "object") {
        const failing = STEPS.findIndex((item) =>
          item.fields.some((field) => field in data)
        );
        if (failing >= 0) setStepIndex(failing);
      }
    }
  };

  const handleSubmit = form.handleSubmit(submit);

  return (
    <Form {...form}>
      <form
        // Entrée dans un champ avance d'une étape ; seule la dernière étape envoie le formulaire
        onSubmit={(event) => {
          event.preventDefault();
          if (isLast) void handleSubmit(event);
          else void goNext();
        }}
        className="flex flex-col gap-5"
        noValidate
      >
        <nav aria-label="Progression" className="flex items-center gap-2">
          {STEPS.map((item, index) => {
            const done = index < stepIndex;
            const current = index === stepIndex;
            return (
              <div
                key={item.title}
                className="flex flex-1 flex-col gap-1.5"
                aria-current={current ? "step" : undefined}
              >
                <div
                  className={cn(
                    "h-1.5 rounded-full",
                    done || current ? "bg-primary" : "bg-muted"
                  )}
                />
                <span
                  className={cn(
                    "flex items-center gap-1 text-xs",
                    current ? "font-medium text-foreground" : "text-muted-foreground"
                  )}
                >
                  {done ? <Check className="size-3" aria-hidden /> : null}
                  {index + 1}. {item.title}
                </span>
              </div>
            );
          })}
        </nav>

        <div>
          <h3 className="text-sm font-semibold text-foreground">
            Étape {stepIndex + 1} sur {STEPS.length} · {step.title}
          </h3>
          <p className="text-xs text-muted-foreground">{step.description}</p>
        </div>

        {globalError}

        {/* Les étapes restent montées (masquées) pour conserver les valeurs saisies */}
        <div className={cn("grid gap-4 sm:grid-cols-2", stepIndex !== 0 && "hidden")}>
          <TextField
            control={form.control}
            name="name"
            label="Nom de l'entreprise"
            className="sm:col-span-2"
          />
          <SelectField control={form.control} name="sector" label="Secteur" options={SECTORS} />
          <SelectField control={form.control} name="size" label="Taille" options={COMPANY_SIZES} />
          <TextareaField
            control={form.control}
            name="description"
            label="Présentation"
            className="sm:col-span-2"
          />
        </div>

        <div className={cn("grid gap-4 sm:grid-cols-2", stepIndex !== 1 && "hidden")}>
          <SelectField
            control={form.control}
            name="country"
            label="Pays"
            options={countryOptions}
          />
          <TextField control={form.control} name="city" label="Ville" />
          <TextField
            control={form.control}
            name="address"
            label="Adresse"
            className="sm:col-span-2"
          />
        </div>

        <div className={cn("grid gap-4 sm:grid-cols-2", stepIndex !== 2 && "hidden")}>
          <TextField
            control={form.control}
            name="contact_email"
            label="E-mail de contact"
            type="email"
          />
          <TextField control={form.control} name="phone" label="Téléphone" />
          <TextField
            control={form.control}
            name="website"
            label="Site web"
            placeholder="https://…"
            className="sm:col-span-2"
          />
        </div>

        <div className="flex items-center justify-between gap-2">
          <Button
            type="button"
            variant="outline"
            onClick={goBack}
            disabled={stepIndex === 0 || isLoading}
          >
            Précédent
          </Button>
          {isLast ? (
            <Button type="submit" disabled={isLoading}>
              Créer mon entreprise
            </Button>
          ) : (
            <Button type="button" onClick={() => void goNext()}>
              Suivant
            </Button>
          )}
        </div>
      </form>
    </Form>
  );
}
