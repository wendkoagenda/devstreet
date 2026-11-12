import { relationLabel } from "@/helpers/api/relations";
import { Label } from "@/components/ui/label";
import { useProfilHistoryStore } from "../../slice";


export default function ShowProfilHistoryDialogContent() {
  const { selectedProfilHistory } = useProfilHistoryStore();

  if (!selectedProfilHistory) return null;

  return (
    <div className="flex flex-col gap-4 mx-4">
      <div className="max-h-[60vh] overflow-y-auto px-2 py-1">
        <div className="space-y-4">
          <div>
            <Label className="text-sm font-medium">Profil</Label>
            <p className="mt-1">{relationLabel(selectedProfilHistory.profil, ["slug", "headline"])}</p>
          </div>
          <div>
            <Label className="text-sm font-medium">Field</Label>
            <p className="mt-1">
              {String(selectedProfilHistory.field ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Old value</Label>
            <p className="mt-1">
              {String(selectedProfilHistory.old_value ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">New value</Label>
            <p className="mt-1">
              {String(selectedProfilHistory.new_value ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Source</Label>
            <p className="mt-1">
              {(() => {
                const labels = {"manual": "Saisie manuelle", "ai": "IA", "system": "Système"} as Record<string, string>;
                const value = selectedProfilHistory.source;
                return labels[String(value ?? "")] ?? String(value ?? "—");
              })()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}