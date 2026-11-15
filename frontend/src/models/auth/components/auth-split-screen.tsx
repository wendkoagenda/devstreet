import { BrandLogo } from "@/components/brand/brand-logo";
import { LanguageToggle } from "@/components/ui/language-toggle";
import { ModeToggle } from "@/components/ui/mode-toggle";
import { Button } from "@/components/ui/button";
import { CreationErrorSonner } from "@/helpers/api/feed-backs";
import { cn } from "@/lib/utils";
import { t } from "i18next";
import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import LoginForm from "./login-form";
import OAuthButtons from "./oauth-buttons";
import RegisterForm from "./register-form";

const OAUTH_ERROR_KEYS: Record<string, string> = {
  denied: "auth.oauth_error_denied",
  inactive: "auth.oauth_error_inactive",
  invalid_state: "auth.oauth_error_invalid_state",
  exchange_failed: "auth.oauth_error_exchange",
  email_required: "auth.oauth_error_email",
  not_configured: "auth.oauth_error_not_configured",
  invalid_provider: "auth.oauth_error_generic",
};

type AuthMode = "login" | "register";

function PanelCopy({ mode }: { mode: AuthMode }) {
  const isLogin = mode === "login";
  return (
    <div className="flex h-full flex-col justify-between gap-8 p-8 text-primary-foreground md:p-10">
      <div>
        <BrandLogo on="dark" className="h-10" />
      </div>
      <div className="space-y-4">
        <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-primary-foreground/70">
          {isLogin ? t("auth.panel_login_kicker") : t("auth.panel_register_kicker")}
        </p>
        <h2 className="text-3xl font-bold tracking-tight md:text-4xl">
          {isLogin ? t("auth.panel_login_title") : t("auth.panel_register_title")}
        </h2>
        <p className="max-w-sm text-sm leading-relaxed text-primary-foreground/80 md:text-base">
          {isLogin
            ? t("auth.panel_login_description")
            : t("auth.panel_register_description")}
        </p>
        <ul className="space-y-2 text-sm text-primary-foreground/75">
          {(isLogin
            ? [
                t("auth.panel_login_point_1"),
                t("auth.panel_login_point_2"),
                t("auth.panel_login_point_3"),
              ]
            : [
                t("auth.panel_register_point_1"),
                t("auth.panel_register_point_2"),
                t("auth.panel_register_point_3"),
              ]
          ).map((point) => (
            <li key={point} className="flex items-start gap-2">
              <span
                className="mt-1.5 size-1.5 shrink-0 rounded-full bg-primary-foreground/80"
                aria-hidden
              />
              <span>{point}</span>
            </li>
          ))}
        </ul>
      </div>
      <p className="text-xs text-primary-foreground/55">
        © {new Date().getFullYear()} OnePourcent
      </p>
    </div>
  );
}

export default function AuthSplitScreen({
  initialMode = "login",
}: {
  initialMode?: AuthMode;
}) {
  const [mode, setMode] = useState<AuthMode>(initialMode);
  const [params, setParams] = useSearchParams();
  const isRegister = mode === "register";

  useEffect(() => {
    const oauthError = params.get("oauth_error");
    if (!oauthError) return;
    const key = OAUTH_ERROR_KEYS[oauthError] ?? "auth.oauth_error_generic";
    CreationErrorSonner(t(key));
    const next = new URLSearchParams(params);
    next.delete("oauth_error");
    next.delete("oauth");
    setParams(next, { replace: true });
  }, [params, setParams]);

  const formTitle = useMemo(
    () => (isRegister ? t("auth.register_title") : t("auth.login_title")),
    [isRegister]
  );
  const formDescription = useMemo(
    () =>
      isRegister
        ? t("auth.register_description")
        : t("login_form_description"),
    [isRegister]
  );

  return (
    <div className="relative flex min-h-screen items-center justify-center bg-muted/40 p-4 md:p-6">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 overflow-hidden"
      >
        <div className="absolute -top-32 left-1/2 h-96 w-96 -translate-x-1/2 rounded-full bg-chart-1/10 blur-3xl" />
        <div className="absolute -bottom-32 right-0 h-96 w-96 rounded-full bg-chart-2/10 blur-3xl" />
      </div>

      <div className="absolute left-4 top-4 z-20">
        <Button asChild variant="ghost" size="sm" className="rounded-xl">
          <Link to="/welcome">DevStreet</Link>
        </Button>
      </div>
      <div className="absolute right-4 top-4 z-20 flex items-center gap-2">
        <LanguageToggle />
        <ModeToggle />
      </div>

      <div className="relative z-10 w-full max-w-5xl overflow-hidden rounded-3xl border border-border/70 bg-card shadow-xl shadow-black/5 dark:shadow-black/40">
        {/* Mobile : bascule simple */}
        <div className="md:hidden">
          <div className="space-y-1 border-b border-border/70 px-6 py-5">
            <h1 className="text-2xl font-semibold tracking-tight">{formTitle}</h1>
            <p className="text-sm text-muted-foreground">{formDescription}</p>
          </div>
          <div className="space-y-5 px-6 py-5">
            <OAuthButtons />
            {isRegister ? <RegisterForm /> : <LoginForm />}
          </div>
          <div className="border-t border-border/70 bg-muted/30 px-6 py-4 text-center text-sm">
            {isRegister ? (
              <>
                <span className="text-muted-foreground">
                  {t("auth.already_have_account")}{" "}
                </span>
                <button
                  type="button"
                  className="font-medium text-foreground underline-offset-4 hover:underline"
                  onClick={() => setMode("login")}
                >
                  {t("auth.switch_to_login")}
                </button>
              </>
            ) : (
              <>
                <span className="text-muted-foreground">
                  {t("auth.no_account")}{" "}
                </span>
                <button
                  type="button"
                  className="font-medium text-foreground underline-offset-4 hover:underline"
                  onClick={() => setMode("register")}
                >
                  {t("auth.switch_to_register")}
                </button>
              </>
            )}
          </div>
        </div>

        {/* Desktop : split + overlay glissant */}
        <div className="relative hidden min-h-[min(52rem,calc(100svh-3rem))] md:block">
          {/* Couche formulaires : Register à gauche, Login à droite */}
          <div className="absolute inset-0 grid grid-cols-2">
            <div
              className={cn(
                "flex flex-col justify-start overflow-y-auto px-8 py-8 transition-opacity duration-500 lg:px-12 lg:py-10",
                isRegister ? "opacity-100" : "pointer-events-none opacity-0"
              )}
              aria-hidden={!isRegister}
            >
              <div className="mb-5 space-y-1">
                <h1 className="text-2xl font-semibold tracking-tight">
                  {t("auth.register_title")}
                </h1>
                <p className="text-sm text-muted-foreground">
                  {t("auth.register_description")}
                </p>
              </div>
              <div className="space-y-4">
                <OAuthButtons />
                <RegisterForm />
              </div>
            </div>
            <div
              className={cn(
                "flex flex-col justify-start overflow-y-auto px-8 py-8 transition-opacity duration-500 lg:px-12 lg:py-10",
                isRegister ? "pointer-events-none opacity-0" : "opacity-100"
              )}
              aria-hidden={isRegister}
            >
              <div className="mb-5 space-y-1">
                <h1 className="text-2xl font-semibold tracking-tight">
                  {t("auth.login_title")}
                </h1>
                <p className="text-sm text-muted-foreground">
                  {t("login_form_description")}
                </p>
              </div>
              <div className="space-y-4">
                <OAuthButtons />
                <LoginForm />
              </div>
            </div>
          </div>

          {/* Overlay info : gauche en login, droite en register */}
          <div
            className={cn(
              "absolute inset-y-0 left-0 z-10 w-1/2 overflow-hidden bg-primary transition-transform duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]",
              isRegister ? "translate-x-full" : "translate-x-0"
            )}
          >
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,hsl(var(--primary-foreground)/0.12),transparent_45%),radial-gradient(circle_at_80%_80%,hsl(var(--primary-foreground)/0.08),transparent_40%)]" />
            <div className="relative flex h-full flex-col">
              <PanelCopy mode={mode} />
              <div className="px-8 pb-10 md:px-10">
                {isRegister ? (
                  <div className="space-y-3">
                    <p className="text-sm text-primary-foreground/80">
                      {t("auth.already_have_account")}
                    </p>
                    <Button
                      type="button"
                      variant="secondary"
                      className="h-10 rounded-xl px-6"
                      onClick={() => setMode("login")}
                    >
                      {t("auth.switch_to_login")}
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <p className="text-sm text-primary-foreground/80">
                      {t("auth.no_account")}
                    </p>
                    <Button
                      type="button"
                      variant="secondary"
                      className="h-10 rounded-xl px-6"
                      onClick={() => setMode("register")}
                    >
                      {t("auth.switch_to_register")}
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
