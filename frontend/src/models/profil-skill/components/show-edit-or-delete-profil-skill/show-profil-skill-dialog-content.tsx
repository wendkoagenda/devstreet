import { relationLabel } from "@/helpers/api/relations";
import { Label } from "@/components/ui/label";
import { useProfilSkillStore } from "../../slice";


export default function ShowProfilSkillDialogContent() {
  const { selectedProfilSkill } = useProfilSkillStore();

  if (!selectedProfilSkill) return null;

  return (
    <div className="flex flex-col gap-4 mx-4">
      <div className="max-h-[60vh] overflow-y-auto px-2 py-1">
        <div className="space-y-4">
          <div>
            <Label className="text-sm font-medium">Profil</Label>
            <p className="mt-1">{relationLabel(selectedProfilSkill.profil, ["slug", "headline"])}</p>
          </div>
          <div>
            <Label className="text-sm font-medium">Compétence</Label>
            <p className="mt-1">{relationLabel(selectedProfilSkill.skill, ["name"])}</p>
          </div>
          <div>
            <Label className="text-sm font-medium">Level</Label>
            <p className="mt-1">
              {String(selectedProfilSkill.level ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Years</Label>
            <p className="mt-1">
              {String(selectedProfilSkill.years ?? "—")}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}