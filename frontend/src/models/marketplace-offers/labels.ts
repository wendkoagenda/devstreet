import type {
  CandidatureStatus,
  ExperienceLevel,
  Offer,
  OfferStatus,
  OfferType,
  WorkMode,
} from "./schema";

export const OFFER_TYPE_LABELS: Record<OfferType, string> = {
  mission: "Mission",
  cdd: "CDD",
  cdi: "CDI",
  stage: "Stage",
};

export const LEVEL_LABELS: Record<ExperienceLevel, string> = {
  junior: "Junior",
  mid: "Confirmé",
  senior: "Sénior",
};

export const WORK_MODE_LABELS: Record<WorkMode, string> = {
  on_site: "Sur site",
  hybrid: "Hybride",
  remote: "À distance",
};

export const OFFER_STATUS_LABELS: Record<OfferStatus, string> = {
  draft: "Brouillon",
  open: "Ouverte",
  closed: "Clôturée",
};

export const CANDIDATURE_STATUS_LABELS: Record<CandidatureStatus, string> = {
  sent: "Envoyée",
  shortlisted: "Retenue",
  rejected: "Refusée",
  accepted: "Acceptée",
};

const PERIOD_LABELS = { day: "/ jour", month: "/ mois", fixed: "forfait" } as const;

export function formatDate(value: string | null | undefined): string {
  if (!value) return "";
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? ""
    : date.toLocaleDateString("fr-FR", { day: "numeric", month: "short", year: "numeric" });
}

const formatAmount = (value: string) =>
  Number(value).toLocaleString("fr-FR", { maximumFractionDigits: 0 });

/** « 300 000 – 500 000 XOF / mois », ou chaîne vide si l'offre n'a pas de budget. */
export function formatBudget(offer: Offer): string {
  const { budget_min: low, budget_max: high, currency, budget_period: period } = offer;
  if (!low && !high) return "";
  const range =
    low && high && low !== high
      ? `${formatAmount(low)} – ${formatAmount(high)}`
      : formatAmount((high ?? low) as string);
  return `${range} ${currency} ${PERIOD_LABELS[period]}`;
}

/** Libellés courts d'une offre : contrat, durée, mode de travail, niveau. */
export function offerFacts(offer: Offer): string[] {
  return [
    OFFER_TYPE_LABELS[offer.type],
    offer.contract_duration ? `${offer.contract_duration} mois` : "",
    WORK_MODE_LABELS[offer.work_mode],
    LEVEL_LABELS[offer.experience_level],
  ].filter(Boolean);
}

export function initialsOf(name: string): string {
  return (
    name
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase() ?? "")
      .join("") || "?"
  );
}
