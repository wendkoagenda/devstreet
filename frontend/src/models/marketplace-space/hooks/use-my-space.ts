import { useGetMySpaceQuery } from "../api";

/**
 * Espace marketplace de l'utilisateur connecté.
 * Un utilisateur dont le profil est rattaché à une entreprise est « recruteur » : il publie des offres
 * et découvre des talents. Les autres sont « candidats ». Sans profil, il doit d'abord le créer.
 */
export function useMySpace() {
  const { data, isLoading, isError, refetch } = useGetMySpaceQuery();
  const profil = data?.profil ?? null;
  const company = data?.company ?? null;

  return {
    profil,
    company,
    hasProfil: profil !== null,
    isRecruiter: company !== null,
    /** Au moins un profil : dev ou entreprise. */
    hasAnyProfile: profil !== null || company !== null,
    isLoading,
    isError,
    refetch,
  };
}
