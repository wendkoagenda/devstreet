import { relationLabel } from "@/helpers/api/relations";
import { buildMediaUrl } from "@/helpers/displayers/media-url-builder";
import { Label } from "@/components/ui/label";
import { useCandidatureStore } from "../../slice";

const IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"];

function isImagePath(path: string | null | undefined): boolean {
  if (!path) return false;
  const lower = path.toLowerCase();
  return IMAGE_EXTENSIONS.some((ext) => lower.endsWith(ext));
}

export default function ShowCandidatureDialogContent() {
  const { selectedCandidature } = useCandidatureStore();

  if (!selectedCandidature) return null;

  return (
    <div className="flex flex-col gap-4 mx-4">
      <div className="max-h-[60vh] overflow-y-auto px-2 py-1">
        <div className="space-y-4">
          <div>
            <Label className="text-sm font-medium">Offre</Label>
            <p className="mt-1">{relationLabel(selectedCandidature.offer, ["title"])}</p>
          </div>
          <div>
            <Label className="text-sm font-medium">Profil</Label>
            <p className="mt-1">{relationLabel(selectedCandidature.profil, ["slug", "headline"])}</p>
          </div>
          <div>
            <Label className="text-sm font-medium">Message</Label>
            <p className="mt-1">
              {String(selectedCandidature.message ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Status</Label>
            <p className="mt-1">
              {(() => {
                const labels = {"sent": "Envoyée", "shortlisted": "Présélectionnée", "rejected": "Refusée", "accepted": "Acceptée"} as Record<string, string>;
                const value = selectedCandidature.status;
                return labels[String(value ?? "")] ?? String(value ?? "—");
              })()}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Ai match score</Label>
            <p className="mt-1">
              {String(selectedCandidature.ai_match_score ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Cv snapshot</Label>
            <p className="mt-1">
              {selectedCandidature.cv_snapshot ? (
                isImagePath(selectedCandidature.cv_snapshot) ? (
                  <img
                    src={buildMediaUrl(selectedCandidature.cv_snapshot!)}
                    alt="Cv snapshot"
                    className="max-h-40 rounded border"
                  />
                ) : (
                  <a
                    href={buildMediaUrl(selectedCandidature.cv_snapshot!)}
                    target="_blank"
                    rel="noreferrer"
                    className="text-primary underline"
                  >
                    Telecharger le fichier
                  </a>
                )
              ) : (
                "—"
              )}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Decided at</Label>
            <p className="mt-1">
              {String(selectedCandidature.decided_at ?? "—")}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}