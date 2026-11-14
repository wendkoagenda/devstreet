import { marketplaceSpaceApi } from "@/models/marketplace-space/api";
import type { StatsByScope, StatsScope } from "./schema";

/**
 * Petites statistiques des pages de la marketplace. Elles se rafraîchissent dès que les données dont elles
 * dépendent changent (profil, candidatures, offres, calendrier, vivier, connexions…).
 */
const marketplaceStatsApi = marketplaceSpaceApi.injectEndpoints({
  endpoints: (builder) => ({
    getStats: builder.query<unknown, StatsScope>({
      query: (scope) => `/marketplace/me/stats?scope=${scope}`,
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

/** Statistiques d'une page, typées selon le `scope` demandé. */
export function useStats<S extends StatsScope>(scope: S, options?: { skip?: boolean }) {
  const result = marketplaceStatsApi.useGetStatsQuery(scope, options);
  return { ...result, data: result.data as StatsByScope[S] | undefined };
}
