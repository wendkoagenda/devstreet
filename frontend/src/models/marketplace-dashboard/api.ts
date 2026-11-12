import { marketplaceSpaceApi } from "@/models/marketplace-space/api";
import type { Dashboard } from "./schema";

/** Tableau de bord : se rafraîchit dès que les données dont il dépend changent (profil, candidatures, offres, calendrier…). */
export const marketplaceDashboardApi = marketplaceSpaceApi.injectEndpoints({
  endpoints: (builder) => ({
    getDashboard: builder.query<Dashboard, void>({
      query: () => "/marketplace/me/dashboard",
      providesTags: [
        "MySpace",
        "MySkills",
        "Experiences",
        "MyCandidatures",
        "MyOffers",
        "OfferCandidatures",
        "Availabilities",
        "Pool",
        "Connections",
        "Offers",
      ],
    }),
  }),
});

export const { useGetDashboardQuery } = marketplaceDashboardApi;
