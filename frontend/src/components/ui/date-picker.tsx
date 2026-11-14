import * as React from "react";
import { CalendarIcon, ChevronLeft, ChevronRight } from "lucide-react";
import { Button, type ButtonProps } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";

const WEEKDAYS = ["lun.", "mar.", "mer.", "jeu.", "ven.", "sam.", "dim."];
const MONTHS = Array.from({ length: 12 }, (_, month) =>
  new Intl.DateTimeFormat("fr-FR", { month: "long" }).format(new Date(2000, month, 1))
);
const DISPLAY = new Intl.DateTimeFormat("fr-FR", {
  day: "numeric",
  month: "long",
  year: "numeric",
});

const pad = (value: number) => String(value).padStart(2, "0");

/** Date locale → « AAAA-MM-JJ » (sans passer par UTC, pour ne pas décaler d'un jour). */
export function toIsoDate(date: Date): string {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

/** « AAAA-MM-JJ » → date locale ; null si la valeur est vide ou invalide. */
export function parseIsoDate(value: string | null | undefined): Date | null {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value ?? "");
  if (!match) return null;
  const date = new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
  return Number.isNaN(date.getTime()) ? null : date;
}

type DatePickerProps = Omit<ButtonProps, "value" | "onChange" | "type"> & {
  /** Date au format « AAAA-MM-JJ », ou chaîne vide. */
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  /** Première et dernière dates sélectionnables (« AAAA-MM-JJ »). */
  min?: string;
  max?: string;
};

/** Sélecteur de date avec calendrier : le champ affiche la date, un clic ouvre le calendrier du mois. */
export const DatePicker = React.forwardRef<HTMLButtonElement, DatePickerProps>(
  (
    { value, onChange, placeholder = "Choisir une date", min, max, className, disabled, ...props },
    ref
  ) => {
    const selected = parseIsoDate(value);
    const minDate = parseIsoDate(min);
    const maxDate = parseIsoDate(max);
    const today = new Date();
    const [open, setOpen] = React.useState(false);
    const [view, setView] = React.useState(() => {
      const base = selected ?? today;
      return { year: base.getFullYear(), month: base.getMonth() };
    });

    // À l'ouverture, le calendrier affiche le mois de la date choisie (ou le mois courant)
    const handleOpenChange = (next: boolean) => {
      if (next) {
        const base = selected ?? today;
        setView({ year: base.getFullYear(), month: base.getMonth() });
      }
      setOpen(next);
    };

    const shiftMonth = (delta: number) =>
      setView((current) => {
        const date = new Date(current.year, current.month + delta, 1);
        return { year: date.getFullYear(), month: date.getMonth() };
      });

    // 42 cases (6 semaines), la semaine commence le lundi
    const cells = React.useMemo(() => {
      const first = new Date(view.year, view.month, 1);
      const offset = (first.getDay() + 6) % 7;
      return Array.from({ length: 42 }, (_, index) => new Date(view.year, view.month, 1 - offset + index));
    }, [view.year, view.month]);

    const isDisabled = (date: Date) =>
      Boolean((minDate && date < minDate) || (maxDate && date > maxDate));
    const sameDay = (a: Date | null, b: Date) =>
      a !== null &&
      a.getFullYear() === b.getFullYear() &&
      a.getMonth() === b.getMonth() &&
      a.getDate() === b.getDate();

    const pick = (date: Date) => {
      onChange(toIsoDate(date));
      setOpen(false);
    };

    const years = React.useMemo(() => {
      const start = Math.min(view.year, today.getFullYear()) - 2;
      const end = Math.max(view.year, today.getFullYear()) + 12;
      return Array.from({ length: end - start + 1 }, (_, index) => start + index);
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [view.year]);

    const selectClass =
      "h-8 rounded-md border border-input bg-background px-2 text-sm capitalize focus:outline-none focus:ring-2 focus:ring-ring";

    return (
      <Popover open={open} onOpenChange={handleOpenChange}>
        <PopoverTrigger asChild>
          <Button
            ref={ref}
            type="button"
            variant="outline"
            disabled={disabled}
            className={cn(
              "w-full justify-start gap-2 font-normal",
              !selected && "text-muted-foreground",
              className
            )}
            {...props}
          >
            <CalendarIcon className="size-4 shrink-0" aria-hidden />
            {selected ? DISPLAY.format(selected) : placeholder}
          </Button>
        </PopoverTrigger>
        <PopoverContent align="start" className="w-auto p-3">
          <div className="mb-2 flex items-center justify-between gap-2">
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="size-8"
              onClick={() => shiftMonth(-1)}
              aria-label="Mois précédent"
            >
              <ChevronLeft className="size-4" aria-hidden />
            </Button>
            <div className="flex items-center gap-1">
              <select
                className={selectClass}
                value={view.month}
                onChange={(event) => setView((current) => ({ ...current, month: Number(event.target.value) }))}
                aria-label="Mois"
              >
                {MONTHS.map((name, month) => (
                  <option key={name} value={month}>
                    {name}
                  </option>
                ))}
              </select>
              <select
                className={selectClass}
                value={view.year}
                onChange={(event) => setView((current) => ({ ...current, year: Number(event.target.value) }))}
                aria-label="Année"
              >
                {years.map((year) => (
                  <option key={year} value={year}>
                    {year}
                  </option>
                ))}
              </select>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="size-8"
              onClick={() => shiftMonth(1)}
              aria-label="Mois suivant"
            >
              <ChevronRight className="size-4" aria-hidden />
            </Button>
          </div>

          <div className="grid grid-cols-7 gap-1 text-center">
            {WEEKDAYS.map((day) => (
              <span key={day} className="py-1 text-xs text-muted-foreground">
                {day}
              </span>
            ))}
            {cells.map((date) => {
              const outside = date.getMonth() !== view.month;
              const isSelected = sameDay(selected, date);
              return (
                <button
                  key={date.toISOString()}
                  type="button"
                  disabled={isDisabled(date)}
                  onClick={() => pick(date)}
                  aria-label={DISPLAY.format(date)}
                  aria-pressed={isSelected}
                  className={cn(
                    "size-9 rounded-md text-sm transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-30",
                    outside && "text-muted-foreground/60",
                    sameDay(today, date) && !isSelected && "border border-primary",
                    isSelected && "bg-primary text-primary-foreground hover:bg-primary"
                  )}
                >
                  {date.getDate()}
                </button>
              );
            })}
          </div>

          <div className="mt-2 flex items-center justify-between border-t border-border pt-2">
            <Button
              type="button"
              variant="ghost"
              size="sm"
              disabled={!selected}
              onClick={() => {
                onChange("");
                setOpen(false);
              }}
            >
              Effacer
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              disabled={isDisabled(today)}
              onClick={() => pick(today)}
            >
              Aujourd'hui
            </Button>
          </div>
        </PopoverContent>
      </Popover>
    );
  }
);
DatePicker.displayName = "DatePicker";
