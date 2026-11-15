import { useState } from "react";
import { Search } from "lucide-react";
import { useTranslation } from "react-i18next";
import { GlobalSearchDialog } from "@/components/layouts/global-search-dialog";
import { cn } from "@/lib/utils";

/** Recherche sticky style X — colonne droite du fil (Ctrl+K reste dans la topbar). */
export function FeedSearchRail() {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className={cn(
          "flex h-11 w-full items-center gap-2.5 rounded-full border border-border bg-muted/70 px-3.5 text-left transition-colors",
          "hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        )}
        aria-label={t("topbar.search_aria")}
      >
        <Search className="size-4 shrink-0 text-muted-foreground" aria-hidden />
        <span className="min-w-0 flex-1 truncate text-sm text-muted-foreground">
          {t("topbar.search_short")}
        </span>
      </button>
      <GlobalSearchDialog open={open} onOpenChange={setOpen} />
    </>
  );
}
