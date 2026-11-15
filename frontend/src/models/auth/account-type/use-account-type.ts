import { useMemo } from "react";
import { useAuthSlice } from "../slice";
import { getHomePath, isEntrepriseOnly, splitAccountType } from "./capabilities";

/**
 * Type de compte du membre connecté et ce qu'il implique pour le menu.
 * Un administrateur voit toutes les sections (comportement historique) mais n'a pas de type.
 */
export function useAccountType() {
  const user = useAuthSlice((state) => state.user);

  return useMemo(() => {
    const isAdmin = Boolean(user?.is_admin);
    const types = splitAccountType(user?.account_type);
    const hasDev = types.includes("dev");
    const hasEntreprise = types.includes("entreprise");
    const entrepriseOnly = isEntrepriseOnly(user);

    return {
      accountType: user?.account_type ?? "",
      isAdmin,
      hasDevType: hasDev,
      hasEntrepriseType: hasEntreprise,
      isEntrepriseOnly: entrepriseOnly,
      onboardingRequired: Boolean(user?.onboarding_required),
      /** Section « Mon espace dev » dans le menu. */
      showDevSpace: isAdmin || hasDev,
      /** Section « Mon entreprise » dans le menu. */
      showEntrepriseSpace: isAdmin || hasEntreprise,
      /** Forum, communautés, chaînes, favoris et projets. */
      showCommunity: !entrepriseOnly,
      /** Type que le membre peut encore ajouter (jamais pour un administrateur). */
      missingType: isAdmin
        ? null
        : hasDev && !hasEntreprise
          ? ("entreprise" as const)
          : hasEntreprise && !hasDev
            ? ("dev" as const)
            : null,
      homePath: getHomePath(user),
    };
  }, [user]);
}
