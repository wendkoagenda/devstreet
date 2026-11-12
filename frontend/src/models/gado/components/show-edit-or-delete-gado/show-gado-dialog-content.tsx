import { buildMediaUrl } from "@/helpers/displayers/media-url-builder";
import { Label } from "@/components/ui/label";
import { useGadoStore } from "../../slice";

const IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"];

function isImagePath(path: string | null | undefined): boolean {
  if (!path) return false;
  const lower = path.toLowerCase();
  return IMAGE_EXTENSIONS.some((ext) => lower.endsWith(ext));
}

export default function ShowGadoDialogContent() {
  const { selectedGado } = useGadoStore();

  if (!selectedGado) return null;

  return (
    <div className="flex flex-col gap-4 mx-4">
      <div className="max-h-[60vh] overflow-y-auto px-2 py-1">
        <div className="space-y-4">
          <div>
            <Label className="text-sm font-medium">Titre</Label>
            <p className="mt-1">
              {String(selectedGado.titre ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Statut</Label>
            <p className="mt-1">
              {(() => {
                const labels = {"draft": "Brouillon", "published": "Publie", "archived": "Archive"} as Record<string, string>;
                const value = selectedGado.statut;
                return labels[String(value ?? "")] ?? String(value ?? "—");
              })()}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Description</Label>
            <p className="mt-1">
              {String(selectedGado.description ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Prix</Label>
            <p className="mt-1">
              {String(selectedGado.prix ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Document</Label>
            <p className="mt-1">
              {selectedGado.document ? (
                isImagePath(selectedGado.document) ? (
                  <img
                    src={buildMediaUrl(selectedGado.document!)}
                    alt="Document"
                    className="max-h-40 rounded border"
                  />
                ) : (
                  <a
                    href={buildMediaUrl(selectedGado.document!)}
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
        </div>
      </div>
    </div>
  );
}