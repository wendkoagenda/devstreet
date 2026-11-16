import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import { AI_CHAT } from "@/models/auth/permissions/constants";
import { usePermissions } from "@/hooks/use-permissions";
import { useAuthSlice } from "@/models/auth/slice";
import { saveRedirectPath } from "@/models/auth/functions/redirect-after-login";
import { apiDetailOf, httpStatusOf } from "@/models/devstreet-hub/functions/api-error";
import { useNavigate } from "react-router-dom";
import {
  useCreateAiConversationMutation,
  useGetAiConversationQuery,
  useListAiConversationsQuery,
  useSendAiMessageMutation,
} from "../api";
import type { ChatTurn } from "../schema";
import { SelinaContext, type SelinaContextValue } from "./selina-context";

export function SelinaProvider({ children }: { children: ReactNode }) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const isAuthenticated = useAuthSlice((state) => state.isAuthenticated);
  const { hasPermission, isSuperAdmin } = usePermissions();
  const canChat = isSuperAdmin || hasPermission(AI_CHAT);

  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState("");
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [recentsOpen, setRecentsOpen] = useState(false);
  const [pendingLoadId, setPendingLoadId] = useState<number | null>(null);

  const [createConversation] = useCreateAiConversationMutation();
  const [sendMessage, sendState] = useSendAiMessageMutation();

  const { data: recentsData, isFetching: recentsLoading } =
    useListAiConversationsQuery(
      { consumer: "selina" },
      { skip: !isAuthenticated || !canChat || (!open && !recentsOpen) }
    );

  const { data: loadedConversation } = useGetAiConversationQuery(
    pendingLoadId ?? 0,
    { skip: !pendingLoadId || !isAuthenticated || !canChat }
  );

  useEffect(() => {
    if (!pendingLoadId || !loadedConversation) return;
    if (loadedConversation.id !== pendingLoadId) return;
    setConversationId(loadedConversation.id);
    setTurns(
      loadedConversation.messages
        .filter((message) => message.role === "user" || message.role === "assistant")
        .map((message) => ({
          id: String(message.id),
          role: message.role as "user" | "assistant",
          content: message.content,
          provider: message.provider,
          failoverReason: message.failover_reason || null,
        }))
    );
    setPendingLoadId(null);
  }, [loadedConversation, pendingLoadId]);

  const requestLogin = useCallback(() => {
    saveRedirectPath();
    navigate("/login");
  }, [navigate]);

  const close = useCallback(() => {
    setOpen(false);
    setRecentsOpen(false);
  }, []);

  const openWithDraft = useCallback(
    (text?: string) => {
      if (!isAuthenticated) {
        requestLogin();
        return;
      }
      if (!canChat) {
        toast.error(t("selina.errors.forbidden"));
        return;
      }
      if (text?.trim()) setDraft(text.trim());
      setOpen(true);
    },
    [canChat, isAuthenticated, requestLogin, t]
  );

  const startNewConversation = useCallback(() => {
    setConversationId(null);
    setTurns([]);
    setDraft("");
    setPendingLoadId(null);
    setRecentsOpen(false);
  }, []);

  const loadConversation = useCallback((id: number) => {
    setRecentsOpen(false);
    setPendingLoadId(id);
    setOpen(true);
  }, []);

  const send = useCallback(
    async (raw?: string) => {
      const message = (raw ?? draft).trim();
      if (!message) return false;
      if (!isAuthenticated) {
        requestLogin();
        return false;
      }
      if (!canChat) {
        toast.error(t("selina.errors.forbidden"));
        return false;
      }

      const userTurn: ChatTurn = {
        id: `u-${Date.now()}`,
        role: "user",
        content: message,
      };
      setTurns((prev) => [...prev, userTurn]);
      setDraft("");
      setOpen(true);

      try {
        let activeId = conversationId;
        if (!activeId) {
          const created = await createConversation({
            consumer: "selina",
            title: message.slice(0, 80),
          }).unwrap();
          activeId = created.id;
          setConversationId(activeId);
        }

        const result = await sendMessage({
          conversationId: activeId,
          content: message,
        }).unwrap();

        setConversationId(result.conversation_id);
        setTurns((prev) => [
          ...prev,
          {
            id: `a-${result.message_id}`,
            role: "assistant",
            content: result.assistant_message,
            provider: result.provider,
            failoverReason: result.failover_reason,
          },
        ]);
        return true;
      } catch (error) {
        setTurns((prev) => prev.filter((turn) => turn.id !== userTurn.id));
        setDraft(message);
        const status = httpStatusOf(error);
        const detail = apiDetailOf(error);
        if (detail) {
          toast.error(detail);
        } else if (status === 503) {
          toast.error(t("selina.errors.unavailable"));
        } else if (status === 429) {
          toast.error(t("selina.errors.quota"));
        } else if (status === 403) {
          toast.error(t("selina.errors.forbidden"));
        } else {
          toast.error(t("selina.errors.generic"));
        }
        return false;
      }
    },
    [
      canChat,
      conversationId,
      createConversation,
      draft,
      isAuthenticated,
      requestLogin,
      sendMessage,
      t,
    ]
  );

  useEffect(() => {
    if (!open) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        close();
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [close, open]);

  const value = useMemo<SelinaContextValue>(
    () => ({
      open,
      setOpen,
      openWithDraft,
      close,
      draft,
      setDraft,
      conversationId,
      turns,
      isBusy: sendState.isLoading,
      recentsOpen,
      setRecentsOpen,
      startNewConversation,
      loadConversation,
      send,
      canChat,
      isAuthenticated,
      requestLogin,
      recentConversations: (recentsData ?? []).map((item) => ({
        id: item.id,
        title: item.title || t("selina.untitled"),
        updated_at: item.updated_at,
      })),
      recentsLoading,
    }),
    [
      canChat,
      close,
      conversationId,
      draft,
      isAuthenticated,
      loadConversation,
      open,
      openWithDraft,
      recentsData,
      recentsLoading,
      recentsOpen,
      requestLogin,
      send,
      sendState.isLoading,
      startNewConversation,
      t,
      turns,
    ]
  );

  return (
    <SelinaContext.Provider value={value}>{children}</SelinaContext.Provider>
  );
}
