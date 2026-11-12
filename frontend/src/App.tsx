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
import ExploreProjectsPage from "./models/devstreet-hub/pages/explore-projects-page";
import CreateProjectPage from "./models/devstreet-hub/pages/create-project-page";
import ProjectDetailPage from "./models/devstreet-hub/pages/project-detail-page";
import TaskContributionPage from "./models/devstreet-hub/pages/task-contribution-page";
import ContributionReviewPage from "./models/devstreet-hub/pages/contribution-review-page";
import AiWorkshopPage from "./models/devstreet-hub/pages/ai-workshop-page";
import ProjectProfilePage from "./models/devstreet-hub/pages/project-profile-page";
import GitAuthAuthorizePage from "./models/devstreet-hub/pages/git-auth-authorize-page";
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
        <Route element={<AppLayout />}>
          <Route element={<ExploreProjectsPage />} path="/hub/projects" />
          <Route element={<CreateProjectPage />} path="/hub/projects/new" />
          <Route element={<ProjectDetailPage />} path="/hub/projects/:id" />
          <Route
            element={<TaskContributionPage />}
            path="/hub/projects/:id/tasks/:taskId"
          />
          <Route
            element={<ContributionReviewPage />}
            path="/hub/projects/:id/reviews"
          />
          <Route element={<AiWorkshopPage />} path="/hub/projects/:id/ai" />
          <Route
            element={<ProjectProfilePage />}
            path="/hub/profiles/:userId"
          />
          <Route
            element={<GitAuthAuthorizePage />}
            path="/hub/git-auth/authorize"
          />

          <Route element={<PrivateRoute />}>
            <Route element={<HomePage />} path="/" />
            <Route element={<UsersList />} path="/users" />
            <Route element={<RolePermissionManagement />} path="/roles" />
            <Route element={<MyAccount />} path="/my-account" />
          </Route>
        </Route>

        <Route element={<PublicRoute />}>
          <Route element={<LoginPage />} path="/login" />
          <Route element={<ForgotPasswordPage />} path="/forgot-password" />
        </Route>
      </Routes>
    </>
  );
}

export default App;
