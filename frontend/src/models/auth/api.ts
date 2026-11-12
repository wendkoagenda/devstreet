import { createApi } from "@reduxjs/toolkit/query/react";
import { authBaseQuery } from "@/helpers/api/base-query";
import {
  LoginResponse,
  LoginSchema,
  ChangePasswordSchema,
  ChangePasswordResponse,
  ForgotPasswordRequest,
  ForgotPasswordResponse,
  VerifyResetCodeRequest,
  VerifyResetCodeResponse,
  ConfirmPasswordResetRequest,
  ConfirmPasswordResetResponse,
} from "./schema";

export const authApi = createApi({
  reducerPath: "authApi",
  baseQuery: authBaseQuery,
  endpoints: (builder) => ({
    login: builder.mutation<LoginResponse, LoginSchema>({
      query: (loginData) => ({
        url: "/auth/login",
        method: "POST",
        body: loginData,
      }),
    }),
    changePassword: builder.mutation<
      ChangePasswordResponse,
      ChangePasswordSchema
    >({
      query: (passwordData) => ({
        url: "/auth/change-password",
        method: "POST",
        body: passwordData,
      }),
    }),
    // Mot de passe oublié (routes publiques) : étape 1, 2 et 3
    forgotPassword: builder.mutation<ForgotPasswordResponse, ForgotPasswordRequest>({
      query: (data) => ({
        url: "/auth/forgot-password",
        method: "POST",
        body: data,
      }),
    }),
    verifyResetCode: builder.mutation<VerifyResetCodeResponse, VerifyResetCodeRequest>({
      query: (data) => ({
        url: "/auth/verify-reset-code",
        method: "POST",
        body: data,
      }),
    }),
    confirmPasswordReset: builder.mutation<
      ConfirmPasswordResetResponse,
      ConfirmPasswordResetRequest
    >({
      query: (data) => ({
        url: "/auth/reset-password",
        method: "POST",
        body: data,
      }),
    }),
  }),
});

export const {
  useLoginMutation,
  useChangePasswordMutation,
  useForgotPasswordMutation,
  useVerifyResetCodeMutation,
  useConfirmPasswordResetMutation,
} = authApi;
