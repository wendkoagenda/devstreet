import { authApi } from "@/models/auth/api";
import type { AccountType, User } from "@/models/auth/schema";

export type ChoosableAccountType = Exclude<AccountType, "">;

export type SetAccountTypeResponse = {
  user: User;
  permissions: string[];
};

/** Choix du type de compte à l'onboarding, ou ajout du type manquant plus tard (un type n'est jamais retiré). */
export const onboardingApi = authApi.injectEndpoints({
  endpoints: (builder) => ({
    setAccountType: builder.mutation<SetAccountTypeResponse, ChoosableAccountType>({
      query: (accountType) => ({
        url: "/auth/account-type",
        method: "POST",
        body: { account_type: accountType },
      }),
    }),
  }),
});

export const { useSetAccountTypeMutation } = onboardingApi;
