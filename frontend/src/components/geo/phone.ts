import {
  AsYouType,
  isValidPhoneNumber,
  parsePhoneNumberFromString,
  type CountryCode,
} from "libphonenumber-js";
import { findCountry } from "./countries";

/** Code pays utilisable par libphonenumber (undefined si inconnu). */
export function toCountryCode(code: string | null | undefined): CountryCode | undefined {
  return findCountry(code)?.code as CountryCode | undefined;
}

/** Décompose un numéro enregistré (« +22670123456 » ou ancien format national) en pays + partie nationale. */
export function splitPhone(
  value: string | null | undefined,
  fallbackCountry: string | null | undefined
): { country: CountryCode | undefined; national: string } {
  const raw = (value ?? "").trim();
  const fallback = toCountryCode(fallbackCountry);
  if (!raw) return { country: fallback, national: "" };
  const parsed = parsePhoneNumberFromString(raw, fallback);
  if (parsed) {
    return { country: parsed.country ?? fallback, national: parsed.formatNational() };
  }
  return { country: fallback, national: raw.replace(/^\+\d+\s*/, "") };
}

/** Numéro au format international (E.164) à partir du pays et de la saisie ; "" si rien n'est saisi. */
export function toInternational(country: CountryCode | undefined, national: string): string {
  const digits = national.replace(/[^\d+]/g, "");
  if (!digits) return "";
  const parsed = parsePhoneNumberFromString(digits, country);
  if (parsed) return parsed.number;
  // Numéro incomplet : on garde l'indicatif pour que la validation explique l'erreur
  const dial = country ? findCountry(country)?.dialCode : undefined;
  return dial ? `+${dial}${digits.replace(/^0+/, "")}` : digits;
}

/** Mise en forme pendant la frappe, selon les règles du pays (« 70 12 34 56 »). */
export function formatAsYouType(country: CountryCode | undefined, national: string): string {
  if (!country) return national;
  return new AsYouType(country).input(national);
}

/** Vide ou numéro valide pour son pays : règle commune aux schémas des formulaires. */
export function isValidOptionalPhone(value: string): boolean {
  const trimmed = value.trim();
  return trimmed === "" || isValidPhoneNumber(trimmed);
}

export const INVALID_PHONE_MESSAGE = "Numéro invalide pour le pays choisi";
