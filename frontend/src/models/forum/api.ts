import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQuery } from "@/helpers/api/base-query";
import {
  cursorFromUrl,
  PAGE_SIZE,
  toQueryString,
  type CursorPaginated,
  type ListParams,
  type Paginated,
} from "@/helpers/api/pagination";
import type {
  AvisChoix,
  Commentaire,
  ConfirmationAideToggleResult,
  CreateApplicationInput,
  CreateChoixInput,
  CreateCommentInput,
  CreateDiscussionInput,
  CreateEntraideInput,
  CreateEspaceInput,
  DecideChoixInput,
  Espace,
  EspaceMembre,
  FavoriToggleResult,
  LienInvitation,
  LikeToggleResult,
  Publication,
  UpsertAvisInput,
} from "./schema";

export type FeedListArg = {
  type?: string;
  page_size?: number;
  search?: string;
  auteur?: number;
  espace?: number;
  invite?: string;
  feed?: "pour-vous" | "abonnements" | "derniers" | "populaires" | "favoris";
};

export type ConversationMember = {
  id: number;
  username: string;
  full_name: string;
  photo?: string;
};

export type ConversationLastMessage = {
  id: number;
  texte: string;
  sent_at: string | null;
  auteur_id: number;
};

export type Conversation = {
  id: number;
  membre_1: ConversationMember | null;
  membre_2: ConversationMember | null;
  autre_membre: ConversationMember | null;
  dernier_message: ConversationLastMessage | null;
  created_at: string;
  updated_at: string;
};

export type PrivateMessage = {
  id: number;
  conversation: number;
  auteur: ConversationMember | null;
  texte: string;
  sent_at: string | null;
  created_at: string;
  updated_at: string;
};

export type EspaceMessageReply = {
  id: number;
  texte: string;
  supprime: boolean;
  auteur: ConversationMember | null;
};

export type EspaceMessageReactions = {
  counts: Array<{ emoji: string; count: number }>;
  ma_reaction: string | null;
};

export type EspaceMessage = {
  id: number;
  espace: number;
  auteur: ConversationMember | null;
  texte: string;
  reply_to: EspaceMessageReply | null;
  reactions: EspaceMessageReactions;
  supprime: boolean;
  sent_at: string | null;
  created_at: string;
  updated_at: string;
};

export const forumApi = createApi({
  reducerPath: "forumApi",
  baseQuery,
  tagTypes: [
    "Publications",
    "Publication",
    "Comments",
    "Avis",
    "PublicProfile",
    "MembresSuivis",
    "Conversations",
    "Messages",
    "Espaces",
    "Espace",
    "EspaceMessages",
    "ActivityBadges",
    "NotificationResume",
  ],
  endpoints: (builder) => ({
    getActivityBadges: builder.query<
      { messages: number; communautes: number; chaines: number },
      void
    >({
      query: () => `/activity/badges`,
      providesTags: ["ActivityBadges"],
    }),

    getResumeActuel: builder.query<
      {
        id: number;
        periode_debut: string;
        periode_fin: string;
        nombre_nouveautes: number;
        read_at: string | null;
      } | null,
      void
    >({
      query: () => ({
        url: `/notifications-resume/actuel`,
        responseHandler: async (response) => {
          if (response.status === 204) return null;
          const text = await response.text();
          if (!text) return null;
          return JSON.parse(text) as {
            id: number;
            periode_debut: string;
            periode_fin: string;
            nombre_nouveautes: number;
            read_at: string | null;
          };
        },
      }),
      providesTags: ["NotificationResume"],
    }),

    markResumeLire: builder.mutation<
      {
        id: number;
        periode_debut: string;
        periode_fin: string;
        nombre_nouveautes: number;
        read_at: string | null;
      },
      number
    >({
      query: (id) => ({
        url: `/notifications-resume/${id}/lire`,
        method: "POST",
      }),
      invalidatesTags: ["NotificationResume"],
    }),

    getPublicProfile: builder.query<
      {
        id: number;
        username: string;
        full_name: string;
        photo?: string;
        banner?: string;
        is_following?: boolean;
      },
      number
    >({
      query: (userId) => `/membres/${userId}`,
      providesTags: (_result, _error, userId) => [
        { type: "PublicProfile", id: userId },
      ],
    }),

    getPublicProfileByUsername: builder.query<
      {
        id: number;
        username: string;
        full_name: string;
        photo?: string;
        banner?: string;
        is_following?: boolean;
      },
      string
    >({
      query: (username) => `/membres/u/${encodeURIComponent(username)}`,
      providesTags: (result) =>
        result ? [{ type: "PublicProfile", id: result.id }] : [],
    }),

    searchMembres: builder.query<
      Array<{
        id: number;
        username: string;
        full_name: string;
        photo?: string;
      }>,
      string
    >({
      query: (q) => `/membres/search${toQueryString({ q })}`,
    }),

    getMembresSuivis: builder.query<
      Array<{
        id: number;
        username: string;
        full_name: string;
        photo?: string;
      }>,
      { q?: string; limit?: number } | void
    >({
      query: (params) =>
        `/membres/suivis${toQueryString({
          q: params?.q || undefined,
          limit: params?.limit ?? 50,
        })}`,
      providesTags: ["MembresSuivis"],
    }),

    toggleSuivreMembre: builder.mutation<
      { following: boolean; suivi_id: number },
      number
    >({
      query: (userId) => ({
        url: `/membres/${userId}/suivre`,
        method: "POST",
      }),
      invalidatesTags: (_result, _error, userId) => [
        "Publications",
        "MembresSuivis",
        { type: "PublicProfile", id: userId },
        { type: "Publications", id: "LIST" },
      ],
    }),

    getConversations: builder.query<Paginated<Conversation>, void>({
      query: () => `/conversations${toQueryString({ page_size: 50 })}`,
      providesTags: (result) =>
        result?.results?.length
          ? [
              ...result.results.map(({ id }) => ({
                type: "Conversations" as const,
                id,
              })),
              { type: "Conversations", id: "LIST" },
            ]
          : [{ type: "Conversations", id: "LIST" }],
    }),

    openConversation: builder.mutation<Conversation, number>({
      query: (destinataireId) => ({
        url: "/conversations",
        method: "POST",
        body: { destinataire_id: destinataireId },
      }),
      invalidatesTags: [{ type: "Conversations", id: "LIST" }],
    }),

    getConversation: builder.query<Conversation, number>({
      query: (id) => `/conversations/${id}`,
      providesTags: (_result, _error, id) => [{ type: "Conversations", id }],
    }),

    getMessages: builder.query<Paginated<PrivateMessage>, number>({
      query: (conversationId) =>
        `/messages${toQueryString({
          conversation: conversationId,
          page_size: 100,
        })}`,
      providesTags: (_result, _error, conversationId) => [
        { type: "Messages", id: conversationId },
      ],
      async onQueryStarted(_arg, { dispatch, queryFulfilled }) {
        try {
          await queryFulfilled;
          dispatch(
            forumApi.util.invalidateTags(["ActivityBadges"])
          );
        } catch {
          /* ignore */
        }
      },
    }),

    sendMessage: builder.mutation<
      PrivateMessage,
      { conversationId: number; texte: string }
    >({
      query: ({ conversationId, texte }) => ({
        url: "/messages",
        method: "POST",
        body: { conversation_id: conversationId, texte },
      }),
      invalidatesTags: (_result, _error, arg) => [
        { type: "Messages", id: arg.conversationId },
        { type: "Conversations", id: "LIST" },
        { type: "Conversations", id: arg.conversationId },
        "ActivityBadges",
      ],
    }),
    getPublications: builder.infiniteQuery<
      CursorPaginated<Publication>,
      FeedListArg | void,
      string | null
    >({
      infiniteQueryOptions: {
        initialPageParam: null,
        getNextPageParam: (lastPage) => cursorFromUrl(lastPage.next) ?? undefined,
        getPreviousPageParam: (firstPage) =>
          cursorFromUrl(firstPage.previous) ?? undefined,
      },
      query: ({ queryArg, pageParam }) => {
        const params: ListParams = {
          page_size: queryArg?.page_size ?? PAGE_SIZE,
          ...(queryArg?.type ? { type: queryArg.type } : {}),
          ...(queryArg?.search ? { search: queryArg.search } : {}),
          ...(queryArg?.auteur ? { auteur: queryArg.auteur } : {}),
          ...(queryArg?.espace ? { espace: queryArg.espace } : {}),
          ...(queryArg?.invite ? { invite: queryArg.invite } : {}),
          ...(queryArg?.feed ? { feed: queryArg.feed } : {}),
          ...(pageParam ? { cursor: pageParam } : {}),
        };
        return `/publications${toQueryString(params)}`;
      },
      providesTags: (result) => {
        const pages = result?.pages ?? [];
        const items = pages.flatMap((page) => page.results);
        return items.length
          ? [
              ...items.map(({ id }) => ({
                type: "Publications" as const,
                id,
              })),
              { type: "Publications", id: "LIST" },
            ]
          : [{ type: "Publications", id: "LIST" }];
      },
    }),

    getPublication: builder.query<Publication, number>({
      query: (id) => `/publications/${id}`,
      providesTags: (_result, _error, id) => [{ type: "Publication", id }],
    }),

    uploadForumImage: builder.mutation<
      { url: string; path: string; kind?: string },
      File
    >({
      query: (file) => {
        const formData = new FormData();
        const safeName = file.name.replace(/[^\w.\-]+/g, "-").toLowerCase();
        const stamp = Date.now();
        formData.append("image", file);
        formData.append("kind", "IMAGE");
        formData.append("image_path", `forum_images/${stamp}-${safeName}`);
        return {
          url: "/publications/upload-image",
          method: "POST",
          body: formData,
        };
      },
    }),

    uploadForumMedia: builder.mutation<
      { url: string; path: string; kind: "IMAGE" | "VIDEO" | "AUDIO" },
      { file: File; kind: "IMAGE" | "VIDEO" | "AUDIO" }
    >({
      query: ({ file, kind }) => {
        const formData = new FormData();
        const safeName = file.name.replace(/[^\w.\-]+/g, "-").toLowerCase();
        const stamp = Date.now();
        const folder =
          kind === "VIDEO"
            ? "forum_videos"
            : kind === "AUDIO"
              ? "forum_audios"
              : "forum_images";
        formData.append("file", file);
        formData.append("kind", kind);
        formData.append("path", `${folder}/${stamp}-${safeName}`);
        return {
          url: "/publications/upload-media",
          method: "POST",
          body: formData,
        };
      },
    }),

    getEspaces: builder.infiniteQuery<
      Paginated<Espace>,
      {
        type?: string;
        acces?: string;
        search?: string;
        mine?: boolean;
        page_size?: number;
      } | void,
      number
    >({
      infiniteQueryOptions: {
        initialPageParam: 1,
        getNextPageParam: (lastPage, _allPages, lastPageParam) =>
          lastPage.next ? lastPageParam + 1 : undefined,
        getPreviousPageParam: (firstPage, _allPages, firstPageParam) =>
          firstPage.previous && firstPageParam > 1
            ? firstPageParam - 1
            : undefined,
      },
      query: ({ queryArg, pageParam }) =>
        `/espaces${toQueryString({
          page: pageParam,
          page_size: queryArg?.page_size ?? PAGE_SIZE,
          type: queryArg?.type ?? "COMMUNAUTE",
          ...(queryArg?.acces ? { acces: queryArg.acces } : {}),
          ...(queryArg?.search ? { search: queryArg.search } : {}),
          ...(queryArg?.mine ? { mine: 1 } : {}),
        })}`,
      providesTags: (result) => {
        const items = result?.pages.flatMap((page) => page.results) ?? [];
        return items.length
          ? [
              ...items.map((espace) => ({
                type: "Espace" as const,
                id: espace.id,
              })),
              { type: "Espaces", id: "LIST" },
            ]
          : [{ type: "Espaces", id: "LIST" }];
      },
    }),

    getEspace: builder.query<Espace, { id: number; invite?: string } | number>({
      query: (arg) => {
        const id = typeof arg === "number" ? arg : arg.id;
        const invite = typeof arg === "number" ? undefined : arg.invite;
        return `/espaces/${id}${toQueryString(invite ? { invite } : {})}`;
      },
      providesTags: (_result, _error, arg) => [
        { type: "Espace", id: typeof arg === "number" ? arg : arg.id },
      ],
    }),

    createEspace: builder.mutation<Espace, CreateEspaceInput>({
      query: (body) => ({
        url: "/espaces",
        method: "POST",
        body,
      }),
      invalidatesTags: [{ type: "Espaces", id: "LIST" }],
    }),

    updateEspace: builder.mutation<
      Espace,
      {
        id: number;
        membres_peuvent_publier?: boolean;
        acces?: "PUBLIC" | "LIEN";
        commentaires_ouverts?: boolean;
        nom?: string;
        description?: string;
        photo?: string;
      }
    >({
      query: ({ id, ...body }) => ({
        url: `/espaces/${id}`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: (_result, _error, arg) => [
        { type: "Espace", id: arg.id },
        { type: "Espaces", id: "LIST" },
      ],
    }),

    exclureEspaceMembre: builder.mutation<
      void,
      { espaceId: number; membreId: number }
    >({
      query: ({ espaceId, membreId }) => ({
        url: `/espaces/${espaceId}/membres/${membreId}/exclure`,
        method: "POST",
      }),
      invalidatesTags: (_result, _error, arg) => [
        { type: "Espace", id: arg.espaceId },
      ],
    }),

    rejoindreEspace: builder.mutation<
      { id: number; role: string; espace: number; membre: number },
      number
    >({
      query: (espaceId) => ({
        url: `/espaces/${espaceId}/rejoindre`,
        method: "POST",
      }),
      invalidatesTags: (_result, _error, id) => [
        { type: "Espace", id },
        { type: "Espaces", id: "LIST" },
        "Publications",
        "ActivityBadges",
      ],
    }),

    quitterEspace: builder.mutation<void, number>({
      query: (espaceId) => ({
        url: `/espaces/${espaceId}/quitter`,
        method: "POST",
      }),
      invalidatesTags: (_result, _error, id) => [
        { type: "Espace", id },
        { type: "Espaces", id: "LIST" },
        "Publications",
        "ActivityBadges",
      ],
    }),

    getEspaceMessages: builder.query<
      Paginated<EspaceMessage>,
      { espaceId: number; page_size?: number }
    >({
      query: ({ espaceId, page_size = 50 }) =>
        `/espaces/${espaceId}/messages${toQueryString({ page_size })}`,
      providesTags: (_result, _error, arg) => [
        { type: "EspaceMessages", id: arg.espaceId },
      ],
      async onQueryStarted(_arg, { dispatch, queryFulfilled }) {
        try {
          await queryFulfilled;
          dispatch(forumApi.util.invalidateTags(["ActivityBadges"]));
        } catch {
          /* ignore */
        }
      },
    }),

    sendEspaceMessage: builder.mutation<
      EspaceMessage,
      { espaceId: number; texte: string; reply_to_id?: number | null }
    >({
      query: ({ espaceId, texte, reply_to_id }) => ({
        url: `/espaces/${espaceId}/messages`,
        method: "POST",
        body: {
          texte,
          ...(reply_to_id != null ? { reply_to_id } : {}),
        },
      }),
      invalidatesTags: (_result, _error, arg) => [
        { type: "EspaceMessages", id: arg.espaceId },
        "ActivityBadges",
      ],
    }),

    deleteEspaceMessage: builder.mutation<
      EspaceMessage,
      { espaceId: number; messageId: number }
    >({
      query: ({ espaceId, messageId }) => ({
        url: `/espaces/${espaceId}/messages/${messageId}/supprimer`,
        method: "POST",
      }),
      invalidatesTags: (_result, _error, arg) => [
        { type: "EspaceMessages", id: arg.espaceId },
      ],
    }),

    reactEspaceMessage: builder.mutation<
      EspaceMessage,
      { espaceId: number; messageId: number; emoji: string }
    >({
      query: ({ espaceId, messageId, emoji }) => ({
        url: `/espaces/${espaceId}/messages/${messageId}/reactions`,
        method: "POST",
        body: { emoji },
      }),
      invalidatesTags: (_result, _error, arg) => [
        { type: "EspaceMessages", id: arg.espaceId },
      ],
    }),

    getEspaceLiens: builder.query<LienInvitation[], number>({
      query: (espaceId) => `/espaces/${espaceId}/liens`,
      providesTags: (_result, _error, id) => [{ type: "Espace", id }],
    }),

    createEspaceLien: builder.mutation<
      LienInvitation,
      { espaceId: number; previsualisation_autorisee?: boolean }
    >({
      query: ({ espaceId, previsualisation_autorisee }) => ({
        url: `/espaces/${espaceId}/liens`,
        method: "POST",
        body: { previsualisation_autorisee: Boolean(previsualisation_autorisee) },
      }),
      invalidatesTags: (_result, _error, arg) => [
        { type: "Espace", id: arg.espaceId },
      ],
    }),

    revoquerEspaceLien: builder.mutation<
      LienInvitation,
      { espaceId: number; lienId: number }
    >({
      query: ({ espaceId, lienId }) => ({
        url: `/espaces/${espaceId}/liens/${lienId}/revoquer`,
        method: "POST",
      }),
      invalidatesTags: (_result, _error, arg) => [
        { type: "Espace", id: arg.espaceId },
      ],
    }),

    getEspaceMembres: builder.query<Paginated<EspaceMembre>, number>({
      query: (espaceId) =>
        `/espaces/${espaceId}/membres${toQueryString({ page_size: 50 })}`,
      providesTags: (_result, _error, id) => [{ type: "Espace", id }],
    }),

    setEspaceMembreRole: builder.mutation<
      EspaceMembre,
      { espaceId: number; membreId: number; role: "ADMIN" | "MEMBRE" }
    >({
      query: ({ espaceId, membreId, role }) => ({
        url: `/espaces/${espaceId}/membres/${membreId}/role`,
        method: "POST",
        body: { role },
      }),
      invalidatesTags: (_result, _error, arg) => [
        { type: "Espace", id: arg.espaceId },
      ],
    }),

    previewInvitation: builder.query<
      {
        espace_id: number;
        espace_nom: string;
        espace_description: string;
        previsualisation_autorisee: boolean;
        deja_membre: boolean;
        mon_role: string | null;
      },
      string
    >({
      query: (code) => `/espaces/invitation/${encodeURIComponent(code)}`,
    }),

    rejoindreViaInvitation: builder.mutation<EspaceMembre, string>({
      query: (code) => ({
        url: `/espaces/invitation/${encodeURIComponent(code)}/rejoindre`,
        method: "POST",
      }),
      invalidatesTags: [
        { type: "Espaces", id: "LIST" },
        "ActivityBadges",
      ],
    }),

    createDiscussion: builder.mutation<Publication, CreateDiscussionInput>({
      query: (body) => ({
        url: "/publications",
        method: "POST",
        body: {
          type: "DISCUSSION",
          titre: body.titre,
          description: body.description,
          images_data: body.images_data ?? [],
          ...(body.espace_id ? { espace_id: body.espace_id } : {}),
        },
      }),
      invalidatesTags: [{ type: "Publications", id: "LIST" }],
    }),

    createApplication: builder.mutation<Publication, CreateApplicationInput>({
      query: (body) => ({
        url: "/publications",
        method: "POST",
        body: {
          type: "APPLICATION",
          titre: body.titre,
          description: body.description,
          lien_app: body.lien_app,
          plateforme_app: body.plateforme_app ?? "WEB",
          images_data: body.images_data ?? [],
        },
      }),
      invalidatesTags: [{ type: "Publications", id: "LIST" }],
    }),

    createEntraide: builder.mutation<Publication, CreateEntraideInput>({
      query: (body) => ({
        url: "/publications",
        method: "POST",
        body: {
          type: "ENTRAIDE",
          titre: body.titre,
          description: body.description,
          images_data: body.images_data ?? [],
        },
      }),
      invalidatesTags: [{ type: "Publications", id: "LIST" }],
    }),

    createChoix: builder.mutation<Publication, CreateChoixInput>({
      query: (body) => ({
        url: "/publications",
        method: "POST",
        body: {
          type: "CHOIX",
          titre: body.titre,
          description: body.description,
          contraintes: body.contraintes ?? "",
          options_data: body.options_data,
          images_data: body.images_data ?? [],
        },
      }),
      invalidatesTags: [{ type: "Publications", id: "LIST" }],
    }),

    getPublicationAvis: builder.query<AvisChoix[], number>({
      query: (id) => `/publications/${id}/avis`,
      providesTags: (_result, _error, id) => [{ type: "Avis", id }],
    }),

    upsertPublicationAvis: builder.mutation<
      AvisChoix,
      { publicationId: number; body: UpsertAvisInput }
    >({
      query: ({ publicationId, body }) => ({
        url: `/publications/${publicationId}/avis`,
        method: "POST",
        body,
      }),
      invalidatesTags: (_result, _error, arg) => [
        { type: "Avis", id: arg.publicationId },
        { type: "Publication", id: arg.publicationId },
        { type: "Publications", id: "LIST" },
      ],
    }),

    decideChoix: builder.mutation<
      Publication,
      { publicationId: number; body: DecideChoixInput }
    >({
      query: ({ publicationId, body }) => ({
        url: `/publications/${publicationId}/decider`,
        method: "POST",
        body,
      }),
      invalidatesTags: (_result, _error, arg) => [
        { type: "Publication", id: arg.publicationId },
        { type: "Publications", id: "LIST" },
        { type: "Avis", id: arg.publicationId },
      ],
    }),

    acceptTechnicalReply: builder.mutation<
      Publication,
      { publicationId: number; commentaireId: number | null }
    >({
      query: ({ publicationId, commentaireId }) => ({
        url: `/publications/${publicationId}/accepter-reponse`,
        method: "POST",
        body: { commentaire_id: commentaireId },
      }),
      invalidatesTags: (_result, _error, arg) => [
        { type: "Publication", id: arg.publicationId },
        { type: "Publications", id: "LIST" },
        { type: "Comments", id: arg.publicationId },
      ],
    }),

    togglePublicationLike: builder.mutation<LikeToggleResult, number>({
      query: (id) => ({
        url: `/publications/${id}/like`,
        method: "POST",
      }),
      async onQueryStarted(id, { dispatch, queryFulfilled, getState }) {
        const patchPublication = (draft: Publication) => {
          const next = !draft.liked_by_me;
          draft.liked_by_me = next;
          draft.likes_count = Math.max(
            0,
            (draft.likes_count ?? 0) + (next ? 1 : -1)
          );
        };
        const patches = [
          dispatch(
            forumApi.util.updateQueryData("getPublication", id, (draft) => {
              patchPublication(draft);
            })
          ),
          ...forumApi.util
            .selectCachedArgsForQuery(getState(), "getPublications")
            .map((arg) =>
              dispatch(
                forumApi.util.updateQueryData(
                  "getPublications",
                  arg,
                  (draft) => {
                    for (const page of draft.pages) {
                      for (const pub of page.results) {
                        if (pub.id === id) patchPublication(pub);
                      }
                    }
                  }
                )
              )
            ),
        ];
        try {
          await queryFulfilled;
        } catch {
          for (const patch of patches) patch.undo();
        }
      },
    }),

    togglePublicationFavori: builder.mutation<FavoriToggleResult, number>({
      query: (id) => ({
        url: `/publications/${id}/favori`,
        method: "POST",
      }),
      async onQueryStarted(id, { dispatch, queryFulfilled, getState }) {
        const patches = [
          dispatch(
            forumApi.util.updateQueryData("getPublication", id, (draft) => {
              draft.saved_by_me = !draft.saved_by_me;
            })
          ),
          ...forumApi.util
            .selectCachedArgsForQuery(getState(), "getPublications")
            .map((arg) =>
              dispatch(
                forumApi.util.updateQueryData(
                  "getPublications",
                  arg,
                  (draft) => {
                    const isFavorisFeed = arg?.feed === "favoris";
                    for (const page of draft.pages) {
                      if (isFavorisFeed) {
                        const next = page.results.filter((pub) => pub.id !== id);
                        if (next.length !== page.results.length) {
                          // Retrait du favori : sortir de la liste « Mes favoris ».
                          const wasSaved = page.results.find(
                            (pub) => pub.id === id
                          )?.saved_by_me;
                          if (wasSaved) {
                            page.results = next;
                            continue;
                          }
                        }
                      }
                      for (const pub of page.results) {
                        if (pub.id === id) pub.saved_by_me = !pub.saved_by_me;
                      }
                    }
                  }
                )
              )
            ),
        ];
        try {
          await queryFulfilled;
        } catch {
          for (const patch of patches) patch.undo();
        }
      },
    }),

    getPublicationComments: builder.query<Commentaire[], number>({
      query: (id) => `/publications/${id}/commentaires`,
      providesTags: (_result, _error, id) => [{ type: "Comments", id }],
    }),

    createPublicationComment: builder.mutation<
      Commentaire,
      { publicationId: number; body: CreateCommentInput }
    >({
      query: ({ publicationId, body }) => ({
        url: `/publications/${publicationId}/commentaires`,
        method: "POST",
        body,
      }),
      invalidatesTags: (_result, _error, arg) => [
        { type: "Comments", id: arg.publicationId },
        { type: "Publication", id: arg.publicationId },
        { type: "Publications", id: "LIST" },
      ],
    }),

    toggleCommentLike: builder.mutation<
      LikeToggleResult,
      { commentaireId: number; publicationId: number }
    >({
      query: ({ commentaireId }) => ({
        url: `/commentaires/${commentaireId}/like`,
        method: "POST",
      }),
      invalidatesTags: (_result, _error, arg) => [
        { type: "Comments", id: arg.publicationId },
      ],
    }),

    toggleConfirmationAide: builder.mutation<
      ConfirmationAideToggleResult,
      { commentaireId: number; publicationId: number }
    >({
      query: ({ commentaireId }) => ({
        url: `/commentaires/${commentaireId}/confirmation-aide`,
        method: "POST",
      }),
      invalidatesTags: (_result, _error, arg) => [
        { type: "Comments", id: arg.publicationId },
      ],
    }),
  }),
});

export const {
  useGetActivityBadgesQuery,
  useGetResumeActuelQuery,
  useMarkResumeLireMutation,
  useGetPublicProfileQuery,
  useGetPublicProfileByUsernameQuery,
  useLazySearchMembresQuery,
  useGetMembresSuivisQuery,
  useToggleSuivreMembreMutation,
  useGetConversationsQuery,
  useOpenConversationMutation,
  useGetConversationQuery,
  useGetMessagesQuery,
  useSendMessageMutation,
  useGetPublicationsInfiniteQuery,
  useGetPublicationQuery,
  useUploadForumImageMutation,
  useUploadForumMediaMutation,
  useGetEspacesInfiniteQuery,
  useGetEspaceQuery,
  useCreateEspaceMutation,
  useUpdateEspaceMutation,
  useRejoindreEspaceMutation,
  useQuitterEspaceMutation,
  useGetEspaceMessagesQuery,
  useSendEspaceMessageMutation,
  useDeleteEspaceMessageMutation,
  useReactEspaceMessageMutation,
  useGetEspaceLiensQuery,
  useCreateEspaceLienMutation,
  useRevoquerEspaceLienMutation,
  useGetEspaceMembresQuery,
  useSetEspaceMembreRoleMutation,
  useExclureEspaceMembreMutation,
  usePreviewInvitationQuery,
  useRejoindreViaInvitationMutation,
  useCreateDiscussionMutation,
  useCreateApplicationMutation,
  useCreateEntraideMutation,
  useCreateChoixMutation,
  useGetPublicationAvisQuery,
  useUpsertPublicationAvisMutation,
  useDecideChoixMutation,
  useAcceptTechnicalReplyMutation,
  useTogglePublicationLikeMutation,
  useTogglePublicationFavoriMutation,
  useGetPublicationCommentsQuery,
  useLazyGetPublicationCommentsQuery,
  useCreatePublicationCommentMutation,
  useToggleCommentLikeMutation,
  useToggleConfirmationAideMutation,
} = forumApi;
