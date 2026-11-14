import { marketplaceSpaceApi } from "@/models/marketplace-space/api";
import type { CvSettings, CvSettingsPayload } from "./cv-settings";
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

    // Réglages de style du CV automatique (couleur, police, mise en page…)
    getMyCvSettings: builder.query<CvSettingsPayload, void>({
      query: () => "/marketplace/me/cv-settings",
      providesTags: ["CvSettings"],
    }),
    updateMyCvSettings: builder.mutation<CvSettingsPayload, Partial<CvSettings>>({
      query: (body) => ({ url: "/marketplace/me/cv-settings", method: "PATCH", body }),
      invalidatesTags: ["CvSettings"],
    }),
    resetMyCvSettings: builder.mutation<CvSettingsPayload, void>({
      query: () => ({ url: "/marketplace/me/cv-settings", method: "DELETE" }),
      invalidatesTags: ["CvSettings"],
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
  useGetMyCvSettingsQuery,
  useUpdateMyCvSettingsMutation,
  useResetMyCvSettingsMutation,
} = marketplaceProfileApi;
