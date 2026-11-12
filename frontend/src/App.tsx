import ConnectionList from "./models/connection/pages/connection-list";
import SwipeList from "./models/swipe/pages/swipe-list";
import ReviewList from "./models/review/pages/review-list";
import AvailabilityList from "./models/availability/pages/availability-list";
import ProfilHistoryList from "./models/profil-history/pages/profil-history-list";
import PrestationList from "./models/prestation/pages/prestation-list";
import ExperienceList from "./models/experience/pages/experience-list";
import ProfilSkillList from "./models/profil-skill/pages/profil-skill-list";
import CandidatureList from "./models/candidature/pages/candidature-list";
import OfferList from "./models/offer/pages/offer-list";
import ProfilList from "./models/profil/pages/profil-list";
import SkillList from "./models/skill/pages/skill-list";
import CompanyList from "./models/company/pages/company-list";
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
import MyProfilePage from "./models/marketplace-space/pages/my-profile-page";
import MarketplaceAdminPage from "./models/marketplace-space/pages/marketplace-admin-page";
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

          <Route element={<PrivateRoute />}>
            <Route element={<HomePage />} path="/" />
            <Route element={<UsersList />} path="/users" />
            <Route element={<RolePermissionManagement />} path="/roles" />
                      <Route element={<CompanyList />} path="/admin/marketplace/companies" />

          <Route element={<SkillList />} path="/admin/marketplace/skills" />

          <Route element={<ProfilList />} path="/admin/marketplace/profils" />

          <Route element={<OfferList />} path="/admin/marketplace/offers" />

          <Route element={<CandidatureList />} path="/admin/marketplace/candidatures" />

          <Route element={<ProfilSkillList />} path="/admin/marketplace/profil-skills" />

          <Route element={<ExperienceList />} path="/admin/marketplace/experiences" />

          <Route element={<PrestationList />} path="/admin/marketplace/prestations" />

          <Route element={<ProfilHistoryList />} path="/admin/marketplace/profil-histories" />

          <Route element={<AvailabilityList />} path="/admin/marketplace/availabilities" />

          <Route element={<ReviewList />} path="/admin/marketplace/reviews" />

          <Route element={<SwipeList />} path="/admin/marketplace/swipes" />

          <Route element={<ConnectionList />} path="/admin/marketplace/connections" />

<Route element={<MyProfilePage />} path="/marketplace/profile" />

          <Route
            element={<MarketplaceAdminPage />}
            path="/admin/marketplace"
          />

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
