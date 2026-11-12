import { relationLabel } from "@/helpers/api/relations";
import { Label } from "@/components/ui/label";
import { useSwipeStore } from "../../slice";


export default function ShowSwipeDialogContent() {
  const { selectedSwipe } = useSwipeStore();

  if (!selectedSwipe) return null;

  return (
    <div className="flex flex-col gap-4 mx-4">
      <div className="max-h-[60vh] overflow-y-auto px-2 py-1">
        <div className="space-y-4">
          <div>
            <Label className="text-sm font-medium">Auteur du swipe</Label>
            <p className="mt-1">{relationLabel(selectedSwipe.author, ["slug", "headline"])}</p>
          </div>
          <div>
            <Label className="text-sm font-medium">Profil ciblé</Label>
            <p className="mt-1">{relationLabel(selectedSwipe.target, ["slug", "headline"])}</p>
          </div>
          <div>
            <Label className="text-sm font-medium">Direction</Label>
            <p className="mt-1">
              {(() => {
                const labels = {"like": "Like", "pass": "Passer"} as Record<string, string>;
                const value = selectedSwipe.direction;
                return labels[String(value ?? "")] ?? String(value ?? "—");
              })()}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Context</Label>
            <p className="mt-1">
              {(() => {
                const labels = {"recruit": "Recrutement", "network": "Réseau"} as Record<string, string>;
                const value = selectedSwipe.context;
                return labels[String(value ?? "")] ?? String(value ?? "—");
              })()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}