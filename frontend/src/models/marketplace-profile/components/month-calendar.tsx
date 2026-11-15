import { useMemo } from "react";
import { useTranslation } from "react-i18next";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Availability, AvailabilityStatus } from "../schema";
import { AVAILABILITY_LABELS } from "../schema";

/** Un jour couvert par plusieurs périodes prend le statut le plus contraignant. */
const PRIORITY: AvailabilityStatus[] = ["busy", "leave", "partial", "available"];

const STATUS_CLASSES: Record<AvailabilityStatus, string> = {
  available: "border border-primary/30 bg-primary/10 text-foreground",
  partial: "bg-secondary text-secondary-foreground",
  busy: "bg-primary text-primary-foreground",
  leave: "border border-dashed border-muted-foreground text-foreground",
};

const pad = (value: number) => String(value).padStart(2, "0");
const isoDay = (year: number, month: number, day: number) => `${year}-${pad(month + 1)}-${pad(day)}`;

function statusOn(day: string, periods: Availability[]): AvailabilityStatus | null {
  const covering = periods.filter((period) => period.start_date <= day && day <= period.end_date);
  return PRIORITY.find((status) => covering.some((period) => period.status === status)) ?? null;
}

type MonthCalendarProps = {
  /** Premier jour du mois affiché. */
  month: Date;
  onMonthChange: (month: Date) => void;
  periods: Availability[];
};

/** Calendrier d'un mois (semaine commençant le lundi) coloré selon les périodes de disponibilité. */
export function MonthCalendar({ month, onMonthChange, periods }: MonthCalendarProps) {
  const { t, i18n } = useTranslation();
  const locale = i18n.language?.startsWith("en") ? "en-GB" : "fr-FR";
  const year = month.getFullYear();
  const index = month.getMonth();
  const daysInMonth = new Date(year, index + 1, 0).getDate();
  // getDay() : dimanche = 0 ; on décale pour que lundi soit la première colonne
  const offset = (new Date(year, index, 1).getDay() + 6) % 7;

  const monthLabel = useMemo(
    () =>
      new Intl.DateTimeFormat(locale, { month: "long", year: "numeric" }).format(month),
    [locale, month]
  );

  const weekdays = useMemo(() => {
    // Une semaine fixe (lun → dim) pour les en-têtes, indépendante du mois affiché
    const monday = new Date(Date.UTC(2024, 0, 1));
    return Array.from({ length: 7 }, (_, day) => {
      const date = new Date(monday);
      date.setUTCDate(monday.getUTCDate() + day);
      return new Intl.DateTimeFormat(locale, { weekday: "short" }).format(date);
    });
  }, [locale]);

  const shift = (delta: number) => onMonthChange(new Date(year, index + delta, 1));

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-foreground capitalize">{monthLabel}</h2>
        <div className="flex gap-1.5">
          <Button
            type="button"
            size="icon"
            variant="outline"
            aria-label={t("marketplace.availability.prev_month")}
            onClick={() => shift(-1)}
          >
            <ChevronLeft className="size-4" />
          </Button>
          <Button
            type="button"
            size="icon"
            variant="outline"
            aria-label={t("marketplace.availability.next_month")}
            onClick={() => shift(1)}
          >
            <ChevronRight className="size-4" />
          </Button>
        </div>
      </div>
      <div
        className="grid grid-cols-7 gap-1"
        role="grid"
        aria-label={t("marketplace.availability.calendar_aria", { month: monthLabel })}
      >
        {weekdays.map((weekday) => (
          <span key={weekday} className="py-1 text-center text-xs capitalize text-muted-foreground">
            {weekday}
          </span>
        ))}
        {Array.from({ length: offset }, (_, blank) => (
          <span key={`blank-${blank}`} />
        ))}
        {Array.from({ length: daysInMonth }, (_, position) => {
          const day = position + 1;
          const status = statusOn(isoDay(year, index, day), periods);
          const weekend = (offset + position) % 7 >= 5;
          return (
            <span
              key={day}
              role="gridcell"
              title={status ? AVAILABILITY_LABELS[status] : undefined}
              className={`flex h-10 items-center justify-center rounded-md text-xs font-medium ${
                status
                  ? STATUS_CLASSES[status]
                  : weekend
                    ? "bg-muted text-muted-foreground"
                    : "text-foreground"
              }`}
            >
              {day}
            </span>
          );
        })}
      </div>
      <div className="flex flex-wrap gap-4 text-xs text-foreground">
        <span className="flex items-center gap-1.5">
          <span className="size-3 rounded-sm border border-border" aria-hidden />
          {t("marketplace.availability.available_default")}
        </span>
        {(Object.keys(STATUS_CLASSES) as AvailabilityStatus[])
          .filter((status) => status !== "available")
          .map((status) => (
            <span key={status} className="flex items-center gap-1.5">
              <span className={`size-3 rounded-sm ${STATUS_CLASSES[status]}`} aria-hidden />
              {AVAILABILITY_LABELS[status]}
            </span>
          ))}
      </div>
    </div>
  );
}
