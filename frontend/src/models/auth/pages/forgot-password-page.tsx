import { useTranslation } from "react-i18next";
import AuthLayout from "../components/auth-layout";
import ForgotPasswordForm from "../components/forgot-password-form";

export default function ForgotPasswordPage() {
  const { t } = useTranslation();

  return (
    <AuthLayout title={t("forgot_password.title")}>
      <ForgotPasswordForm />
    </AuthLayout>
  );
}
