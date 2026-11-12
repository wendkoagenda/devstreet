import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQuery } from "@/helpers/api/base-query";
import {
  toQueryString,
  type ListParams,
  type Paginated,
} from "@/helpers/api/pagination";
import type {
  CreateOfferSchema,
  GetOfferSchema,
  UpdateOfferSchema,
} from "./schema";

export type CreateOfferMutationArg = CreateOfferSchema;
export type UpdateOfferMutationArg = UpdateOfferSchema;

export const offerApi = createApi({
  reducerPath: "offerApi",
  baseQuery,
  tagTypes: ["Offers"],
  endpoints: (builder) => ({
    createOffer: builder.mutation<void, CreateOfferMutationArg>({
      query: (payload) => {
        return {
          url: "/offers",
          method: "POST",
          body: payload,
        };
      },
      invalidatesTags: ["Offers"],
    }),
    getOffers: builder.query<Paginated<GetOfferSchema>, ListParams | void>({
      query: (params) => `/offers${toQueryString(params)}`,
      providesTags: ["Offers"],
    }),
    getOffer: builder.query<GetOfferSchema, number>({
      query: (id) => `/offers/${id}`,
      providesTags: ["Offers"],
    }),
    updateOffer: builder.mutation<void, UpdateOfferMutationArg>({
      query: (payload) => {
        return {
          url: `/offers/${payload.id}`,
          method: "PUT",
          body: payload,
        };
      },
      invalidatesTags: ["Offers"],
    }),
    deleteOffer: builder.mutation<void, number>({
      query: (id) => ({
        url: `/offers/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Offers"],
    }),
  }),
});

export const {
  useCreateOfferMutation,
  useGetOffersQuery,
  useGetOfferQuery,
  useUpdateOfferMutation,
  useDeleteOfferMutation,
} = offerApi;