import { marketplaceSpaceApi } from "@/models/marketplace-space/api";
import type {
  ConnectionEntry,
  DeckCard,
  PoolEntry,
  PublicProfile,
  SwipeContext,
  SwipeDirection,
  SwipeResult,
} from "./schema";

/** Découverte de profils, vivier, connexions et fiche publique : endpoints injectés dans l'API « espace marketplace ». */
export const marketplaceNetworkApi = marketplaceSpaceApi.injectEndpoints({
  endpoints: (builder) => ({
    getDeck: builder.query<DeckCard[], SwipeContext>({
      query: (context) => `/marketplace/me/deck?context=${context}`,
    }),
    swipe: builder.mutation<
      SwipeResult,
      { target_id: number; direction: SwipeDirection; context: SwipeContext }
    >({
      query: (body) => ({ url: "/marketplace/me/swipes", method: "POST", body }),
      // Le paquet affiché n'est pas relu à chaque choix (il avance localement) ; le vivier et les connexions, si.
      invalidatesTags: ["Pool", "Connections"],
    }),
    undoSwipe: builder.mutation<{ undone: number }, SwipeContext>({
      query: (context) => ({
        url: `/marketplace/me/swipes/last?context=${context}`,
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
    getPublicProfile: builder.query<PublicProfile, number>({
      query: (id) => `/marketplace/profils/${id}`,
      // l'aperçu de mon propre profil / CV suit mes modifications
      providesTags: ["MySpace", "MySkills", "Experiences"],
    }),
  }),
});

export const {
  useGetDeckQuery,
  useSwipeMutation,
  useUndoSwipeMutation,
  useGetPoolQuery,
  useGetConnectionsQuery,
  useGetPublicProfileQuery,
} = marketplaceNetworkApi;
