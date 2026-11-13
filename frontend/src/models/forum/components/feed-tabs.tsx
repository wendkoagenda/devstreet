import { cn } from "@/lib/utils";

export type FeedTabId =
  | "pour-vous"
  | "abonnements"
  | "populaires"
  | "discussions"
  | "showcase"
  | "derniers";

const TABS: Array<{ id: FeedTabId; label: string; enabled: boolean }> = [
  { id: "pour-vous", label: "Pour vous", enabled: true },
  { id: "abonnements", label: "Abonnements", enabled: true },
  { id: "populaires", label: "Populaires", enabled: false },
  { id: "discussions", label: "Discussions", enabled: true },
  { id: "showcase", label: "Showcase Projets", enabled: true },
  { id: "derniers", label: "Derniers posts", enabled: true },
];

type FeedTabsProps = {
  value: FeedTabId;
  onChange: (tab: FeedTabId) => void;
};

export function FeedTabs({ value, onChange }: FeedTabsProps) {
  return (
    <div className="overflow-x-auto border-b border-border">
      <div role="tablist" aria-label="Filtres du fil" className="flex min-w-max gap-1">
        {TABS.map((tab) => {
          const active = value === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              role="tab"
              aria-selected={active}
              disabled={!tab.enabled}
              onClick={() => onChange(tab.id)}
              className={cn(
                "relative px-3 py-2.5 text-sm font-medium transition-colors",
                active
                  ? "text-foreground"
                  : "text-muted-foreground hover:text-foreground",
                !tab.enabled &&
                  "cursor-not-allowed opacity-45 hover:text-muted-foreground"
              )}
            >
              {tab.label}
              {active ? (
                <span className="absolute inset-x-2 -bottom-px h-0.5 rounded-full bg-brand" />
              ) : null}
            </button>
          );
        })}
      </div>
    </div>
  );
}
