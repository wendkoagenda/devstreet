import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQuery } from "@/helpers/api/base-query";
import type {
  AiChatResponse,
  AiConversation,
  AiConversationListItem,
  AiConsumer,
  HubAssistantChatBody,
} from "./schema";

export const aiApi = createApi({
  reducerPath: "aiApi",
  baseQuery,
  tagTypes: ["AiConversation", "AiConversationList"],
  endpoints: (builder) => ({
    listAiConversations: builder.query<
      AiConversationListItem[],
      { consumer?: AiConsumer } | void
    >({
      query: (params) => ({
        url: "/ai/conversations",
        params: {
          page_size: 100,
          ...(params?.consumer ? { consumer: params.consumer } : {}),
        },
      }),
      transformResponse: (
        response:
          | AiConversationListItem[]
          | { results?: AiConversationListItem[] }
      ) => (Array.isArray(response) ? response : response.results ?? []),
      providesTags: [{ type: "AiConversationList", id: "LIST" }],
    }),

    getAiConversation: builder.query<AiConversation, number>({
      query: (id) => `/ai/conversations/${id}`,
      providesTags: (_result, _error, id) => [{ type: "AiConversation", id }],
    }),

    createAiConversation: builder.mutation<
      AiConversation,
      { consumer?: AiConsumer; title?: string }
    >({
      query: (body) => ({
        url: "/ai/conversations",
        method: "POST",
        body,
      }),
      invalidatesTags: [{ type: "AiConversationList", id: "LIST" }],
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
        { type: "AiConversationList", id: "LIST" },
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
  useListAiConversationsQuery,
  useGetAiConversationQuery,
  useCreateAiConversationMutation,
  useSendAiMessageMutation,
  useHubAssistantChatMutation,
} = aiApi;
