import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQuery } from "@/helpers/api/base-query";
import {
  toQueryString,
  type ListParams,
  type Paginated,
} from "@/helpers/api/pagination";
import type {
  CreateSwipeSchema,
  GetSwipeSchema,
  UpdateSwipeSchema,
} from "./schema";

export type CreateSwipeMutationArg = CreateSwipeSchema;
export type UpdateSwipeMutationArg = UpdateSwipeSchema;

export const swipeApi = createApi({
  reducerPath: "swipeApi",
  baseQuery,
  tagTypes: ["Swipes"],
  endpoints: (builder) => ({
    createSwipe: builder.mutation<void, CreateSwipeMutationArg>({
      query: (payload) => {
        return {
          url: "/swipes",
          method: "POST",
          body: payload,
        };
      },
      invalidatesTags: ["Swipes"],
    }),
    getSwipes: builder.query<Paginated<GetSwipeSchema>, ListParams | void>({
      query: (params) => `/swipes${toQueryString(params)}`,
      providesTags: ["Swipes"],
    }),
    getSwipe: builder.query<GetSwipeSchema, number>({
      query: (id) => `/swipes/${id}`,
      providesTags: ["Swipes"],
    }),
    updateSwipe: builder.mutation<void, UpdateSwipeMutationArg>({
      query: (payload) => {
        return {
          url: `/swipes/${payload.id}`,
          method: "PUT",
          body: payload,
        };
      },
      invalidatesTags: ["Swipes"],
    }),
    deleteSwipe: builder.mutation<void, number>({
      query: (id) => ({
        url: `/swipes/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Swipes"],
    }),
  }),
});

export const {
  useCreateSwipeMutation,
  useGetSwipesQuery,
  useGetSwipeQuery,
  useUpdateSwipeMutation,
  useDeleteSwipeMutation,
} = swipeApi;