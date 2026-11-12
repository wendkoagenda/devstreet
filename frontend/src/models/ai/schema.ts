import { z } from "zod";

export const aiChatResponseSchema = z.object({
  conversation_id: z.number(),
  user_message: z.string(),
  assistant_message: z.string(),
  provider: z.string(),
  model: z.string(),
  failover_reason: z.string().nullable().optional(),
  message_id: z.number(),
});

export const aiMessageSchema = z.object({
  id: z.number(),
  role: z.enum(["user", "assistant", "system"]),
  content: z.string(),
  provider: z.string().optional().default(""),
  failover_reason: z.string().optional().default(""),
  created_at: z.string(),
});

export const aiConversationSchema = z.object({
  id: z.number(),
  consumer: z.enum(["hub", "generic"]),
  title: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
  messages: z.array(aiMessageSchema).default([]),
});

export type AiChatResponse = z.infer<typeof aiChatResponseSchema>;
export type AiMessage = z.infer<typeof aiMessageSchema>;
export type AiConversation = z.infer<typeof aiConversationSchema>;

export type HubAssistantChatBody = {
  message: string;
  conversation_id?: number;
  task_id?: number;
  include_repo?: boolean;
};

export type ChatTurn = {
  id: string;
  role: "user" | "assistant";
  content: string;
  provider?: string;
  failoverReason?: string | null;
};
