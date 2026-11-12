import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQuery } from "@/helpers/api/base-query";
import {
  toQueryString,
  type ListParams,
  type Paginated,
} from "@/helpers/api/pagination";
import type {
  CreateAvailabilitySchema,
  GetAvailabilitySchema,
  UpdateAvailabilitySchema,
} from "./schema";

export type CreateAvailabilityMutationArg = CreateAvailabilitySchema;
export type UpdateAvailabilityMutationArg = UpdateAvailabilitySchema;

export const availabilityApi = createApi({
  reducerPath: "availabilityApi",
  baseQuery,
  tagTypes: ["Availabilities"],
  endpoints: (builder) => ({
    createAvailability: builder.mutation<void, CreateAvailabilityMutationArg>({
      query: (payload) => {
        return {
          url: "/availabilities",
          method: "POST",
          body: payload,
        };
      },
      invalidatesTags: ["Availabilities"],
    }),
    getAvailabilities: builder.query<Paginated<GetAvailabilitySchema>, ListParams | void>({
      query: (params) => `/availabilities${toQueryString(params)}`,
      providesTags: ["Availabilities"],
    }),
    getAvailability: builder.query<GetAvailabilitySchema, number>({
      query: (id) => `/availabilities/${id}`,
      providesTags: ["Availabilities"],
    }),
    updateAvailability: builder.mutation<void, UpdateAvailabilityMutationArg>({
      query: (payload) => {
        return {
          url: `/availabilities/${payload.id}`,
          method: "PUT",
          body: payload,
        };
      },
      invalidatesTags: ["Availabilities"],
    }),
    deleteAvailability: builder.mutation<void, number>({
      query: (id) => ({
        url: `/availabilities/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Availabilities"],
    }),
  }),
});

export const {
  useCreateAvailabilityMutation,
  useGetAvailabilitiesQuery,
  useGetAvailabilityQuery,
  useUpdateAvailabilityMutation,
  useDeleteAvailabilityMutation,
} = availabilityApi;