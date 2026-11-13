import { useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import AuthSplitScreen from "../components/auth-split-screen";

export default function LoginPage() {
  const [params] = useSearchParams();
  const initialMode = useMemo(
    () => (params.get("mode") === "register" ? "register" : "login"),
    [params]
  );
  return <AuthSplitScreen initialMode={initialMode} />;
}
