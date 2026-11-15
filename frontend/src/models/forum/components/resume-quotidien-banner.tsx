import { Button } from "@/components/ui/button";
import {
  useGetResumeActuelQuery,
  useMarkResumeLireMutation,
} from "../api";

type ResumeQuotidienBannerProps = {
  onOpenAbonnements: () => void;
};

function formatPeriode(isoDate: string): string {
  const parsed = new Date(`${isoDate}T12:00:00`);
  if (Number.isNaN(parsed.getTime())) return isoDate;
  return parsed.toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "long",
  });
}

export function ResumeQuotidienBanner({
  onOpenAbonnements,
}: ResumeQuotidienBannerProps) {
  const { data: resume } = useGetResumeActuelQuery();
  const [markLire, { isLoading }] = useMarkResumeLireMutation();

  if (!resume || resume.nombre_nouveautes <= 0) {
    return null;
  }

  const label =
    resume.nombre_nouveautes === 1
      ? "nouveauté de vos abonnements"
      : "nouveautés de vos abonnements";

  const handleOpen = async () => {
    try {
      await markLire(resume.id).unwrap();
    } catch (error) {
      // Naviguer quand même : le contenu reste dans le fil Abonnements.
      console.warn("Résumé quotidien non marqué comme lu :", error);
    }
    onOpenAbonnements();
  };

  const handleDismiss = async () => {
    try {
      await markLire(resume.id).unwrap();
    } catch (error) {
      console.warn("Résumé quotidien non marqué comme lu :", error);
    }
  };

  return (
    <aside
      className="flex flex-col gap-3 overflow-hidden rounded-xl border border-brand-soft-border bg-brand-soft px-4 py-3 sm:flex-row sm:items-center sm:justify-between"
      aria-live="polite"
    >
      <div className="flex min-w-0 items-start gap-3">
        <span className="mt-0.5 font-mono text-2xl font-semibold tabular-nums leading-none text-brand">
          {resume.nombre_nouveautes}
        </span>
        <div className="min-w-0 space-y-0.5">
          <p className="text-sm font-medium text-foreground">{label}</p>
          <p className="text-xs text-muted-foreground">
            Résumé du {formatPeriode(resume.periode_debut)}
          </p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <Button
          type="button"
          size="sm"
          className="bg-foreground text-background hover:bg-foreground/90"
          onClick={() => void handleOpen()}
          disabled={isLoading}
        >
          Voir les abonnements
        </Button>
        <Button
          type="button"
          size="sm"
          variant="ghost"
          className="text-muted-foreground"
          onClick={() => void handleDismiss()}
          disabled={isLoading}
        >
          Marquer lu
        </Button>
      </div>
    </aside>
  );
}
