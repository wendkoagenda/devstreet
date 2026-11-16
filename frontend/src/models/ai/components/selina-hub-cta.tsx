import { useTranslation } from "react-i18next";
import { Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { useSelina } from "./use-selina";

type SelinaHubCtaProps = {
  className?: string;
};

/** Bouton fixe pour ouvrir Selina depuis une page projet / tâche. */
export function SelinaHubCta({ className }: SelinaHubCtaProps) {
  const { t } = useTranslation();
  const selina = useSelina();

  if (selina.open) return null;
  if (selina.isAuthenticated && !selina.canChat) return null;

  return (
    <button
      type="button"
      onClick={() => {
        if (!selina.isAuthenticated) {
          selina.requestLogin();
          return;
        }
        selina.setOpen(true);
      }}
      className={cn(
        "fixed bottom-5 right-5 z-30 inline-flex h-11 items-center gap-2 rounded-full border border-border bg-card px-3.5 text-xs font-semibold text-foreground shadow-floating",
        "transition hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/40",
        className
      )}
      aria-label={t("selina.hub_ask")}
    >
      <span className="inline-flex size-7 items-center justify-center rounded-full bg-gradient-to-tr from-brand to-brand-strong text-white">
        <Sparkles aria-hidden className="size-3.5" />
      </span>
      {t("selina.hub_ask")}
    </button>
  );
}
