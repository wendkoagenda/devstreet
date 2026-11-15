import { useEffect, useRef } from "react";
import {
  History,
  Loader2,
  SquarePen,
  ArrowUp,
  Sparkles,
  ChevronDown,
} from "lucide-react";
import { useTranslation } from "react-i18next";
import { cn } from "@/lib/utils";
import { SafeMarkdown } from "@/models/devstreet-hub/functions/safe-markdown";
import type { ChatTurn } from "../schema";
import { SelinaRecents } from "./selina-recents";
import { useSelina } from "./use-selina";

function ThinkingStatus({ label, ariaLabel }: { label: string; ariaLabel: string }) {
  return (
    <div
      className="animate-assistant-msg-in flex items-center gap-2 px-1 py-1 text-sm text-muted-foreground"
      role="status"
      aria-live="polite"
      aria-label={ariaLabel}
    >
      <span
        className="grid size-4 shrink-0 grid-cols-2 gap-0.5"
        aria-hidden
      >
        <span className="size-1.5 rounded-[1px] bg-muted-foreground/70" />
        <span className="size-1.5 rounded-[1px] bg-muted-foreground/70" />
        <span className="size-1.5 rounded-[1px] bg-muted-foreground/50" />
        <span className="size-1.5 rounded-[1px] bg-muted-foreground/50" />
      </span>
      <span className="font-normal tracking-tight">{label}</span>
    </div>
  );
}

function MessageRow({ turn }: { turn: ChatTurn }) {
  const isUser = turn.role === "user";

  if (isUser) {
    return (
      <div className="animate-assistant-msg-in flex justify-end">
        <div className="max-w-[88%] rounded-[1.35rem] bg-muted px-4 py-2.5 text-[15px] leading-relaxed text-foreground">
          <p className="whitespace-pre-wrap">{turn.content}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-assistant-msg-in max-w-[95%] px-1 text-[15px] leading-relaxed text-foreground">
      <SafeMarkdown content={turn.content} />
      {turn.provider ? (
        <p className="mt-2 text-[11px] text-muted-foreground/80">
          {turn.provider}
          {turn.failoverReason ? ` · ${turn.failoverReason}` : ""}
        </p>
      ) : null}
    </div>
  );
}

/** Dock Selina — intérieur style Grok (bulles, thinking, header icônes). */
export function SelinaPanel() {
  const { t } = useTranslation();
  const selina = useSelina();
  const panelRef = useRef<HTMLElement>(null);
  const scrollerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!selina.open) return;
    const node = scrollerRef.current;
    if (!node) return;
    node.scrollTo({ top: node.scrollHeight, behavior: "smooth" });
  }, [selina.turns, selina.isBusy, selina.open]);

  useEffect(() => {
    if (!selina.open || selina.recentsOpen) return;
    const timer = window.setTimeout(() => inputRef.current?.focus(), 80);
    return () => window.clearTimeout(timer);
  }, [selina.open, selina.recentsOpen]);

  useEffect(() => {
    if (!selina.open) return;
    const previouslyFocused = document.activeElement as HTMLElement | null;
    return () => {
      previouslyFocused?.focus?.();
    };
  }, [selina.open]);

  useEffect(() => {
    if (!selina.open) return;
    const panel = panelRef.current;
    if (!panel) return;

    const focusableSelector =
      'button:not([disabled]), [href], textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])';

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key !== "Tab") return;
      const focusable = Array.from(
        panel.querySelectorAll<HTMLElement>(focusableSelector)
      ).filter(
        (node) => !node.hasAttribute("disabled") && node.offsetParent !== null
      );
      if (focusable.length === 0) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      const active = document.activeElement as HTMLElement | null;
      if (event.shiftKey && active === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && active === last) {
        event.preventDefault();
        first.focus();
      }
    };

    panel.addEventListener("keydown", onKeyDown);
    return () => panel.removeEventListener("keydown", onKeyDown);
  }, [selina.open, selina.recentsOpen]);

  if (!selina.open) return null;
  if (!selina.isAuthenticated || !selina.canChat) return null;

  const canSend = Boolean(selina.draft.trim()) && !selina.isBusy;

  return (
    <aside
      ref={panelRef}
      className={cn(
        "fixed bottom-0 right-0 top-0 z-40 flex w-[min(400px,100vw)] flex-col",
        "border-l border-border bg-card shadow-[0_8px_40px_hsl(var(--foreground)/0.08)]",
        "sm:top-[4.75rem] sm:bottom-3 sm:right-3 sm:rounded-2xl sm:border",
        "animate-in slide-in-from-right duration-200"
      )}
      role="complementary"
      aria-label={t("selina.title")}
    >
      {/* Header Grok : icônes à droite uniquement */}
      <header className="flex h-12 shrink-0 items-center justify-end gap-0.5 px-2.5">
        <button
          type="button"
          onClick={() => selina.setRecentsOpen(true)}
          className="inline-flex size-9 items-center justify-center rounded-full text-foreground/80 transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          aria-label={t("selina.history")}
        >
          <History className="size-[18px]" strokeWidth={1.75} aria-hidden />
        </button>
        <button
          type="button"
          onClick={selina.startNewConversation}
          className="inline-flex size-9 items-center justify-center rounded-full text-foreground/80 transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          aria-label={t("selina.new")}
        >
          <SquarePen className="size-[18px]" strokeWidth={1.75} aria-hidden />
        </button>
        <button
          type="button"
          onClick={selina.close}
          className="inline-flex size-9 items-center justify-center rounded-full text-foreground/80 transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          aria-label={t("selina.close")}
        >
          <ChevronDown className="size-[18px]" strokeWidth={1.75} aria-hidden />
        </button>
      </header>

      <div className="relative flex min-h-0 flex-1 flex-col">
        <SelinaRecents />

        <div
          ref={scrollerRef}
          className="flex-1 space-y-5 overflow-y-auto px-4 pb-3 pt-1 scrollbar-none"
        >
          {selina.turns.length === 0 && !selina.isBusy ? (
            <div className="flex h-full flex-col items-center justify-center gap-3 px-4 text-center">
              <Sparkles
                className="size-7 text-muted-foreground/70"
                strokeWidth={1.5}
                aria-hidden
              />
              <p className="text-[17px] font-semibold tracking-tight text-foreground">
                {t("selina.empty_title")}
              </p>
              <p className="max-w-[15rem] text-sm leading-snug text-muted-foreground">
                {t("selina.empty")}
              </p>
            </div>
          ) : (
            <>
              {selina.turns.map((turn) => (
                <MessageRow key={turn.id} turn={turn} />
              ))}
              {selina.isBusy ? (
                <ThinkingStatus
                  label={t("selina.thinking_status")}
                  ariaLabel={t("selina.thinking_aria")}
                />
              ) : null}
            </>
          )}
        </div>

        {/* Input Grok : cadre arrondi + send cercle */}
        <footer className="shrink-0 px-3 pb-3 pt-1">
          <form
            className={cn(
              "rounded-[1.35rem] border border-border bg-card px-3.5 pb-2.5 pt-3 shadow-sm",
              "focus-within:border-foreground/20"
            )}
            onSubmit={(event) => {
              event.preventDefault();
              void selina.send();
            }}
          >
            <textarea
              ref={inputRef}
              rows={1}
              value={selina.draft}
              onChange={(event) => selina.setDraft(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  void selina.send();
                }
              }}
              placeholder={t("selina.ask_placeholder")}
              className="max-h-32 min-h-[28px] w-full resize-none bg-transparent text-[15px] leading-snug text-foreground placeholder:text-muted-foreground focus-visible:outline-none scrollbar-none"
              aria-label={t("selina.ask_placeholder")}
              disabled={selina.isBusy}
            />
            <div className="mt-2 flex items-center justify-end">
              <button
                type="submit"
                disabled={!canSend && !selina.isBusy}
                className={cn(
                  "inline-flex size-9 items-center justify-center rounded-full transition-colors",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                  selina.isBusy || canSend
                    ? "bg-foreground text-background hover:bg-foreground/90"
                    : "bg-muted text-muted-foreground"
                )}
                aria-label={
                  selina.isBusy ? t("selina.thinking_aria") : t("selina.send")
                }
              >
                {selina.isBusy ? (
                  <Loader2 className="size-4 animate-spin" aria-hidden />
                ) : (
                  <ArrowUp className="size-4" strokeWidth={2.25} aria-hidden />
                )}
              </button>
            </div>
          </form>
          <p className="mt-2 px-1 text-center text-[10px] text-muted-foreground/80">
            {t("selina.disclaimer")}
          </p>
        </footer>
      </div>
    </aside>
  );
}
