import { configureStore } from "@reduxjs/toolkit";
import { userApi } from "@/models/user/api";
import { authApi } from "@/models/auth/api";
import { rolePermissionApi } from "@/models/roles-permissions/Api";

export const store = configureStore({
  reducer: {
    [userApi.reducerPath]: userApi.reducer,
    [rolePermissionApi.reducerPath]: rolePermissionApi.reducer,
    [authApi.reducerPath]: authApi.reducer,

  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(
      userApi.middleware,
      rolePermissionApi.middleware,
      authApi.middleware,
    ),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
