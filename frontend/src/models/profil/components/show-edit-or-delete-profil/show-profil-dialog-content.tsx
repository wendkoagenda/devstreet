import { relationLabel } from "@/helpers/api/relations";
import { buildMediaUrl } from "@/helpers/displayers/media-url-builder";
import { Label } from "@/components/ui/label";
import { useProfilStore } from "../../slice";

const IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"];

function isImagePath(path: string | null | undefined): boolean {
  if (!path) return false;
  const lower = path.toLowerCase();
  return IMAGE_EXTENSIONS.some((ext) => lower.endsWith(ext));
}

export default function ShowProfilDialogContent() {
  const { selectedProfil } = useProfilStore();

  if (!selectedProfil) return null;

  return (
    <div className="flex flex-col gap-4 mx-4">
      <div className="max-h-[60vh] overflow-y-auto px-2 py-1">
        <div className="space-y-4">
          <div>
            <Label className="text-sm font-medium">Entreprise</Label>
            <p className="mt-1">{relationLabel(selectedProfil.company, ["name"])}</p>
          </div>
          <div>
            <Label className="text-sm font-medium">Compte utilisateur</Label>
            <p className="mt-1">{selectedProfil.user_id != null ? `#${selectedProfil.user_id}` : "—"}</p>
          </div>
          <div>
            <Label className="text-sm font-medium">Is company owner</Label>
            <p className="mt-1">
              {selectedProfil.is_company_owner ? "Oui" : "Non"}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Slug</Label>
            <p className="mt-1">
              {String(selectedProfil.slug ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Photo</Label>
            <p className="mt-1">
              {selectedProfil.photo ? (
                isImagePath(selectedProfil.photo) ? (
                  <img
                    src={buildMediaUrl(selectedProfil.photo!)}
                    alt="Photo"
                    className="max-h-40 rounded border"
                  />
                ) : (
                  <a
                    href={buildMediaUrl(selectedProfil.photo!)}
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
            <Label className="text-sm font-medium">Headline</Label>
            <p className="mt-1">
              {String(selectedProfil.headline ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Bio</Label>
            <p className="mt-1">
              {String(selectedProfil.bio ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Phone</Label>
            <p className="mt-1">
              {String(selectedProfil.phone ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Country</Label>
            <p className="mt-1">
              {String(selectedProfil.country ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">City</Label>
            <p className="mt-1">
              {String(selectedProfil.city ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Remote</Label>
            <p className="mt-1">
              {selectedProfil.remote ? "Oui" : "Non"}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Timezone</Label>
            <p className="mt-1">
              {String(selectedProfil.timezone ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Default hours per week</Label>
            <p className="mt-1">
              {String(selectedProfil.default_hours_per_week ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Is open to work</Label>
            <p className="mt-1">
              {selectedProfil.is_open_to_work ? "Oui" : "Non"}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Daily rate</Label>
            <p className="mt-1">
              {String(selectedProfil.daily_rate ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Currency</Label>
            <p className="mt-1">
              {String(selectedProfil.currency ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Years of experience</Label>
            <p className="mt-1">
              {String(selectedProfil.years_of_experience ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Languages</Label>
            <p className="mt-1">
              {String(selectedProfil.languages ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Github url</Label>
            <p className="mt-1">
              {String(selectedProfil.github_url ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Linkedin url</Label>
            <p className="mt-1">
              {String(selectedProfil.linkedin_url ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Portfolio url</Label>
            <p className="mt-1">
              {String(selectedProfil.portfolio_url ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Cv visibility</Label>
            <p className="mt-1">
              {(() => {
                const labels = {"public": "Public", "companies": "Entreprises", "private": "Privé"} as Record<string, string>;
                const value = selectedProfil.cv_visibility;
                return labels[String(value ?? "")] ?? String(value ?? "—");
              })()}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Embedding</Label>
            <p className="mt-1">
              {String(selectedProfil.embedding ?? "—")}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}