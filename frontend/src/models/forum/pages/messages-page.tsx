import { profilePath } from "@/helpers/routes/profile-path";
import { useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useDispatch } from "react-redux";
import type { AppDispatch } from "@/redux/store";
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
import { cn } from "@/lib/utils";
import { useAuthSlice } from "@/models/auth/slice";
import { PAGE_SIZE } from "@/helpers/api/pagination";
import {
  forumApi,
  useGetConversationQuery,
  useGetConversationsQuery,
  useGetEspaceQuery,
  useGetEspacesInfiniteQuery,
  useGetMembresSuivisQuery,
  useGetMessagesQuery,
  useGetPublicationsInfiniteQuery,
  useOpenConversationMutation,
  useSendMessageMutation,
  type Conversation,
  type ConversationMember,
} from "../api";
import { ChatAttachMenu } from "../components/chat-attach-menu";
import { ChatMessageBody } from "../components/chat-message-body";
import { EspaceChat } from "../components/espace-chat";
import { FeedComposer } from "../components/feed-composer";
import { ForumAvatar } from "../components/forum-avatar";
import { PublicationCard } from "../components/publication-card";
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
  isMediaBubble,
  parseRichMessage,
} from "../lib/rich-message";
import type { Espace } from "../schema";
import i18n from "i18next";

function memberLabel(member: ConversationMember | null | undefined) {
  if (!member) return i18n.t("forum.member");
  return member.full_name || member.username || i18n.t("forum.member");
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
  const locale = i18n.language?.startsWith("en") ? "en-GB" : "fr-FR";
  return new Intl.DateTimeFormat(locale, {
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
  const { t } = useTranslation();
  const navigate = useNavigate();
  const isChaine = espace.type === "CHAINE";
  const count = espace.membres_count ?? 0;
  const subtitle = isChaine
    ? t(count > 1 ? "forum.channel_meta_plural" : "forum.channel_meta", { count })
    : t(count > 1 ? "forum.group_meta_plural" : "forum.group_meta", { count });

  const unread = Boolean(espace.has_unread);

  return (
    <button
      type="button"
      onClick={() => navigate(`/messages?groupe=${espace.id}`)}
      className={cn(
        "flex w-full items-start gap-3 rounded-xl px-3 py-2.5 text-left transition-colors",
        active ? "bg-brand-soft" : "hover:bg-muted"
      )}
      aria-label={
        unread
          ? t("forum.unread_aria", { name: espace.nom })
          : undefined
      }
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
        {unread ? (
          <span
            className="absolute right-0 top-0 size-2 rounded-full bg-brand ring-2 ring-card"
            aria-hidden
          />
        ) : null}
      </span>
      <div className="min-w-0 flex-1">
        <p
          className={cn(
            "flex items-center gap-1.5 truncate text-sm text-foreground",
            unread ? "font-bold" : "font-semibold"
          )}
        >
          <Hash className="size-3 shrink-0 text-muted-foreground" aria-hidden />
          <span className="truncate">{espace.nom}</span>
        </p>
        <p className="truncate text-xs text-muted-foreground">{subtitle}</p>
      </div>
      {unread ? (
        <span
          className="mt-1.5 size-2 shrink-0 rounded-full bg-brand"
          aria-hidden
        />
      ) : null}
    </button>
  );
}

export default function MessagesPage() {
  const { t } = useTranslation();
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

  const conversations = useMemo(
    () => conversationsData?.results ?? [],
    [conversationsData?.results]
  );
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
      toast.error(t("forum.open_conversation_error"));
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
          toast.error(t("forum.open_conversation_error"));
          navigate("/messages", { replace: true });
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [withUserId, currentUserId, openConversation, navigate, t]);

  useEffect(() => {
    connectMessagingSocket();
  }, []);

  const threadOpen = hasGroupe || hasConversation;

  return (
    <div className="mx-auto flex h-[calc(100dvh-8rem)] w-full max-w-5xl flex-col gap-3 overflow-hidden">
      <header className="shrink-0">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">
          {t("forum.messages_title")}
        </h1>
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
                placeholder={t("forum.search_messages")}
                className="h-9 pl-8 text-sm"
                aria-label={t("forum.search_messages_aria")}
              />
            </label>
          </div>
          <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain p-2 scrollbar-none">
            <p className="px-2 pb-1.5 pt-2 text-[10px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
              {t("forum.groups_section")}
            </p>
            {loadingGroups ? (
              <p className="px-2 py-4 text-center text-xs text-muted-foreground">
                {t("forum.loading_groups")}
              </p>
            ) : null}
            {!loadingGroups && groupes.length === 0 ? (
              <p className="px-2 py-3 text-xs text-muted-foreground">
                {t("forum.empty_groups")}
              </p>
            ) : null}
            {!loadingGroups &&
            groupes.length > 0 &&
            filteredGroupes.length === 0 ? (
              <p className="px-2 py-3 text-xs text-muted-foreground">
                {t("forum.empty_groups_search")}
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
              {t("forum.contacts_section")}
            </p>
            {loadingList || loadingSuivis || opening ? (
              <p className="px-2 py-6 text-center text-sm text-muted-foreground">
                {t("forum.loading")}
              </p>
            ) : null}
            {listError ? (
              <div className="space-y-2 px-2 py-4 text-center">
                <p className="text-sm text-destructive">
                  {t("forum.conversations_error")}
                </p>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={() => void refetchList()}
                >
                  {t("forum.retry")}
                </Button>
              </div>
            ) : null}
            {suivisError ? (
              <div className="space-y-2 px-2 py-2 text-center">
                <p className="text-xs text-destructive">
                  {t("forum.follows_error")}
                </p>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={() => void refetchSuivis()}
                >
                  {t("forum.retry")}
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
                  ? t("forum.empty_contacts_search")
                  : t("forum.empty_contacts")}
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
                t("forum.new_conversation");
              const unread = Boolean(conversation.has_unread);
              const peerName = memberLabel(peer);
              return (
                <button
                  key={conversation.id}
                  type="button"
                  onClick={() => navigate(`/messages/${conversation.id}`)}
                  className={cn(
                    "flex w-full items-start gap-3 rounded-xl px-3 py-2.5 text-left transition-colors",
                    active ? "bg-brand-soft" : "hover:bg-muted"
                  )}
                  aria-label={
                    unread
                      ? t("forum.unread_aria", { name: peerName })
                      : undefined
                  }
                >
                  <span className="relative shrink-0">
                    <ForumAvatar
                      name={peerName}
                      photo={peer?.photo}
                      size="sm"
                      tone="soft"
                    />
                    {unread ? (
                      <span
                        className="absolute right-0 top-0 size-2 rounded-full bg-brand ring-2 ring-card"
                        aria-hidden
                      />
                    ) : null}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p
                      className={cn(
                        "truncate text-sm text-foreground",
                        unread ? "font-bold" : "font-semibold"
                      )}
                    >
                      {peerName}
                    </p>
                    <p
                      className={cn(
                        "truncate text-xs",
                        unread
                          ? "font-medium text-foreground"
                          : "text-muted-foreground"
                      )}
                    >
                      {preview}
                    </p>
                  </div>
                  {unread ? (
                    <span
                      className="mt-1.5 size-2 shrink-0 rounded-full bg-brand"
                      aria-hidden
                    />
                  ) : null}
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
                        ? t("forum.opening")
                        : membre.username
                          ? `@${membre.username} · ${t("forum.follow_prefix")}`
                          : t("forum.follow_write")}
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
              {t("forum.select_thread")}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

function GroupeThread({ espaceId }: { espaceId: number }) {
  const { t } = useTranslation();
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

  const {
    data: feed,
    isLoading: feedLoading,
    isFetching,
    isError: feedError,
    fetchNextPage,
    hasNextPage,
    refetch: refetchFeed,
  } = useGetPublicationsInfiniteQuery(
    { espace: espaceId, page_size: PAGE_SIZE },
    { skip: !isChaine || !isMember }
  );
  const publications =
    feed?.pages.flatMap((page) => page.results ?? []) ?? [];

  if (isLoading) {
    return (
      <div className="flex flex-1 items-center justify-center text-sm text-muted-foreground">
        {t("forum.opening_group")}
      </div>
    );
  }

  if (isError || !espace) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 px-6 text-center">
        <p className="text-sm text-destructive">{t("forum.open_group_error")}</p>
        <Button type="button" variant="outline" onClick={() => void refetch()}>
          {t("forum.retry")}
        </Button>
      </div>
    );
  }

  if (!isMember) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 px-6 text-center">
        <p className="text-sm text-muted-foreground">
          {t("forum.must_join", { name: espace.nom })}
        </p>
        <Button asChild>
          <Link to={detailHref}>{t("forum.view_space")}</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="flex h-full min-h-0 flex-1 flex-col overflow-hidden">
      <div className="flex shrink-0 items-center gap-2 border-b border-border px-3 py-2.5 sm:px-4 sm:py-3">
        <Button
          asChild
          type="button"
          size="icon"
          variant="ghost"
          className="size-8 shrink-0 lg:hidden"
          aria-label={t("forum.back_to_list")}
        >
          <Link to="/messages">
            <ArrowLeft className="size-4" />
          </Link>
        </Button>
        <div className="min-w-0 flex-1">
          <p className="truncate text-[13px] font-semibold text-foreground sm:text-sm">
            {espace.nom}
          </p>
          <p className="truncate text-[11px] text-muted-foreground sm:text-xs">
            {isChaine ? t("forum.channel_label") : t("forum.community_label")}
          </p>
        </div>
        <Button
          asChild
          size="sm"
          variant="outline"
          className="h-7 shrink-0 px-2 text-[11px] sm:h-8 sm:px-3 sm:text-sm"
        >
          <Link to={`${detailHref}?manage=1`}>{t("forum.infos")}</Link>
        </Button>
      </div>

      {isChaine ? (
        <div className="min-h-0 flex-1 space-y-3 overflow-y-auto overscroll-contain px-3 py-3 scrollbar-none sm:px-4">
          {canWrite ? (
            <FeedComposer
              espaceId={espaceId}
              discussionOnly
              onCreated={() => {
                void refetchFeed();
              }}
            />
          ) : (
            <p className="rounded-xl border border-border bg-muted/40 px-3 py-2 text-[12px] text-muted-foreground sm:text-sm">
              {t("forum.channel_admins_publish")}
            </p>
          )}

          {feedLoading ? (
            <p className="py-8 text-center text-sm text-muted-foreground">
              {t("forum.loading")}
            </p>
          ) : null}

          {feedError ? (
            <div className="space-y-2 py-6 text-center">
              <p className="text-sm text-destructive">
                {t("forum.load_announcements_error")}
              </p>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => void refetchFeed()}
              >
                {t("forum.retry")}
              </Button>
            </div>
          ) : null}

          {!feedLoading && !feedError && publications.length === 0 ? (
            <p className="rounded-2xl border border-dashed border-border px-4 py-10 text-center text-sm text-muted-foreground">
              {t("forum.empty_announcements")}
            </p>
          ) : null}

          {publications.map((publication) => (
            <PublicationCard
              key={publication.id}
              publication={publication}
            />
          ))}

          {hasNextPage ? (
            <div className="flex justify-center pb-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={isFetching}
                onClick={() => void fetchNextPage()}
              >
                {isFetching ? t("forum.loading") : t("forum.see_more")}
              </Button>
            </div>
          ) : null}
        </div>
      ) : (
        <div className="min-h-0 flex-1 overflow-hidden">
          <EspaceChat
            embedded
            espaceId={espaceId}
            canWrite={canWrite}
            canReact={isMember}
            canModerate={isAdmin}
            readOnlyHint={t("forum.admins_only_hint")}
          />
        </div>
      )}
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
  const { t } = useTranslation();
  const dispatch = useDispatch<AppDispatch>();
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
      toast.error(t("forum.send_message_error"));
    }
  };

  const handleSendEncoded = async (texte: string) => {
    await sendMessage({ conversationId, texte }).unwrap();
  };

  const handleSendVocal = async (url: string) => {
    try {
      await handleSendEncoded(encodeVocalMessage(url));
    } catch {
      toast.error(t("forum.send_voice_error"));
      throw new Error("send vocal failed");
    }
  };

  if (loadingConversation || loadingMessages) {
    return (
      <div className="flex flex-1 items-center justify-center text-sm text-muted-foreground">
        {t("forum.load_thread")}
      </div>
    );
  }

  if (conversationError || messagesError || !conversation) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 px-6 text-center">
        <p className="text-sm text-destructive">
          {t("forum.load_conversation_error")}
        </p>
        <Button
          type="button"
          variant="outline"
          onClick={() => void refetchMessages()}
        >
          {t("forum.retry")}
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
          aria-label={t("forum.back_to_list")}
        >
          <Link to="/messages">
            <ArrowLeft className="size-4" />
          </Link>
        </Button>
        <Link
          to={peer?.username ? profilePath(peer.username) : "/messages"}
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
        className="min-h-0 flex-1 space-y-3 overflow-y-auto overscroll-contain px-4 py-4 scrollbar-none"
      >
        {messages.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">
            {t("forum.say_hello")}
          </p>
        ) : null}
        {messages.map((message) => {
          const mine =
            currentUserId != null && message.auteur?.id === currentUserId;
          const rich = parseRichMessage(message.texte);
          const media = isMediaBubble(message.texte);
          const hasCode =
            rich.kind === "text" && looksLikeCodeBlock(message.texte);
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
                    : media || mine
                      ? mine
                        ? "bg-brand text-brand-foreground"
                        : "bg-muted text-foreground"
                      : "bg-muted text-foreground"
                )}
              >
                <ChatMessageBody texte={message.texte} mine={mine} />
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
            placeholder={t("forum.write_message")}
            rows={2}
            className="min-h-[44px] resize-none"
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                void handleSend();
              }
            }}
          />
          <ChatAttachMenu
            disabled={sending}
            onSendEncoded={async (texte) => {
              try {
                await handleSendEncoded(texte);
              } catch {
                toast.error(t("forum.send_attachment_error"));
                throw new Error("send attachment failed");
              }
            }}
          />
          <VoiceRecorderButton
            compact
            disabled={sending}
            confirmLabel={t("forum.send")}
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
            <span className="sr-only">{t("forum.send")}</span>
          </Button>
        </div>
      </form>
    </div>
  );
}
