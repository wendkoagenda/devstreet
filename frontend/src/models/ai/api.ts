import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQuery } from "@/helpers/api/base-query";
import type {
  AiChatResponse,
  AiConversation,
  HubAssistantChatBody,
} from "./schema";

export const aiApi = createApi({
  reducerPath: "aiApi",
  baseQuery,
  tagTypes: ["AiConversation"],
  endpoints: (builder) => ({
    getAiConversation: builder.query<AiConversation, number>({
      query: (id) => `/ai/conversations/${id}`,
      providesTags: (_result, _error, id) => [{ type: "AiConversation", id }],
    }),

    createAiConversation: builder.mutation<
      AiConversation,
      { consumer?: "hub" | "generic"; title?: string }
    >({
      query: (body) => ({
        url: "/ai/conversations",
        method: "POST",
        body,
      }),
    }),

    sendAiMessage: builder.mutation<
      AiChatResponse,
      { conversationId: number; content: string; context_text?: string }
    >({
      query: ({ conversationId, content, context_text }) => ({
        url: `/ai/conversations/${conversationId}/messages`,
        method: "POST",
        body: { content, context_text },
      }),
      invalidatesTags: (_result, _error, { conversationId }) => [
        { type: "AiConversation", id: conversationId },
      ],
    }),

    hubAssistantChat: builder.mutation<
      AiChatResponse,
      { projectId: number; body: HubAssistantChatBody }
    >({
      query: ({ projectId, body }) => ({
        url: `/projects/${projectId}/assistant/chat`,
        method: "POST",
        body,
      }),
      invalidatesTags: (result) =>
        result
          ? [{ type: "AiConversation", id: result.conversation_id }]
          : [],
    }),
  }),
});

export const {
  useGetAiConversationQuery,
  useCreateAiConversationMutation,
  useSendAiMessageMutation,
  useHubAssistantChatMutation,
} = aiApi;
