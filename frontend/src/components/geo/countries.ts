import { getCountries, getCountryCallingCode, type CountryCode } from "libphonenumber-js";
import { COUNTRIES as SUGGESTED_COUNTRIES } from "@/models/marketplace-space/options";

export type CountryOption = {
  /** Code ISO à 2 lettres, en majuscules (valeur enregistrée). */
  code: string;
  /** Nom en français. */
  name: string;
  /** Indicatif téléphonique sans « + » (ex. « 226 »). */
  dialCode: string;
  /** Pays mis en avant en tête de liste. */
  suggested: boolean;
};

const SUGGESTED_CODES: string[] = SUGGESTED_COUNTRIES.map((country) => country.code);

let regionNames: Intl.DisplayNames | null = null;
try {
  regionNames = new Intl.DisplayNames(["fr"], { type: "region" });
} catch (error) {
  // Navigateur sans Intl.DisplayNames : les codes ISO tiennent lieu de noms
  console.warn("Noms de pays en français indisponibles, affichage des codes", error);
}

/** Nom du pays en français (le code s'il est inconnu). */
export function countryName(code: string): string {
  const upper = code.toUpperCase();
  return regionNames?.of(upper) ?? upper;
}

/** Retire les accents et la casse, pour une recherche tolérante (« cote » trouve « Côte d'Ivoire »). */
export function normalizeSearch(value: string): string {
  return value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
}

/** Tous les pays connus (indicatif compris) : d'abord les pays suggérés, puis les autres par ordre alphabétique. */
export const COUNTRY_OPTIONS: CountryOption[] = (() => {
  const all: CountryOption[] = getCountries().map((code: CountryCode) => ({
    code,
    name: countryName(code),
    dialCode: getCountryCallingCode(code),
    suggested: SUGGESTED_CODES.includes(code),
  }));
  const suggested = SUGGESTED_CODES.map((code) => all.find((item) => item.code === code)).filter(
    (item): item is CountryOption => Boolean(item)
  );
  const others = all
    .filter((item) => !item.suggested)
    .sort((a, b) => a.name.localeCompare(b.name, "fr"));
  return [...suggested, ...others];
})();

export function findCountry(code: string | null | undefined): CountryOption | undefined {
  if (!code) return undefined;
  const upper = code.toUpperCase();
  return COUNTRY_OPTIONS.find((item) => item.code === upper);
}

/** Pays dont le nom, le code ou l'indicatif correspond à la recherche. */
export function filterCountries(search: string): CountryOption[] {
  const query = normalizeSearch(search).replace(/^\+/, "");
  if (!query) return COUNTRY_OPTIONS;
  return COUNTRY_OPTIONS.filter(
    (item) =>
      normalizeSearch(item.name).includes(query) ||
      item.code.toLowerCase() === query ||
      item.dialCode.startsWith(query)
  );
}
