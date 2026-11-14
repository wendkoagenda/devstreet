import { useAuth } from "@/models/auth/hooks/useAuth";
import { Navigate, Outlet } from "react-router-dom";

const PrivateRoutes = () => {
  const { isAuthenticated, isInitialized } = useAuth();

  if (!isInitialized) {
    return null;
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/welcome" replace />;
};

export default PrivateRoutes;
