import { useEffect } from "react";
import { useSelina } from "./use-selina";

/** Lie le contexte projet/tâche à Selina pendant le cycle de vie de la page. */
export function useSelinaHubContext(
  projectId: number | null | undefined,
  projectTitle: string | undefined,
  taskId?: number,
  taskTitle?: string
) {
  const { setHubContext, clearHubContext } = useSelina();

  useEffect(() => {
    if (!projectId || !projectTitle) {
      clearHubContext();
      return;
    }
    setHubContext({
      projectId,
      projectTitle,
      taskId,
      taskTitle,
    });
    return () => clearHubContext();
  }, [
    clearHubContext,
    projectId,
    projectTitle,
    setHubContext,
    taskId,
    taskTitle,
  ]);
}
