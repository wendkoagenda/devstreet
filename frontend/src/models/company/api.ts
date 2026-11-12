import { createApi } from "@reduxjs/toolkit/query/react";
import { baseQuery } from "@/helpers/api/base-query";
import {
  toQueryString,
  type ListParams,
  type Paginated,
} from "@/helpers/api/pagination";
import {
  buildModelFormData,
  hasFilePayload,
} from "@/helpers/api/form-data-builder";
import type {
  CreateCompanySchema,
  GetCompanySchema,
  UpdateCompanySchema,
} from "./schema";

const FILE_FIELDS = [{"name": "logo", "uploadFolder": "companies/logo"}] as const;

export type CreateCompanyMutationArg = CreateCompanySchema & {
  _files?: Record<string, File | undefined>;
};

export type UpdateCompanyMutationArg = UpdateCompanySchema & {
  _files?: Record<string, File | undefined>;
};

export const companyApi = createApi({
  reducerPath: "companyApi",
  baseQuery,
  tagTypes: ["Companies"],
  endpoints: (builder) => ({
    createCompany: builder.mutation<void, CreateCompanyMutationArg>({
      query: (payload) => {
        const { _files, ...body } = payload;
        if (hasFilePayload([...FILE_FIELDS], _files)) {
          return {
            url: "/companies",
            method: "POST",
            body: buildModelFormData(body, {
              fileFields: [...FILE_FIELDS],
              fileValues: _files,
            }),
          };
        }
        return {
          url: "/companies",
          method: "POST",
          body,
        };
      },
      invalidatesTags: ["Companies"],
    }),
    getCompanies: builder.query<Paginated<GetCompanySchema>, ListParams | void>({
      query: (params) => `/companies${toQueryString(params)}`,
      providesTags: ["Companies"],
    }),
    getCompany: builder.query<GetCompanySchema, number>({
      query: (id) => `/companies/${id}`,
      providesTags: ["Companies"],
    }),
    updateCompany: builder.mutation<void, UpdateCompanyMutationArg>({
      query: (payload) => {
        const { _files, ...body } = payload;
        if (hasFilePayload([...FILE_FIELDS], _files)) {
          return {
            url: `/companies/${payload.id}`,
            method: "PUT",
            body: buildModelFormData(body, {
              fileFields: [...FILE_FIELDS],
              fileValues: _files,
            }),
          };
        }
        return {
          url: `/companies/${payload.id}`,
          method: "PUT",
          body,
        };
      },
      invalidatesTags: ["Companies"],
    }),
    deleteCompany: builder.mutation<void, number>({
      query: (id) => ({
        url: `/companies/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Companies"],
    }),
  }),
});

export const {
  useCreateCompanyMutation,
  useGetCompaniesQuery,
  useGetCompanyQuery,
  useUpdateCompanyMutation,
  useDeleteCompanyMutation,
} = companyApi;