import { useState, type ReactNode } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { Form } from "@/components/ui/form";
import { CreationSuccessSonner } from "@/helpers/api/feed-backs";
import {
  useCreateMyCompanyMutation,
  useUpdateMyCompanyMutation,
} from "../api";
import { COMPANY_SIZES, COUNTRIES, SECTORS } from "../options";
import {
  companyFormSchema,
  companyToForm,
  companyToPayload,
  type CompanyFormValues,
  type MyCompany,
} from "../schema";
import {
  SelectField,
  TextareaField,
  TextField,
} from "./form-fields";
import { applySubmitError } from "./submit-error";

type CompanyFormProps = {
  /** Entreprise à modifier ; null pour créer l'entreprise de l'utilisateur. */
  company: MyCompany | null;
  /** Seul le propriétaire peut modifier une entreprise existante. */
  canEdit: boolean;
  /** Appelé après la création de l'entreprise (ex. pour fermer la boîte de dialogue). */
  onCreated?: () => void;
  /** Appelé après l'enregistrement des modifications d'une entreprise existante. */
  onUpdated?: () => void;
};

const countryOptions = COUNTRIES.map((country) => ({
  value: country.code,
  label: country.name,
}));

/** Formulaire de l'entreprise de l'utilisateur (création, puis modification par son propriétaire). */
export function CompanyForm({ company, canEdit, onCreated, onUpdated }: CompanyFormProps) {
  const { t } = useTranslation();
  const [createCompany, { isLoading: isCreating }] =
    useCreateMyCompanyMutation();
  const [updateCompany, { isLoading: isUpdating }] =
    useUpdateMyCompanyMutation();
  const [globalError, setGlobalError] = useState<ReactNode>(null);
  const isEdit = company !== null;

  const form = useForm<CompanyFormValues>({
    resolver: zodResolver(companyFormSchema),
    defaultValues: companyToForm(company),
  });

  const onSubmit = async (values: CompanyFormValues) => {
    setGlobalError(null);
    const payload = companyToPayload(values);
    try {
      if (isEdit) {
        await updateCompany(payload).unwrap();
        CreationSuccessSonner("Entreprise enregistrée");
        onUpdated?.();
      } else {
        await createCompany(payload).unwrap();
        CreationSuccessSonner("Entreprise créée");
        onCreated?.();
      }
    } catch (err) {
      setGlobalError(applySubmitError(err, form, t));
    }
  };

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="flex flex-col gap-6"
        noValidate
      >
        {globalError}

        <fieldset
          disabled={isEdit && !canEdit}
          className="grid gap-4 sm:grid-cols-2"
        >
          <TextField
            control={form.control}
            name="name"
            label="Nom de l'entreprise"
            className="sm:col-span-2"
          />
          <TextareaField
            control={form.control}
            name="description"
            label="Présentation"
            className="sm:col-span-2"
          />
          <SelectField
            control={form.control}
            name="sector"
            label="Secteur"
            options={SECTORS}
          />
          <SelectField
            control={form.control}
            name="size"
            label="Taille"
            options={COMPANY_SIZES}
          />
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
        </fieldset>

        {!isEdit || canEdit ? (
          <div className="flex justify-end">
            <Button type="submit" disabled={isCreating || isUpdating}>
              {isEdit ? "Enregistrer" : "Créer mon entreprise"}
            </Button>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">
            Seul le propriétaire de l'entreprise peut la modifier.
          </p>
        )}
      </form>
    </Form>
  );
}
