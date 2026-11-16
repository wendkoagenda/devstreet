import { useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Laptop, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  useGetGitConnectedComputersQuery,
  useRevokeGitConnectedComputerMutation,
} from "../api";

interface ConnectedComputersSectionProps {
  /** Lien vers /hub/git-setup (désactivé sur la page elle-même). */
  showSetupLink?: boolean;
}

/**
 * Liste des ordinateurs autorisés (PAT Gitea) + révocation serveur.
 */
export function ConnectedComputersSection({
  showSetupLink = true,
}: ConnectedComputersSectionProps) {
  const { t } = useTranslation();
  const { data, isLoading, isError, refetch } = useGetGitConnectedComputersQuery();
  const [revoke, revokeState] = useRevokeGitConnectedComputerMutation();
  const [confirmId, setConfirmId] = useState<number | null>(null);

  const computers = data ?? [];
  const activeCount = computers.filter((c) => c.status === "active").length;

  return (
    <section className="mt-8 flex flex-col gap-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="flex items-center gap-2 text-lg font-semibold text-foreground">
            <Laptop aria-hidden className="size-5 text-brand" />
            {t("hub.git_computers.title")}
          </h2>
          <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
            {t("hub.git_computers.hint")}
          </p>
        </div>
        {showSetupLink ? (
          <Button asChild type="button" variant="outline" className="h-8 w-fit text-xs">
            <Link to="/hub/git-setup">{t("hub.git_setup.open_page")}</Link>
          </Button>
        ) : null}
      </div>

      {isLoading ? (
        <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
      ) : isError ? (
        <div className="flex flex-col gap-2">
          <p className="text-sm text-destructive">{t("hub.git_computers.load_error")}</p>
          <Button type="button" variant="outline" className="w-fit" onClick={() => refetch()}>
            {t("common.retry", "Réessayer")}
          </Button>
        </div>
      ) : computers.length === 0 ? (
        <div className="flex flex-col gap-3 rounded-xl border border-dashed border-border bg-secondary/40 px-4 py-3">
          <p className="text-sm text-muted-foreground">{t("hub.git_computers.empty")}</p>
          {showSetupLink ? (
            <Button asChild type="button" className="h-8 w-fit text-xs font-semibold">
              <Link to="/hub/git-setup">{t("hub.git_setup.link_computer_cta")}</Link>
            </Button>
          ) : null}
        </div>
      ) : (
        <ul className="flex flex-col gap-2">
          {computers.map((computer) => {
            const active = computer.status === "active";
            const created = (() => {
              try {
                return new Date(computer.created_at).toLocaleString();
              } catch {
                return computer.created_at;
              }
            })();
            return (
              <li
                key={computer.id}
                className="flex flex-col gap-3 rounded-xl border border-border bg-card p-4 sm:flex-row sm:items-center sm:justify-between"
              >
                <div className="min-w-0">
                  <p className="font-medium text-foreground">{computer.name}</p>
                  <p className="mt-0.5 text-xs text-muted-foreground">
                    {t("hub.git_computers.meta", {
                      login: computer.forge_login,
                      created,
                      status: active
                        ? t("hub.git_computers.status_active")
                        : t("hub.git_computers.status_revoked"),
                      suffix: computer.token_last_eight
                        ? `…${computer.token_last_eight}`
                        : "",
                    })}
                  </p>
                </div>
                {active ? (
                  confirmId === computer.id ? (
                    <div className="flex flex-wrap gap-2">
                      <Button
                        type="button"
                        variant="destructive"
                        className="h-8 gap-1.5 text-xs"
                        disabled={revokeState.isLoading}
                        onClick={async () => {
                          await revoke(computer.id);
                          setConfirmId(null);
                        }}
                      >
                        <Trash2 aria-hidden className="size-3.5" />
                        {t("hub.git_computers.revoke_confirm")}
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        className="h-8 text-xs"
                        onClick={() => setConfirmId(null)}
                      >
                        {t("common.cancel")}
                      </Button>
                    </div>
                  ) : (
                    <Button
                      type="button"
                      variant="outline"
                      className="h-8 text-xs"
                      onClick={() => setConfirmId(computer.id)}
                    >
                      {t("hub.git_computers.revoke")}
                    </Button>
                  )
                ) : null}
              </li>
            );
          })}
        </ul>
      )}

      {!isLoading && !isError && activeCount > 0 && showSetupLink ? (
        <p className="text-xs text-muted-foreground">
          {t("hub.git_setup.reconfig_hint")}{" "}
          <Link to="/hub/git-setup" className="text-brand underline-offset-2 hover:underline">
            {t("hub.git_setup.open_page")}
          </Link>
        </p>
      ) : null}
    </section>
  );
}
