import { Badge } from "@/components/ui/badge";
import type { ScoreItem } from "../schema";

/** Score total sur 100, avec une légende (« correspondance »). */
export function ScoreBadge({ score, caption = "correspondance" }: { score: number; caption?: string }) {
  return (
    <div className="flex shrink-0 flex-col items-end gap-0.5">
      <span className="text-2xl font-semibold leading-none text-foreground">{score}</span>
      <span className="text-xs text-muted-foreground">{caption}</span>
    </div>
  );
}

/** Détail du score par critère (barres de progression). La part IA est annoncée mais pas encore active. */
export function ScoreBreakdown({ items }: { items: ScoreItem[] }) {
  return (
    <div className="flex flex-col gap-3">
      {items.map((item) => (
        <div key={item.key} className="flex flex-col gap-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-foreground">{item.label}</span>
            <span className="text-muted-foreground">
              {item.score} / {item.max}
            </span>
          </div>
          <div
            className="h-1.5 overflow-hidden rounded-full bg-muted"
            role="progressbar"
            aria-label={item.label}
            aria-valuemin={0}
            aria-valuemax={item.max}
            aria-valuenow={item.score}
          >
            <div
              className="h-full rounded-full bg-primary"
              style={{ width: `${item.max ? (item.score / item.max) * 100 : 0}%` }}
            />
          </div>
          <span className="text-xs text-muted-foreground">{item.detail}</span>
        </div>
      ))}
      <div className="flex items-center justify-between border-t border-border pt-3 text-xs text-muted-foreground">
        <span>Part IA du score</span>
        <Badge variant="secondary">Bientôt disponible</Badge>
      </div>
    </div>
  );
}
