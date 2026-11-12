import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQuery } from "@/helpers/api/base-query";
import {
  toQueryString,
  type ListParams,
  type Paginated,
} from "@/helpers/api/pagination";
import type {
  CreateConnectionSchema,
  GetConnectionSchema,
  UpdateConnectionSchema,
} from "./schema";

export type CreateConnectionMutationArg = CreateConnectionSchema;
export type UpdateConnectionMutationArg = UpdateConnectionSchema;

export const connectionApi = createApi({
  reducerPath: "connectionApi",
  baseQuery,
  tagTypes: ["Connections"],
  endpoints: (builder) => ({
    createConnection: builder.mutation<void, CreateConnectionMutationArg>({
      query: (payload) => {
        return {
          url: "/connections",
          method: "POST",
          body: payload,
        };
      },
      invalidatesTags: ["Connections"],
    }),
    getConnections: builder.query<Paginated<GetConnectionSchema>, ListParams | void>({
      query: (params) => `/connections${toQueryString(params)}`,
      providesTags: ["Connections"],
    }),
    getConnection: builder.query<GetConnectionSchema, number>({
      query: (id) => `/connections/${id}`,
      providesTags: ["Connections"],
    }),
    updateConnection: builder.mutation<void, UpdateConnectionMutationArg>({
      query: (payload) => {
        return {
          url: `/connections/${payload.id}`,
          method: "PUT",
          body: payload,
        };
      },
      invalidatesTags: ["Connections"],
    }),
    deleteConnection: builder.mutation<void, number>({
      query: (id) => ({
        url: `/connections/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Connections"],
    }),
  }),
});

export const {
  useCreateConnectionMutation,
  useGetConnectionsQuery,
  useGetConnectionQuery,
  useUpdateConnectionMutation,
  useDeleteConnectionMutation,
} = connectionApi;