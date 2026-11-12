import { useCallback, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import { useSetProjectStarMutation } from "../api";
import { useProjectStarSlice } from "../slice";
import type { Project, StarResult } from "../schema";
import { apiDetailOf, httpStatusOf } from "../functions/api-error";
import { useHubAccess } from "./use-hub-access";

const NO_RESULTS: Record<number, StarResult> = {};

export interface ProjectStarView {
  starred: boolean;
  count: number;
  isPending: boolean;
  /** Seuls les projets publiés reçoivent des étoiles (règle serveur). */
  isAvailable: boolean;
}

/**
 * Étoiler / retirer l'étoile d'un projet. Une seule requête par projet à la fois (le double clic
 * n'envoie rien de plus) ; le total affiché est celui renvoyé par le serveur.
 */
export function useProjectStar() {
  const { t } = useTranslation();
  const { isAuthenticated, userId, canStarProject, requestLogin } = useHubAccess();
  const [setProjectStar] = useSetProjectStarMutation();
  const results = useProjectStarSlice((state) =>
    state.userId !== null && state.userId === userId ? state.results : NO_RESULTS
  );
  const record = useProjectStarSlice((state) => state.record);

  const inFlight = useRef(new Set<number>());
  const [pendingIds, setPendingIds] = useState<ReadonlySet<number>>(new Set());

  const setPending = (projectId: number, pending: boolean) => {
    if (pending) inFlight.current.add(projectId);
    else inFlight.current.delete(projectId);
    setPendingIds(new Set(inFlight.current));
  };

  const viewOf = useCallback(
    (project: Project): ProjectStarView => {
      const result = results[project.id];
      return {
        starred: result?.starred ?? false,
        count: result?.star_count ?? project.star_count,
        isPending: pendingIds.has(project.id),
        isAvailable: project.status === "published",
      };
    },
    [results, pendingIds]
  );

  const toggle = async (project: Project) => {
    if (!isAuthenticated || userId === null) {
      toast(t("hub.star.login_required"), {
        action: { label: t("hub.common.login"), onClick: requestLogin },
      });
      return;
    }
    if (!canStarProject) {
      toast.error(t("hub.star.forbidden"));
      return;
    }
    if (project.status !== "published" || inFlight.current.has(project.id)) return;

    const nextStarred = !(results[project.id]?.starred ?? false);
    setPending(project.id, true);
    try {
      const result = await setProjectStar({
        projectId: project.id,
        starred: nextStarred,
      }).unwrap();
      record(userId, project.id, result);
    } catch (error) {
      const status = httpStatusOf(error);
      if (status === 401) return; // flux de session existant (renouvellement ou reconnexion)
      const messages: Record<number, string> = {
        403: t("hub.star.forbidden"),
        404: t("hub.star.not_found"),
        409: apiDetailOf(error) ?? t("hub.star.conflict"),
        429: t("hub.common.rate_limited"),
      };
      toast.error((status !== null && messages[status]) || t("hub.star.error"));
    } finally {
      setPending(project.id, false);
    }
  };

  return { viewOf, toggle };
}
