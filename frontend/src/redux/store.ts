import { gadoApi } from "@/models/gado/api";
import { fusionApi } from "@/models/fusion/api";
import { dragonApi } from "@/models/dragon/api";
import { elitestyApi } from "@/models/elitesty/api";
import { elitestApi } from "@/models/elitest/api";
import { configureStore } from "@reduxjs/toolkit";
import { userApi } from "@/models/user/api";
import { authApi } from "@/models/auth/api";
import { rolePermissionApi } from "@/models/roles-permissions/Api";

export const store = configureStore({
  reducer: {
    [userApi.reducerPath]: userApi.reducer,
    [rolePermissionApi.reducerPath]: rolePermissionApi.reducer,
    [authApi.reducerPath]: authApi.reducer,
    [elitestApi.reducerPath]: elitestApi.reducer,
    [elitestyApi.reducerPath]: elitestyApi.reducer,
    [dragonApi.reducerPath]: dragonApi.reducer,
    [fusionApi.reducerPath]: fusionApi.reducer,
    [gadoApi.reducerPath]: gadoApi.reducer,
  
  
  
  
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(
      userApi.middleware,
      rolePermissionApi.middleware,
      authApi.middleware,
      elitestApi.middleware,
      elitestyApi.middleware,
      dragonApi.middleware,
      fusionApi.middleware,
      gadoApi.middleware,
    ),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
