import { useState, type ReactNode } from "react";
import { CityField, CountryField } from "@/components/geo/geo-form-fields";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useTranslation } from "react-i18next";
import { Check } from "lucide-react";
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
import { cn } from "@/lib/utils";
import {
  DateField,
  SelectField,
  TextareaField,
  TextField,
} from "@/models/marketplace-space/components/form-fields";
import { applySubmitError } from "@/models/marketplace-space/components/submit-error";
import { CURRENCIES, countryName } from "@/models/marketplace-space/options";
import { useCreateMyOfferMutation, useUpdateMyOfferMutation } from "../api";
import {
  DURATION_UNIT_LABELS,
  LEVEL_LABELS,
  OFFER_TYPE_LABELS,
  WORK_MODE_LABELS,
  formatDate,
  formatDuration,
} from "../labels";
import { offerFormSchema, offerToForm, offerToPayload, type Offer, type OfferFormValues } from "../schema";
import { OfferAiPrompt } from "./offer-ai-prompt";
import { SkillPicker } from "./skill-picker";

const toOptions = (labels: Record<string, string>) =>
  Object.entries(labels).map(([value, label]) => ({ value, label }));

const typeOptions = toOptions(OFFER_TYPE_LABELS);
const levelOptions = toOptions(LEVEL_LABELS);
const durationUnitOptions = toOptions(DURATION_UNIT_LABELS);
const workModeOptions = toOptions(WORK_MODE_LABELS);
const PERIOD_LABELS: Record<string, string> = {
  month: "Par mois",
  day: "Par jour",
  fixed: "Forfait",
};
const periodOptions = toOptions(PERIOD_LABELS);
const currencyOptions = CURRENCIES.map((currency) => ({ value: currency.code, label: currency.code }));

type Step = {
  title: string;
  description: string;
  /** Champs validés avant de passer à l'étape suivante. */
  fields: (keyof OfferFormValues)[];
};

const STEPS: Step[] = [
  {
    title: "L'offre",
    description: "Que recherchez-vous ?",
    fields: ["title", "description", "type", "contract_duration", "contract_duration_unit", "experience_level"],
  },
  {
    title: "Lieu et dates",
    description: "Où et quand la mission ou le poste démarre-t-il ?",
    fields: ["work_mode", "country", "city", "start_date", "deadline"],
  },
  {
    title: "Budget et compétences",
    description: "Quel budget et quelles compétences attendez-vous ?",
    fields: ["budget_min", "budget_max", "currency", "budget_period", "required_skill_ids"],
  },
  {
    title: "Récapitulatif",
    description: "Vérifiez l'offre, puis publiez-la ou gardez-la en brouillon.",
    fields: [],
  },
];

function Recap({ values }: { values: OfferFormValues }) {
  const budget =
    values.budget_min || values.budget_max
      ? `${values.budget_min || "—"} à ${values.budget_max || "—"} ${values.currency} · ${
          PERIOD_LABELS[values.budget_period] ?? values.budget_period
        }`
      : "Non précisé";
  const rows: [string, string][] = [
    ["Titre", values.title],
    ["Contrat", `${OFFER_TYPE_LABELS[values.type]}${values.contract_duration ? ` · ${formatDuration(values.contract_duration, values.contract_duration_unit)}` : ""}`],
    ["Niveau", LEVEL_LABELS[values.experience_level]],
    ["Mode de travail", WORK_MODE_LABELS[values.work_mode]],
    ["Lieu", [values.city, countryName(values.country)].filter(Boolean).join(", ")],
    ["Démarrage", values.start_date ? formatDate(values.start_date) : "Non précisé"],
    ["Date limite", values.deadline ? formatDate(values.deadline) : "Non précisée"],
    ["Budget", budget],
    ["Compétences", values.required_skill_ids.length ? `${values.required_skill_ids.length} sélectionnée(s)` : "Aucune"],
  ];
  return (
    <dl className="grid gap-x-4 gap-y-2 rounded-lg border border-border bg-muted/30 p-4 text-sm sm:grid-cols-[auto_1fr]">
      {rows.map(([label, value]) => (
        <div key={label} className="contents">
          <dt className="text-muted-foreground">{label}</dt>
          <dd className="font-medium text-foreground">{value}</dd>
        </div>
      ))}
    </dl>
  );
}

/**
 * Formulaire d'offre en plusieurs étapes : offre, lieu et dates, budget et compétences, puis récapitulatif.
 * Il sert à la boîte de dialogue « Créer une offre » et à la page de modification d'une offre.
 */
export function OfferStepsForm({
  offer = null,
  defaults,
  onSaved,
}: {
  /** Offre à modifier ; absente pour en créer une. */
  offer?: Offer | null;
  /** Pays et ville de l'entreprise, proposés pour une nouvelle offre. */
  defaults?: { country?: string; city?: string };
  /** Appelé après l'enregistrement, avec l'offre enregistrée. */
  onSaved?: (offer: Offer) => void;
}) {
  const { t } = useTranslation();
  const [createOffer, { isLoading: isCreating }] = useCreateMyOfferMutation();
  const [updateOffer, { isLoading: isUpdating }] = useUpdateMyOfferMutation();
  const isEdit = offer !== null;
  const isLoading = isCreating || isUpdating;
  const [stepIndex, setStepIndex] = useState(0);
  const [globalError, setGlobalError] = useState<ReactNode>(null);

  const form = useForm<OfferFormValues>({
    resolver: zodResolver(offerFormSchema),
    defaultValues: offerToForm(offer, defaults),
  });

  const step = STEPS[stepIndex];
  const isLast = stepIndex === STEPS.length - 1;

  const goNext = async () => {
    const valid = await form.trigger(step.fields);
    if (valid) setStepIndex((index) => Math.min(index + 1, STEPS.length - 1));
  };

  const goBack = () => {
    setGlobalError(null);
    setStepIndex((index) => Math.max(index - 1, 0));
  };

  const save = (publish: boolean) =>
    form.handleSubmit(async (values) => {
      setGlobalError(null);
      try {
        const payload = offerToPayload(values);
        const saved = offer
          ? await updateOffer({ id: offer.id, ...payload }).unwrap()
          : await createOffer({ ...payload, publish }).unwrap();
        CreationSuccessSonner(isEdit ? "Offre enregistrée" : publish ? "Offre publiée" : "Brouillon enregistré");
        onSaved?.(saved);
      } catch (err) {
        setGlobalError(applySubmitError(err, form, t));
        // Une erreur du serveur sur un champ d'une étape précédente y ramène l'utilisateur
        const data = (err as { data?: Record<string, unknown> }).data;
        if (data && typeof data === "object") {
          const failing = STEPS.findIndex((item) => item.fields.some((field) => field in data));
          if (failing >= 0) setStepIndex(failing);
        }
      }
    });

  return (
    <Form {...form}>
      <form
        // Entrée dans un champ avance d'une étape ; l'envoi se fait uniquement par les boutons du récapitulatif
        onSubmit={(event) => {
          event.preventDefault();
          if (!isLast) void goNext();
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
                <div className={cn("h-1.5 rounded-full", done || current ? "bg-primary" : "bg-muted")} />
                <span
                  className={cn(
                    "flex items-center gap-1 text-xs",
                    current ? "font-medium text-foreground" : "text-muted-foreground"
                  )}
                >
                  {done ? <Check className="size-3" aria-hidden /> : null}
                  <span className="truncate">
                    {index + 1}. {item.title}
                  </span>
                </span>
              </div>
            );
          })}
        </nav>

        <div>
          <h3 className="text-sm font-semibold text-foreground">
            Étape {stepIndex + 1} sur {STEPS.length} · {step.title}
          </h3>
          <p className="text-xs text-muted-foreground">
            {isLast && isEdit ? "Vérifiez l'offre, puis enregistrez vos modifications." : step.description}
          </p>
        </div>

        {globalError}

        {/* Les étapes restent montées (masquées) pour conserver les valeurs saisies */}
        <div className={cn("grid gap-4 sm:grid-cols-2", stepIndex !== 0 && "hidden")}>
          {/* Prompt de génération de l'offre (création uniquement) */}
          {isEdit ? null : <OfferAiPrompt className="sm:col-span-2" />}
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
          <TextField control={form.control} name="contract_duration" label="Durée" type="number" placeholder="Ex. 3" />
          <SelectField
            control={form.control}
            name="contract_duration_unit"
            label="Unité de durée"
            options={durationUnitOptions}
          />
          <SelectField control={form.control} name="experience_level" label="Niveau" options={levelOptions} />
        </div>

        <div className={cn("grid gap-4 sm:grid-cols-2", stepIndex !== 1 && "hidden")}>
          <SelectField control={form.control} name="work_mode" label="Mode de travail" options={workModeOptions} />
          <CountryField control={form.control} name="country" label="Pays" resetOnChange={["city"]} />
          <CityField control={form.control} name="city" label="Ville" countryName="country" />
          <DateField
            control={form.control}
            name="start_date"
            label="Date de démarrage"
            placeholder="Choisir la date de démarrage"
          />
          {/* La date limite de candidature précède le démarrage */}
          <DateField
            control={form.control}
            name="deadline"
            label="Date limite de candidature"
            placeholder="Choisir la date limite"
            max={form.watch("start_date") || undefined}
          />
        </div>

        <div className={cn("flex flex-col gap-4", stepIndex !== 2 && "hidden")}>
          <div className="grid gap-4 sm:grid-cols-2">
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
        </div>

        {isLast ? <Recap values={form.getValues()} /> : null}

        <div className="flex flex-wrap items-center justify-between gap-2">
          <Button type="button" variant="outline" onClick={goBack} disabled={stepIndex === 0 || isLoading}>
            Précédent
          </Button>
          {isLast ? (
            isEdit ? (
              <Button type="button" disabled={isLoading} onClick={save(false)}>
                Enregistrer
              </Button>
            ) : (
              <div className="flex flex-wrap justify-end gap-2">
                <Button type="button" variant="outline" disabled={isLoading} onClick={save(false)}>
                  Enregistrer le brouillon
                </Button>
                <Button type="button" disabled={isLoading} onClick={save(true)}>
                  Publier l'offre
                </Button>
              </div>
            )
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
