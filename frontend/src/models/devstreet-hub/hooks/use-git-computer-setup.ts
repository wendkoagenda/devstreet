import { useCallback, useEffect, useMemo, useState } from "react";
import {
  useGetGitConnectedComputersQuery,
  useGetGitOAuthClientConfigQuery,
} from "../api";
import { copyText } from "@/helpers/clipboard";

const DISMISS_SESSION_KEY = "devstreet.git-setup.dismissed";

/**
 * État « ordinateur Git relié » : ordinateurs actifs côté Hub + commandes GCM.
 * Le navigateur ne peut pas vérifier la config locale ; le gate se base sur les PAT actifs.
 */
export function useGitComputerSetup(options?: { skip?: boolean }) {
  const skip = options?.skip ?? false;
  const computersQuery = useGetGitConnectedComputersQuery(undefined, { skip });
  const configQuery = useGetGitOAuthClientConfigQuery(undefined, { skip });

  const [copied, setCopied] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    try {
      if (sessionStorage.getItem(DISMISS_SESSION_KEY) === "1") {
        setDismissed(true);
      }
    } catch (error) {
      console.warn("sessionStorage indisponible (lecture dismiss git-setup) :", error);
    }
  }, []);

  const activeComputers = useMemo(
    () => (computersQuery.data ?? []).filter((c) => c.status === "active"),
    [computersQuery.data]
  );

  const needsLink = !skip && !computersQuery.isLoading && activeComputers.length === 0;

  const commands = configQuery.data?.git_config_commands ?? [];
  const commandsBlock = commands.join("\n");

  const copyCommands = useCallback(async () => {
    if (!commandsBlock) return false;
    const ok = await copyText(commandsBlock);
    if (ok) {
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    }
    return ok;
  }, [commandsBlock]);

  const dismissForSession = useCallback(() => {
    try {
      sessionStorage.setItem(DISMISS_SESSION_KEY, "1");
    } catch (error) {
      console.warn("sessionStorage indisponible (écriture dismiss git-setup) :", error);
    }
    setDismissed(true);
  }, []);

  return {
    needsLink,
    dismissed,
    dismissForSession,
    shouldPrompt: needsLink && !dismissed,
    activeCount: activeComputers.length,
    computers: computersQuery.data ?? [],
    isLoadingComputers: computersQuery.isLoading,
    isErrorComputers: computersQuery.isError,
    refetchComputers: computersQuery.refetch,
    commands,
    commandsBlock,
    isLoadingConfig: configQuery.isLoading,
    isErrorConfig: configQuery.isError,
    refetchConfig: configQuery.refetch,
    giteaOrigin: configQuery.data?.gitea_origin ?? null,
    copied,
    copyCommands,
  };
}
