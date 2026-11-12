import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff, Mail } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Icons } from "@/lib/constants/icons";
import {
  CreationErrorSonner,
  CreationSuccessSonner,
} from "@/helpers/api/feed-backs";
import PasswordStrengthIndicator from "@/helpers/displayers/password-strength-indicator";
import {
  useConfirmPasswordResetMutation,
  useForgotPasswordMutation,
  useVerifyResetCodeMutation,
} from "../api";
import { getResetErrorMessage } from "../functions/get-reset-error-message";
import {
  ForgotPasswordEmailSchema,
  forgotPasswordEmailSchema,
  ResetPasswordSchema,
  resetPasswordSchema,
  VerifyResetCodeSchema,
  verifyResetCodeSchema,
} from "../schema";

type Step = "email" | "code" | "password";

/** Délai avant de pouvoir redemander un code (aligné sur RESEND_COOLDOWN_SECONDS du backend). */
const RESEND_COOLDOWN_SECONDS = 60;

/**
 * Flux « mot de passe oublié » en 3 étapes : e-mail → code → nouveau mot de passe.
 * Le reset_token reste uniquement en mémoire (jamais dans l'URL ni dans le stockage du navigateur).
 */
export default function ForgotPasswordForm() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const [step, setStep] = useState<Step>("email");
  const [email, setEmail] = useState("");
  const [resetToken, setResetToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cooldown, setCooldown] = useState(0);

  const [forgotPassword, { isLoading: isSendingCode }] =
    useForgotPasswordMutation();
  const [verifyResetCode, { isLoading: isVerifying }] =
    useVerifyResetCodeMutation();
  const [confirmPasswordReset, { isLoading: isResetting }] =
    useConfirmPasswordResetMutation();

  // Compte à rebours du bouton « Renvoyer le code »
  useEffect(() => {
    if (cooldown <= 0) return;
    const timer = setTimeout(() => setCooldown((value) => value - 1), 1000);
    return () => clearTimeout(timer);
  }, [cooldown]);

  const emailForm = useForm<ForgotPasswordEmailSchema>({
    resolver: zodResolver(forgotPasswordEmailSchema(t)),
    defaultValues: { email: "" },
  });
  const codeForm = useForm<VerifyResetCodeSchema>({
    resolver: zodResolver(verifyResetCodeSchema(t)),
    defaultValues: { code: "" },
  });
  const passwordForm = useForm<ResetPasswordSchema>({
    resolver: zodResolver(resetPasswordSchema(t)),
    defaultValues: { new_password: "", new_password_confirm: "" },
  });
  const [showPassword, setShowPassword] = useState(false);
  const watchedNewPassword = passwordForm.watch("new_password");

  const startOver = () => {
    setStep("email");
    setResetToken(null);
    setError(null);
    setCooldown(0);
    codeForm.reset();
    passwordForm.reset();
  };

  // Étape 1 : demande du code
  const onSubmitEmail = async (data: ForgotPasswordEmailSchema) => {
    try {
      setError(null);
      await forgotPassword({ email: data.email }).unwrap();
      setEmail(data.email);
      setCooldown(RESEND_COOLDOWN_SECONDS);
      setStep("code");
    } catch (err) {
      setError(getResetErrorMessage(err, t));
    }
  };

  const handleResendCode = async () => {
    try {
      setError(null);
      await forgotPassword({ email }).unwrap();
      setCooldown(RESEND_COOLDOWN_SECONDS);
      CreationSuccessSonner(t("forgot_password.code_resent"));
    } catch (err) {
      setError(getResetErrorMessage(err, t));
    }
  };

  // Étape 2 : vérification du code
  const onSubmitCode = async (data: VerifyResetCodeSchema) => {
    try {
      setError(null);
      const response = await verifyResetCode({ email, code: data.code }).unwrap();
      setResetToken(response.reset_token);
      setStep("password");
    } catch (err) {
      setError(getResetErrorMessage(err, t));
    }
  };

  // Étape 3 : nouveau mot de passe
  const onSubmitPassword = async (data: ResetPasswordSchema) => {
    if (!resetToken) {
      startOver();
      return;
    }
    try {
      setError(null);
      await confirmPasswordReset({
        reset_token: resetToken,
        new_password: data.new_password,
        new_password_confirm: data.new_password_confirm,
      }).unwrap();
      CreationSuccessSonner(t("forgot_password.success"));
      navigate("/login", { replace: true });
    } catch (err) {
      const message = getResetErrorMessage(err, t);
      setError(message);
      CreationErrorSonner(message);
    }
  };

  const description =
    step === "email"
      ? t("forgot_password.email_description")
      : step === "code"
        ? t("forgot_password.code_description", { email })
        : t("forgot_password.password_description");

  return (
    <div className="flex flex-col gap-4">
      <p className="text-center text-sm text-muted-foreground">{description}</p>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {step === "email" && (
        <Form {...emailForm}>
          <form
            className="space-y-4"
            onSubmit={emailForm.handleSubmit(onSubmitEmail)}
            noValidate
          >
            <FormField
              control={emailForm.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-sm font-medium">
                    {t("email")} *
                  </FormLabel>
                  <FormControl>
                    <div className="relative">
                      <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        type="email"
                        autoComplete="email"
                        autoFocus
                        {...field}
                        placeholder="utilisateur@exemple.com"
                        className="h-10 pl-10"
                      />
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit" className="h-10 w-full" disabled={isSendingCode}>
              {isSendingCode ? (
                <>
                  <Icons.Loading className="mr-2 h-4 w-4 animate-spin" />
                  {t("forgot_password.sending")}
                </>
              ) : (
                t("forgot_password.send_code")
              )}
            </Button>
          </form>
        </Form>
      )}

      {step === "code" && (
        <Form {...codeForm}>
          <form
            className="space-y-4"
            onSubmit={codeForm.handleSubmit(onSubmitCode)}
            noValidate
          >
            <FormField
              control={codeForm.control}
              name="code"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-sm font-medium">
                    {t("forgot_password.code_label")} *
                  </FormLabel>
                  <FormControl>
                    <Input
                      inputMode="numeric"
                      autoComplete="one-time-code"
                      maxLength={6}
                      autoFocus
                      {...field}
                      onChange={(event) =>
                        field.onChange(event.target.value.replace(/\D/g, ""))
                      }
                      placeholder={t("forgot_password.code_placeholder")}
                      className="h-12 text-center font-mono text-xl tracking-[0.5em]"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit" className="h-10 w-full" disabled={isVerifying}>
              {isVerifying ? (
                <>
                  <Icons.Loading className="mr-2 h-4 w-4 animate-spin" />
                  {t("forgot_password.verifying")}
                </>
              ) : (
                t("forgot_password.verify")
              )}
            </Button>
            <div className="flex flex-col items-center gap-1">
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={handleResendCode}
                disabled={cooldown > 0 || isSendingCode}
              >
                {cooldown > 0
                  ? t("forgot_password.resend_in", { seconds: cooldown })
                  : t("forgot_password.resend_code")}
              </Button>
              <Button type="button" variant="link" size="sm" onClick={startOver}>
                {t("forgot_password.change_email")}
              </Button>
            </div>
          </form>
        </Form>
      )}

      {step === "password" && (
        <Form {...passwordForm}>
          <form
            className="space-y-4"
            onSubmit={passwordForm.handleSubmit(onSubmitPassword)}
            noValidate
          >
            <FormField
              control={passwordForm.control}
              name="new_password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-sm font-medium">
                    {t("forgot_password.new_password")} *
                  </FormLabel>
                  <FormControl>
                    <div className="relative">
                      <Input
                        type={showPassword ? "text" : "password"}
                        autoComplete="new-password"
                        autoFocus
                        {...field}
                        placeholder="••••••••"
                        className="h-10 pr-10"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-1 top-1 h-8 w-8 text-muted-foreground hover:text-foreground"
                      >
                        {showPassword ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </FormControl>
                  {watchedNewPassword && (
                    <PasswordStrengthIndicator password={watchedNewPassword} />
                  )}
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={passwordForm.control}
              name="new_password_confirm"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-sm font-medium">
                    {t("forgot_password.confirm_password")} *
                  </FormLabel>
                  <FormControl>
                    <Input
                      type={showPassword ? "text" : "password"}
                      autoComplete="new-password"
                      {...field}
                      placeholder="••••••••"
                      className="h-10"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit" className="h-10 w-full" disabled={isResetting}>
              {isResetting ? (
                <>
                  <Icons.Loading className="mr-2 h-4 w-4 animate-spin" />
                  {t("forgot_password.resetting")}
                </>
              ) : (
                t("forgot_password.reset")
              )}
            </Button>
            <div className="flex justify-center">
              <Button type="button" variant="link" size="sm" onClick={startOver}>
                {t("forgot_password.start_over")}
              </Button>
            </div>
          </form>
        </Form>
      )}

      <Button variant="ghost" size="sm" className="self-center" asChild>
        <Link to="/login">{t("forgot_password.back_to_login")}</Link>
      </Button>
    </div>
  );
}
