import { useFormContext, useWatch, type Control, type FieldValues, type Path, type PathValue } from "react-hook-form";
import {
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { CitySelect } from "./city-select";
import { CountrySelect } from "./country-select";
import { PhoneInput } from "./phone-input";

type BaseProps<T extends FieldValues> = {
  control: Control<T>;
  name: Path<T>;
  label: string;
  description?: string;
  className?: string;
};

/**
 * Pays (drapeau, nom, recherche). `resetOnChange` vide les champs qui dépendent du pays (ex. la ville)
 * quand l'utilisateur en choisit un autre.
 */
export function CountryField<T extends FieldValues>({
  control,
  name,
  label,
  description,
  className,
  resetOnChange = [],
  onValueChange,
}: BaseProps<T> & {
  resetOnChange?: Path<T>[];
  /** Appelé après le changement de pays (ex. proposer le fuseau horaire). */
  onValueChange?: (code: string) => void;
}) {
  const form = useFormContext<T>();
  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem className={className}>
          <FormLabel>{label}</FormLabel>
          <FormControl>
            <CountrySelect
              value={field.value as string}
              disabled={field.disabled}
              onChange={(code) => {
                if (code !== field.value) {
                  for (const dependent of resetOnChange) {
                    form.setValue(dependent, "" as PathValue<T, Path<T>>, { shouldDirty: true });
                  }
                }
                field.onChange(code);
                onValueChange?.(code);
              }}
            />
          </FormControl>
          {description ? <FormDescription>{description}</FormDescription> : null}
          <FormMessage />
        </FormItem>
      )}
    />
  );
}

/** Ville du pays saisi dans `countryName` (liste avec recherche, saisie libre possible). */
export function CityField<T extends FieldValues>({
  control,
  name,
  label,
  description,
  className,
  countryName,
}: BaseProps<T> & { countryName: Path<T> }) {
  const country = useWatch({ control, name: countryName }) as string | undefined;
  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem className={className}>
          <FormLabel>{label}</FormLabel>
          <FormControl>
            <CitySelect
              country={country}
              value={field.value as string}
              disabled={field.disabled}
              onChange={field.onChange}
            />
          </FormControl>
          {description ? <FormDescription>{description}</FormDescription> : null}
          <FormMessage />
        </FormItem>
      )}
    />
  );
}

/** Téléphone avec indicatif ; l'indicatif suit le pays saisi dans `countryName` tant que le numéro est vide. */
export function PhoneField<T extends FieldValues>({
  control,
  name,
  label,
  description,
  className,
  countryName,
}: BaseProps<T> & { countryName?: Path<T> }) {
  const country = useWatch({ control, name: (countryName ?? name) as Path<T> }) as string | undefined;
  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem className={className}>
          <FormLabel>{label}</FormLabel>
          <FormControl>
            <PhoneInput
              value={field.value as string}
              onChange={field.onChange}
              disabled={field.disabled}
              defaultCountry={countryName ? country : undefined}
            />
          </FormControl>
          {description ? <FormDescription>{description}</FormDescription> : null}
          <FormMessage />
        </FormItem>
      )}
    />
  );
}
