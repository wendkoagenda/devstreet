import { ArrowLeft, Construction } from "lucide-react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";

interface UpcomingScreenPageProps {
  /** Clé i18n sous `hub.upcoming.screens`. */
  screen:
    | "create_project"
    | "project_detail"
    | "task_contribution"
    | "contribution_review"
    | "ai_workshop";
  /** Lien de retour contextuel (fiche projet si fourni). */
  backTo?: string;
}

/** Destination réservée à un écran pas encore livré : rien n'y est présenté comme disponible. */
export default function UpcomingScreenPage({
  screen,
  backTo = "/hub/projects",
}: UpcomingScreenPageProps) {
  const { t } = useTranslation();

  return (
    <div className="mx-auto w-full max-w-2xl">
      <section className="flex flex-col items-center rounded-xl border border-dashed border-input bg-card px-6 py-14 text-center shadow-sm">
        <span className="mb-4 flex h-12 w-12 items-center justify-center rounded-full border border-warning/30 bg-warning-soft text-warning">
          <Construction aria-hidden className="h-6 w-6" />
        </span>
        <span className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-warning">
          {t("hub.upcoming.badge")}
        </span>
        <h1 className="mb-2 text-xl font-bold text-foreground">
          {t(`hub.upcoming.screens.${screen}`)}
        </h1>
        <p className="mb-6 max-w-md text-sm text-muted-foreground">{t("hub.upcoming.text")}</p>
        <Button asChild variant="outline" className="h-9 gap-1.5 rounded-lg text-xs font-semibold">
          <Link to={backTo}>
            <ArrowLeft aria-hidden />
            {t("hub.upcoming.back")}
          </Link>
        </Button>
      </section>
    </div>
  );
}
