import { Bell } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  useGetResumeActuelQuery,
  useMarkResumeLireMutation,
} from "../api";

function formatPeriode(isoDate: string): string {
  const parsed = new Date(`${isoDate}T12:00:00`);
  if (Number.isNaN(parsed.getTime())) return isoDate;
  return parsed.toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "long",
  });
}

type ResumeNotificationBellProps = {
  /** Affichage du badge : compteur ou simple point. */
  indicator?: "count" | "dot";
};

export function ResumeNotificationBell({
  indicator = "count",
}: ResumeNotificationBellProps) {
  const navigate = useNavigate();
  const { data: resume } = useGetResumeActuelQuery();
  const [markLire, { isLoading }] = useMarkResumeLireMutation();

  const count = resume?.nombre_nouveautes ?? 0;
  const hasNotif = Boolean(resume && count > 0);

  const handleOpen = async () => {
    if (!resume) return;
    try {
      await markLire(resume.id).unwrap();
    } catch (error) {
      console.warn("Résumé non marqué comme lu, navigation poursuivie", error);
    }
    navigate("/?tab=abonnements");
  };

  const handleDismiss = async () => {
    if (!resume) return;
    try {
      await markLire(resume.id).unwrap();
    } catch (error) {
      console.warn("Résumé non marqué comme lu", error);
    }
  };

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="relative size-9 rounded-xl"
          aria-label={
            hasNotif
              ? `${count} nouveautés d'abonnements`
              : "Notifications"
          }
        >
          <Bell className="size-4" aria-hidden />
          {hasNotif ? (
            indicator === "dot" ? (
              <span
                className="absolute right-2 top-2 size-1.5 rounded-full bg-foreground"
                aria-hidden
              />
            ) : (
              <span className="absolute right-1.5 top-1.5 flex size-4 items-center justify-center rounded-full bg-brand font-mono text-[9px] font-semibold text-brand-foreground">
                {count > 9 ? "9+" : count}
              </span>
            )
          ) : null}
        </Button>
      </PopoverTrigger>
      <PopoverContent align="end" className="w-72 p-3">
        {!hasNotif || !resume ? (
          <p className="text-sm text-muted-foreground">
            Aucune nouveauté pour le moment.
          </p>
        ) : (
          <div className="space-y-3">
            <div>
              <p className="text-sm font-medium text-foreground">
                <span className="font-mono tabular-nums text-brand">
                  {count}
                </span>{" "}
                {count === 1
                  ? "nouveauté d’abonnements"
                  : "nouveautés d’abonnements"}
              </p>
              <p className="mt-0.5 text-xs text-muted-foreground">
                Résumé du {formatPeriode(resume.periode_debut)}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button
                type="button"
                size="sm"
                className="flex-1"
                disabled={isLoading}
                onClick={() => void handleOpen()}
              >
                Voir
              </Button>
              <Button
                type="button"
                size="sm"
                variant="ghost"
                disabled={isLoading}
                onClick={() => void handleDismiss()}
              >
                Lu
              </Button>
            </div>
          </div>
        )}
      </PopoverContent>
    </Popover>
  );
}
