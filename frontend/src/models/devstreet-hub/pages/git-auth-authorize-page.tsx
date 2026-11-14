import { useMemo } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Monitor, ShieldAlert } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useHubAccess } from "../hooks/use-hub-access";
import {
  useAuthorizeGitDeviceMutation,
  useDenyGitDeviceMutation,
  useGetGitDeviceAuthRequestQuery,
} from "../api";

/**
 * Confirmation explicite navigateur DevStreet (jamais auto-approuvée).
 * Aucune UI Gitea : autorisation d'un PAT HTTPS pour le CLI local.
 */
export default function GitAuthAuthorizePage() {
  const { t } = useTranslation();
  const [params] = useSearchParams();
  const requestId = (params.get("request") || "").trim();
  const access = useHubAccess();

  const { data, isLoading, isError, error, refetch } =
    useGetGitDeviceAuthRequestQuery(requestId, { skip: !requestId });

  const [authorize, authorizeState] = useAuthorizeGitDeviceMutation();
  const [deny, denyState] = useDenyGitDeviceMutation();

  const status = data?.status;
  const pending = status === "pending";
  const busy = authorizeState.isLoading || denyState.isLoading;

  const expiresLabel = useMemo(() => {
    if (!data?.expires_at) return null;
    try {
      return new Date(data.expires_at).toLocaleString();
    } catch {
      return data.expires_at;
    }
  }, [data?.expires_at]);

  if (!requestId) {
    return (
      <main className="mx-auto flex max-w-lg flex-col gap-4 px-4 py-16">
        <h1 className="text-xl font-bold text-foreground">
          {t("hub.git_auth.title")}
        </h1>
        <p className="text-sm text-muted-foreground">
          {t("hub.git_auth.missing_request")}
        </p>
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
            <h1 className="text-xl font-bold text-foreground">
              {t("hub.git_auth.title")}
            </h1>
            <p className="mt-2 text-sm text-muted-foreground">
              {t("hub.git_auth.login_required")}
            </p>
          </div>
        </div>
        <Button type="button" className="w-fit" onClick={access.requestLogin}>
          {t("hub.git_auth.login_cta")}
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
        <h1 className="text-xl font-bold text-foreground">
          {t("hub.git_auth.title")}
        </h1>
        <p className="text-sm text-destructive">
          {statusCode === 404
            ? t("hub.git_auth.not_found")
            : t("hub.git_auth.load_error")}
        </p>
        <Button type="button" variant="outline" onClick={() => refetch()}>
          {t("common.retry", "Réessayer")}
        </Button>
      </main>
    );
  }

  return (
    <main className="mx-auto flex max-w-lg flex-col gap-6 px-4 py-12 sm:py-16">
      <div className="flex items-start gap-3">
        <Monitor aria-hidden className="mt-0.5 size-7 text-brand" />
        <div>
          <h1 className="text-xl font-bold text-foreground">
            {t("hub.git_auth.title")}
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {t("hub.git_auth.subtitle")}
          </p>
        </div>
      </div>

      <section className="flex flex-col gap-3 rounded-2xl border border-border bg-card p-5 shadow-card">
        <dl className="grid gap-3 text-sm">
          <div>
            <dt className="text-xs font-medium text-muted-foreground">
              {t("hub.git_auth.computer")}
            </dt>
            <dd className="font-semibold text-foreground">{data.computer_name}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-muted-foreground">
              {t("hub.git_auth.instance")}
            </dt>
            <dd className="break-all text-foreground">{data.hub_base_url}</dd>
          </div>
          {data.gitea_host ? (
            <div>
              <dt className="text-xs font-medium text-muted-foreground">
                {t("hub.git_auth.forge_host")}
              </dt>
              <dd className="text-foreground">{data.gitea_host}</dd>
            </div>
          ) : null}
          <div>
            <dt className="text-xs font-medium text-muted-foreground">
              {t("hub.git_auth.expires")}
            </dt>
            <dd className="text-foreground">{expiresLabel}</dd>
          </div>
          <div>
            <dt className="mb-1 text-xs font-medium text-muted-foreground">
              {t("hub.git_auth.scopes")}
            </dt>
            <dd>
              <ul className="list-disc space-y-1 pl-5 text-foreground">
                {(data.scope_labels.length
                  ? data.scope_labels
                  : data.scopes
                ).map((label) => (
                  <li key={label}>{label}</li>
                ))}
              </ul>
            </dd>
          </div>
        </dl>

        <div className="flex items-start gap-2 rounded-xl border border-warning/30 bg-warning-soft/70 p-3 text-xs text-foreground">
          <ShieldAlert aria-hidden className="mt-0.5 size-4 shrink-0 text-warning" />
          <p>{t("hub.git_auth.confirm_hint")}</p>
        </div>

        {pending ? (
          <div className="flex flex-wrap gap-2 pt-1">
            <Button
              type="button"
              disabled={busy}
              onClick={async () => {
                await authorize(requestId);
              }}
            >
              {authorizeState.isLoading
                ? t("hub.git_auth.authorizing")
                : t("hub.git_auth.authorize")}
            </Button>
            <Button
              type="button"
              variant="outline"
              disabled={busy}
              onClick={async () => {
                await deny(requestId);
              }}
            >
              {denyState.isLoading
                ? t("hub.git_auth.denying")
                : t("hub.git_auth.deny")}
            </Button>
          </div>
        ) : (
          <p className="text-sm font-medium text-foreground">
            {status === "authorized" || status === "consumed"
              ? t("hub.git_auth.done_authorized")
              : status === "denied"
                ? t("hub.git_auth.done_denied")
                : t("hub.git_auth.done_expired")}
          </p>
        )}

        {authorizeState.isError || denyState.isError ? (
          <p className="text-sm text-destructive">
            {t("hub.git_auth.action_error")}
          </p>
        ) : null}
      </section>

      <p className="text-xs text-muted-foreground">
        <Link to="/profil/me?edit=1" className="text-brand underline-offset-2 hover:underline">
          {t("hub.git_auth.manage_computers")}
        </Link>
      </p>
    </main>
  );
}
