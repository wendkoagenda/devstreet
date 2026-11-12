import { relationLabel } from "@/helpers/api/relations";
import { Label } from "@/components/ui/label";
import { useExperienceStore } from "../../slice";


export default function ShowExperienceDialogContent() {
  const { selectedExperience } = useExperienceStore();

  if (!selectedExperience) return null;

  return (
    <div className="flex flex-col gap-4 mx-4">
      <div className="max-h-[60vh] overflow-y-auto px-2 py-1">
        <div className="space-y-4">
          <div>
            <Label className="text-sm font-medium">Profil</Label>
            <p className="mt-1">{relationLabel(selectedExperience.profil, ["slug", "headline"])}</p>
          </div>
          <div>
            <Label className="text-sm font-medium">Title</Label>
            <p className="mt-1">
              {String(selectedExperience.title ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Company name</Label>
            <p className="mt-1">
              {String(selectedExperience.company_name ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Location</Label>
            <p className="mt-1">
              {String(selectedExperience.location ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Contract type</Label>
            <p className="mt-1">
              {(() => {
                const labels = {"cdi": "CDI", "cdd": "CDD", "freelance": "Freelance", "stage": "Stage"} as Record<string, string>;
                const value = selectedExperience.contract_type;
                return labels[String(value ?? "")] ?? String(value ?? "—");
              })()}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Start date</Label>
            <p className="mt-1">
              {String(selectedExperience.start_date ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">End date</Label>
            <p className="mt-1">
              {String(selectedExperience.end_date ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Is current</Label>
            <p className="mt-1">
              {selectedExperience.is_current ? "Oui" : "Non"}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Description</Label>
            <p className="mt-1">
              {String(selectedExperience.description ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Technologies</Label>
            <p className="mt-1">
              {String(selectedExperience.technologies ?? "—")}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}