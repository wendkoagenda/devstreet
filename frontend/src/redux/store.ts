import { marketplaceSpaceApi } from "@/models/marketplace-space/api";
import { connectionApi } from "@/models/connection/api";
import { swipeApi } from "@/models/swipe/api";
import { reviewApi } from "@/models/review/api";
import { availabilityApi } from "@/models/availability/api";
import { profilHistoryApi } from "@/models/profil-history/api";
import { prestationApi } from "@/models/prestation/api";
import { experienceApi } from "@/models/experience/api";
import { profilSkillApi } from "@/models/profil-skill/api";
import { candidatureApi } from "@/models/candidature/api";
import { offerApi } from "@/models/offer/api";
import { profilApi } from "@/models/profil/api";
import { skillApi } from "@/models/skill/api";
import { companyApi } from "@/models/company/api";
import { configureStore } from "@reduxjs/toolkit";
import { userApi } from "@/models/user/api";
import { authApi } from "@/models/auth/api";
import { rolePermissionApi } from "@/models/roles-permissions/Api";
import { devstreetHubApi } from "@/models/devstreet-hub/api";

export const store = configureStore({
  reducer: {
    [userApi.reducerPath]: userApi.reducer,
    [rolePermissionApi.reducerPath]: rolePermissionApi.reducer,
    [authApi.reducerPath]: authApi.reducer,
    [devstreetHubApi.reducerPath]: devstreetHubApi.reducer,
    [companyApi.reducerPath]: companyApi.reducer,
    [skillApi.reducerPath]: skillApi.reducer,
    [profilApi.reducerPath]: profilApi.reducer,
    [offerApi.reducerPath]: offerApi.reducer,
    [candidatureApi.reducerPath]: candidatureApi.reducer,
    [profilSkillApi.reducerPath]: profilSkillApi.reducer,
    [experienceApi.reducerPath]: experienceApi.reducer,
    [prestationApi.reducerPath]: prestationApi.reducer,
    [profilHistoryApi.reducerPath]: profilHistoryApi.reducer,
    [availabilityApi.reducerPath]: availabilityApi.reducer,
    [reviewApi.reducerPath]: reviewApi.reducer,
    [swipeApi.reducerPath]: swipeApi.reducer,
    [connectionApi.reducerPath]: connectionApi.reducer,
    [marketplaceSpaceApi.reducerPath]: marketplaceSpaceApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(
      userApi.middleware,
      rolePermissionApi.middleware,
      authApi.middleware,
      devstreetHubApi.middleware,
      companyApi.middleware,
      skillApi.middleware,
      profilApi.middleware,
      offerApi.middleware,
      candidatureApi.middleware,
      profilSkillApi.middleware,
      experienceApi.middleware,
      prestationApi.middleware,
      profilHistoryApi.middleware,
      availabilityApi.middleware,
      reviewApi.middleware,
      swipeApi.middleware,
      connectionApi.middleware,
      marketplaceSpaceApi.middleware,
    ),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
