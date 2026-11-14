import { Sparkles } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";

/**
 * Emplacement de l'assistant IA qui rédige l'offre à partir d'un court besoin : annoncé, désactivé
 * tant que la génération n'est pas branchée. Il vit dans le formulaire d'offre (page et boîte de dialogue).
 */
export function OfferAiPrompt({ className }: { className?: string }) {
  return (
    <div className={className}>
      <div className="flex flex-col gap-2 rounded-lg border border-dashed border-brand-soft-border bg-brand-soft/40 p-3">
        <div className="flex items-center justify-between gap-2">
          <label
            htmlFor="offer-ai-prompt"
            className="flex items-center gap-2 text-sm font-medium text-foreground"
          >
            <Sparkles className="size-4 text-brand-strong" aria-hidden />
            Décrivez votre besoin, l'IA rédige l'offre
          </label>
          <Badge variant="secondary">Bientôt disponible</Badge>
        </div>
        <Textarea
          id="offer-ai-prompt"
          disabled
          rows={2}
          placeholder="Ex. J'ai besoin d'une application de livraison pour mon restaurant, avec suivi des commandes."
        />
      </div>
    </div>
  );
}
