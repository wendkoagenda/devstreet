import { marketplaceSpaceApi } from "@/models/marketplace-space/api";
import type { Availability, Experience } from "./schema";

/** Calendrier de disponibilité et expériences du profil connecté (endpoints injectés dans l'API « espace marketplace »). */
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
} = marketplaceProfileApi;
