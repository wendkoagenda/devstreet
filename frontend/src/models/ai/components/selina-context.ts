import { createContext } from "react";
import type { ChatTurn } from "../schema";

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
};

export const SelinaContext = createContext<SelinaContextValue | null>(null);
