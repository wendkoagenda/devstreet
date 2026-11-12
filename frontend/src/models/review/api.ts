import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQuery } from "@/helpers/api/base-query";
import {
  toQueryString,
  type ListParams,
  type Paginated,
} from "@/helpers/api/pagination";
import type {
  CreateReviewSchema,
  GetReviewSchema,
  UpdateReviewSchema,
} from "./schema";

export type CreateReviewMutationArg = CreateReviewSchema;
export type UpdateReviewMutationArg = UpdateReviewSchema;

export const reviewApi = createApi({
  reducerPath: "reviewApi",
  baseQuery,
  tagTypes: ["Reviews"],
  endpoints: (builder) => ({
    createReview: builder.mutation<void, CreateReviewMutationArg>({
      query: (payload) => {
        return {
          url: "/reviews",
          method: "POST",
          body: payload,
        };
      },
      invalidatesTags: ["Reviews"],
    }),
    getReviews: builder.query<Paginated<GetReviewSchema>, ListParams | void>({
      query: (params) => `/reviews${toQueryString(params)}`,
      providesTags: ["Reviews"],
    }),
    getReview: builder.query<GetReviewSchema, number>({
      query: (id) => `/reviews/${id}`,
      providesTags: ["Reviews"],
    }),
    updateReview: builder.mutation<void, UpdateReviewMutationArg>({
      query: (payload) => {
        return {
          url: `/reviews/${payload.id}`,
          method: "PUT",
          body: payload,
        };
      },
      invalidatesTags: ["Reviews"],
    }),
    deleteReview: builder.mutation<void, number>({
      query: (id) => ({
        url: `/reviews/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Reviews"],
    }),
  }),
});

export const {
  useCreateReviewMutation,
  useGetReviewsQuery,
  useGetReviewQuery,
  useUpdateReviewMutation,
  useDeleteReviewMutation,
} = reviewApi;