import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Check, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ApplicationsStatsStrip } from "@/models/marketplace-stats/components/page-stats";
import { RequireProfil } from "@/models/marketplace-space/components/guards";
import { useGetMyCandidaturesQuery } from "../api";
import { formatDate } from "../labels";
import type { Candidature, CandidatureStatus } from "../schema";

type Step = { label: string; date: string; state: "done" | "final" | "refused" };

function statusLabel(
  t: (key: string) => string,
  status: CandidatureStatus
): string {
  return t(`marketplace.labels.candidature_status.${status}`);
}

/** Étapes connues d'une candidature : envoi, puis la dernière décision de l'entreprise. */
function stepsOf(
  candidature: Candidature,
  t: (key: string) => string
): Step[] {
  const steps: Step[] = [
    {
      label: statusLabel(t, "sent"),
      date: formatDate(candidature.created_at),
      state: "done",
    },
  ];
  if (candidature.status !== "sent") {
    steps.push({
      label: statusLabel(t, candidature.status),
      date: formatDate(candidature.decided_at),
      state:
        candidature.status === "accepted"
          ? "final"
          : candidature.status === "rejected"
            ? "refused"
            : "done",
    });
  }
  return steps;
}

function ApplicationCard({ candidature }: { candidature: Candidature }) {
  const { t } = useTranslation();
  const offer = candidature.offer;
  return (
    <Card>
      <CardHeader className="gap-1">
        <CardTitle className="text-base">
          {offer ? (
            <Link to={`/marketplace/offers/${offer.id}`} className="hover:underline">
              {offer.title}
            </Link>
          ) : (
            t("marketplace.offer_fallback")
          )}
        </CardTitle>
        <span className="text-xs text-muted-foreground">{offer?.company.name}</span>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <ol className="flex flex-col gap-3">
          {stepsOf(candidature, t).map((step) => (
            <li key={step.label} className="flex items-start gap-3">
              <span
                className={`flex size-6 shrink-0 items-center justify-center rounded-full ${
                  step.state === "refused"
                    ? "bg-destructive text-destructive-foreground"
                    : step.state === "final"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-foreground"
                }`}
                aria-hidden
              >
                {step.state === "refused" ? <X className="size-3.5" /> : <Check className="size-3.5" />}
              </span>
              <span className="flex flex-col">
                <span className="text-sm font-medium text-foreground">{step.label}</span>
                <span className="text-xs text-muted-foreground">{step.date}</span>
              </span>
            </li>
          ))}
        </ol>
        {candidature.status === "accepted" ? (
          <p className="rounded-lg border border-border bg-muted/40 p-3 text-xs leading-relaxed text-foreground">
            {t("marketplace.accepted_notice", {
              company: offer?.company.name ?? "",
            })}{" "}
            <Link to="/marketplace/availability" className="underline">
              {t("marketplace.availability_calendar")}
            </Link>
            .
          </p>
        ) : null}
      </CardContent>
    </Card>
  );
}

function MyApplicationsContent() {
  const { t } = useTranslation();
  const { data, isLoading, isError } = useGetMyCandidaturesQuery();

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-4">
      <ApplicationsStatsStrip />
      <div className="flex flex-col gap-1">
        <h1 className="text-xl font-semibold text-foreground">
          {t("marketplace.my_applications")}
        </h1>
        <p className="text-sm text-muted-foreground">
          {t("marketplace.my_applications_sub")}
        </p>
      </div>
      {isLoading ? (
        <Skeleton className="h-40 w-full" />
      ) : isError ? (
        <p className="rounded-lg border border-destructive/40 bg-card p-6 text-sm text-destructive">
          {t("marketplace.load_applications_error")}
        </p>
      ) : data && data.length > 0 ? (
        data.map((candidature) => (
          <ApplicationCard key={candidature.id} candidature={candidature} />
        ))
      ) : (
        <div className="flex flex-col items-center gap-3 rounded-lg border border-dashed border-input bg-card p-8 text-center text-sm text-muted-foreground">
          {t("marketplace.empty_applications")}
          <Button asChild>
            <Link to="/marketplace/offers">{t("marketplace.see_offers_for_me")}</Link>
          </Button>
        </div>
      )}
    </div>
  );
}

/** Mes candidatures : suivi de l'envoi à la décision de l'entreprise. */
export default function MyApplicationsPage() {
  return (
    <RequireProfil>
      <MyApplicationsContent />
    </RequireProfil>
  );
}
