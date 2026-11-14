import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { API_URL } from "@/helpers/api/csrf";

type Providers = {
  google: boolean;
  github: boolean;
};

function GoogleIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" aria-hidden>
      <path
        fill="#EA4335"
        d="M12 10.2v3.6h5.1c-.2 1.2-1.5 3.6-5.1 3.6-3.1 0-5.6-2.5-5.6-5.6S8.9 6.2 12 6.2c1.8 0 3 .7 3.7 1.4l2.5-2.4C16.7 3.7 14.6 2.8 12 2.8 6.9 2.8 2.8 6.9 2.8 12S6.9 21.2 12 21.2c5.2 0 8.7-3.6 8.7-8.7 0-.6-.1-1-.2-1.5H12z"
      />
      <path
        fill="#34A853"
        d="M3.9 7.4 6.9 9.6C7.7 7.6 9.7 6.2 12 6.2c1.8 0 3 .7 3.7 1.4l2.5-2.4C16.7 3.7 14.6 2.8 12 2.8 8.3 2.8 5.1 4.9 3.9 7.4z"
      />
      <path
        fill="#4A90E2"
        d="M12 21.2c2.5 0 4.6-.8 6.1-2.2l-2.9-2.2c-.8.6-1.9 1-3.2 1-3.1 0-5.6-2-6.5-4.7l-3 2.3C4.1 18.9 7.7 21.2 12 21.2z"
      />
      <path
        fill="#FBBC05"
        d="M5.5 13.1c-.2-.6-.3-1.2-.3-1.9s.1-1.3.3-1.9L2.5 6.9C1.9 8.2 1.6 9.5 1.6 11s.3 2.8.9 4.1l3-2z"
      />
    </svg>
  );
}

function GitHubIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden>
      <path d="M12 2C6.48 2 2 6.58 2 12.26c0 4.52 2.87 8.35 6.84 9.7.5.1.68-.22.68-.48 0-.24-.01-.87-.01-1.7-2.78.62-3.37-1.37-3.37-1.37-.45-1.18-1.11-1.5-1.11-1.5-.91-.64.07-.63.07-.63 1 .07 1.53 1.06 1.53 1.06.89 1.56 2.34 1.11 2.91.85.09-.66.35-1.11.63-1.37-2.22-.26-4.55-1.14-4.55-5.07 0-1.12.39-2.03 1.03-2.75-.1-.26-.45-1.3.1-2.7 0 0 .84-.27 2.75 1.05A9.3 9.3 0 0 1 12 6.8c.85 0 1.7.12 2.5.34 1.9-1.32 2.74-1.05 2.74-1.05.55 1.4.2 2.44.1 2.7.64.72 1.03 1.63 1.03 2.75 0 3.94-2.34 4.8-4.57 5.06.36.32.68.94.68 1.9 0 1.37-.01 2.47-.01 2.8 0 .27.18.59.69.48A10.03 10.03 0 0 0 22 12.26C22 6.58 17.52 2 12 2z" />
    </svg>
  );
}

function startOAuth(provider: "google" | "github") {
  window.location.assign(`${API_URL}/auth/oauth/${provider}/start`);
}

export default function OAuthButtons() {
  const { t } = useTranslation();
  const [providers, setProviders] = useState<Providers | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch(`${API_URL}/auth/oauth/providers`, { credentials: "include" })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (!cancelled && data && typeof data === "object") {
          setProviders({
            google: Boolean(data.google),
            github: Boolean(data.github),
          });
        } else if (!cancelled) {
          setProviders({ google: false, github: false });
        }
      })
      .catch(() => {
        if (!cancelled) setProviders({ google: false, github: false });
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (!providers || (!providers.google && !providers.github)) {
    return null;
  }

  const oauthBtnClass =
    "h-10 w-full justify-center gap-2 rounded-xl border border-border bg-muted text-foreground shadow-none hover:bg-muted/80";

  return (
    <div className="space-y-3">
      <div className="grid gap-2">
        {providers.google ? (
          <Button
            type="button"
            variant="secondary"
            className={oauthBtnClass}
            onClick={() => startOAuth("google")}
          >
            <GoogleIcon className="size-4 shrink-0" />
            {t("auth.oauth_google")}
          </Button>
        ) : null}
        {providers.github ? (
          <Button
            type="button"
            variant="secondary"
            className={oauthBtnClass}
            onClick={() => startOAuth("github")}
          >
            <GitHubIcon className="size-4 shrink-0" />
            {t("auth.oauth_github")}
          </Button>
        ) : null}
      </div>
      <div className="relative py-1">
        <div className="absolute inset-0 flex items-center" aria-hidden>
          <span className="w-full border-t border-border" />
        </div>
        <div className="relative flex justify-center text-xs uppercase tracking-wide">
          <span className="bg-card px-3 text-muted-foreground">
            {t("auth.oauth_or")}
          </span>
        </div>
      </div>
    </div>
  );
}
