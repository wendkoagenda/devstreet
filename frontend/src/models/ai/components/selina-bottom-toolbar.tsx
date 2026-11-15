import { Clock3, Sparkles } from "lucide-react";
import { useTranslation } from "react-i18next";
import { cn } from "@/lib/utils";
import { useSelina } from "./use-selina";

/**
 * Toolbar flottante bas : hauteur ~44px, centrée, z-30.
 * Point d'entrée Selina (dock Sidekick) — plus de hero sous le titre du fil.
 */
export function SelinaBottomToolbar() {
  const { t } = useTranslation();
  const selina = useSelina();

  if (!selina.isAuthenticated || !selina.canChat) return null;
  if (selina.open) return null;

  return (
    <div className="pointer-events-none fixed inset-x-0 bottom-2 z-20 flex justify-center px-4 pb-[max(0.25rem,env(safe-area-inset-bottom))] sm:bottom-3">
      <div
        className={cn(
          "pointer-events-auto flex h-10 max-w-md items-center gap-2 rounded-full border border-border bg-card/95 px-3 shadow-md backdrop-blur-sm",
          "animate-in fade-in slide-in-from-bottom-2 duration-200"
        )}
      >
        <span
          className="inline-flex size-7 shrink-0 items-center justify-center rounded-full border border-brand-soft-border bg-brand-soft text-brand"
          aria-hidden
        >
          <Sparkles className="size-3.5" />
        </span>
        <button
          type="button"
          onClick={() => selina.openWithDraft()}
          className="min-w-0 flex-1 truncate text-left text-sm text-muted-foreground transition-colors duration-200 hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded-md"
          aria-label={t("selina.open")}
        >
          {t("selina.toolbar_placeholder")}
        </button>
        <button
          type="button"
          onClick={() => {
            selina.setOpen(true);
            selina.setRecentsOpen(true);
          }}
          className="inline-flex size-8 shrink-0 items-center justify-center rounded-full text-muted-foreground transition-colors duration-200 hover:bg-secondary hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          aria-label={t("selina.recents")}
        >
          <Clock3 className="size-3.5" aria-hidden />
        </button>
      </div>
    </div>
  );
}
