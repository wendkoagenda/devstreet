import { Link } from "react-router-dom";
import { Check, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { RequireProfil } from "@/models/marketplace-space/components/guards";
import { useGetMyCandidaturesQuery } from "../api";
import { CANDIDATURE_STATUS_LABELS, formatDate } from "../labels";
import type { Candidature } from "../schema";

type Step = { label: string; date: string; state: "done" | "final" | "refused" };

/** Étapes connues d'une candidature : envoi, puis la dernière décision de l'entreprise. */
function stepsOf(candidature: Candidature): Step[] {
  const steps: Step[] = [
    { label: CANDIDATURE_STATUS_LABELS.sent, date: formatDate(candidature.created_at), state: "done" },
  ];
  if (candidature.status !== "sent") {
    steps.push({
      label: CANDIDATURE_STATUS_LABELS[candidature.status],
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
            "Offre"
          )}
        </CardTitle>
        <span className="text-xs text-muted-foreground">{offer?.company.name}</span>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <ol className="flex flex-col gap-3">
          {stepsOf(candidature).map((step) => (
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
            {offer?.company.name} vous a choisi. La mission est ajoutée à votre calendrier de disponibilité.
          </p>
        ) : null}
      </CardContent>
    </Card>
  );
}

function MyApplicationsContent() {
  const { data, isLoading, isError } = useGetMyCandidaturesQuery();

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-4">
      <div className="flex flex-col gap-1">
        <h1 className="text-xl font-semibold text-foreground">Suivi de mes candidatures</h1>
        <p className="text-sm text-muted-foreground">
          L'état de chaque candidature envoyée, mis à jour par les entreprises.
        </p>
      </div>
      {isLoading ? (
        <Skeleton className="h-40 w-full" />
      ) : isError ? (
        <p className="rounded-lg border border-destructive/40 bg-card p-6 text-sm text-destructive">
          Impossible de charger vos candidatures.
        </p>
      ) : data && data.length > 0 ? (
        data.map((candidature) => <ApplicationCard key={candidature.id} candidature={candidature} />)
      ) : (
        <div className="flex flex-col items-center gap-3 rounded-lg border border-dashed border-input bg-card p-8 text-center text-sm text-muted-foreground">
          Vous n'avez encore postulé à aucune offre.
          <Button asChild>
            <Link to="/marketplace/offers">Voir les offres pour moi</Link>
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
