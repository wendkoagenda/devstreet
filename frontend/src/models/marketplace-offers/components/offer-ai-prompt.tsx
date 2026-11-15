import { useState } from "react";
import { useFormContext } from "react-hook-form";
import { Loader2, Sparkles, Undo2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useGenerateMyOfferMutation } from "../api";
import { draftToForm, type OfferFormValues } from "../schema";

const MIN_BRIEF_LENGTH = 12;
const MAX_BRIEF_LENGTH = 4000;

/** Champs du formulaire remplis par l'IA ; les dates restent à la main du recruteur. */
const AI_FIELDS = [
  "title",
  "description",
  "type",
  "experience_level",
  "work_mode",
  "contract_duration",
  "contract_duration_unit",
  "budget_min",
  "budget_max",
  "currency",
  "budget_period",
  "country",
  "city",
  "required_skill_ids",
] as const satisfies readonly (keyof OfferFormValues)[];

type Summary = {
  provider: string;
  model: string;
  skills: number;
  profils: number;
};

/** Message lisible renvoyé par l'API (`detail` ou erreur de champ `brief`), sinon un repli selon le code HTTP. */
function errorMessage(error: unknown): string {
  const { status, data } = error as { status?: number | string; data?: Record<string, unknown> };
  const raw = data?.detail ?? data?.brief;
  const text = Array.isArray(raw) ? raw[0] : raw;
  if (typeof text === "string" && text) return text;
  if (status === 429) return "Vous avez atteint votre quota de générations pour aujourd'hui. Réessayez demain ou rédigez l'offre à la main.";
  if (status === 503) return "L'assistant IA est indisponible pour le moment. Vous pouvez rédiger l'offre à la main.";
  if (status === "FETCH_ERROR") return "Connexion impossible. Vérifiez votre réseau et réessayez.";
  return "La génération a échoué. Réessayez ou rédigez l'offre à la main.";
}

/**
 * Assistant IA du formulaire d'offre : à partir d'un court besoin, il propose un brouillon (titre, description,
 * type, niveau, budget, compétences). Le formulaire est prérempli, jamais publié : le recruteur relit et décide.
 * Il vit dans le formulaire d'offre (page et boîte de dialogue), à la création uniquement.
 */
export function OfferAiPrompt({ className }: { className?: string }) {
  const form = useFormContext<OfferFormValues>();
  const [generate, { isLoading }] = useGenerateMyOfferMutation();
  const [brief, setBrief] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<Summary | null>(null);
  // Valeurs d'avant la génération, pour pouvoir revenir en arrière
  const [previous, setPrevious] = useState<Partial<OfferFormValues> | null>(null);

  const trimmed = brief.trim();
  const tooShort = trimmed.length < MIN_BRIEF_LENGTH;

  const handleGenerate = async () => {
    if (tooShort || isLoading) return;
    setError(null);
    try {
      const result = await generate({ brief: trimmed }).unwrap();
      const values = draftToForm(result.draft);
      const snapshot = Object.fromEntries(AI_FIELDS.map((field) => [field, form.getValues(field)]));
      setPrevious(snapshot as Partial<OfferFormValues>);
      for (const field of AI_FIELDS) {
        form.setValue(field, values[field] as never, { shouldDirty: true, shouldValidate: false });
      }
      form.clearErrors();
      setSummary({
        provider: result.provider,
        model: result.model,
        skills: result.draft.required_skill_ids.length,
        profils: result.suggested_profils.length,
      });
    } catch (err) {
      setSummary(null);
      setError(errorMessage(err));
    }
  };

  const handleUndo = () => {
    if (!previous) return;
    for (const field of AI_FIELDS) {
      form.setValue(field, previous[field] as never, { shouldDirty: true });
    }
    setPrevious(null);
    setSummary(null);
  };

  return (
    <div className={className}>
      <div className="flex flex-col gap-2 rounded-lg border border-dashed border-brand-soft-border bg-brand-soft/40 p-3">
        <label
          htmlFor="offer-ai-prompt"
          className="flex items-center gap-2 text-sm font-medium text-foreground"
        >
          <Sparkles className="size-4 text-brand-strong" aria-hidden />
          Décrivez votre besoin, l'IA rédige l'offre
        </label>
        <Textarea
          id="offer-ai-prompt"
          rows={3}
          value={brief}
          maxLength={MAX_BRIEF_LENGTH}
          disabled={isLoading}
          onChange={(event) => setBrief(event.target.value)}
          onKeyDown={(event) => {
            // Entrée seule reste un retour à la ligne ; Ctrl/Cmd + Entrée lance la génération
            if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
              event.preventDefault();
              void handleGenerate();
            }
          }}
          placeholder="Ex. J'ai besoin d'une application de livraison pour mon restaurant, avec suivi des commandes."
        />
        <div className="flex flex-wrap items-center justify-between gap-2">
          <p className="text-xs text-muted-foreground">
            {tooShort && trimmed.length > 0
              ? `Encore ${MIN_BRIEF_LENGTH - trimmed.length} caractères au minimum.`
              : "Le formulaire est prérempli : vous relisez et modifiez avant de publier."}
          </p>
          <div className="flex items-center gap-2">
            {previous ? (
              <Button type="button" variant="ghost" size="sm" onClick={handleUndo} disabled={isLoading}>
                <Undo2 className="size-3.5" aria-hidden />
                Annuler
              </Button>
            ) : null}
            <Button
              type="button"
              size="sm"
              onClick={() => void handleGenerate()}
              disabled={tooShort || isLoading}
              className="gap-1.5"
            >
              {isLoading ? (
                <Loader2 className="size-3.5 animate-spin" aria-hidden />
              ) : (
                <Sparkles className="size-3.5" aria-hidden />
              )}
              {isLoading ? "Rédaction…" : summary ? "Régénérer" : "Rédiger l'offre"}
            </Button>
          </div>
        </div>

        {error ? (
          <p role="alert" className="text-sm text-destructive">
            {error}
          </p>
        ) : null}

        {summary ? (
          <p role="status" className="text-xs text-muted-foreground">
            Brouillon généré ({summary.provider}, {summary.model}).{" "}
            {summary.skills > 0
              ? `${summary.skills} compétence${summary.skills > 1 ? "s" : ""} rattachée${summary.skills > 1 ? "s" : ""} à l'offre. `
              : "Aucune compétence reconnue : ajoutez-les à l'étape suivante. "}
            {summary.profils > 0
              ? `${summary.profils} profil${summary.profils > 1 ? "s" : ""} correspondent déjà à ce besoin.`
              : ""}
          </p>
        ) : null}
      </div>
    </div>
  );
}
