import { Check, Plus, RotateCw, Search, X } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import type { Technology } from "../schema";

const ALL_TECHNOLOGIES = "__all__";

export type CreateAction = "allowed" | "login" | "hidden";

interface ExplorerToolbarProps {
  searchInput: string;
  onSearchChange: (value: string) => void;
  onSearchClear: () => void;
  technology: string;
  technologies: Technology[];
  isCatalogLoading: boolean;
  hasCatalogError: boolean;
  onRetryCatalog: () => void;
  onTechnologyChange: (slug: string) => void;
  createAction: CreateAction;
  onCreate: () => void;
}

function CreateButton({
  createAction,
  onCreate,
  className,
}: Pick<ExplorerToolbarProps, "createAction" | "onCreate"> & { className?: string }) {
  const { t } = useTranslation();
  if (createAction === "hidden") return null;
  return (
    <Button
      type="button"
      onClick={onCreate}
      className={cn("group h-10 gap-1.5 rounded-lg px-4 text-xs font-semibold", className)}
    >
      <Plus
        aria-hidden
        className="text-brand transition-transform duration-200 group-hover:rotate-90"
      />
      {createAction === "login" ? t("hub.explorer.create_login") : t("hub.explorer.create")}
    </Button>
  );
}

export function ExplorerToolbar({
  searchInput,
  onSearchChange,
  onSearchClear,
  technology,
  technologies,
  isCatalogLoading,
  hasCatalogError,
  onRetryCatalog,
  onTechnologyChange,
  createAction,
  onCreate,
}: ExplorerToolbarProps) {
  const { t } = useTranslation();

  return (
    <div className="mb-4 flex flex-col gap-3">
      {/* Mobile : action principale visible au-dessus de la recherche */}
      <CreateButton
        createAction={createAction}
        onCreate={onCreate}
        className="h-11 w-full text-sm md:hidden"
      />

      <div className="rounded-xl border border-border bg-card p-3 shadow-sm sm:p-4">
        <div className="flex flex-col items-stretch gap-3 lg:flex-row lg:items-center">
          <div className="relative flex-1">
            <Search
              aria-hidden
              className="pointer-events-none absolute left-3.5 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-muted-foreground"
            />
            <label htmlFor="hub-project-search" className="sr-only">
              {t("hub.explorer.search_label")}
            </label>
            <input
              id="hub-project-search"
              type="search"
              value={searchInput}
              onChange={(event) => onSearchChange(event.target.value)}
              placeholder={t("hub.explorer.search_placeholder")}
              maxLength={200}
              autoComplete="off"
              className={cn(
                "h-10 w-full rounded-lg border border-input bg-background pl-11 pr-10 text-sm text-foreground transition-colors",
                "placeholder:text-muted-foreground focus-visible:border-brand focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring",
                "[&::-webkit-search-cancel-button]:hidden"
              )}
            />
            {searchInput && (
              <button
                type="button"
                onClick={onSearchClear}
                aria-label={t("hub.explorer.clear_search")}
                className="absolute right-2 top-1/2 flex h-7 w-7 -translate-y-1/2 items-center justify-center rounded-md text-muted-foreground hover:bg-accent hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <X aria-hidden className="h-4 w-4" />
              </button>
            )}
          </div>

          <div className="hidden items-center gap-2.5 md:flex">
            {hasCatalogError ? (
              <Button
                type="button"
                variant="outline"
                onClick={onRetryCatalog}
                className="h-10 min-w-[200px] justify-start gap-2 rounded-lg text-xs"
              >
                <RotateCw aria-hidden />
                {t("hub.explorer.catalog_retry")}
              </Button>
            ) : (
              <Select
                value={technology || ALL_TECHNOLOGIES}
                onValueChange={(value) =>
                  onTechnologyChange(value === ALL_TECHNOLOGIES ? "" : value)
                }
                disabled={isCatalogLoading}
              >
                <SelectTrigger
                  aria-label={t("hub.explorer.technology_label")}
                  className="h-10 min-w-[200px] rounded-lg bg-background text-xs font-medium shadow-none focus:border-brand"
                >
                  <SelectValue
                    placeholder={
                      isCatalogLoading
                        ? t("hub.explorer.catalog_loading")
                        : t("hub.explorer.all_technologies")
                    }
                  />
                </SelectTrigger>
                <SelectContent className="max-h-72">
                  <SelectItem value={ALL_TECHNOLOGIES}>
                    {t("hub.explorer.all_technologies")}
                  </SelectItem>
                  {technologies.map((tech) => (
                    <SelectItem key={tech.id} value={tech.slug}>
                      {tech.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
            <CreateButton createAction={createAction} onCreate={onCreate} />
          </div>
        </div>
      </div>

      {/* Mobile : technologies en pastilles défilantes, une seule sélection (contrat serveur) */}
      <div className="md:hidden">
        {hasCatalogError ? (
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onRetryCatalog}
            className="gap-2 rounded-full font-mono text-xs"
          >
            <RotateCw aria-hidden />
            {t("hub.explorer.catalog_retry")}
          </Button>
        ) : (
          <div
            role="radiogroup"
            aria-label={t("hub.explorer.technology_label")}
            className="-mx-4 flex gap-2 overflow-x-auto px-4 pb-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
          >
            {[{ id: 0, label: t("hub.explorer.all_short"), slug: "" }, ...technologies].map(
              (tech) => {
                const selected = technology === tech.slug;
                return (
                  <button
                    key={tech.slug || ALL_TECHNOLOGIES}
                    type="button"
                    role="radio"
                    aria-checked={selected}
                    onClick={() => onTechnologyChange(tech.slug)}
                    className={cn(
                      "inline-flex h-8 shrink-0 items-center gap-1 rounded-full border px-3.5 font-mono text-xs transition-colors",
                      "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
                      selected
                        ? "border-brand-strong bg-brand-strong font-semibold text-brand-foreground"
                        : "border-border bg-card text-foreground hover:bg-accent"
                    )}
                  >
                    {tech.label}
                    {selected && tech.slug && <Check aria-hidden className="h-3.5 w-3.5" />}
                  </button>
                );
              }
            )}
          </div>
        )}
      </div>
    </div>
  );
}
