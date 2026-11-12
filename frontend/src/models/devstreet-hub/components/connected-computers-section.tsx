import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Laptop, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  useGetGitConnectedComputersQuery,
  useRevokeGitConnectedComputerMutation,
} from "../api";

/**
 * Liste des ordinateurs autorisés (PAT Gitea) + révocation serveur.
 */
export function ConnectedComputersSection() {
  const { t } = useTranslation();
  const { data, isLoading, isError, refetch } = useGetGitConnectedComputersQuery();
  const [revoke, revokeState] = useRevokeGitConnectedComputerMutation();
  const [confirmId, setConfirmId] = useState<number | null>(null);

  const computers = data ?? [];

  return (
    <section className="mt-8 flex flex-col gap-4">
      <div>
        <h2 className="flex items-center gap-2 text-lg font-semibold text-foreground">
          <Laptop aria-hidden className="size-5 text-brand" />
          {t("hub.git_computers.title")}
        </h2>
        <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
          {t("hub.git_computers.hint")}
        </p>
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
        <p className="rounded-xl border border-dashed border-border bg-secondary/40 px-4 py-3 text-sm text-muted-foreground">
          {t("hub.git_computers.empty")}
        </p>
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
    </section>
  );
}
