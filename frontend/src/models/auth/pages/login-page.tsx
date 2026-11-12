import { useTranslation } from "react-i18next";
import AuthLayout from "../components/auth-layout";
import LoginForm from "../components/login-form";

export default function LoginPage() {
  const { t } = useTranslation();

  return (
    <AuthLayout title={t("login")} description={t("login_form_description")}>
      <LoginForm />
    </AuthLayout>
  );
}
