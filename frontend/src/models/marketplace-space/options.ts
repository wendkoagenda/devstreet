/** Listes de choix des formulaires du profil et de l'entreprise. */
import i18n from "i18next";

export const COUNTRIES = [
  { code: "BJ", name: "Bénin", timezone: "Africa/Porto-Novo" },
  { code: "BF", name: "Burkina Faso", timezone: "Africa/Ouagadougou" },
  { code: "CM", name: "Cameroun", timezone: "Africa/Douala" },
  { code: "CI", name: "Côte d'Ivoire", timezone: "Africa/Abidjan" },
  { code: "GA", name: "Gabon", timezone: "Africa/Libreville" },
  { code: "GH", name: "Ghana", timezone: "Africa/Accra" },
  { code: "GN", name: "Guinée", timezone: "Africa/Conakry" },
  { code: "ML", name: "Mali", timezone: "Africa/Bamako" },
  { code: "MA", name: "Maroc", timezone: "Africa/Casablanca" },
  { code: "NE", name: "Niger", timezone: "Africa/Niamey" },
  { code: "NG", name: "Nigeria", timezone: "Africa/Lagos" },
  { code: "CD", name: "RD Congo", timezone: "Africa/Kinshasa" },
  { code: "SN", name: "Sénégal", timezone: "Africa/Dakar" },
  { code: "TG", name: "Togo", timezone: "Africa/Lome" },
  { code: "TN", name: "Tunisie", timezone: "Africa/Tunis" },
  { code: "FR", name: "France", timezone: "Europe/Paris" },
  { code: "BE", name: "Belgique", timezone: "Europe/Brussels" },
  { code: "CA", name: "Canada", timezone: "America/Toronto" },
] as const;

export const TIMEZONES: string[] = [
  "UTC",
  ...Array.from(new Set(COUNTRIES.map((country) => country.timezone))),
];

export const CURRENCIES = [
  { code: "XOF", name: "Franc CFA (UEMOA)" },
  { code: "XAF", name: "Franc CFA (CEMAC)" },
  { code: "EUR", name: "Euro" },
  { code: "USD", name: "Dollar américain" },
  { code: "MAD", name: "Dirham marocain" },
  { code: "NGN", name: "Naira" },
  { code: "GHS", name: "Cedi" },
];

export const CV_VISIBILITIES = [
  {
    value: "companies",
    get label() {
      return i18n.t("marketplace.labels.cv_visibility.companies");
    },
  },
  {
    value: "public",
    get label() {
      return i18n.t("marketplace.labels.cv_visibility.public");
    },
  },
  {
    value: "private",
    get label() {
      return i18n.t("marketplace.labels.cv_visibility.private");
    },
  },
];

export const SECTORS = [
  { value: "fintech", label: "Fintech" },
  { value: "ecommerce", label: "E-commerce" },
  { value: "agritech", label: "Agritech" },
  { value: "edtech", label: "Edtech" },
  { value: "health", label: "Santé" },
  { value: "ngo", label: "ONG" },
  { value: "public", label: "Secteur public" },
  { value: "other", label: "Autre" },
];

export const COMPANY_SIZES = [
  { value: "1-10", label: "1 à 10 personnes" },
  { value: "11-50", label: "11 à 50 personnes" },
  { value: "51-200", label: "51 à 200 personnes" },
  { value: "200+", label: "Plus de 200 personnes" },
];

/** Nom du pays selon la langue (Intl), avec repli sur la liste locale. */
export function countryName(code: string, language?: string): string {
  const normalized = code.toUpperCase();
  let localized: string | undefined;
  try {
    const locale = language?.startsWith("en") ? "en" : language || "fr";
    localized = new Intl.DisplayNames([locale], { type: "region" }).of(
      normalized
    );
  } catch (error) {
    // Navigateur sans Intl.DisplayNames : repli sur COUNTRIES.
    if (import.meta.env.DEV) {
      console.debug("[countryName] Intl.DisplayNames indisponible", error);
    }
  }
  if (localized) return localized;
  return COUNTRIES.find((country) => country.code === normalized)?.name ?? code;
}
