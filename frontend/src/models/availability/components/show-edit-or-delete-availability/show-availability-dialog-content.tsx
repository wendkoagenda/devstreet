import { relationLabel } from "@/helpers/api/relations";
import { Label } from "@/components/ui/label";
import { useAvailabilityStore } from "../../slice";


export default function ShowAvailabilityDialogContent() {
  const { selectedAvailability } = useAvailabilityStore();

  if (!selectedAvailability) return null;

  return (
    <div className="flex flex-col gap-4 mx-4">
      <div className="max-h-[60vh] overflow-y-auto px-2 py-1">
        <div className="space-y-4">
          <div>
            <Label className="text-sm font-medium">Profil</Label>
            <p className="mt-1">{relationLabel(selectedAvailability.profil, ["slug", "headline"])}</p>
          </div>
          <div>
            <Label className="text-sm font-medium">Start date</Label>
            <p className="mt-1">
              {String(selectedAvailability.start_date ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">End date</Label>
            <p className="mt-1">
              {String(selectedAvailability.end_date ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Status</Label>
            <p className="mt-1">
              {(() => {
                const labels = {"available": "Disponible", "partial": "Partiel", "busy": "Occupé", "leave": "Congé"} as Record<string, string>;
                const value = selectedAvailability.status;
                return labels[String(value ?? "")] ?? String(value ?? "—");
              })()}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Hours per week</Label>
            <p className="mt-1">
              {String(selectedAvailability.hours_per_week ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Source</Label>
            <p className="mt-1">
              {(() => {
                const labels = {"manual": "Saisie manuelle", "mission": "Mission"} as Record<string, string>;
                const value = selectedAvailability.source;
                return labels[String(value ?? "")] ?? String(value ?? "—");
              })()}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Note</Label>
            <p className="mt-1">
              {String(selectedAvailability.note ?? "—")}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}