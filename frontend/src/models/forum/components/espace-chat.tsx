import { useEffect, useMemo, useRef, useState } from "react";
import {
  Loader2,
  MessageCircle,
  Reply,
  SendHorizontal,
  SmilePlus,
  Trash2,
  X,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import { useAuthSlice } from "@/models/auth/slice";
import {
  type EspaceMessage,
  useDeleteEspaceMessageMutation,
  useGetEspaceMessagesQuery,
  useReactEspaceMessageMutation,
  useSendEspaceMessageMutation,
} from "../api";
import { encodeVocalMessage, richMessagePreview } from "../lib/rich-message";
import { ChatAttachMenu } from "./chat-attach-menu";
import { ChatMessageBody } from "./chat-message-body";
import { ForumAvatar } from "./forum-avatar";
import { VoiceRecorderButton } from "./voice-recorder-button";

const REACTION_EMOJIS = ["👍", "❤️", "😂", "😮", "😢", "🙏"] as const;

type EspaceChatProps = {
  espaceId: number;
  canWrite: boolean;
  canReact?: boolean;
  canModerate?: boolean;
  readOnlyHint?: string;
  /** Mode Messages : remplit le parent, sans chrome dupliqué. */
  embedded?: boolean;
};

function formatTime(value: string | null | undefined) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat("fr-FR", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function formatDayLabel(value: string | null | undefined) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);
  const sameDay = (a: Date, b: Date) =>
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate();
  if (sameDay(date, today)) return "Aujourd'hui";
  if (sameDay(date, yesterday)) return "Hier";
  return new Intl.DateTimeFormat("fr-FR", {
    weekday: "long",
    day: "numeric",
    month: "long",
  }).format(date);
}

function dayKey(value: string | null | undefined) {
  if (!value) return "unknown";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "unknown";
  return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
}

function authorLabel(message: Pick<EspaceMessage, "auteur"> | null | undefined) {
  return (
    message?.auteur?.full_name ||
    message?.auteur?.username ||
    "Membre"
  );
}

function truncate(text: string, max = 90) {
  const cleaned = text.trim();
  if (cleaned.length <= max) return cleaned;
  return `${cleaned.slice(0, max).trimEnd()}…`;
}

export function EspaceChat({
  espaceId,
  canWrite,
  canReact,
  canModerate = false,
  readOnlyHint,
  embedded = false,
}: EspaceChatProps) {
  const allowReact = canReact ?? canWrite;
  const currentUserId = useAuthSlice((state) => state.user?.id ?? null);
  const listRef = useRef<HTMLDivElement | null>(null);
  const composerRef = useRef<HTMLTextAreaElement | null>(null);
  const [texte, setTexte] = useState("");
  const [replyTo, setReplyTo] = useState<EspaceMessage | null>(null);
  const [highlightId, setHighlightId] = useState<number | null>(null);
  const { data, isLoading, isError, refetch } = useGetEspaceMessagesQuery(
    {
      espaceId,
      page_size: 100,
    },
    { pollingInterval: 4000 }
  );
  const [sendMessage, { isLoading: sending }] = useSendEspaceMessageMutation();
  const [deleteMessage] = useDeleteEspaceMessageMutation();
  const [reactMessage] = useReactEspaceMessageMutation();

  const messages = data?.results ?? [];

  const threaded = useMemo(() => {
    const rows: Array<
      | { kind: "day"; key: string; label: string }
      | {
          kind: "message";
          message: EspaceMessage;
          showAvatar: boolean;
          showName: boolean;
        }
    > = [];
    let lastDay = "";
    let lastAuthor: number | null | undefined = undefined;

    for (const message of messages) {
      const key = dayKey(message.sent_at);
      if (key !== lastDay) {
        rows.push({
          kind: "day",
          key,
          label: formatDayLabel(message.sent_at),
        });
        lastDay = key;
        lastAuthor = undefined;
      }
      const authorId = message.auteur?.id ?? null;
      const sameAuthor = authorId != null && authorId === lastAuthor;
      rows.push({
        kind: "message",
        message,
        showAvatar: !sameAuthor,
        showName: !sameAuthor,
      });
      lastAuthor = authorId;
    }
    return rows;
  }, [messages]);

  useEffect(() => {
    const list = listRef.current;
    if (!list) return;
    list.scrollTop = list.scrollHeight;
  }, [messages.length]);

  useEffect(() => {
    if (highlightId == null) return;
    const timer = window.setTimeout(() => setHighlightId(null), 1600);
    return () => window.clearTimeout(timer);
  }, [highlightId]);

  const scrollToMessage = (messageId: number) => {
    const list = listRef.current;
    const node = document.getElementById(`espace-msg-${messageId}`);
    if (!list || !node) return;
    const listRect = list.getBoundingClientRect();
    const nodeRect = node.getBoundingClientRect();
    const nextTop =
      list.scrollTop +
      (nodeRect.top - listRect.top) -
      list.clientHeight / 2 +
      nodeRect.height / 2;
    list.scrollTo({ top: Math.max(0, nextTop), behavior: "smooth" });
    setHighlightId(messageId);
  };

  const handleReply = (message: EspaceMessage) => {
    if (message.supprime) return;
    setReplyTo(message);
    composerRef.current?.focus();
  };

  const handleSend = async () => {
    const trimmed = texte.trim();
    if (!trimmed || sending) return;
    try {
      await sendMessage({
        espaceId,
        texte: trimmed,
        reply_to_id: replyTo?.id ?? null,
      }).unwrap();
      setTexte("");
      setReplyTo(null);
      void refetch();
    } catch {
      toast.error("Impossible d'envoyer le message");
    }
  };

  const handleDelete = async (message: EspaceMessage) => {
    try {
      await deleteMessage({
        espaceId,
        messageId: message.id,
      }).unwrap();
      if (replyTo?.id === message.id) setReplyTo(null);
      void refetch();
    } catch {
      toast.error("Impossible de supprimer le message");
    }
  };

  const handleReact = async (message: EspaceMessage, emoji: string) => {
    try {
      await reactMessage({
        espaceId,
        messageId: message.id,
        emoji,
      }).unwrap();
      void refetch();
    } catch {
      toast.error("Impossible d'ajouter la réaction");
    }
  };

  if (isLoading) {
    return (
      <div
        className={cn(
          "flex items-center justify-center bg-card",
          embedded
            ? "h-full min-h-0"
            : "min-h-[420px] rounded-2xl border border-border"
        )}
      >
        <p className="text-sm text-muted-foreground">
          Chargement de la discussion…
        </p>
      </div>
    );
  }

  if (isError) {
    return (
      <div
        className={cn(
          "flex flex-col items-center justify-center gap-3 bg-card",
          embedded
            ? "h-full min-h-0"
            : "min-h-[420px] rounded-2xl border border-border"
        )}
      >
        <p className="text-sm text-destructive">
          Impossible de charger la discussion.
        </p>
        <Button type="button" variant="outline" onClick={() => refetch()}>
          Réessayer
        </Button>
      </div>
    );
  }

  return (
    <section
      className={cn(
        "flex min-h-0 flex-col overflow-hidden bg-card",
        embedded
          ? "h-full"
          : "min-h-[480px] rounded-2xl border border-border shadow-sm"
      )}
    >
      {!embedded ? (
        <header className="flex shrink-0 items-center gap-3 border-b border-border px-4 py-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-soft text-brand-strong">
            <MessageCircle className="h-4 w-4" aria-hidden />
          </div>
          <div className="min-w-0 flex-1">
            <h2 className="text-sm font-semibold text-foreground">Discussion</h2>
            <p className="text-xs text-muted-foreground">
              {messages.length === 0
                ? "Le fil est encore vide"
                : `${messages.length} message${messages.length > 1 ? "s" : ""}`}
            </p>
          </div>
        </header>
      ) : null}

      <div
        ref={listRef}
        className={cn(
          "relative min-h-0 flex-1 space-y-1 overflow-y-auto overscroll-contain px-3 py-4 sm:px-4",
          "bg-[radial-gradient(circle_at_1px_1px,hsl(var(--border))_1px,transparent_0)] bg-[length:18px_18px]",
          "bg-muted/30"
        )}
      >
        {messages.length === 0 ? (
          <div className="mx-auto flex max-w-sm flex-col items-center gap-2 py-16 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-card text-brand shadow-sm">
              <MessageCircle className="h-5 w-5" aria-hidden />
            </div>
            <p className="text-sm font-medium text-foreground">
              Lance la conversation
            </p>
            <p className="text-xs text-muted-foreground">
              Premier message, réponses et réactions — comme un groupe, ici.
            </p>
          </div>
        ) : (
          threaded.map((row) => {
            if (row.kind === "day") {
              return (
                <div
                  key={`day-${row.key}`}
                  className="flex justify-center py-3"
                >
                  <span className="rounded-full border border-border/80 bg-card/90 px-3 py-1 text-[11px] font-medium capitalize text-muted-foreground shadow-sm backdrop-blur-sm">
                    {row.label}
                  </span>
                </div>
              );
            }

            const { message, showAvatar, showName } = row;
            const mine = message.auteur?.id === currentUserId;
            const name = authorLabel(message);
            const reactions = message.reactions ?? {
              counts: [],
              ma_reaction: null,
            };

            return (
              <div
                key={message.id}
                id={`espace-msg-${message.id}`}
                className={cn(
                  "group flex gap-2 scroll-mt-6 px-1 py-0.5 transition-colors",
                  mine ? "flex-row-reverse" : "flex-row",
                  !showAvatar && (mine ? "pr-10" : "pl-10"),
                  highlightId === message.id &&
                    "rounded-xl bg-brand-soft/50 ring-1 ring-brand-soft-border"
                )}
              >
                {!mine ? (
                  showAvatar ? (
                    <ForumAvatar
                      name={name}
                      photo={message.auteur?.photo}
                      size="sm"
                      tone="soft"
                      className="mt-1"
                    />
                  ) : (
                    <span className="w-8 shrink-0" aria-hidden />
                  )
                ) : null}

                <div
                  className={cn(
                    "relative max-w-[min(85%,28rem)] px-3.5 py-2 text-sm shadow-sm",
                    mine
                      ? "rounded-2xl rounded-br-md bg-brand text-brand-foreground"
                      : "rounded-2xl rounded-bl-md border border-border/70 bg-card text-foreground",
                    message.supprime && "opacity-70"
                  )}
                >
                  {!mine && showName ? (
                    <p className="mb-1 text-[11px] font-semibold text-brand-strong">
                      {name}
                    </p>
                  ) : null}

                  {message.reply_to ? (
                    <button
                      type="button"
                      onClick={() => scrollToMessage(message.reply_to!.id)}
                      className={cn(
                        "mb-2 w-full overflow-hidden rounded-lg border-l-[3px] px-2.5 py-1.5 text-left text-xs transition-opacity hover:opacity-90",
                        mine
                          ? "border-brand-foreground/70 bg-black/15"
                          : "border-brand bg-muted/80"
                      )}
                    >
                      <span className="block font-semibold">
                        {authorLabel(message.reply_to)}
                      </span>
                      <span className="line-clamp-2 opacity-80">
                        {message.reply_to.supprime
                          ? "Message supprimé"
                          : richMessagePreview(message.reply_to.texte || "…")}
                      </span>
                    </button>
                  ) : null}

                  {message.supprime ? (
                    <p className="italic opacity-80">Message supprimé</p>
                  ) : (
                    <ChatMessageBody texte={message.texte} mine={mine} />
                  )}

                  {reactions.counts.length > 0 ? (
                    <div
                      className={cn(
                        "mt-2 flex flex-wrap gap-1",
                        mine ? "justify-end" : "justify-start"
                      )}
                    >
                      {reactions.counts.map((item) => (
                        <button
                          key={item.emoji}
                          type="button"
                          disabled={!allowReact || message.supprime}
                          onClick={() => void handleReact(message, item.emoji)}
                          className={cn(
                            "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium transition-transform hover:scale-105",
                            reactions.ma_reaction === item.emoji
                              ? mine
                                ? "bg-black/20 ring-1 ring-brand-foreground/40"
                                : "bg-brand-soft text-brand-strong ring-1 ring-brand-soft-border"
                              : mine
                                ? "bg-black/10"
                                : "border border-border bg-muted/70"
                          )}
                        >
                          <span>{item.emoji}</span>
                          <span>{item.count}</span>
                        </button>
                      ))}
                    </div>
                  ) : null}

                  <div
                    className={cn(
                      "mt-1 flex items-center gap-2 text-[10px]",
                      mine
                        ? "justify-end text-brand-foreground/75"
                        : "justify-end text-muted-foreground"
                    )}
                  >
                    <span>{formatTime(message.sent_at)}</span>
                  </div>

                  {(canWrite || allowReact || mine || canModerate) &&
                  !message.supprime ? (
                    <div
                      className={cn(
                        "absolute -top-3 z-10 flex items-center gap-0.5 rounded-full border border-border bg-card p-0.5 opacity-100 shadow-md sm:opacity-0 sm:transition-opacity sm:group-hover:opacity-100 sm:group-focus-within:opacity-100",
                        mine ? "-left-1" : "-right-1"
                      )}
                    >
                      {canWrite ? (
                        <Button
                          type="button"
                          size="icon"
                          variant="ghost"
                          className="h-7 w-7"
                          aria-label="Répondre"
                          onClick={() => handleReply(message)}
                        >
                          <Reply className="h-3.5 w-3.5" />
                        </Button>
                      ) : null}
                      {allowReact ? (
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button
                              type="button"
                              size="icon"
                              variant="ghost"
                              className="h-7 w-7"
                              aria-label="Réagir"
                            >
                              <SmilePlus className="h-3.5 w-3.5" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align={mine ? "start" : "end"}>
                            <div className="flex gap-1 p-1">
                              {REACTION_EMOJIS.map((emoji) => (
                                <button
                                  key={emoji}
                                  type="button"
                                  className="rounded-md px-1.5 py-1 text-base transition-transform hover:scale-110 hover:bg-muted"
                                  onClick={() =>
                                    void handleReact(message, emoji)
                                  }
                                >
                                  {emoji}
                                </button>
                              ))}
                            </div>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      ) : null}
                      {mine || canModerate ? (
                        <Button
                          type="button"
                          size="icon"
                          variant="ghost"
                          className="h-7 w-7 text-destructive"
                          aria-label="Supprimer"
                          onClick={() => void handleDelete(message)}
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      ) : null}
                    </div>
                  ) : null}
                </div>
              </div>
            );
          })
        )}
      </div>

      {canWrite ? (
        <div className="shrink-0 border-t border-border bg-card p-3">
          {replyTo ? (
            <div className="mb-2 flex items-start gap-2 rounded-xl border border-brand-soft-border bg-brand-soft/40 px-3 py-2">
              <div className="mt-0.5 h-8 w-1 shrink-0 rounded-full bg-brand" />
              <div className="min-w-0 flex-1">
                <p className="text-xs font-semibold text-brand-strong">
                  Réponse à {authorLabel(replyTo)}
                </p>
                <p className="truncate text-xs text-muted-foreground">
                  {replyTo.supprime
                    ? "Message supprimé"
                    : truncate(richMessagePreview(replyTo.texte))}
                </p>
              </div>
              <Button
                type="button"
                size="icon"
                variant="ghost"
                className="h-7 w-7 shrink-0"
                aria-label="Annuler la réponse"
                onClick={() => setReplyTo(null)}
              >
                <X className="h-3.5 w-3.5" />
              </Button>
            </div>
          ) : null}
          <div className="flex flex-col gap-2">
            <div className="flex items-end gap-2 rounded-2xl border border-border bg-muted/40 p-1.5 pl-2.5 focus-within:border-brand-soft-border focus-within:ring-2 focus-within:ring-brand/15">
              <Textarea
                ref={composerRef}
                value={texte}
                onChange={(event) => setTexte(event.target.value)}
                placeholder={
                  replyTo ? "Écrire une réponse…" : "Écrire un message…"
                }
                className="min-h-[40px] max-h-32 flex-1 resize-none border-0 bg-transparent px-1 py-2 shadow-none focus-visible:ring-0"
                rows={1}
                onKeyDown={(event) => {
                  if (
                    event.key === "Enter" &&
                    !event.shiftKey &&
                    !sending &&
                    texte.trim()
                  ) {
                    event.preventDefault();
                    void handleSend();
                  }
                }}
              />
              <ChatAttachMenu
                disabled={sending}
                onSendEncoded={async (encoded) => {
                  try {
                    await sendMessage({
                      espaceId,
                      texte: encoded,
                      reply_to_id: replyTo?.id ?? null,
                    }).unwrap();
                    setReplyTo(null);
                    void refetch();
                  } catch {
                    toast.error("Impossible d'envoyer la pièce jointe");
                    throw new Error("send attachment failed");
                  }
                }}
              />
              <VoiceRecorderButton
                compact
                disabled={sending}
                confirmLabel="Envoyer"
                onRecorded={async ({ url }) => {
                  try {
                    await sendMessage({
                      espaceId,
                      texte: encodeVocalMessage(url),
                      reply_to_id: replyTo?.id ?? null,
                    }).unwrap();
                    setReplyTo(null);
                    void refetch();
                  } catch {
                    toast.error("Impossible d'envoyer le vocal");
                    throw new Error("send vocal failed");
                  }
                }}
              />
              <Button
                type="button"
                size="icon"
                className="h-10 w-10 shrink-0 rounded-xl bg-brand text-brand-foreground hover:bg-brand/90"
                disabled={sending || !texte.trim()}
                aria-label="Envoyer"
                onClick={() => void handleSend()}
              >
                {sending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <SendHorizontal className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
        </div>
      ) : (
        <p className="shrink-0 border-t border-border px-4 py-3 text-sm text-muted-foreground">
          {readOnlyHint ??
            "Rejoignez la communauté pour participer à la discussion."}
        </p>
      )}
    </section>
  );
}
