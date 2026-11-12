import type { ReactNode } from "react";
import { Card, CardContent } from "@/components/ui/card";
import type { StatusCounts } from "../schema";

/** Indicateur chiffré : libellé, valeur et précision. */
export function StatCard({
  label,
  value,
  hint,
  icon,
}: {
  label: string;
  value: ReactNode;
  hint?: ReactNode;
  icon?: ReactNode;
}) {
  return (
    <Card>
      <CardContent className="flex items-start justify-between gap-3 p-5">
        <div className="flex min-w-0 flex-col gap-1">
          <span className="text-xs text-muted-foreground">{label}</span>
          <span className="text-2xl font-semibold leading-tight text-foreground">{value}</span>
          {hint ? <span className="text-xs text-muted-foreground">{hint}</span> : null}
        </div>
        {icon ? <span className="shrink-0 text-muted-foreground">{icon}</span> : null}
      </CardContent>
    </Card>
  );
}

/** Barre de progression accessible (valeur sur 100). */
export function ProgressBar({ value, label }: { value: number; label: string }) {
  return (
    <div
      className="h-2 overflow-hidden rounded-full bg-muted"
      role="progressbar"
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={value}
    >
      <div className="h-full rounded-full bg-primary" style={{ width: `${value}%` }} />
    </div>
  );
}

const FUNNEL: { key: keyof Omit<StatusCounts, "total">; label: string }[] = [
  { key: "sent", label: "Envoyées" },
  { key: "shortlisted", label: "Retenues" },
  { key: "accepted", label: "Acceptées" },
  { key: "rejected", label: "Refusées" },
];

/** Répartition des candidatures par statut, en barres horizontales proportionnelles. */
export function StatusBars({ counts }: { counts: StatusCounts }) {
  const max = Math.max(1, ...FUNNEL.map((step) => counts[step.key]));
  return (
    <ul className="flex flex-col gap-3">
      {FUNNEL.map((step) => (
        <li key={step.key} className="flex flex-col gap-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-foreground">{step.label}</span>
            <span className="font-medium text-foreground">{counts[step.key]}</span>
          </div>
          <div
            className="h-2 overflow-hidden rounded-full bg-muted"
            role="progressbar"
            aria-label={step.label}
            aria-valuemin={0}
            aria-valuemax={max}
            aria-valuenow={counts[step.key]}
          >
            <div
              className={`h-full rounded-full ${step.key === "rejected" ? "bg-muted-foreground" : "bg-primary"}`}
              style={{ width: `${(counts[step.key] / max) * 100}%` }}
            />
          </div>
        </li>
      ))}
    </ul>
  );
}

const shortDate = (iso: string) =>
  new Date(`${iso}T00:00:00`).toLocaleDateString("fr-FR", { day: "numeric", month: "short" });

/** Histogramme hebdomadaire : une colonne par semaine, la plus récente à droite. */
export function WeeklyBars({ weeks }: { weeks: { week_start: string; count: number }[] }) {
  const max = Math.max(1, ...weeks.map((week) => week.count));
  const total = weeks.reduce((sum, week) => sum + week.count, 0);
  return (
    <div
      role="img"
      aria-label={`${total} candidatures reçues sur les ${weeks.length} dernières semaines`}
      className="flex h-36 items-end gap-2"
    >
      {weeks.map((week) => (
        <div key={week.week_start} className="flex h-full flex-1 flex-col items-center justify-end gap-1">
          <span className="text-xs font-medium text-foreground">{week.count > 0 ? week.count : ""}</span>
          <div
            className={`w-full rounded-t-md ${week.count > 0 ? "bg-primary" : "bg-muted"}`}
            style={{ height: `${week.count > 0 ? Math.max(8, (week.count / max) * 100) : 4}%` }}
            title={`Semaine du ${shortDate(week.week_start)} : ${week.count}`}
          />
          <span className="text-[10px] text-muted-foreground">{shortDate(week.week_start)}</span>
        </div>
      ))}
    </div>
  );
}
