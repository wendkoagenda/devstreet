import { relationLabel } from "@/helpers/api/relations";
import { Label } from "@/components/ui/label";
import { useOfferStore } from "../../slice";


export default function ShowOfferDialogContent() {
  const { selectedOffer } = useOfferStore();

  if (!selectedOffer) return null;

  return (
    <div className="flex flex-col gap-4 mx-4">
      <div className="max-h-[60vh] overflow-y-auto px-2 py-1">
        <div className="space-y-4">
          <div>
            <Label className="text-sm font-medium">Entreprise</Label>
            <p className="mt-1">{relationLabel(selectedOffer.company, ["name"])}</p>
          </div>
          <div>
            <Label className="text-sm font-medium">Recruteur</Label>
            <p className="mt-1">{relationLabel(selectedOffer.recruiter, ["slug", "headline"])}</p>
          </div>
          <div>
            <Label className="text-sm font-medium">Compétences requises</Label>
            <p className="mt-1">
              {selectedOffer.required_skills?.map((item) => relationLabel(item, ["name"])).join(", ") || "—"}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Title</Label>
            <p className="mt-1">
              {String(selectedOffer.title ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Slug</Label>
            <p className="mt-1">
              {String(selectedOffer.slug ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Description</Label>
            <p className="mt-1">
              {String(selectedOffer.description ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Type</Label>
            <p className="mt-1">
              {(() => {
                const labels = {"mission": "Mission", "cdd": "CDD", "cdi": "CDI", "stage": "Stage"} as Record<string, string>;
                const value = selectedOffer.type;
                return labels[String(value ?? "")] ?? String(value ?? "—");
              })()}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Contract duration</Label>
            <p className="mt-1">
              {String(selectedOffer.contract_duration ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Experience level</Label>
            <p className="mt-1">
              {(() => {
                const labels = {"junior": "Junior", "mid": "Confirmé", "senior": "Sénior"} as Record<string, string>;
                const value = selectedOffer.experience_level;
                return labels[String(value ?? "")] ?? String(value ?? "—");
              })()}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Budget min</Label>
            <p className="mt-1">
              {String(selectedOffer.budget_min ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Budget max</Label>
            <p className="mt-1">
              {String(selectedOffer.budget_max ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Currency</Label>
            <p className="mt-1">
              {String(selectedOffer.currency ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Budget period</Label>
            <p className="mt-1">
              {(() => {
                const labels = {"day": "Par jour", "month": "Par mois", "fixed": "Forfait"} as Record<string, string>;
                const value = selectedOffer.budget_period;
                return labels[String(value ?? "")] ?? String(value ?? "—");
              })()}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Country</Label>
            <p className="mt-1">
              {String(selectedOffer.country ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">City</Label>
            <p className="mt-1">
              {String(selectedOffer.city ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Work mode</Label>
            <p className="mt-1">
              {(() => {
                const labels = {"on_site": "Sur site", "hybrid": "Hybride", "remote": "À distance"} as Record<string, string>;
                const value = selectedOffer.work_mode;
                return labels[String(value ?? "")] ?? String(value ?? "—");
              })()}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Start date</Label>
            <p className="mt-1">
              {String(selectedOffer.start_date ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Deadline</Label>
            <p className="mt-1">
              {String(selectedOffer.deadline ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Status</Label>
            <p className="mt-1">
              {(() => {
                const labels = {"draft": "Brouillon", "open": "Ouverte", "closed": "Clôturée"} as Record<string, string>;
                const value = selectedOffer.status;
                return labels[String(value ?? "")] ?? String(value ?? "—");
              })()}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Published at</Label>
            <p className="mt-1">
              {String(selectedOffer.published_at ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Views count</Label>
            <p className="mt-1">
              {String(selectedOffer.views_count ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Embedding</Label>
            <p className="mt-1">
              {String(selectedOffer.embedding ?? "—")}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}