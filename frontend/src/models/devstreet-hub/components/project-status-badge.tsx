import { Archive, Globe, Lock } from "lucide-react";
import { useTranslation } from "react-i18next";
import { cn } from "@/lib/utils";
import type { ProjectStatus } from "../schema";

const STYLES: Record<ProjectStatus, string> = {
  published: "border-border bg-secondary text-muted-foreground",
  draft: "border-warning/30 bg-warning-soft text-warning",
  archived: "border-border bg-muted text-muted-foreground",
};

const ICONS = { published: Globe, draft: Lock, archived: Archive } as const;

export function ProjectStatusBadge({ status }: { status: ProjectStatus }) {
  const { t } = useTranslation();
  const Icon = ICONS[status];

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded border px-2 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-wide",
        STYLES[status]
      )}
    >
      <Icon aria-hidden className="h-3 w-3" />
      {t(`hub.status.${status}`)}
    </span>
  );
}
