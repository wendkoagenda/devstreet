import { useTranslation } from "react-i18next";
import { Badge } from "@/components/ui/badge";
import type { ScoreItem } from "../schema";

/** Score total sur 100, avec une légende (« correspondance »). */
export function ScoreBadge({
  score,
  caption,
}: {
  score: number;
  caption?: string;
}) {
  const { t } = useTranslation();
  return (
    <div className="flex shrink-0 flex-col items-end gap-0.5">
      <span className="text-2xl font-semibold leading-none text-foreground">
        {score}
      </span>
      <span className="text-xs text-muted-foreground">
        {caption ?? t("marketplace.match_caption")}
      </span>
    </div>
  );
}

function criterionLabel(
  t: (key: string, options?: Record<string, unknown>) => string,
  item: ScoreItem
) {
  const key = `marketplace.labels.score_criterion.${item.key}`;
  const translated = t(key);
  return translated === key ? item.label : translated;
}

function criterionDetail(
  t: (key: string, options?: Record<string, unknown>) => string,
  item: ScoreItem
) {
  if (!item.detail_key) return item.detail;
  const params = item.detail_params ?? {};
  if (item.detail_key === "skills_matched") {
    const matched = Number(params.matched ?? 0);
    return t("marketplace.labels.score_detail.skills_matched", {
      count: matched,
      total: params.total ?? 0,
    });
  }
  if (item.detail_key === "experience_years") {
    const years = Number(params.years ?? 0);
    const needed = Number(params.needed ?? 0);
    return t("marketplace.labels.score_detail.experience_years", {
      yearsLabel: t("marketplace.years_short", { count: years }),
      neededLabel: t("marketplace.years_short", { count: needed }),
    });
  }
  const key = `marketplace.labels.score_detail.${item.detail_key}`;
  const translated = t(key, params);
  return translated === key ? item.detail : translated;
}

/** Détail du score par critère (barres de progression). La part IA est annoncée mais pas encore active. */
export function ScoreBreakdown({ items }: { items: ScoreItem[] }) {
  const { t } = useTranslation();
  return (
    <div className="flex flex-col gap-3">
      {items.map((item) => {
        const label = criterionLabel(t, item);
        const detail = criterionDetail(t, item);
        return (
          <div key={item.key} className="flex flex-col gap-1">
            <div className="flex items-center justify-between text-xs">
              <span className="text-foreground">{label}</span>
              <span className="text-muted-foreground">
                {item.score} / {item.max}
              </span>
            </div>
            <div
              className="h-1.5 overflow-hidden rounded-full bg-muted"
              role="progressbar"
              aria-label={label}
              aria-valuemin={0}
              aria-valuemax={item.max}
              aria-valuenow={item.score}
            >
              <div
                className="h-full rounded-full bg-primary"
                style={{
                  width: `${item.max ? (item.score / item.max) * 100 : 0}%`,
                }}
              />
            </div>
            <span className="text-xs text-muted-foreground">{detail}</span>
          </div>
        );
      })}
      <div className="flex items-center justify-between border-t border-border pt-3 text-xs text-muted-foreground">
        <span>{t("marketplace.ai_score_share")}</span>
        <Badge variant="secondary">{t("marketplace.ai_score_soon")}</Badge>
      </div>
    </div>
  );
}
