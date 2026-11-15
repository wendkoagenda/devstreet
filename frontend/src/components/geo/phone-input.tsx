import { useEffect, useRef, useState } from "react";
import type { CountryCode } from "libphonenumber-js";
import { Input } from "@/components/ui/input";
import { CountrySelect } from "./country-select";
import { formatAsYouType, splitPhone, toCountryCode, toInternational } from "./phone";

export type PhoneInputProps = {
  /** Numéro au format international (« +22670123456 ») ; "" si vide. */
  value: string | null | undefined;
  onChange: (value: string) => void;
  /** Pays du formulaire : préremplit l'indicatif tant que le numéro est vide. */
  defaultCountry?: string | null;
  disabled?: boolean;
  placeholder?: string;
};

/**
 * Téléphone avec indicatif : sélecteur de pays (drapeau + « +226 ») et numéro national mis en forme à la frappe.
 * La valeur transmise au formulaire est toujours au format international.
 */
export function PhoneInput({ value, onChange, defaultCountry, disabled = false, placeholder }: PhoneInputProps) {
  const initial = splitPhone(value, defaultCountry);
  const [country, setCountry] = useState<CountryCode | undefined>(initial.country);
  const [national, setNational] = useState(initial.national);
  const lastEmitted = useRef<string>(value ?? "");

  // Valeur modifiée de l'extérieur (réinitialisation du formulaire, chargement des données)
  useEffect(() => {
    if ((value ?? "") === lastEmitted.current) return;
    const next = splitPhone(value, defaultCountry);
    setCountry(next.country);
    setNational(next.national);
    lastEmitted.current = value ?? "";
  }, [value, defaultCountry]);

  // Ancien numéro enregistré sans indicatif (« 70123456 ») : converti au format international à l'ouverture
  useEffect(() => {
    const raw = (value ?? "").trim();
    if (!raw || raw.startsWith("+")) return;
    const international = toInternational(country, national);
    if (international.startsWith("+") && international !== raw) {
      lastEmitted.current = international;
      onChange(international);
    }
    // Une seule fois, au montage
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Tant que le numéro est vide, l'indicatif suit le pays du formulaire
  useEffect(() => {
    if (national.trim()) return;
    const next = toCountryCode(defaultCountry);
    if (next) setCountry(next);
  }, [defaultCountry, national]);

  const emit = (nextCountry: CountryCode | undefined, nextNational: string) => {
    const international = toInternational(nextCountry, nextNational);
    lastEmitted.current = international;
    onChange(international);
  };

  return (
    <div className="flex gap-2">
      <CountrySelect
        compact
        showDialCode
        value={country}
        disabled={disabled}
        aria-label="Indicatif du pays"
        onChange={(code) => {
          const next = toCountryCode(code);
          setCountry(next);
          emit(next, national);
        }}
      />
      <Input
        type="tel"
        inputMode="tel"
        autoComplete="tel-national"
        disabled={disabled}
        placeholder={placeholder ?? "Numéro de téléphone"}
        value={national}
        maxLength={20}
        onChange={(event) => {
          const formatted = formatAsYouType(country, event.target.value);
          // Effacement : on ne reformate pas, sinon les espaces bloquent la suppression
          const next = event.target.value.length < national.length ? event.target.value : formatted;
          setNational(next);
          emit(country, next);
        }}
        className="min-w-0 flex-1"
      />
    </div>
  );
}
