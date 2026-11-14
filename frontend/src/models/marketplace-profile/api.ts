import { marketplaceSpaceApi } from "@/models/marketplace-space/api";
import type { Availability, Experience, PendingReview, Prestation } from "./schema";

/** Calendrier, expériences et prestations du profil connecté (endpoints injectés dans l'API « espace marketplace »). */
export const marketplaceProfileApi = marketplaceSpaceApi.injectEndpoints({
  endpoints: (builder) => ({
    getMyAvailabilities: builder.query<Availability[], void>({
      query: () => "/marketplace/me/availabilities",
      providesTags: ["Availabilities"],
    }),
    createAvailability: builder.mutation<Availability, Record<string, unknown>>({
      query: (body) => ({ url: "/marketplace/me/availabilities", method: "POST", body }),
      invalidatesTags: ["Availabilities", "Offers"],
    }),
    updateAvailability: builder.mutation<Availability, { id: number } & Record<string, unknown>>({
      query: ({ id, ...body }) => ({
        url: `/marketplace/me/availabilities/${id}`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: ["Availabilities", "Offers"],
    }),
    deleteAvailability: builder.mutation<void, number>({
      query: (id) => ({ url: `/marketplace/me/availabilities/${id}`, method: "DELETE" }),
      invalidatesTags: ["Availabilities", "Offers"],
    }),

    getMyExperiences: builder.query<Experience[], void>({
      query: () => "/marketplace/me/experiences",
      providesTags: ["Experiences"],
    }),
    createExperience: builder.mutation<Experience, Record<string, unknown>>({
      query: (body) => ({ url: "/marketplace/me/experiences", method: "POST", body }),
      invalidatesTags: ["Experiences"],
    }),
    updateExperience: builder.mutation<Experience, { id: number } & Record<string, unknown>>({
      query: ({ id, ...body }) => ({
        url: `/marketplace/me/experiences/${id}`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: ["Experiences"],
    }),
    deleteExperience: builder.mutation<void, number>({
      query: (id) => ({ url: `/marketplace/me/experiences/${id}`, method: "DELETE" }),
      invalidatesTags: ["Experiences"],
    }),

    getMyPrestations: builder.query<Prestation[], void>({
      query: () => "/marketplace/me/prestations",
      providesTags: ["Prestations"],
    }),
    createPrestation: builder.mutation<Prestation, Record<string, unknown>>({
      query: (body) => ({ url: "/marketplace/me/prestations", method: "POST", body }),
      invalidatesTags: ["Prestations"],
    }),
    updatePrestation: builder.mutation<Prestation, { id: number } & Record<string, unknown>>({
      query: ({ id, ...body }) => ({
        url: `/marketplace/me/prestations/${id}`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: ["Prestations"],
    }),
    deletePrestation: builder.mutation<void, number>({
      query: (id) => ({ url: `/marketplace/me/prestations/${id}`, method: "DELETE" }),
      invalidatesTags: ["Prestations"],
    }),

    getPendingReviews: builder.query<PendingReview[], void>({
      query: () => "/marketplace/me/reviews/pending",
      providesTags: ["PendingReviews"],
    }),
    createReview: builder.mutation<
      Record<string, unknown>,
      { candidature_id: number; rating: number; comment: string; is_public: boolean }
    >({
      query: (body) => ({ url: "/marketplace/me/reviews", method: "POST", body }),
      invalidatesTags: ["PendingReviews", "MyReviews"],
    }),
  }),
});

export const {
  useGetMyAvailabilitiesQuery,
  useCreateAvailabilityMutation,
  useUpdateAvailabilityMutation,
  useDeleteAvailabilityMutation,
  useGetMyExperiencesQuery,
  useCreateExperienceMutation,
  useUpdateExperienceMutation,
  useDeleteExperienceMutation,
  useGetMyPrestationsQuery,
  useCreatePrestationMutation,
  useUpdatePrestationMutation,
  useDeletePrestationMutation,
  useGetPendingReviewsQuery,
  useCreateReviewMutation,
} = marketplaceProfileApi;
