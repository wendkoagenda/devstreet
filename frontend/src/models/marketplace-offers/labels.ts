import i18n from "i18next";
import type {
  CandidatureStatus,
  DurationUnit,
  ExperienceLevel,
  Offer,
  OfferStatus,
  OfferType,
  WorkMode,
} from "./schema";

/** Libellés résolus à la lecture (suivent la langue i18n courante). */
function labelsOf<T extends string>(prefix: string, keys: readonly T[]): Record<T, string> {
  return Object.fromEntries(
    keys.map((key) => [key, i18n.t(`${prefix}.${key}`)])
  ) as Record<T, string>;
}

const OFFER_TYPES = ["mission", "cdd", "cdi", "stage"] as const satisfies readonly OfferType[];
const LEVELS = ["junior", "mid", "senior", "expert"] as const satisfies readonly ExperienceLevel[];
const DURATION_UNITS = ["hour", "day", "month", "year"] as const satisfies readonly DurationUnit[];
const WORK_MODES = ["on_site", "hybrid", "remote"] as const satisfies readonly WorkMode[];
const OFFER_STATUSES = ["draft", "open", "closed"] as const satisfies readonly OfferStatus[];
const CANDIDATURE_STATUSES = [
  "sent",
  "shortlisted",
  "rejected",
  "accepted",
] as const satisfies readonly CandidatureStatus[];

export const OFFER_TYPE_LABELS: Record<OfferType, string> = new Proxy({} as Record<OfferType, string>, {
  get: (_target, prop: string) => i18n.t(`marketplace.labels.offer_type.${prop}`),
  ownKeys: () => [...OFFER_TYPES],
  getOwnPropertyDescriptor: () => ({ enumerable: true, configurable: true }),
});

export const LEVEL_LABELS: Record<ExperienceLevel, string> = new Proxy(
  {} as Record<ExperienceLevel, string>,
  {
    get: (_target, prop: string) => i18n.t(`marketplace.labels.level.${prop}`),
    ownKeys: () => [...LEVELS],
    getOwnPropertyDescriptor: () => ({ enumerable: true, configurable: true }),
  }
);

/** Unités de durée proposées (heures, jours, mois, années). */
export const DURATION_UNIT_LABELS: Record<DurationUnit, string> = new Proxy(
  {} as Record<DurationUnit, string>,
  {
    get: (_target, prop: string) => i18n.t(`marketplace.labels.duration_unit.${prop}`),
    ownKeys: () => [...DURATION_UNITS],
    getOwnPropertyDescriptor: () => ({ enumerable: true, configurable: true }),
  }
);

/** Durée lisible : « 1 heure », « 3 mois », « 2 ans ». */
export function formatDuration(value: number | string, unit: DurationUnit): string {
  const amount = Number(value);
  const key = amount > 1 ? "duration_plural" : "duration_singular";
  return `${amount} ${i18n.t(`marketplace.labels.${key}.${unit}`)}`;
}

export const WORK_MODE_LABELS: Record<WorkMode, string> = new Proxy(
  {} as Record<WorkMode, string>,
  {
    get: (_target, prop: string) => i18n.t(`marketplace.labels.work_mode.${prop}`),
    ownKeys: () => [...WORK_MODES],
    getOwnPropertyDescriptor: () => ({ enumerable: true, configurable: true }),
  }
);

export const OFFER_STATUS_LABELS: Record<OfferStatus, string> = new Proxy(
  {} as Record<OfferStatus, string>,
  {
    get: (_target, prop: string) => i18n.t(`marketplace.labels.offer_status.${prop}`),
    ownKeys: () => [...OFFER_STATUSES],
    getOwnPropertyDescriptor: () => ({ enumerable: true, configurable: true }),
  }
);

export const CANDIDATURE_STATUS_LABELS: Record<CandidatureStatus, string> = new Proxy(
  {} as Record<CandidatureStatus, string>,
  {
    get: (_target, prop: string) => i18n.t(`marketplace.labels.candidature_status.${prop}`),
    ownKeys: () => [...CANDIDATURE_STATUSES],
    getOwnPropertyDescriptor: () => ({ enumerable: true, configurable: true }),
  }
);

export function formatDate(value: string | null | undefined): string {
  if (!value) return "";
  const date = new Date(value);
  const locale = i18n.language?.startsWith("en") ? "en-GB" : "fr-FR";
  return Number.isNaN(date.getTime())
    ? ""
    : date.toLocaleDateString(locale, { day: "numeric", month: "short", year: "numeric" });
}

const formatAmount = (value: string) => {
  const locale = i18n.language?.startsWith("en") ? "en-GB" : "fr-FR";
  return Number(value).toLocaleString(locale, { maximumFractionDigits: 0 });
};

/** « 300 000 – 500 000 XOF / mois », ou chaîne vide si l'offre n'a pas de budget. */
export function formatBudget(offer: Offer): string {
  const { budget_min: low, budget_max: high, currency, budget_period: period } = offer;
  if (!low && !high) return "";
  const range =
    low && high && low !== high
      ? `${formatAmount(low)} – ${formatAmount(high)}`
      : formatAmount((high ?? low) as string);
  return `${range} ${currency} ${i18n.t(`marketplace.labels.budget_period.${period}`)}`;
}

/** Libellés courts d'une offre : contrat, durée, mode de travail, niveau. */
export function offerFacts(offer: Offer): string[] {
  return [
    OFFER_TYPE_LABELS[offer.type],
    offer.contract_duration ? formatDuration(offer.contract_duration, offer.contract_duration_unit) : "",
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

/** Snapshot figé des libellés (ex. options de select au moment du rendu). */
export function offerTypeLabelEntries() {
  return labelsOf("marketplace.labels.offer_type", OFFER_TYPES);
}
