import { useMemo } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Monitor } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useHubAccess } from "../hooks/use-hub-access";
import {
  useApproveGitOAuthMutation,
  useDenyGitOAuthMutation,
  useGetGitOAuthRequestQuery,
} from "../api";

/**
 * Confirmation OAuth GCM dans DevStreet (jamais auto-approuvée).
 * Après approve : redirection loopback GCM (pas d'UI Gitea).
 */
export default function GitOAuthAuthorizePage() {
  const { t } = useTranslation();
  const [params] = useSearchParams();
  const requestId = (params.get("request") || "").trim();
  const access = useHubAccess();

  const { data, isLoading, isError, error, refetch } = useGetGitOAuthRequestQuery(
    requestId,
    { skip: !requestId }
  );

  const [approve, approveState] = useApproveGitOAuthMutation();
  const [deny, denyState] = useDenyGitOAuthMutation();

  const status = data?.status;
  const pending = status === "pending";
  const busy = approveState.isLoading || denyState.isLoading;

  const expiresLabel = useMemo(() => {
    if (!data?.expires_at) return null;
    try {
      return new Date(data.expires_at).toLocaleString();
    } catch {
      return data.expires_at;
    }
  }, [data?.expires_at]);

  const redirectBrowser = (url: string) => {
    window.location.assign(url);
  };

  if (!requestId) {
    return (
      <main className="mx-auto flex max-w-lg flex-col gap-4 px-4 py-16">
        <h1 className="text-xl font-bold text-foreground">{t("hub.git_oauth.title")}</h1>
        <p className="text-sm text-muted-foreground">{t("hub.git_oauth.missing_request")}</p>
      </main>
    );
  }

  if (!access.isInitialized || isLoading) {
    return (
      <main className="mx-auto flex max-w-lg flex-col gap-3 px-4 py-16">
        <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
      </main>
    );
  }

  if (!access.isAuthenticated) {
    return (
      <main className="mx-auto flex max-w-lg flex-col gap-4 px-4 py-16">
        <div className="flex items-start gap-3">
          <Monitor aria-hidden className="mt-0.5 size-6 text-brand" />
          <div>
            <h1 className="text-xl font-bold text-foreground">{t("hub.git_oauth.title")}</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              {t("hub.git_oauth.login_required")}
            </p>
          </div>
        </div>
        <Button type="button" className="w-fit" onClick={access.requestLogin}>
          {t("hub.git_oauth.login_cta")}
        </Button>
      </main>
    );
  }

  if (isError || !data) {
    const statusCode =
      error && typeof error === "object" && "status" in error
        ? Number((error as { status?: number }).status)
        : null;
    return (
      <main className="mx-auto flex max-w-lg flex-col gap-4 px-4 py-16">
        <h1 className="text-xl font-bold text-foreground">{t("hub.git_oauth.title")}</h1>
        <p className="text-sm text-destructive">
          {statusCode === 404
            ? t("hub.git_oauth.not_found")
            : t("hub.git_oauth.load_error")}
        </p>
        <Button type="button" variant="outline" onClick={() => refetch()}>
          {t("common.retry", "Réessayer")}
        </Button>
      </main>
    );
  }

  return (
    <main className="mx-auto flex max-w-lg flex-col gap-5 px-4 py-16">
      <div className="flex items-start gap-3">
        <Monitor aria-hidden className="mt-0.5 size-6 text-brand" />
        <div className="flex flex-col gap-1">
          <h1 className="text-xl font-bold text-foreground">{t("hub.git_oauth.title")}</h1>
          <p className="text-sm text-muted-foreground">{t("hub.git_oauth.subtitle")}</p>
        </div>
      </div>

      <div className="rounded-xl border border-border bg-card p-4 text-sm">
        <p className="font-medium text-foreground">{data.computer_name}</p>
        <p className="mt-1 text-xs text-muted-foreground">
          {t("hub.git_oauth.host", { host: data.gitea_host || "—" })}
        </p>
        {expiresLabel ? (
          <p className="mt-1 text-xs text-muted-foreground">
            {t("hub.git_oauth.expires", { when: expiresLabel })}
          </p>
        ) : null}
        <ul className="mt-3 list-disc space-y-1 pl-4 text-xs text-muted-foreground">
          {(data.scope_labels || []).map((label) => (
            <li key={label}>{label}</li>
          ))}
        </ul>
      </div>

      {pending ? (
        <div className="flex flex-wrap gap-2">
          <Button
            type="button"
            disabled={busy}
            onClick={async () => {
              const result = await approve(requestId).unwrap();
              if (result.redirect_uri) redirectBrowser(result.redirect_uri);
            }}
          >
            {approveState.isLoading
              ? t("hub.git_oauth.approving")
              : t("hub.git_oauth.approve")}
          </Button>
          <Button
            type="button"
            variant="outline"
            disabled={busy}
            onClick={async () => {
              const result = await deny(requestId).unwrap();
              if (result.redirect_uri) redirectBrowser(result.redirect_uri);
            }}
          >
            {t("hub.git_oauth.deny")}
          </Button>
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">
          {status === "authorized" || status === "consumed"
            ? t("hub.git_oauth.done_authorized")
            : status === "denied"
              ? t("hub.git_oauth.done_denied")
              : t("hub.git_oauth.done_other", { status })}
        </p>
      )}

      {approveState.isError || denyState.isError ? (
        <p className="text-sm text-destructive">{t("hub.git_oauth.action_error")}</p>
      ) : null}

      <p className="text-xs text-muted-foreground">
        <Link to="/hub/git-setup" className="text-brand underline-offset-2 hover:underline">
          {t("hub.git_setup.open_page")}
        </Link>
      </p>
    </main>
  );
}
