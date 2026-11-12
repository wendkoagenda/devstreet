import { configureStore } from "@reduxjs/toolkit";
import { userApi } from "@/models/user/api";
import { authApi } from "@/models/auth/api";
import { rolePermissionApi } from "@/models/roles-permissions/Api";
import { devstreetHubApi } from "@/models/devstreet-hub/api";
import { aiApi } from "@/models/ai/api";

export const store = configureStore({
  reducer: {
    [userApi.reducerPath]: userApi.reducer,
    [rolePermissionApi.reducerPath]: rolePermissionApi.reducer,
    [authApi.reducerPath]: authApi.reducer,
    [devstreetHubApi.reducerPath]: devstreetHubApi.reducer,
    [aiApi.reducerPath]: aiApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(
      userApi.middleware,
      rolePermissionApi.middleware,
      authApi.middleware,
      devstreetHubApi.middleware,
      aiApi.middleware
    ),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
