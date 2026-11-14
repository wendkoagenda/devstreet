import { useId, useState } from "react";
import { BadgeCheck, Check, Lock } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { buildMediaUrl } from "@/helpers/displayers/media-url-builder";
import { cn } from "@/lib/utils";
import { useAuthSlice } from "@/models/auth/slice";
import {
  useCreatePublicationCommentMutation,
  useLazyGetPublicationCommentsQuery,
  useUpsertPublicationAvisMutation,
} from "../api";
import type { Publication } from "../schema";

type ChoixOptionsButtonsProps = {
  publication: Publication;
  /** Affiche la description sous le libellé (page détail) */
  showDescriptions?: boolean;
};

export function ChoixOptionsButtons({
  publication,
  showDescriptions = false,
}: ChoixOptionsButtonsProps) {
  const decided = Boolean(publication.decided_at);
  const options = publication.options ?? [];
  const myChoice = publication.mon_avis_option_id ?? null;
  const locked = Boolean(myChoice) || decided;
  const currentUserId = useAuthSlice((state) => state.user?.id);
  const commentFieldId = useId();

  const [pendingOptionId, setPendingOptionId] = useState<number | null>(null);
  const [comment, setComment] = useState("");

  const [loadComments] = useLazyGetPublicationCommentsQuery();
  const [upsertAvis, { isLoading: savingVote }] =
    useUpsertPublicationAvisMutation();
  const [createComment, { isLoading: savingComment }] =
    useCreatePublicationCommentMutation();
  const isLoading = savingVote || savingComment;

  if (options.length === 0) return null;

  const activeOptionId = locked ? myChoice : pendingOptionId;
  const totalVotes = options.reduce(
    (sum, option) => sum + (option.avis_count || 0),
    0
  );

  const handleSelectOption = (optionId: number) => {
    if (locked || isLoading) return;
    setPendingOptionId((current) => (current === optionId ? null : optionId));
    setComment("");
  };

  const handleConfirm = async () => {
    if (!pendingOptionId || locked) return;
    const texte = comment.trim();
    try {
      await upsertAvis({
        publicationId: publication.id,
        body: { option_id: pendingOptionId, explication: "" },
      }).unwrap();

      if (texte) {
        const existing = await loadComments(publication.id).unwrap();
        const alreadyCommented = existing.some(
          (item) =>
            item.parent == null &&
            item.auteur?.id != null &&
            item.auteur.id === currentUserId
        );

        if (!alreadyCommented) {
          await createComment({
            publicationId: publication.id,
            body: {
              texte,
              est_anonyme: false,
              nature: "COMMENTAIRE",
              medias_data: [],
              option_id: pendingOptionId,
            },
          }).unwrap();
          toast.success("Choix et commentaire enregistrés");
        } else {
          toast.success("Choix enregistré");
        }
      } else {
        toast.success("Choix enregistré");
      }

      setPendingOptionId(null);
      setComment("");
    } catch {
      toast.error("Impossible d'enregistrer ton choix");
    }
  };

  return (
    <div className="space-y-2" role="group" aria-label="Options de vote">
      {!decided ? (
        <p className="text-xs text-muted-foreground">
          {locked ? (
            <span className="inline-flex items-center gap-1">
              <Lock className="h-3 w-3" />
              Ton vote est enregistré — plus de changement possible
            </span>
          ) : (
            "Choisis une option, puis valide (commentaire optionnel)"
          )}
        </p>
      ) : null}

      {options.map((option) => {
        const selected = activeOptionId === option.id;
        const retained = publication.option_retenue === option.id;
        const confirmed = myChoice === option.id;
        const showForm = !locked && pendingOptionId === option.id;
        const percent =
          totalVotes > 0
            ? Math.round(((option.avis_count || 0) / totalVotes) * 100)
            : 0;

        return (
          <div
            key={option.id}
            className={cn(
              "overflow-hidden rounded-xl border transition-colors",
              retained
                ? "border-brand-soft-border bg-brand-soft/30"
                : selected
                  ? "border-brand-soft-border bg-brand-soft/15"
                  : "border-border bg-muted/20"
            )}
          >
            <button
              type="button"
              disabled={locked || isLoading}
              onClick={() => handleSelectOption(option.id)}
              aria-pressed={selected}
              className={cn(
                "relative flex w-full items-center gap-3 px-3 py-3 text-left",
                locked && "cursor-default"
              )}
            >
              <span
                aria-hidden
                className="pointer-events-none absolute inset-y-0 left-0 bg-brand-soft/35"
                style={{ width: `${percent}%` }}
              />
              <span
                className={cn(
                  "relative z-[1] flex h-5 w-5 shrink-0 items-center justify-center rounded-full border",
                  selected || retained
                    ? "border-brand-soft-border bg-brand-soft text-brand-strong"
                    : "border-border bg-background text-transparent"
                )}
              >
                <Check className="h-3 w-3" strokeWidth={3} />
              </span>
              {option.image_url ? (
                <img
                  src={buildMediaUrl(option.image_url)}
                  alt=""
                  className="relative z-[1] h-10 w-10 shrink-0 rounded-md border border-border object-cover"
                />
              ) : null}
              <div className="relative z-[1] min-w-0 flex-1 space-y-0.5">
                <p className="flex flex-wrap items-center gap-2 text-sm font-semibold text-foreground">
                  {option.libelle}
                  {confirmed && !retained ? (
                    <span className="text-[11px] font-medium text-brand-strong">
                      Ton choix
                    </span>
                  ) : null}
                  {showForm ? (
                    <span className="text-[11px] font-medium text-brand-strong">
                      Sélectionné
                    </span>
                  ) : null}
                  {retained ? (
                    <span className="inline-flex items-center gap-1 text-[11px] font-medium text-brand-strong">
                      <BadgeCheck className="h-3 w-3" />
                      Retenue
                    </span>
                  ) : null}
                </p>
                {showDescriptions && option.description ? (
                  <p className="whitespace-pre-wrap text-xs text-muted-foreground">
                    {option.description}
                  </p>
                ) : null}
              </div>
              <span className="relative z-[1] shrink-0 text-xs font-medium text-muted-foreground">
                {option.avis_count}
                {totalVotes > 0 ? (
                  <span className="text-muted-foreground/70"> · {percent}%</span>
                ) : null}
              </span>
            </button>

            {showForm ? (
              <div className="space-y-2 border-t border-border/80 bg-background/40 px-3 py-3">
                <label
                  htmlFor={`${commentFieldId}-${option.id}`}
                  className="text-xs font-medium text-muted-foreground"
                >
                  Commentaire sur ce choix{" "}
                  <span className="font-normal">(optionnel)</span>
                </label>
                <Textarea
                  id={`${commentFieldId}-${option.id}`}
                  rows={2}
                  value={comment}
                  onChange={(event) => setComment(event.target.value)}
                  placeholder="Pourquoi tu votes ça…"
                  disabled={isLoading}
                  className="resize-none bg-background"
                />
                <Button
                  type="button"
                  size="sm"
                  disabled={isLoading}
                  onClick={handleConfirm}
                >
                  {isLoading ? "Envoi…" : "Valider mon choix"}
                </Button>
              </div>
            ) : null}
          </div>
        );
      })}
    </div>
  );
}
