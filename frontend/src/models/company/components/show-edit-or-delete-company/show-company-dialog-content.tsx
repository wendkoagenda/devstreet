import { buildMediaUrl } from "@/helpers/displayers/media-url-builder";
import { Label } from "@/components/ui/label";
import { useCompanyStore } from "../../slice";

const IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"];

function isImagePath(path: string | null | undefined): boolean {
  if (!path) return false;
  const lower = path.toLowerCase();
  return IMAGE_EXTENSIONS.some((ext) => lower.endsWith(ext));
}

export default function ShowCompanyDialogContent() {
  const { selectedCompany } = useCompanyStore();

  if (!selectedCompany) return null;

  return (
    <div className="flex flex-col gap-4 mx-4">
      <div className="max-h-[60vh] overflow-y-auto px-2 py-1">
        <div className="space-y-4">
          <div>
            <Label className="text-sm font-medium">Name</Label>
            <p className="mt-1">
              {String(selectedCompany.name ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Slug</Label>
            <p className="mt-1">
              {String(selectedCompany.slug ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Logo</Label>
            <p className="mt-1">
              {selectedCompany.logo ? (
                isImagePath(selectedCompany.logo) ? (
                  <img
                    src={buildMediaUrl(selectedCompany.logo!)}
                    alt="Logo"
                    className="max-h-40 rounded border"
                  />
                ) : (
                  <a
                    href={buildMediaUrl(selectedCompany.logo!)}
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
            <Label className="text-sm font-medium">Description</Label>
            <p className="mt-1">
              {String(selectedCompany.description ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Sector</Label>
            <p className="mt-1">
              {(() => {
                const labels = {"fintech": "Fintech", "ecommerce": "E-commerce", "agritech": "Agritech", "edtech": "Edtech", "health": "Santé", "ngo": "ONG", "public": "Secteur public", "other": "Autre"} as Record<string, string>;
                const value = selectedCompany.sector;
                return labels[String(value ?? "")] ?? String(value ?? "—");
              })()}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Size</Label>
            <p className="mt-1">
              {(() => {
                const labels = {"1-10": "1-10", "11-50": "11-50", "51-200": "51-200", "200+": "200+"} as Record<string, string>;
                const value = selectedCompany.size;
                return labels[String(value ?? "")] ?? String(value ?? "—");
              })()}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Website</Label>
            <p className="mt-1">
              {String(selectedCompany.website ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Contact email</Label>
            <p className="mt-1">
              {String(selectedCompany.contact_email ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Phone</Label>
            <p className="mt-1">
              {String(selectedCompany.phone ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Country</Label>
            <p className="mt-1">
              {String(selectedCompany.country ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">City</Label>
            <p className="mt-1">
              {String(selectedCompany.city ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Address</Label>
            <p className="mt-1">
              {String(selectedCompany.address ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Is verified</Label>
            <p className="mt-1">
              {selectedCompany.is_verified ? "Oui" : "Non"}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Verified at</Label>
            <p className="mt-1">
              {String(selectedCompany.verified_at ?? "—")}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}