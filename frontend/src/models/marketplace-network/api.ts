import { marketplaceSpaceApi } from "@/models/marketplace-space/api";
import type {
  ConnectionEntry,
  DeckCard,
  NetworkRequests,
  PoolEntry,
  ActingAs,
  PublicProfile,
  SwipeContext,
  SwipeDirection,
  SwipeResult,
  TalentDirectoryCard,
  TalentDirectoryFilters,
} from "./schema";

const talentsQuery = (filters?: TalentDirectoryFilters | void): string => {
  const query = new URLSearchParams();
  Object.entries(filters ?? {}).forEach(([key, value]) => {
    if (value) query.set(key, value);
  });
  const text = query.toString();
  return text ? `?${text}` : "";
};

/** Découverte de profils, vivier, connexions et fiche publique : endpoints injectés dans l'API « espace marketplace ». */
export const marketplaceNetworkApi = marketplaceSpaceApi.injectEndpoints({
  endpoints: (builder) => ({
    getTalents: builder.query<TalentDirectoryCard[], TalentDirectoryFilters | void>({
      query: (filters) => `/marketplace/talents${talentsQuery(filters)}`,
    }),
    getDeck: builder.query<DeckCard[], { context: SwipeContext; acting?: ActingAs }>({
      query: ({ context, acting }) =>
        `/marketplace/me/deck?context=${context}${acting ? `&acting=${acting}` : ""}`,
    }),
    swipe: builder.mutation<
      SwipeResult,
      { target_id: number; direction: SwipeDirection; context: SwipeContext; acting?: ActingAs }
    >({
      query: (body) => ({ url: "/marketplace/me/swipes", method: "POST", body }),
      // Le paquet affiché n'est pas relu à chaque choix (il avance localement) ; le vivier et les connexions, si.
      invalidatesTags: ["Pool", "Connections"],
    }),
    undoSwipe: builder.mutation<{ undone: number }, { context: SwipeContext; acting?: ActingAs }>({
      query: ({ context, acting }) => ({
        url: `/marketplace/me/swipes/last?context=${context}${acting ? `&acting=${acting}` : ""}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Pool", "Connections"],
    }),
    getPool: builder.query<PoolEntry[], void>({
      query: () => "/marketplace/me/pool",
      providesTags: ["Pool"],
    }),
    getConnections: builder.query<ConnectionEntry[], void>({
      query: () => "/marketplace/me/connections",
      providesTags: ["Connections"],
    }),
    getNetworkRequests: builder.query<NetworkRequests, void>({
      query: () => "/marketplace/me/network-requests",
      providesTags: ["Connections"],
    }),
    getPublicProfile: builder.query<PublicProfile, number>({
      query: (id) => `/marketplace/profils/${id}`,
      // l'aperçu de mon propre profil / CV suit mes modifications
      providesTags: ["MySpace", "MySkills", "Experiences"],
    }),
  }),
});

export const {
  useGetTalentsQuery,
  useGetDeckQuery,
  useSwipeMutation,
  useUndoSwipeMutation,
  useGetPoolQuery,
  useGetConnectionsQuery,
  useGetNetworkRequestsQuery,
  useGetPublicProfileQuery,
} = marketplaceNetworkApi;
