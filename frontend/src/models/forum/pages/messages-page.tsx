import { useEffect, useRef, useState } from "react";
import { useDispatch } from "react-redux";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { Loader2, SendHorizontal } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { useAuthSlice } from "@/models/auth/slice";
import {
  forumApi,
  useGetConversationQuery,
  useGetConversationsQuery,
  useGetMessagesQuery,
  useOpenConversationMutation,
  useSendMessageMutation,
  type Conversation,
  type ConversationMember,
} from "../api";
import { ForumAvatar } from "../components/forum-avatar";
import { ForumRichText } from "../components/forum-rich-text";
import {
  connectMessagingSocket,
  joinConversationRoom,
  leaveConversationRoom,
  subscribeToNewMessages,
} from "../lib/messaging-socket";
import { looksLikeCodeBlock } from "../lib/parse-mixed-content";

function memberLabel(member: ConversationMember | null | undefined) {
  if (!member) return "Membre";
  return member.full_name || member.username || "Membre";
}

function peerOf(conversation: Conversation, currentUserId: number | null) {
  if (conversation.autre_membre) return conversation.autre_membre;
  if (currentUserId == null) return conversation.membre_1 || conversation.membre_2;
  if (conversation.membre_1?.id === currentUserId) return conversation.membre_2;
  if (conversation.membre_2?.id === currentUserId) return conversation.membre_1;
  return conversation.membre_1 || conversation.membre_2;
}

function formatTime(value: string | null | undefined) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat("fr-FR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(date);
}

export default function MessagesPage() {
  const navigate = useNavigate();
  const params = useParams();
  const [searchParams] = useSearchParams();
  const currentUserId = useAuthSlice((state) => state.user?.id ?? null);

  const conversationId = Number(params.conversationId);
  const hasConversation =
    Number.isFinite(conversationId) && conversationId > 0;
  const withUserId = Number(searchParams.get("with"));

  const [openConversation, { isLoading: opening }] =
    useOpenConversationMutation();
  const {
    data: conversationsData,
    isLoading: loadingList,
    isError: listError,
    refetch: refetchList,
  } = useGetConversationsQuery();

  const conversations = conversationsData?.results ?? [];

  useEffect(() => {
    if (!Number.isFinite(withUserId) || withUserId <= 0) return;
    if (currentUserId != null && withUserId === currentUserId) {
      navigate("/messages", { replace: true });
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        const conversation = await openConversation(withUserId).unwrap();
        if (!cancelled) {
          navigate(`/messages/${conversation.id}`, { replace: true });
        }
      } catch {
        if (!cancelled) {
          toast.error("Impossible d'ouvrir la conversation");
          navigate("/messages", { replace: true });
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [withUserId, currentUserId, openConversation, navigate]);

  useEffect(() => {
    connectMessagingSocket();
  }, []);

  return (
    <div className="mx-auto flex h-[calc(100vh-7rem)] w-full max-w-5xl flex-col gap-4">
      <header>
        <h1 className="text-2xl font-bold tracking-tight text-foreground">
          Messages
        </h1>
        <p className="text-sm text-muted-foreground">
          Conversations privées entre membres · temps réel
        </p>
      </header>

      <div className="grid min-h-0 flex-1 overflow-hidden rounded-2xl border border-border bg-card shadow-sm lg:grid-cols-[280px_minmax(0,1fr)]">
        <aside className="flex min-h-0 flex-col border-b border-border lg:border-b-0 lg:border-r">
          <div className="border-b border-border px-4 py-3 text-sm font-medium">
            Conversations
          </div>
          <div className="min-h-0 flex-1 overflow-y-auto p-2">
            {loadingList || opening ? (
              <p className="px-2 py-6 text-center text-sm text-muted-foreground">
                Chargement…
              </p>
            ) : null}
            {listError ? (
              <div className="space-y-2 px-2 py-4 text-center">
                <p className="text-sm text-destructive">
                  Impossible de charger les conversations.
                </p>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={() => void refetchList()}
                >
                  Réessayer
                </Button>
              </div>
            ) : null}
            {!loadingList && !listError && conversations.length === 0 ? (
              <p className="px-2 py-6 text-center text-sm text-muted-foreground">
                Aucune conversation. Écris à quelqu&apos;un depuis son profil.
              </p>
            ) : null}
            {conversations.map((conversation) => {
              const peer = peerOf(conversation, currentUserId);
              const active = hasConversation && conversation.id === conversationId;
              const preview =
                conversation.dernier_message?.texte?.trim() ||
                "Nouvelle conversation";
              return (
                <button
                  key={conversation.id}
                  type="button"
                  onClick={() => navigate(`/messages/${conversation.id}`)}
                  className={cn(
                    "flex w-full items-start gap-3 rounded-xl px-3 py-2.5 text-left transition-colors",
                    active ? "bg-brand-soft" : "hover:bg-muted"
                  )}
                >
                  <ForumAvatar
                    name={memberLabel(peer)}
                    photo={peer?.photo}
                    size="sm"
                    tone="soft"
                  />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-semibold text-foreground">
                      {memberLabel(peer)}
                    </p>
                    <p className="truncate text-xs text-muted-foreground">
                      {preview}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        </aside>

        <section className="flex min-h-0 min-w-0 flex-col">
          {hasConversation ? (
            <ConversationThread
              conversationId={conversationId}
              currentUserId={currentUserId}
            />
          ) : (
            <div className="flex flex-1 items-center justify-center px-6 text-center text-sm text-muted-foreground">
              Sélectionne une conversation ou contacte un membre depuis son
              profil.
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

function ConversationThread({
  conversationId,
  currentUserId,
}: {
  conversationId: number;
  currentUserId: number | null;
}) {
  const dispatch = useDispatch();
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const [draft, setDraft] = useState("");
  const {
    data: conversation,
    isLoading: loadingConversation,
    isError: conversationError,
  } = useGetConversationQuery(conversationId);
  const {
    data: messagesData,
    isLoading: loadingMessages,
    isError: messagesError,
    refetch: refetchMessages,
  } = useGetMessagesQuery(conversationId);
  const [sendMessage, { isLoading: sending }] = useSendMessageMutation();

  const peer = conversation
    ? peerOf(conversation, currentUserId)
    : null;
  const messages = messagesData?.results ?? [];

  useEffect(() => {
    connectMessagingSocket();
    joinConversationRoom(conversationId);
    const unsubscribe = subscribeToNewMessages((message) => {
      if (message.conversation !== conversationId) return;
      dispatch(
        forumApi.util.updateQueryData(
          "getMessages",
          conversationId,
          (draftCache) => {
            if (draftCache.results.some((item) => item.id === message.id)) {
              return;
            }
            draftCache.results.push(message);
          }
        )
      );
      dispatch(
        forumApi.util.invalidateTags([{ type: "Conversations", id: "LIST" }])
      );
    });
    return () => {
      leaveConversationRoom(conversationId);
      unsubscribe();
    };
  }, [conversationId, dispatch]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length, conversationId]);

  const handleSend = async () => {
    const texte = draft.trim();
    if (!texte || sending) return;
    try {
      await sendMessage({ conversationId, texte }).unwrap();
      setDraft("");
    } catch {
      toast.error("Impossible d'envoyer le message");
    }
  };

  if (loadingConversation || loadingMessages) {
    return (
      <div className="flex flex-1 items-center justify-center text-sm text-muted-foreground">
        Chargement du fil…
      </div>
    );
  }

  if (conversationError || messagesError || !conversation) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 px-6 text-center">
        <p className="text-sm text-destructive">
          Impossible de charger cette conversation.
        </p>
        <Button
          type="button"
          variant="outline"
          onClick={() => void refetchMessages()}
        >
          Réessayer
        </Button>
      </div>
    );
  }

  return (
    <>
      <div className="flex items-center gap-3 border-b border-border px-4 py-3">
        <Link
          to={peer?.id ? `/forum/profil/${peer.id}` : "/messages"}
          className="flex min-w-0 items-center gap-3"
        >
          <ForumAvatar
            name={memberLabel(peer)}
            photo={peer?.photo}
            size="sm"
            tone="soft"
          />
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-foreground">
              {memberLabel(peer)}
            </p>
            {peer?.username ? (
              <p className="truncate text-xs text-muted-foreground">
                @{peer.username}
              </p>
            ) : null}
          </div>
        </Link>
      </div>

      <div className="min-h-0 flex-1 space-y-3 overflow-y-auto px-4 py-4">
        {messages.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">
            Dis bonjour — envoie le premier message.
          </p>
        ) : null}
        {messages.map((message) => {
          const mine =
            currentUserId != null && message.auteur?.id === currentUserId;
          const hasCode = looksLikeCodeBlock(message.texte);
          return (
            <div
              key={message.id}
              className={cn("flex", mine ? "justify-end" : "justify-start")}
            >
              <div
                className={cn(
                  "max-w-[min(100%,36rem)] rounded-2xl px-3 py-2 text-sm",
                  hasCode
                    ? "w-full border border-border bg-card text-foreground"
                    : mine
                      ? "bg-brand text-brand-foreground"
                      : "bg-muted text-foreground"
                )}
              >
                <ForumRichText
                  text={message.texte}
                  compact
                  className={cn(
                    hasCode
                      ? "text-foreground"
                      : mine
                        ? "text-brand-foreground [&_code]:border-brand-foreground/30 [&_code]:bg-brand-foreground/15 [&_code]:text-brand-foreground"
                        : "text-foreground"
                  )}
                />
                <p
                  className={cn(
                    "mt-1 text-[10px]",
                    hasCode
                      ? "text-muted-foreground"
                      : mine
                        ? "text-brand-foreground/80"
                        : "text-muted-foreground"
                  )}
                >
                  {formatTime(message.sent_at || message.created_at)}
                </p>
              </div>
            </div>
          );
        })}
        <div ref={bottomRef} />
      </div>

      <form
        className="flex items-end gap-2 border-t border-border p-3"
        onSubmit={(event) => {
          event.preventDefault();
          void handleSend();
        }}
      >
        <Textarea
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Écrire un message…"
          rows={2}
          className="min-h-[44px] resize-none"
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              void handleSend();
            }
          }}
        />
        <Button type="submit" disabled={sending || !draft.trim()} size="icon">
          {sending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <SendHorizontal className="h-4 w-4" />
          )}
          <span className="sr-only">Envoyer</span>
        </Button>
      </form>
    </>
  );
}
