/** Listes de choix des formulaires du profil et de l'entreprise. */

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
  { value: "companies", label: "Les entreprises" },
  { value: "public", label: "Tout le monde" },
  { value: "private", label: "Moi uniquement" },
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

export function countryName(code: string): string {
  return (
    COUNTRIES.find((country) => country.code === code.toUpperCase())?.name ??
    code
  );
}
