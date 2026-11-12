import { useCallback, useState } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import { apiDetailOf, httpStatusOf } from "@/models/devstreet-hub/functions/api-error";
import { useHubAccess } from "@/models/devstreet-hub/hooks/use-hub-access";
import { useHubAssistantChatMutation } from "../api";
import type { ChatTurn } from "../schema";

interface UseHubAssistantArgs {
  projectId: number;
  projectTitle: string;
  taskId?: number;
  taskTitle?: string;
}

export function useHubAssistant({
  projectId,
  projectTitle,
  taskId,
  taskTitle,
}: UseHubAssistantArgs) {
  const { t } = useTranslation();
  const access = useHubAccess();
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState("");
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [includeTask, setIncludeTask] = useState(Boolean(taskId));
  const [includeRepo, setIncludeRepo] = useState(true);
  const [chat, chatState] = useHubAssistantChatMutation();

  const suggestions = [
    t("ai.hub.suggestions.summarize"),
    t("ai.hub.suggestions.criteria"),
    t("ai.hub.suggestions.explain"),
  ];

  const send = useCallback(
    async (raw?: string) => {
      const message = (raw ?? draft).trim();
      if (!message) return false;
      if (!access.isAuthenticated) {
        access.requestLogin();
        return false;
      }
      if (!access.canChat) {
        toast.error(t("ai.hub.errors.forbidden"));
        return false;
      }

      const userTurn: ChatTurn = {
        id: `u-${Date.now()}`,
        role: "user",
        content: message,
      };
      setTurns((prev) => [...prev, userTurn]);
      setDraft("");

      try {
        const result = await chat({
          projectId,
          body: {
            message,
            conversation_id: conversationId ?? undefined,
            task_id: includeTask && taskId ? taskId : undefined,
            include_repo: includeRepo,
          },
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
          toast.error(t("ai.hub.errors.unavailable"));
        } else if (status === 429) {
          toast.error(t("ai.hub.errors.quota"));
        } else if (status === 403) {
          toast.error(t("ai.hub.errors.forbidden"));
        } else {
          toast.error(t("ai.hub.errors.generic"));
        }
        return false;
      }
    },
    [
      access,
      chat,
      conversationId,
      draft,
      includeRepo,
      includeTask,
      projectId,
      t,
      taskId,
    ]
  );

  const reset = useCallback(() => {
    setConversationId(null);
    setTurns([]);
    setDraft("");
  }, []);

  return {
    open,
    setOpen,
    draft,
    setDraft,
    turns,
    send,
    reset,
    isBusy: chatState.isLoading,
    canChat: access.canChat,
    isAuthenticated: access.isAuthenticated,
    requestLogin: access.requestLogin,
    suggestions,
    includeTask,
    setIncludeTask,
    includeRepo,
    setIncludeRepo,
    contextLabel: includeTask && taskTitle
      ? `${projectTitle} · ${taskTitle}`
      : projectTitle,
    hasTaskContext: Boolean(taskId),
  };
}
