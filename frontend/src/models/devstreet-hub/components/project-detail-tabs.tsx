import { useTranslation } from "react-i18next";
import { cn } from "@/lib/utils";
import type { ProjectDetailTab } from "../schema";

const TABS: ProjectDetailTab[] = [
  "presentation",
  "code",
  "contribute",
  "team",
];

interface ProjectDetailTabsProps {
  active: ProjectDetailTab;
  onChange: (tab: ProjectDetailTab) => void;
}

export function ProjectDetailTabs({ active, onChange }: ProjectDetailTabsProps) {
  const { t } = useTranslation();

  return (
    <nav
      aria-label={t("hub.detail.tabs_label")}
      className="flex gap-1 overflow-x-auto border-b border-border"
    >
      {TABS.map((tab) => {
        const selected = active === tab;
        return (
          <button
            key={tab}
            type="button"
            onClick={() => onChange(tab)}
            className={cn(
              "shrink-0 border-b-2 px-3 py-2.5 text-xs font-semibold transition-colors",
              selected
                ? "border-brand text-brand"
                : "border-transparent text-muted-foreground hover:text-foreground"
            )}
            aria-current={selected ? "page" : undefined}
          >
            {t(`hub.detail.tabs.${tab}`)}
          </button>
        );
      })}
    </nav>
  );
}
