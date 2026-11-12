import { useEffect, useMemo, useRef, useState } from "react";
import { Bot, RotateCcw, Send, Sparkles, X } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { SafeMarkdown } from "@/models/devstreet-hub/functions/safe-markdown";
import { useHubAssistant } from "../hooks/use-hub-assistant";
import type { ChatTurn } from "../schema";

interface HubAssistantPanelProps {
  projectId: number;
  projectTitle: string;
  taskId?: number;
  taskTitle?: string;
}

const THINKING_PHASE_MS = 1400;

function UserAvatar({ label }: { label: string }) {
  return (
    <span
      className="inline-flex size-8 shrink-0 items-center justify-center rounded-full border border-border bg-secondary text-[10px] font-semibold text-foreground"
      aria-hidden
    >
      {label.slice(0, 3)}
    </span>
  );
}

function RobotAvatar({ writing = false }: { writing?: boolean }) {
  return (
    <span
      className={cn(
        "relative inline-flex size-8 shrink-0 items-center justify-center rounded-full border border-brand-soft-border bg-brand-soft text-brand",
        writing && "animate-assistant-bot"
      )}
      aria-hidden
    >
      <Bot className="size-4" />
      {writing ? (
        <span className="absolute -bottom-0.5 -right-0.5 size-2.5 rounded-full border-2 border-card bg-success" />
      ) : null}
    </span>
  );
}

function ThinkingSpectacle({
  phases,
  ariaLabel,
}: {
  phases: string[];
  ariaLabel: string;
}) {
  const [phaseIndex, setPhaseIndex] = useState(0);

  useEffect(() => {
    if (phases.length <= 1) return;
    const timer = window.setInterval(() => {
      setPhaseIndex((current) => (current + 1) % phases.length);
    }, THINKING_PHASE_MS);
    return () => window.clearInterval(timer);
  }, [phases.length]);

  const phaseLabel = phases[phaseIndex] ?? phases[0] ?? "";

  return (
    <div
      className="animate-assistant-msg-in flex items-start gap-2.5"
      role="status"
      aria-live="polite"
      aria-label={ariaLabel}
    >
      <div className="relative mt-0.5 size-10 shrink-0">
        <span
          className="absolute inset-0 rounded-full bg-brand/15 animate-assistant-pulse-ring"
          aria-hidden
        />
        <span
          className="absolute inset-[-3px] rounded-full border border-dashed border-brand/35 animate-assistant-orbit"
          aria-hidden
        />
        <span
          className="absolute inset-[-7px] rounded-full border border-dotted border-brand/20 animate-assistant-orbit-rev"
          aria-hidden
        />
        <span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
          <RobotAvatar writing />
        </span>
        <Sparkles
          aria-hidden
          className="absolute -right-1 -top-1 size-3 text-brand animate-assistant-spark"
        />
        <span
          className="absolute -left-0.5 top-0 size-1.5 rounded-full bg-brand animate-assistant-spark-2"
          aria-hidden
        />
        <span
          className="absolute bottom-0 -right-0.5 size-1 rounded-full bg-brand/70 animate-assistant-spark-3"
          aria-hidden
        />
      </div>

      <div className="min-w-0 flex-1 rounded-md rounded-tl-sm border border-brand-soft-border bg-card px-3 py-2.5 shadow-sm">
        <div className="mb-2 flex items-center gap-2">
          <div className="flex items-center gap-1.5">
            <span className="size-1.5 rounded-full bg-brand animate-assistant-dot" />
            <span className="size-1.5 rounded-full bg-brand animate-assistant-dot-2" />
            <span className="size-1.5 rounded-full bg-brand animate-assistant-dot-3" />
          </div>
          <p
            key={phaseLabel}
            className="animate-assistant-phase-in text-[11px] font-medium text-foreground"
          >
            {phaseLabel}
          </p>
        </div>

        <div className="relative mb-2.5 h-1 overflow-hidden rounded-full bg-secondary">
          <span
            className="absolute inset-y-0 w-1/2 rounded-full bg-brand/55 animate-assistant-shimmer"
            aria-hidden
          />
        </div>

        <div className="space-y-1.5" aria-hidden>
          <div className="h-1.5 rounded-full bg-muted animate-assistant-draft-1" />
          <div className="h-1.5 rounded-full bg-muted animate-assistant-draft-2" />
          <div className="h-1.5 max-w-[70%] rounded-full bg-muted animate-assistant-draft-3" />
        </div>
      </div>
    </div>
  );
}

function MessageRow({ turn, youLabel, assistantLabel, failoverLabel }: {
  turn: ChatTurn;
  youLabel: string;
  assistantLabel: string;
  failoverLabel: string;
}) {
  const isUser = turn.role === "user";
  return (
    <div
      className={cn(
        "animate-assistant-msg-in flex items-start gap-2.5",
        isUser && "flex-row-reverse"
      )}
    >
      {isUser ? <UserAvatar label={youLabel} /> : <RobotAvatar />}
      <div
        className={cn(
          "max-w-[85%] rounded-md border border-border px-3 py-2 text-sm shadow-sm",
          isUser
            ? "rounded-tr-sm bg-secondary/70 text-foreground"
            : "rounded-tl-sm bg-card text-foreground"
        )}
      >
        <p className="mb-1 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
          {isUser ? youLabel : assistantLabel}
          {!isUser && turn.provider ? ` · ${turn.provider}` : ""}
          {!isUser && turn.failoverReason ? ` (${failoverLabel})` : ""}
        </p>
        {isUser ? (
          <p className="whitespace-pre-wrap leading-relaxed">{turn.content}</p>
        ) : (
          <div className="leading-relaxed">
            <SafeMarkdown content={turn.content} />
          </div>
        )}
      </div>
    </div>
  );
}

export function HubAssistantPanel({
  projectId,
  projectTitle,
  taskId,
  taskTitle,
}: HubAssistantPanelProps) {
  const { t } = useTranslation();
  const assistant = useHubAssistant({
    projectId,
    projectTitle,
    taskId,
    taskTitle,
  });
  const scrollerRef = useRef<HTMLDivElement>(null);
  const thinkingPhases = useMemo(
    () => [
      t("ai.hub.thinking"),
      t("ai.hub.analyzing"),
      t("ai.hub.writing"),
    ],
    [t]
  );

  useEffect(() => {
    const node = scrollerRef.current;
    if (!node) return;
    node.scrollTo({ top: node.scrollHeight, behavior: "smooth" });
  }, [assistant.turns, assistant.isBusy, assistant.open]);

  if (assistant.isAuthenticated && !assistant.canChat) {
    return null;
  }

  return (
    <>
      {!assistant.open ? (
        <button
          type="button"
          onClick={() => {
            if (!assistant.isAuthenticated) {
              assistant.requestLogin();
              return;
            }
            if (!assistant.canChat) return;
            assistant.setOpen(true);
          }}
          className={cn(
            "animate-assistant-launcher fixed bottom-5 right-5 z-40 inline-flex h-11 items-center gap-2 rounded-md border border-border bg-card px-3.5 text-xs font-semibold text-foreground",
            "transition hover:bg-secondary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          )}
          aria-label={t("ai.hub.open")}
        >
          <span className="relative inline-flex size-7 items-center justify-center rounded-full border border-brand-soft-border bg-brand-soft text-brand">
            <Bot aria-hidden className="size-3.5 animate-assistant-bot" />
          </span>
          {t("ai.hub.open")}
        </button>
      ) : null}

      {assistant.open ? (
        <aside
          className="animate-assistant-panel-in fixed bottom-5 right-5 z-40 flex h-[min(600px,calc(100vh-4.5rem))] w-[min(400px,calc(100vw-1.5rem))] flex-col overflow-hidden rounded-md border border-border bg-card shadow-card"
          aria-label={t("ai.hub.title")}
        >
          <header className="flex items-center justify-between gap-2 border-b border-border bg-secondary/40 px-3 py-2.5">
            <div className="flex min-w-0 items-center gap-2.5">
              <RobotAvatar writing={assistant.isBusy} />
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-foreground">
                  {t("ai.hub.title")}
                </p>
                <p className="truncate text-[11px] text-muted-foreground">
                  {assistant.isBusy
                    ? t("ai.hub.thinking")
                    : assistant.contextLabel}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="h-7 w-7"
                aria-label={t("ai.hub.reset")}
                onClick={assistant.reset}
              >
                <RotateCcw aria-hidden className="size-3.5" />
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="h-7 w-7"
                aria-label={t("cancel")}
                onClick={() => assistant.setOpen(false)}
              >
                <X aria-hidden className="size-3.5" />
              </Button>
            </div>
          </header>

          <div className="flex flex-wrap gap-1.5 border-b border-border px-3 py-2">
            {assistant.hasTaskContext ? (
              <button
                type="button"
                className={cn(
                  "rounded-md border px-2 py-0.5 text-[11px] transition",
                  assistant.includeTask
                    ? "border-border bg-secondary text-foreground"
                    : "border-dashed border-border text-muted-foreground"
                )}
                onClick={() => assistant.setIncludeTask((value) => !value)}
              >
                {t("ai.hub.context.task")}
                {assistant.includeTask ? (
                  <span className="ml-1 opacity-60">×</span>
                ) : null}
              </button>
            ) : null}
            <button
              type="button"
              className={cn(
                "rounded-md border px-2 py-0.5 text-[11px] transition",
                assistant.includeRepo
                  ? "border-border bg-secondary text-foreground"
                  : "border-dashed border-border text-muted-foreground"
              )}
              onClick={() => assistant.setIncludeRepo((value) => !value)}
            >
              {t("ai.hub.context.repo")}
              {assistant.includeRepo ? (
                <span className="ml-1 opacity-60">×</span>
              ) : null}
            </button>
          </div>

          <div
            ref={scrollerRef}
            className="flex-1 space-y-3.5 overflow-y-auto bg-gradient-to-b from-secondary/20 to-card px-3 py-3"
          >
            {assistant.turns.length === 0 ? (
              <div className="flex h-full flex-col items-center justify-center gap-4 text-center">
                <div className="relative">
                  <span className="absolute inset-0 rounded-full bg-brand/10 blur-md" />
                  <RobotAvatar writing />
                </div>
                <p className="max-w-[240px] text-xs leading-relaxed text-muted-foreground">
                  {t("ai.hub.empty")}
                </p>
                <div className="flex flex-wrap justify-center gap-1.5">
                  {assistant.suggestions.map((suggestion) => (
                    <button
                      key={suggestion}
                      type="button"
                      className="rounded-md border border-border bg-card px-2.5 py-1 text-[11px] text-foreground shadow-sm transition hover:border-brand-soft-border hover:bg-brand-soft/40"
                      onClick={() => void assistant.send(suggestion)}
                      disabled={assistant.isBusy}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
                <p className="text-[10px] text-muted-foreground">
                  {t("ai.hub.disclaimer")}
                </p>
              </div>
            ) : (
              <>
                {assistant.turns.map((turn) => (
                  <MessageRow
                    key={turn.id}
                    turn={turn}
                    youLabel={t("ai.hub.you")}
                    assistantLabel={t("ai.hub.assistant")}
                    failoverLabel={t("ai.hub.failover")}
                  />
                ))}
                {assistant.isBusy ? (
                  <ThinkingSpectacle
                    phases={thinkingPhases}
                    ariaLabel={t("ai.hub.thinking_aria")}
                  />
                ) : null}
              </>
            )}
          </div>

          <form
            className="border-t border-border bg-card p-3"
            onSubmit={(event) => {
              event.preventDefault();
              void assistant.send();
            }}
          >
            <div className="overflow-hidden rounded-md border border-border focus-within:ring-2 focus-within:ring-ring">
              <Textarea
                value={assistant.draft}
                onChange={(event) => assistant.setDraft(event.target.value)}
                placeholder={t("ai.hub.placeholder")}
                className="min-h-[76px] resize-none border-0 bg-background text-sm shadow-none focus-visible:ring-0"
                disabled={assistant.isBusy || !assistant.canChat}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    void assistant.send();
                  }
                }}
              />
              <div className="flex items-center justify-between gap-2 border-t border-border bg-secondary/30 px-2 py-1.5">
                <p className="truncate text-[10px] text-muted-foreground">
                  {assistant.canChat
                    ? t("ai.hub.hint")
                    : t("ai.hub.errors.forbidden")}
                </p>
                <Button
                  type="submit"
                  disabled={
                    assistant.isBusy ||
                    !assistant.canChat ||
                    !assistant.draft.trim()
                  }
                  className="h-7 gap-1.5 rounded-md px-2.5 text-xs"
                >
                  <Send aria-hidden className="size-3.5" />
                  {t("ai.hub.send")}
                </Button>
              </div>
            </div>
          </form>
        </aside>
      ) : null}
    </>
  );
}
