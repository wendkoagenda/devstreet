import { create } from "zustand";
import type { StarResult } from "./schema";

/**
 * Étoiles posées ou retirées pendant la session. Le serveur ne renvoie pas encore l'état personnel
 * de l'étoile dans la liste : on garde en mémoire (jamais dans le stockage du navigateur) le dernier
 * résultat serveur, rattaché à l'utilisateur qui l'a obtenu.
 */
interface ProjectStarState {
  userId: number | null;
  results: Record<number, StarResult>;
  record: (userId: number, projectId: number, result: StarResult) => void;
}

export const useProjectStarSlice = create<ProjectStarState>((set) => ({
  userId: null,
  results: {},
  record: (userId, projectId, result) =>
    set((state) => ({
      userId,
      results: {
        ...(state.userId === userId ? state.results : {}),
        [projectId]: result,
      },
    })),
}));
