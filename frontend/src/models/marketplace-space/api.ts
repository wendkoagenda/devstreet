import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQuery } from "@/helpers/api/base-query";
import type { EntrepriseInvitation, InvitationDetail, MySpace } from "./schema";

/** Profil et entreprise de l'utilisateur connecté (aucune permission RBAC : chacun gère ses propres données). */
export const marketplaceSpaceApi = createApi({
  reducerPath: "marketplaceSpaceApi",
  baseQuery,
  tagTypes: [
    "MySpace",
    "MySkills",
    "Offers",
    "MyOffers",
    "MyCandidatures",
    "OfferCandidatures",
    "Deck",
    "Pool",
    "Connections",
    "Availabilities",
    "Experiences",
    "Invitations",
    "Prestations",
    "PendingReviews",
    "MyReviews",
    "CvSettings",
  ],
  endpoints: (builder) => ({
    getMySpace: builder.query<MySpace, void>({
      query: () => "/marketplace/me",
      providesTags: ["MySpace"],
    }),
    createMyProfil: builder.mutation<MySpace, Record<string, unknown>>({
      query: (body) => ({
        url: "/marketplace/me/profil",
        method: "POST",
        body,
      }),
      invalidatesTags: ["MySpace"],
    }),
    updateMyProfil: builder.mutation<MySpace, Record<string, unknown>>({
      query: (body) => ({
        url: "/marketplace/me/profil",
        method: "PATCH",
        body,
      }),
      invalidatesTags: ["MySpace"],
    }),
    createMyCompany: builder.mutation<MySpace, Record<string, unknown>>({
      query: (body) => ({
        url: "/marketplace/me/company",
        method: "POST",
        body,
      }),
      invalidatesTags: ["MySpace"],
    }),
    updateMyCompany: builder.mutation<MySpace, Record<string, unknown>>({
      query: (body) => ({
        url: "/marketplace/me/company",
        method: "PATCH",
        body,
      }),
      invalidatesTags: ["MySpace"],
    }),
    getMyInvitations: builder.query<EntrepriseInvitation[], void>({
      query: () => "/marketplace/me/invitations",
      providesTags: ["Invitations"],
    }),
    createInvitation: builder.mutation<EntrepriseInvitation, { email?: string }>({
      query: (body) => ({
        url: "/marketplace/me/invitations",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Invitations"],
    }),
    revokeInvitation: builder.mutation<EntrepriseInvitation, number>({
      query: (id) => ({
        url: `/marketplace/me/invitations/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Invitations"],
    }),
    getInvitation: builder.query<InvitationDetail, string>({
      query: (token) => `/marketplace/invitations/${encodeURIComponent(token)}`,
    }),
    acceptInvitation: builder.mutation<{ company: { id: number; name: string } }, string>({
      query: (token) => ({
        url: `/marketplace/invitations/${encodeURIComponent(token)}/accept`,
        method: "POST",
      }),
      invalidatesTags: ["MySpace", "Invitations"],
    }),
  }),
});

export const {
  useGetMySpaceQuery,
  useCreateMyProfilMutation,
  useUpdateMyProfilMutation,
  useCreateMyCompanyMutation,
  useUpdateMyCompanyMutation,
  useGetMyInvitationsQuery,
  useCreateInvitationMutation,
  useRevokeInvitationMutation,
  useGetInvitationQuery,
  useAcceptInvitationMutation,
} = marketplaceSpaceApi;
