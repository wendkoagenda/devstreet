import { authApi } from "@/models/auth/api";

export type CountryCities = {
  country: string;
  cities: string[];
  /** Faux si aucune liste n'est disponible : le champ ville passe en saisie libre. */
  available: boolean;
};

/** Villes d'un pays, servies (et mises en cache) par le serveur. */
export const geoApi = authApi.injectEndpoints({
  endpoints: (builder) => ({
    getCountryCities: builder.query<CountryCities, string>({
      query: (countryCode) => `/v1/geo/countries/${encodeURIComponent(countryCode.toUpperCase())}/cities`,
      // Les villes ne changent pas pendant une session : la liste reste en cache une heure
      keepUnusedDataFor: 3600,
    }),
  }),
});

export const { useGetCountryCitiesQuery } = geoApi;
