import { useMemo } from "react";
import { X } from "lucide-react";
import { useTranslation } from "react-i18next";
import { cn } from "@/lib/utils";
import { useSelina } from "./use-selina";

type RecentItem = {
  id: number;
  title: string;
  updated_at: string;
};

function startOfDay(date: Date): number {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime();
}

function groupLabel(
  iso: string,
  locale: string,
  todayLabel: string
): string {
  try {
    const date = new Date(iso);
    const today = startOfDay(new Date());
    const day = startOfDay(date);
    if (day === today) return todayLabel;
    return new Intl.DateTimeFormat(locale, {
      day: "numeric",
      month: "short",
      year: "numeric",
    }).format(date);
  } catch {
    return iso;
  }
}

function groupByDay(
  items: RecentItem[],
  locale: string,
  todayLabel: string
): Array<{ label: string; items: RecentItem[] }> {
  const map = new Map<string, RecentItem[]>();
  for (const item of items) {
    const label = groupLabel(item.updated_at, locale, todayLabel);
    const list = map.get(label) ?? [];
    list.push(item);
    map.set(label, list);
  }
  return Array.from(map.entries()).map(([label, groupItems]) => ({
    label,
    items: groupItems,
  }));
}

/** Historique style Grok : titre centré, groupes par date, ligne sélectionnée. */
export function SelinaRecents() {
  const { t, i18n } = useTranslation();
  const selina = useSelina();

  const groups = useMemo(
    () =>
      groupByDay(
        selina.recentConversations,
        i18n.language,
        t("selina.today")
      ),
    [i18n.language, selina.recentConversations, t]
  );

  if (!selina.recentsOpen) return null;

  return (
    <div
      className={cn(
        "absolute inset-0 z-20 flex flex-col bg-card",
        "animate-in fade-in duration-200 sm:rounded-2xl"
      )}
      role="dialog"
      aria-label={t("selina.history")}
    >
      <header className="relative flex h-12 shrink-0 items-center justify-center px-12">
        <button
          type="button"
          onClick={() => selina.setRecentsOpen(false)}
          className="absolute left-2 top-1/2 inline-flex size-9 -translate-y-1/2 items-center justify-center rounded-full text-foreground transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          aria-label={t("selina.back")}
        >
          <X className="size-[18px]" strokeWidth={1.75} aria-hidden />
        </button>
        <h2 className="text-[17px] font-bold tracking-tight text-foreground">
          {t("selina.history")}
        </h2>
      </header>

      <div className="border-b border-border px-4">
        <div className="relative inline-flex pb-2.5">
          <span className="text-[15px] font-semibold text-foreground">
            {t("selina.history_chats")}
          </span>
          <span
            className="absolute inset-x-0 -bottom-px h-0.5 rounded-full bg-brand"
            aria-hidden
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-2 pb-6 pt-3">
        {selina.recentsLoading ? (
          <p className="px-3 py-8 text-center text-sm text-muted-foreground">
            {t("selina.recents_loading")}
          </p>
        ) : null}

        {!selina.recentsLoading &&
        selina.recentConversations.length === 0 ? (
          <p className="px-3 py-8 text-center text-sm text-muted-foreground">
            {t("selina.recents_empty")}
          </p>
        ) : null}

        <div className="space-y-5">
          {groups.map((group) => (
            <section key={group.label}>
              <h3 className="mb-1 px-3 text-[13px] font-bold text-foreground/90">
                {group.label}
              </h3>
              <ul className="space-y-0.5">
                {group.items.map((item) => {
                  const active = selina.conversationId === item.id;
                  return (
                    <li key={item.id}>
                      <button
                        type="button"
                        onClick={() => selina.loadConversation(item.id)}
                        className={cn(
                          "flex w-full items-center rounded-xl px-3 py-2.5 text-left text-[15px] text-foreground transition-colors",
                          "hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                          active && "bg-muted"
                        )}
                      >
                        <span className="min-w-0 flex-1 truncate font-normal tracking-tight">
                          {item.title}
                        </span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            </section>
          ))}
        </div>
      </div>
    </div>
  );
}
