import GadoList from "./models/gado/pages/gado-list";
import FusionList from "./models/fusion/pages/fusion-list";
import DragonList from "./models/dragon/pages/dragon-list";
import ElitestyList from "./models/elitesty/pages/elitesty-list";
import ElitestList from "./models/elitest/pages/elitest-list";
import { Route, Routes } from "react-router-dom";
import PrivateRoute from "./components/layouts/private-route";
import PublicRoute from "./components/layouts/public-route";
import LoginPage from "./models/auth/pages/login-page";
import ForgotPasswordPage from "./models/auth/pages/forgot-password-page";
import HomePage from "./models/common/home-page";
import AppLayout from "./components/layouts/app-layout";
import UsersList from "./models/user/pages/users-list";
import MyAccount from "./models/auth/pages/my-account";
import RolePermissionManagement from "./models/roles-permissions/pages/role-permissions-page";
import { useAuthSlice } from "./models/auth/slice";
import { useEffect } from "react";

function App() {
  const initializeAuth = useAuthSlice((state) => state.initializeAuth);

  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  return (
    <>
      <Routes>
        {/* Routes necessitant l'authentification */}
        <Route element={<PrivateRoute />}>
          <Route element={<AppLayout />}>
            <Route element={<HomePage />} path="/" />

            <Route element={<UsersList />} path="/users" />

            <Route element={<RolePermissionManagement />} path="/roles" />

            <Route element={<ElitestList />} path="/elitests" />

                      <Route element={<ElitestyList />} path="/elitesties" />

          <Route element={<DragonList />} path="/dragons" />

          <Route element={<FusionList />} path="/fusions" />

          <Route element={<GadoList />} path="/gados" />

<Route element={<MyAccount />} path="/my-account" />
          </Route>
        </Route>

        {/* Routes publiques */}
        <Route element={<PublicRoute />}>
          <Route element={<LoginPage />} path="/login" />
          <Route element={<ForgotPasswordPage />} path="/forgot-password" />
        </Route>
      </Routes>
    </>
  );
}

export default App;
