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
      ? "1 nouveauté de tes abonnements"
      : `${resume.nombre_nouveautes} nouveautés de tes abonnements`;

  const handleOpen = async () => {
    try {
      await markLire(resume.id).unwrap();
    } catch {
      // Naviguer quand même : le contenu reste dans le fil Abonnements.
    }
    onOpenAbonnements();
  };

  const handleDismiss = async () => {
    try {
      await markLire(resume.id).unwrap();
    } catch {
      // ignore
    }
  };

  return (
    <aside
      className="flex flex-col gap-3 rounded-2xl border border-border bg-muted/40 px-4 py-3 sm:flex-row sm:items-center sm:justify-between"
      aria-live="polite"
    >
      <div className="space-y-0.5">
        <p className="text-sm font-medium text-foreground">{label}</p>
        <p className="text-xs text-muted-foreground">
          Résumé du {formatPeriode(resume.periode_debut)}
        </p>
      </div>
      <div className="flex items-center gap-2">
        <Button
          type="button"
          size="sm"
          onClick={() => void handleOpen()}
          disabled={isLoading}
        >
          Voir les abonnements
        </Button>
        <Button
          type="button"
          size="sm"
          variant="ghost"
          onClick={() => void handleDismiss()}
          disabled={isLoading}
        >
          Marquer lu
        </Button>
      </div>
    </aside>
  );
}
