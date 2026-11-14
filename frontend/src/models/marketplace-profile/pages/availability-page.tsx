import { useState } from "react";
import { Pencil, Trash2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { CreationErrorSonner, CreationSuccessSonner } from "@/helpers/api/feed-backs";
import { formatDate } from "@/models/marketplace-offers/labels";
import { AvailabilityStatsStrip } from "@/models/marketplace-stats/components/page-stats";
import { RequireProfil } from "@/models/marketplace-space/components/guards";
import { useDeleteAvailabilityMutation, useGetMyAvailabilitiesQuery } from "../api";
import { AvailabilityForm } from "../components/availability-form";
import { MonthCalendar } from "../components/month-calendar";
import { AVAILABILITY_LABELS, type Availability } from "../schema";

function firstOfMonth(date: Date) {
  return new Date(date.getFullYear(), date.getMonth(), 1);
}

function AvailabilityContent() {
  const { data, isLoading } = useGetMyAvailabilitiesQuery();
  const [remove] = useDeleteAvailabilityMutation();
  const [month, setMonth] = useState(() => firstOfMonth(new Date()));
  // null : liste ; "new" : ajout ; une période : modification
  const [editing, setEditing] = useState<Availability | "new" | null>(null);

  const periods = data ?? [];

  const onDelete = async (period: Availability) => {
    try {
      await remove(period.id).unwrap();
      CreationSuccessSonner("Période supprimée");
    } catch {
      CreationErrorSonner("Impossible de supprimer cette période");
    }
  };

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-4">
      <AvailabilityStatsStrip />
      <div className="flex flex-col gap-1">
        <h1 className="text-xl font-semibold text-foreground">Mes disponibilités</h1>
        <p className="text-sm text-muted-foreground">
          Sans période, vous êtes disponible : ajoutez seulement vos plages occupées (mission, congé, charge
          partielle). Votre calendrier alimente le score des offres, et une candidature acceptée ajoute
          automatiquement la mission en « occupé ».
        </p>
      </div>

      <div className="grid items-start gap-4 lg:grid-cols-[minmax(0,1fr)_340px]">
        <Card>
          <CardContent className="p-5">
            {isLoading ? (
              <Skeleton className="h-72 w-full" />
            ) : (
              <MonthCalendar month={month} onMonthChange={setMonth} periods={periods} />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">
              {editing === "new"
                ? "Ajouter une période"
                : editing
                  ? "Modifier la période"
                  : "Mes périodes"}
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            {editing ? (
              <AvailabilityForm
                key={editing === "new" ? "new" : editing.id}
                period={editing === "new" ? null : editing}
                onDone={() => setEditing(null)}
              />
            ) : (
              <>
                {periods.length === 0 && !isLoading ? (
                  <p className="text-sm text-muted-foreground">Aucune période renseignée.</p>
                ) : null}
                {periods.map((period) => (
                  <div
                    key={period.id}
                    className="flex items-start justify-between gap-2 rounded-lg border border-border p-3"
                  >
                    <div className="flex min-w-0 flex-col gap-0.5">
                      <span className="text-sm font-medium text-foreground">
                        {formatDate(period.start_date)} – {formatDate(period.end_date)}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {AVAILABILITY_LABELS[period.status]}
                        {period.hours_per_week ? ` · ${period.hours_per_week} h / semaine` : ""}
                        {period.note ? ` · ${period.note}` : ""}
                      </span>
                      {period.source === "mission" ? (
                        <Badge variant="secondary" className="mt-1 w-fit">
                          Ajoutée par une mission
                        </Badge>
                      ) : null}
                    </div>
                    {period.source === "manual" ? (
                      <div className="flex shrink-0 gap-1">
                        <Button
                          type="button"
                          size="icon"
                          variant="ghost"
                          aria-label="Modifier la période"
                          onClick={() => setEditing(period)}
                        >
                          <Pencil className="size-4" />
                        </Button>
                        <Button
                          type="button"
                          size="icon"
                          variant="ghost"
                          aria-label="Supprimer la période"
                          onClick={() => onDelete(period)}
                        >
                          <Trash2 className="size-4" />
                        </Button>
                      </div>
                    ) : null}
                  </div>
                ))}
                <Button type="button" variant="outline" onClick={() => setEditing("new")}>
                  Ajouter une période
                </Button>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

/** Disponibilités : calendrier mensuel et périodes du profil. */
export default function AvailabilityPage() {
  return (
    <RequireProfil>
      <AvailabilityContent />
    </RequireProfil>
  );
}
