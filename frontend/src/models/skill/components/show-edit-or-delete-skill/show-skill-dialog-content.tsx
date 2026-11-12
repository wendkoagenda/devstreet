import { Label } from "@/components/ui/label";
import { useSkillStore } from "../../slice";


export default function ShowSkillDialogContent() {
  const { selectedSkill } = useSkillStore();

  if (!selectedSkill) return null;

  return (
    <div className="flex flex-col gap-4 mx-4">
      <div className="max-h-[60vh] overflow-y-auto px-2 py-1">
        <div className="space-y-4">
          <div>
            <Label className="text-sm font-medium">Name</Label>
            <p className="mt-1">
              {String(selectedSkill.name ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Slug</Label>
            <p className="mt-1">
              {String(selectedSkill.slug ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Type</Label>
            <p className="mt-1">
              {(() => {
                const labels = {"hard": "Technique", "soft": "Comportementale"} as Record<string, string>;
                const value = selectedSkill.type;
                return labels[String(value ?? "")] ?? String(value ?? "—");
              })()}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Category</Label>
            <p className="mt-1">
              {(() => {
                const labels = {"frontend": "Frontend", "backend": "Backend", "mobile": "Mobile", "devops": "DevOps", "data": "Data", "design": "Design", "management": "Management", "soft": "Comportementale"} as Record<string, string>;
                const value = selectedSkill.category;
                return labels[String(value ?? "")] ?? String(value ?? "—");
              })()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}