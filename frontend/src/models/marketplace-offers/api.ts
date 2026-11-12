import { marketplaceSpaceApi } from "@/models/marketplace-space/api";
import type {
  Candidature,
  CandidatureStatus,
  MySkill,
  Offer,
  OfferFilters,
  SkillOption,
  TalentCard,
} from "./schema";

const toQuery = (params?: OfferFilters | void): string => {
  const query = new URLSearchParams();
  Object.entries(params ?? {}).forEach(([key, value]) => {
    if (value) query.set(key, value);
  });
  const text = query.toString();
  return text ? `?${text}` : "";
};

/** Offres, candidatures et compétences : endpoints injectés dans l'API « espace marketplace » (un seul reducer). */
export const marketplaceOffersApi = marketplaceSpaceApi.injectEndpoints({
  endpoints: (builder) => ({
    getSkillOptions: builder.query<SkillOption[], void>({
      query: () => "/marketplace/skills",
    }),
    getMySkills: builder.query<MySkill[], void>({
      query: () => "/marketplace/me/skills",
      providesTags: ["MySkills"],
    }),
    setMySkills: builder.mutation<
      MySkill[],
      { skill_id: number; level: number; years: number }[]
    >({
      query: (skills) => ({
        url: "/marketplace/me/skills",
        method: "PUT",
        body: { skills },
      }),
      invalidatesTags: ["MySkills", "Offers"],
    }),

    getOffers: builder.query<Offer[], OfferFilters | void>({
      query: (filters) => `/marketplace/offers${toQuery(filters)}`,
      providesTags: ["Offers"],
    }),
    getOffer: builder.query<Offer, number>({
      query: (id) => `/marketplace/offers/${id}`,
      providesTags: (_result, _error, id) => [{ type: "Offers", id }],
    }),
    applyToOffer: builder.mutation<Candidature, { id: number; message: string }>({
      query: ({ id, message }) => ({
        url: `/marketplace/offers/${id}/apply`,
        method: "POST",
        body: { message },
      }),
      invalidatesTags: ["Offers", "MyCandidatures"],
    }),
    getMyCandidatures: builder.query<Candidature[], void>({
      query: () => "/marketplace/me/candidatures",
      providesTags: ["MyCandidatures"],
    }),

    getMyOffers: builder.query<Offer[], void>({
      query: () => "/marketplace/me/offers",
      providesTags: ["MyOffers"],
    }),
    getMyOffer: builder.query<Offer, number>({
      query: (id) => `/marketplace/me/offers/${id}`,
      providesTags: (_result, _error, id) => [{ type: "MyOffers", id }],
    }),
    createMyOffer: builder.mutation<Offer, Record<string, unknown>>({
      query: (body) => ({ url: "/marketplace/me/offers", method: "POST", body }),
      invalidatesTags: ["MyOffers", "Offers"],
    }),
    updateMyOffer: builder.mutation<Offer, { id: number } & Record<string, unknown>>({
      query: ({ id, ...body }) => ({
        url: `/marketplace/me/offers/${id}`,
        method: "PATCH",
        body,
      }),
      invalidatesTags: ["MyOffers", "Offers"],
    }),
    getOfferCandidatures: builder.query<Candidature[], number>({
      query: (id) => `/marketplace/me/offers/${id}/candidatures`,
      providesTags: ["OfferCandidatures"],
    }),
    getRecommendedProfils: builder.query<TalentCard[], number>({
      query: (id) => `/marketplace/me/offers/${id}/recommended-profils`,
    }),
    decideCandidature: builder.mutation<
      Candidature,
      { id: number; status: Exclude<CandidatureStatus, "sent"> }
    >({
      query: ({ id, status }) => ({
        url: `/marketplace/candidatures/${id}/decision`,
        method: "POST",
        body: { status },
      }),
      invalidatesTags: ["OfferCandidatures", "MyOffers", "Availabilities"],
    }),
  }),
});

export const {
  useGetSkillOptionsQuery,
  useGetMySkillsQuery,
  useSetMySkillsMutation,
  useGetOffersQuery,
  useGetOfferQuery,
  useApplyToOfferMutation,
  useGetMyCandidaturesQuery,
  useGetMyOffersQuery,
  useGetMyOfferQuery,
  useCreateMyOfferMutation,
  useUpdateMyOfferMutation,
  useGetOfferCandidaturesQuery,
  useGetRecommendedProfilsQuery,
  useDecideCandidatureMutation,
} = marketplaceOffersApi;
