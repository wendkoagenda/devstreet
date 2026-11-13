import { useEffect, useMemo, useRef, useState } from "react";
import { useDispatch } from "react-redux";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import {
  ArrowLeft,
  Hash,
  Loader2,
  Radio,
  Search,
  SendHorizontal,
  Users,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { buildMediaUrl } from "@/helpers/displayers/media-url-builder";
import { cn } from "@/lib/utils";
import { useAuthSlice } from "@/models/auth/slice";
import {
  forumApi,
  useGetConversationQuery,
  useGetConversationsQuery,
  useGetEspaceQuery,
  useGetEspacesInfiniteQuery,
  useGetMembresSuivisQuery,
  useGetMessagesQuery,
  useOpenConversationMutation,
  useSendMessageMutation,
  type Conversation,
  type ConversationMember,
} from "../api";
import { EspaceChat } from "../components/espace-chat";
import { ForumAudioPlayer } from "../components/forum-audio-player";
import { ForumAvatar } from "../components/forum-avatar";
import { ForumRichText } from "../components/forum-rich-text";
import { VoiceRecorderButton } from "../components/voice-recorder-button";
import {
  connectMessagingSocket,
  joinConversationRoom,
  leaveConversationRoom,
  subscribeToNewMessages,
} from "../lib/messaging-socket";
import { looksLikeCodeBlock } from "../lib/parse-mixed-content";
import {
  encodeVocalMessage,
  parseVocalUrl,
} from "../lib/vocal-message";
import type { Espace } from "../schema";

function memberLabel(member: ConversationMember | null | undefined) {
  if (!member) return "Membre";
  return member.full_name || member.username || "Membre";
}

function matchesQuery(
  query: string,
  ...parts: Array<string | null | undefined>
) {
  const needle = query.trim().toLowerCase();
  if (!needle) return true;
  return parts.some((part) => (part || "").toLowerCase().includes(needle));
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

function GroupeListItem({
  espace,
  active,
}: {
  espace: Espace;
  active?: boolean;
}) {
  const navigate = useNavigate();
  const isChaine = espace.type === "CHAINE";
  const count = espace.membres_count ?? 0;
  const subtitle = isChaine
    ? `Chaîne · ${count} abonné${count > 1 ? "s" : ""}`
    : `Groupe · ${count} membre${count > 1 ? "s" : ""}`;

  return (
    <button
      type="button"
      onClick={() => navigate(`/messages?groupe=${espace.id}`)}
      className={cn(
        "flex w-full items-start gap-3 rounded-xl px-3 py-2.5 text-left transition-colors",
        active ? "bg-brand-soft" : "hover:bg-muted"
      )}
    >
      <span className="relative flex size-8 shrink-0 items-center justify-center overflow-hidden rounded-full bg-brand-soft text-brand">
        {espace.photo ? (
          <ForumAvatar
            name={espace.nom}
            photo={espace.photo}
            size="sm"
            tone="soft"
          />
        ) : isChaine ? (
          <Radio className="size-3.5" aria-hidden />
        ) : (
          <Users className="size-3.5" aria-hidden />
        )}
      </span>
      <div className="min-w-0 flex-1">
        <p className="flex items-center gap-1.5 truncate text-sm font-semibold text-foreground">
          <Hash className="size-3 shrink-0 text-muted-foreground" aria-hidden />
          <span className="truncate">{espace.nom}</span>
        </p>
        <p className="truncate text-xs text-muted-foreground">{subtitle}</p>
      </div>
    </button>
  );
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
  const groupeId = Number(searchParams.get("groupe"));
  const hasGroupe = Number.isFinite(groupeId) && groupeId > 0;

  const [sidebarQuery, setSidebarQuery] = useState("");
  const [openingSuiviId, setOpeningSuiviId] = useState<number | null>(null);
  const [openConversation, { isLoading: opening }] =
    useOpenConversationMutation();
  const {
    data: conversationsData,
    isLoading: loadingList,
    isError: listError,
    refetch: refetchList,
  } = useGetConversationsQuery();
  const {
    data: suivisData,
    isLoading: loadingSuivis,
    isError: suivisError,
    refetch: refetchSuivis,
  } = useGetMembresSuivisQuery({ limit: 50 });

  const {
    data: communautesData,
    isLoading: loadingCommunautes,
  } = useGetEspacesInfiniteQuery({
    type: "COMMUNAUTE",
    mine: true,
    page_size: 50,
  });
  const {
    data: chainesData,
    isLoading: loadingChaines,
  } = useGetEspacesInfiniteQuery({
    type: "CHAINE",
    mine: true,
    page_size: 50,
  });

  const conversations = conversationsData?.results ?? [];
  const groupes = useMemo(() => {
    const communautes =
      communautesData?.pages.flatMap((page) => page.results) ?? [];
    const chaines = chainesData?.pages.flatMap((page) => page.results) ?? [];
    return [...communautes, ...chaines].sort((a, b) =>
      a.nom.localeCompare(b.nom, "fr")
    );
  }, [communautesData?.pages, chainesData?.pages]);
  const loadingGroups = loadingCommunautes || loadingChaines;

  const filteredGroupes = useMemo(
    () =>
      groupes.filter((espace) =>
        matchesQuery(sidebarQuery, espace.nom, espace.description)
      ),
    [groupes, sidebarQuery]
  );

  const filteredConversations = useMemo(() => {
    return conversations.filter((conversation) => {
      const peer = peerOf(conversation, currentUserId);
      return matchesQuery(
        sidebarQuery,
        memberLabel(peer),
        peer?.username,
        conversation.dernier_message?.texte
      );
    });
  }, [conversations, currentUserId, sidebarQuery]);

  const conversationPeerIds = useMemo(() => {
    const ids = new Set<number>();
    for (const conversation of conversations) {
      const peer = peerOf(conversation, currentUserId);
      if (peer?.id != null) ids.add(peer.id);
    }
    return ids;
  }, [conversations, currentUserId]);

  const filteredSuivisSansConversation = useMemo(() => {
    return (suivisData ?? []).filter((membre) => {
      if (conversationPeerIds.has(membre.id)) return false;
      return matchesQuery(sidebarQuery, membre.full_name, membre.username);
    });
  }, [suivisData, conversationPeerIds, sidebarQuery]);

  const handleOpenSuivi = async (userId: number) => {
    if (openingSuiviId != null) return;
    setOpeningSuiviId(userId);
    try {
      const conversation = await openConversation(userId).unwrap();
      navigate(`/messages/${conversation.id}`);
    } catch {
      toast.error("Impossible d'ouvrir la conversation");
    } finally {
      setOpeningSuiviId(null);
    }
  };

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

  const threadOpen = hasGroupe || hasConversation;

  return (
    <div className="mx-auto flex h-[calc(100dvh-8rem)] w-full max-w-5xl flex-col gap-3 overflow-hidden">
      <header className="shrink-0">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">
          Messages
        </h1>
        <p className="text-sm text-muted-foreground">
          Groupes (communautés = chat · chaînes = annonces) et conversations
          privées
        </p>
      </header>

      <div className="grid min-h-0 flex-1 overflow-hidden rounded-2xl border border-border bg-card shadow-sm lg:grid-cols-[300px_minmax(0,1fr)] lg:grid-rows-[minmax(0,1fr)]">
        <aside
          className={cn(
            "flex h-full min-h-0 flex-col overflow-hidden border-b border-border lg:border-b-0 lg:border-r",
            threadOpen ? "hidden lg:flex" : "flex"
          )}
        >
          <div className="shrink-0 border-b border-border p-2">
            <label className="relative block">
              <Search
                className="pointer-events-none absolute left-2.5 top-1/2 size-3.5 -translate-y-1/2 text-muted-foreground"
                aria-hidden
              />
              <Input
                value={sidebarQuery}
                onChange={(event) => setSidebarQuery(event.target.value)}
                placeholder="Rechercher un groupe ou un contact…"
                className="h-9 pl-8 text-sm"
                aria-label="Rechercher dans Messages"
              />
            </label>
          </div>
          <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain p-2">
            <p className="px-2 pb-1.5 pt-2 text-[10px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
              Groupes
            </p>
            {loadingGroups ? (
              <p className="px-2 py-4 text-center text-xs text-muted-foreground">
                Chargement des groupes…
              </p>
            ) : null}
            {!loadingGroups && groupes.length === 0 ? (
              <p className="px-2 py-3 text-xs text-muted-foreground">
                Rejoins une communauté ou une chaîne : elle apparaîtra ici.
              </p>
            ) : null}
            {!loadingGroups &&
            groupes.length > 0 &&
            filteredGroupes.length === 0 ? (
              <p className="px-2 py-3 text-xs text-muted-foreground">
                Aucun groupe ne correspond.
              </p>
            ) : null}
            {filteredGroupes.map((espace) => (
              <GroupeListItem
                key={`espace-${espace.id}`}
                espace={espace}
                active={hasGroupe && espace.id === groupeId}
              />
            ))}

            <p className="px-2 pb-1.5 pt-4 text-[10px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
              Privés
            </p>
            {loadingList || loadingSuivis || opening ? (
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
            {suivisError ? (
              <div className="space-y-2 px-2 py-2 text-center">
                <p className="text-xs text-destructive">
                  Impossible de charger tes abonnements.
                </p>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={() => void refetchSuivis()}
                >
                  Réessayer
                </Button>
              </div>
            ) : null}
            {!loadingList &&
            !loadingSuivis &&
            !listError &&
            filteredConversations.length === 0 &&
            filteredSuivisSansConversation.length === 0 ? (
              <p className="px-2 py-4 text-center text-xs text-muted-foreground">
                {sidebarQuery.trim()
                  ? "Aucun contact ne correspond."
                  : "Suis quelqu’un pour lui écrire ici, ou ouvre une conversation depuis son profil."}
              </p>
            ) : null}
            {filteredConversations.map((conversation) => {
              const peer = peerOf(conversation, currentUserId);
              const active =
                !hasGroupe &&
                hasConversation &&
                conversation.id === conversationId;
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
            {filteredSuivisSansConversation.map((membre) => {
              const label = membre.full_name || membre.username || "Membre";
              const busy = openingSuiviId === membre.id;
              return (
                <button
                  key={`suivi-${membre.id}`}
                  type="button"
                  disabled={busy || openingSuiviId != null}
                  onClick={() => void handleOpenSuivi(membre.id)}
                  className="flex w-full items-start gap-3 rounded-xl px-3 py-2.5 text-left transition-colors hover:bg-muted disabled:opacity-60"
                >
                  <ForumAvatar
                    name={label}
                    photo={membre.photo}
                    size="sm"
                    tone="soft"
                  />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-semibold text-foreground">
                      {label}
                    </p>
                    <p className="truncate text-xs text-muted-foreground">
                      {busy
                        ? "Ouverture…"
                        : membre.username
                          ? `@${membre.username} · Suivi`
                          : "Suivi · Écrire"}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        </aside>

        <section
          className={cn(
            "min-h-0 min-w-0 flex-col overflow-hidden",
            threadOpen ? "flex" : "hidden lg:flex"
          )}
        >
          {hasGroupe ? (
            <GroupeThread espaceId={groupeId} />
          ) : hasConversation ? (
            <ConversationThread
              conversationId={conversationId}
              currentUserId={currentUserId}
            />
          ) : (
            <div className="flex flex-1 items-center justify-center px-6 text-center text-sm text-muted-foreground">
              Sélectionne un groupe ou une conversation privée.
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

function GroupeThread({ espaceId }: { espaceId: number }) {
  const {
    data: espace,
    isLoading,
    isError,
    refetch,
  } = useGetEspaceQuery(espaceId);
  const isMember = Boolean(espace?.mon_role);
  const isAdmin =
    espace?.mon_role === "SUPER_ADMIN" || espace?.mon_role === "ADMIN";
  const canWrite = Boolean(espace?.can_publish);
  const isChaine = espace?.type === "CHAINE";
  const detailHref = isChaine
    ? `/forum/chaines/${espaceId}`
    : `/forum/communautes/${espaceId}`;

  if (isLoading) {
    return (
      <div className="flex flex-1 items-center justify-center text-sm text-muted-foreground">
        Ouverture du groupe…
      </div>
    );
  }

  if (isError || !espace) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 px-6 text-center">
        <p className="text-sm text-destructive">Impossible d&apos;ouvrir ce groupe.</p>
        <Button type="button" variant="outline" onClick={() => void refetch()}>
          Réessayer
        </Button>
      </div>
    );
  }

  if (!isMember) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 px-6 text-center">
        <p className="text-sm text-muted-foreground">
          Tu dois rejoindre « {espace.nom} » pour y accéder ici.
        </p>
        <Button asChild>
          <Link to={detailHref}>Voir l&apos;espace</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="flex h-full min-h-0 flex-1 flex-col overflow-hidden">
      <div className="flex shrink-0 items-center justify-between gap-3 border-b border-border px-4 py-3">
        <div className="flex min-w-0 items-center gap-2">
          <Button
            asChild
            type="button"
            size="icon"
            variant="ghost"
            className="shrink-0 lg:hidden"
            aria-label="Retour à la liste"
          >
            <Link to="/messages">
              <ArrowLeft className="size-4" />
            </Link>
          </Button>
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-foreground">
              {espace.nom}
            </p>
            <p className="text-xs text-muted-foreground">
              {isChaine
                ? "Chaîne · lecture & réactions · admins seuls publient"
                : "Communauté · chat de groupe"}
            </p>
          </div>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          {isChaine ? (
            <Button asChild size="sm" variant="outline">
              <Link to={detailHref}>Fil publications</Link>
            </Button>
          ) : null}
          <Button asChild size="sm" variant="outline">
            <Link to={`${detailHref}?manage=1`}>Infos</Link>
          </Button>
        </div>
      </div>
      <div className="min-h-0 flex-1 overflow-hidden">
        <EspaceChat
          embedded
          espaceId={espaceId}
          canWrite={canWrite}
          canReact={isMember}
          canModerate={isAdmin}
          readOnlyHint={
            isChaine
              ? "Chaîne en lecture : tu peux liker / réagir, seuls les admins publient."
              : "Seuls les administrateurs peuvent écrire ici."
          }
        />
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
  const listRef = useRef<HTMLDivElement | null>(null);
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
  } = useGetMessagesQuery(conversationId, { pollingInterval: 8000 });
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
    const list = listRef.current;
    if (!list) return;
    list.scrollTop = list.scrollHeight;
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

  const handleSendVocal = async (url: string) => {
    try {
      await sendMessage({
        conversationId,
        texte: encodeVocalMessage(url),
      }).unwrap();
    } catch {
      toast.error("Impossible d'envoyer le vocal");
      throw new Error("send vocal failed");
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
    <div className="flex h-full min-h-0 flex-1 flex-col overflow-hidden">
      <div className="flex shrink-0 items-center gap-2 border-b border-border px-4 py-3">
        <Button
          asChild
          type="button"
          size="icon"
          variant="ghost"
          className="shrink-0 lg:hidden"
          aria-label="Retour à la liste"
        >
          <Link to="/messages">
            <ArrowLeft className="size-4" />
          </Link>
        </Button>
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

      <div
        ref={listRef}
        className="min-h-0 flex-1 space-y-3 overflow-y-auto overscroll-contain px-4 py-4"
      >
        {messages.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">
            Dis bonjour — envoie le premier message.
          </p>
        ) : null}
        {messages.map((message) => {
          const mine =
            currentUserId != null && message.auteur?.id === currentUserId;
          const vocalUrl = parseVocalUrl(message.texte);
          const hasCode = !vocalUrl && looksLikeCodeBlock(message.texte);
          return (
            <div
              key={message.id}
              className={cn("flex", mine ? "justify-end" : "justify-start")}
            >
              <div
                className={cn(
                  "max-w-[min(100%,36rem)] rounded-2xl px-3 py-2 text-sm",
                  vocalUrl
                    ? mine
                      ? "bg-brand text-brand-foreground"
                      : "bg-muted text-foreground"
                    : hasCode
                      ? "w-full border border-border bg-card text-foreground"
                      : mine
                        ? "bg-brand text-brand-foreground"
                        : "bg-muted text-foreground"
                )}
              >
                {vocalUrl ? (
                  <ForumAudioPlayer
                    compact
                    src={buildMediaUrl(vocalUrl)}
                    className={
                      mine
                        ? "border-brand-foreground/20 bg-brand-foreground/10"
                        : undefined
                    }
                  />
                ) : (
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
                )}
                <p
                  className={cn(
                    "mt-1 text-[10px]",
                    hasCode || !mine
                      ? "text-muted-foreground"
                      : "text-brand-foreground/80"
                  )}
                >
                  {formatTime(message.sent_at || message.created_at)}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      <form
        className="flex shrink-0 flex-col gap-2 border-t border-border p-3"
        onSubmit={(event) => {
          event.preventDefault();
          void handleSend();
        }}
      >
        <div className="flex items-end gap-2">
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
          <VoiceRecorderButton
            compact
            disabled={sending}
            confirmLabel="Envoyer"
            onRecorded={async ({ url }) => {
              await handleSendVocal(url);
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
        </div>
      </form>
    </div>
  );
}
