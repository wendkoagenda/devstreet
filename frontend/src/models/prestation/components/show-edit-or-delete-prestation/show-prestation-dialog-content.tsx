import { relationLabel } from "@/helpers/api/relations";
import { buildMediaUrl } from "@/helpers/displayers/media-url-builder";
import { Label } from "@/components/ui/label";
import { usePrestationStore } from "../../slice";

const IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"];

function isImagePath(path: string | null | undefined): boolean {
  if (!path) return false;
  const lower = path.toLowerCase();
  return IMAGE_EXTENSIONS.some((ext) => lower.endsWith(ext));
}

export default function ShowPrestationDialogContent() {
  const { selectedPrestation } = usePrestationStore();

  if (!selectedPrestation) return null;

  return (
    <div className="flex flex-col gap-4 mx-4">
      <div className="max-h-[60vh] overflow-y-auto px-2 py-1">
        <div className="space-y-4">
          <div>
            <Label className="text-sm font-medium">Profil</Label>
            <p className="mt-1">{relationLabel(selectedPrestation.profil, ["slug", "headline"])}</p>
          </div>
          <div>
            <Label className="text-sm font-medium">Title</Label>
            <p className="mt-1">
              {String(selectedPrestation.title ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Slug</Label>
            <p className="mt-1">
              {String(selectedPrestation.slug ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Description</Label>
            <p className="mt-1">
              {String(selectedPrestation.description ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Category</Label>
            <p className="mt-1">
              {(() => {
                const labels = {"web": "Web", "mobile": "Mobile", "design": "Design", "devops": "DevOps", "data": "Data", "other": "Autre"} as Record<string, string>;
                const value = selectedPrestation.category;
                return labels[String(value ?? "")] ?? String(value ?? "—");
              })()}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Price</Label>
            <p className="mt-1">
              {String(selectedPrestation.price ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Currency</Label>
            <p className="mt-1">
              {String(selectedPrestation.currency ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Delivery days</Label>
            <p className="mt-1">
              {String(selectedPrestation.delivery_days ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Revisions</Label>
            <p className="mt-1">
              {String(selectedPrestation.revisions ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Cover image</Label>
            <p className="mt-1">
              {selectedPrestation.cover_image ? (
                isImagePath(selectedPrestation.cover_image) ? (
                  <img
                    src={buildMediaUrl(selectedPrestation.cover_image!)}
                    alt="Cover image"
                    className="max-h-40 rounded border"
                  />
                ) : (
                  <a
                    href={buildMediaUrl(selectedPrestation.cover_image!)}
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
            <Label className="text-sm font-medium">Is active</Label>
            <p className="mt-1">
              {selectedPrestation.is_active ? "Oui" : "Non"}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}