import { relationLabel } from "@/helpers/api/relations";
import { Label } from "@/components/ui/label";
import { useReviewStore } from "../../slice";


export default function ShowReviewDialogContent() {
  const { selectedReview } = useReviewStore();

  if (!selectedReview) return null;

  return (
    <div className="flex flex-col gap-4 mx-4">
      <div className="max-h-[60vh] overflow-y-auto px-2 py-1">
        <div className="space-y-4">
          <div>
            <Label className="text-sm font-medium">Profil noté</Label>
            <p className="mt-1">{relationLabel(selectedReview.target, ["slug", "headline"])}</p>
          </div>
          <div>
            <Label className="text-sm font-medium">Auteur de l'avis</Label>
            <p className="mt-1">{relationLabel(selectedReview.author, ["slug", "headline"])}</p>
          </div>
          <div>
            <Label className="text-sm font-medium">Candidature</Label>
            <p className="mt-1">{relationLabel(selectedReview.candidature, [])}</p>
          </div>
          <div>
            <Label className="text-sm font-medium">Rating</Label>
            <p className="mt-1">
              {String(selectedReview.rating ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Comment</Label>
            <p className="mt-1">
              {String(selectedReview.comment ?? "—")}
            </p>
          </div>
          <div>
            <Label className="text-sm font-medium">Is public</Label>
            <p className="mt-1">
              {selectedReview.is_public ? "Oui" : "Non"}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}