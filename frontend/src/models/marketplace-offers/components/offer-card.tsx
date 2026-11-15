import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { BadgeCheck } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { countryName } from "@/models/marketplace-space/options";
import {
  CANDIDATURE_STATUS_LABELS,
  formatBudget,
  offerFacts,
} from "../labels";
import type { Offer } from "../schema";
import { ScoreBadge } from "./score";

/** Carte d'une offre dans une liste : titre, entreprise, faits clés, compétences et score. */
export function OfferCard({ offer, to }: { offer: Offer; to: string }) {
  const { t, i18n } = useTranslation();
  const place = [offer.city, countryName(offer.country, i18n.language)]
    .filter(Boolean)
    .join(", ");
  const budget = formatBudget(offer);
  const matched = new Set(offer.matched_skill_ids ?? []);

  return (
    <Link to={to} className="group block">
      <Card className="transition-colors group-hover:bg-muted">
        <CardContent className="flex flex-wrap items-start gap-4 p-5">
          <div className="flex min-w-0 flex-1 basis-72 flex-col gap-2">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-sm font-semibold text-foreground">
                {offer.title}
              </span>
              {offer.my_candidature ? (
                <Badge variant="secondary">
                  {CANDIDATURE_STATUS_LABELS[offer.my_candidature.status]}
                </Badge>
              ) : null}
            </div>
            <span className="flex flex-wrap items-center gap-1 text-xs text-muted-foreground">
              {offer.company.name}
              {offer.company.is_verified ? (
                <BadgeCheck
                  className="size-3.5"
                  aria-label={t("marketplace.company_verified")}
                />
              ) : null}
              <span>· {place}</span>
              <span>· {offerFacts(offer).join(" · ")}</span>
              {budget ? <span>· {budget}</span> : null}
            </span>
            {offer.skills.length > 0 ? (
              <div className="flex flex-wrap gap-1.5">
                {offer.skills.map((skill) => (
                  <Badge
                    key={skill.id}
                    variant={matched.has(skill.id) ? "default" : "outline"}
                  >
                    {skill.name}
                  </Badge>
                ))}
              </div>
            ) : null}
          </div>
          {offer.score !== undefined ? <ScoreBadge score={offer.score} /> : null}
        </CardContent>
      </Card>
    </Link>
  );
}
