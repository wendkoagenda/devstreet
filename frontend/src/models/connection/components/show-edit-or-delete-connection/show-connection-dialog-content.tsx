import { relationLabel } from "@/helpers/api/relations";
import { Label } from "@/components/ui/label";
import { useConnectionStore } from "../../slice";


export default function ShowConnectionDialogContent() {
  const { selectedConnection } = useConnectionStore();

  if (!selectedConnection) return null;

  return (
    <div className="flex flex-col gap-4 mx-4">
      <div className="max-h-[60vh] overflow-y-auto px-2 py-1">
        <div className="space-y-4">
          <div>
            <Label className="text-sm font-medium">Profil A</Label>
            <p className="mt-1">{relationLabel(selectedConnection.profil_a, ["slug", "headline"])}</p>
          </div>
          <div>
            <Label className="text-sm font-medium">Profil B</Label>
            <p className="mt-1">{relationLabel(selectedConnection.profil_b, ["slug", "headline"])}</p>
          </div>
          <div>
            <Label className="text-sm font-medium">Status</Label>
            <p className="mt-1">
              {(() => {
                const labels = {"matched": "Connectés", "blocked": "Bloquée"} as Record<string, string>;
                const value = selectedConnection.status;
                return labels[String(value ?? "")] ?? String(value ?? "—");
              })()}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Matched at</Label>
            <p className="mt-1">
              {String(selectedConnection.matched_at ?? "—")}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}