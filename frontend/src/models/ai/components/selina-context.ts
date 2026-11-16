import { createContext } from "react";
import type { ChatTurn } from "../schema";

export type SelinaHubContext = {
  projectId: number;
  projectTitle: string;
  taskId?: number;
  taskTitle?: string;
  includeRepo: boolean;
  includeTask: boolean;
};

export type SelinaHubContextInput = {
  projectId: number;
  projectTitle: string;
  taskId?: number;
  taskTitle?: string;
};

export type SelinaContextValue = {
  open: boolean;
  setOpen: (open: boolean) => void;
  openWithDraft: (text?: string) => void;
  close: () => void;
  draft: string;
  setDraft: (value: string) => void;
  conversationId: number | null;
  turns: ChatTurn[];
  isBusy: boolean;
  recentsOpen: boolean;
  setRecentsOpen: (open: boolean) => void;
  startNewConversation: () => void;
  loadConversation: (id: number) => void;
  send: (raw?: string) => Promise<boolean>;
  canChat: boolean;
  isAuthenticated: boolean;
  requestLogin: () => void;
  recentConversations: Array<{
    id: number;
    title: string;
    updated_at: string;
  }>;
  recentsLoading: boolean;
  hubContext: SelinaHubContext | null;
  setHubContext: (context: SelinaHubContextInput | null) => void;
  clearHubContext: () => void;
  setIncludeRepo: (value: boolean) => void;
  setIncludeTask: (value: boolean) => void;
};

export const SelinaContext = createContext<SelinaContextValue | null>(null);
