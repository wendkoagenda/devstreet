import { createApi } from "@reduxjs/toolkit/query/react";
import { authBaseQuery } from "@/helpers/api/base-query";
import {
  LoginResponse,
  LoginSchema,
  RegisterSchema,
  ChangePasswordSchema,
  ChangePasswordResponse,
  ForgotPasswordRequest,
  ForgotPasswordResponse,
  VerifyResetCodeRequest,
  VerifyResetCodeResponse,
  ConfirmPasswordResetRequest,
  ConfirmPasswordResetResponse,
  User,
} from "./schema";

export type PublicProfile = {
  id: number;
  username: string;
  full_name: string;
  photo?: string;
  banner?: string;
};

export const authApi = createApi({
  reducerPath: "authApi",
  baseQuery: authBaseQuery,
  tagTypes: ["PublicProfile"],
  endpoints: (builder) => ({
    login: builder.mutation<LoginResponse, LoginSchema>({
      query: (loginData) => ({
        url: "/auth/login",
        method: "POST",
        body: loginData,
      }),
    }),
    register: builder.mutation<LoginResponse, RegisterSchema>({
      query: (registerData) => ({
        url: "/auth/register",
        method: "POST",
        body: registerData,
      }),
    }),
    getPublicProfile: builder.query<PublicProfile, number>({
      query: (userId) => `/auth/public-profile/${userId}`,
      providesTags: (_result, _error, userId) => [
        { type: "PublicProfile", id: userId },
      ],
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
    uploadProfilePhoto: builder.mutation<User, File>({
      query: (file) => {
        const formData = new FormData();
        const safeName = file.name.replace(/[^\w.-]+/g, "-").toLowerCase();
        const stamp = Date.now();
        formData.append("photo", file);
        formData.append("photo_path", `profile_photos/${stamp}-${safeName}`);
        return {
          url: "/auth/profile/photo",
          method: "POST",
          body: formData,
        };
      },
    }),
    deleteProfilePhoto: builder.mutation<User, void>({
      query: () => ({
        url: "/auth/profile/photo",
        method: "DELETE",
      }),
    }),
    uploadProfileBanner: builder.mutation<User, File>({
      query: (file) => {
        const formData = new FormData();
        const safeName = file.name.replace(/[^\w.-]+/g, "-").toLowerCase();
        const stamp = Date.now();
        formData.append("banner", file);
        formData.append("banner_path", `profile_banners/${stamp}-${safeName}`);
        return {
          url: "/auth/profile/banner",
          method: "POST",
          body: formData,
        };
      },
    }),
    /** Profil complet du membre connecté, relu à la demande (prénom, nom, e-mail…). */
    getMyProfile: builder.query<User, void>({
      query: () => "/auth/profile",
    }),
    /** Prénom, nom et nom d'utilisateur du membre connecté. */
    updateMyProfile: builder.mutation<
      User,
      { first_name: string; last_name: string; username: string }
    >({
      query: (body) => ({
        url: "/auth/profile",
        method: "PATCH",
        body,
      }),
    }),
    deleteProfileBanner: builder.mutation<User, void>({
      query: () => ({
        url: "/auth/profile/banner",
        method: "DELETE",
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
  useRegisterMutation,
  useGetPublicProfileQuery,
  useChangePasswordMutation,
  useUploadProfilePhotoMutation,
  useDeleteProfilePhotoMutation,
  useUploadProfileBannerMutation,
  useDeleteProfileBannerMutation,
  useUpdateMyProfileMutation,
  useGetMyProfileQuery,
  useForgotPasswordMutation,
  useVerifyResetCodeMutation,
  useConfirmPasswordResetMutation,
} = authApi;
