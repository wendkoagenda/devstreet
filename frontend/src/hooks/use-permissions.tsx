import { useMemo } from "react";
import { useAuthSlice } from "../models/auth/slice";
import { getPermission } from "@/models/auth/permissions/constants";
import { hasPermission } from "@/models/auth/permissions/utils";

export const usePermissions = () => {
  const permissions = useAuthSlice((state) => state.permissions);
  const isAuthenticated = useAuthSlice((state) => state.isAuthenticated);

  return useMemo(() => {
    if (!isAuthenticated) {
      return {
        hasPermission: () => false,

        canViewUsers: false,
        canCreateUsers: false,
        canUpdateUsers: false,
        canDeleteUsers: false,

        canViewRoles: false,
        canCreateRoles: false,
        canUpdateRoles: false,
        canDeleteRoles: false,

        canViewConnections: false,
        canCreateConnections: false,
        canUpdateConnections: false,
        canDeleteConnections: false,

        canViewSwipes: false,
        canCreateSwipes: false,
        canUpdateSwipes: false,
        canDeleteSwipes: false,

        canViewReviews: false,
        canCreateReviews: false,
        canUpdateReviews: false,
        canDeleteReviews: false,

        canViewAvailabilities: false,
        canCreateAvailabilities: false,
        canUpdateAvailabilities: false,
        canDeleteAvailabilities: false,

        canViewProfilHistories: false,
        canCreateProfilHistories: false,
        canUpdateProfilHistories: false,
        canDeleteProfilHistories: false,

        canViewPrestations: false,
        canCreatePrestations: false,
        canUpdatePrestations: false,
        canDeletePrestations: false,

        canViewExperiences: false,
        canCreateExperiences: false,
        canUpdateExperiences: false,
        canDeleteExperiences: false,

        canViewProfilSkills: false,
        canCreateProfilSkills: false,
        canUpdateProfilSkills: false,
        canDeleteProfilSkills: false,

        canViewCandidatures: false,
        canCreateCandidatures: false,
        canUpdateCandidatures: false,
        canDeleteCandidatures: false,

        canViewOffers: false,
        canCreateOffers: false,
        canUpdateOffers: false,
        canDeleteOffers: false,

        canViewProfils: false,
        canCreateProfils: false,
        canUpdateProfils: false,
        canDeleteProfils: false,

        canViewSkills: false,
        canCreateSkills: false,
        canUpdateSkills: false,
        canDeleteSkills: false,

        canViewCompanies: false,
        canCreateCompanies: false,
        canUpdateCompanies: false,
        canDeleteCompanies: false,

        canCreateProjects: false,
        canStarProjects: false,

        isSuperAdmin: false,
        permissions: [],
      };
    }

    return {
      hasPermission: (permission: string) =>
        hasPermission(permissions, permission),
      canViewUsers: hasPermission(permissions, getPermission("USER", "VIEW")),
      canCreateUsers: hasPermission(
        permissions,
        getPermission("USER", "CREATE")
      ),
      canUpdateUsers: hasPermission(
        permissions,
        getPermission("USER", "UPDATE")
      ),
      canDeleteUsers: hasPermission(
        permissions,
        getPermission("USER", "DELETE")
      ),

      canViewRoles: hasPermission(permissions, getPermission("ROLE", "VIEW")),
      canCreateRoles: hasPermission(
        permissions,
        getPermission("ROLE", "CREATE")
      ),
      canUpdateRoles: hasPermission(
        permissions,
        getPermission("ROLE", "UPDATE")
      ),
      canDeleteRoles: hasPermission(
        permissions,
        getPermission("ROLE", "DELETE")
      ),

      canViewConnections: hasPermission(permissions, getPermission("CONNECTION", "VIEW")),
      canCreateConnections: hasPermission(permissions, getPermission("CONNECTION", "CREATE")),
      canUpdateConnections: hasPermission(permissions, getPermission("CONNECTION", "UPDATE")),
      canDeleteConnections: hasPermission(permissions, getPermission("CONNECTION", "DELETE")),

      canViewSwipes: hasPermission(permissions, getPermission("SWIPE", "VIEW")),
      canCreateSwipes: hasPermission(permissions, getPermission("SWIPE", "CREATE")),
      canUpdateSwipes: hasPermission(permissions, getPermission("SWIPE", "UPDATE")),
      canDeleteSwipes: hasPermission(permissions, getPermission("SWIPE", "DELETE")),

      canViewReviews: hasPermission(permissions, getPermission("REVIEW", "VIEW")),
      canCreateReviews: hasPermission(permissions, getPermission("REVIEW", "CREATE")),
      canUpdateReviews: hasPermission(permissions, getPermission("REVIEW", "UPDATE")),
      canDeleteReviews: hasPermission(permissions, getPermission("REVIEW", "DELETE")),

      canViewAvailabilities: hasPermission(permissions, getPermission("AVAILABILITY", "VIEW")),
      canCreateAvailabilities: hasPermission(permissions, getPermission("AVAILABILITY", "CREATE")),
      canUpdateAvailabilities: hasPermission(permissions, getPermission("AVAILABILITY", "UPDATE")),
      canDeleteAvailabilities: hasPermission(permissions, getPermission("AVAILABILITY", "DELETE")),

      canViewProfilHistories: hasPermission(permissions, getPermission("PROFILHISTORY", "VIEW")),
      canCreateProfilHistories: hasPermission(permissions, getPermission("PROFILHISTORY", "CREATE")),
      canUpdateProfilHistories: hasPermission(permissions, getPermission("PROFILHISTORY", "UPDATE")),
      canDeleteProfilHistories: hasPermission(permissions, getPermission("PROFILHISTORY", "DELETE")),

      canViewPrestations: hasPermission(permissions, getPermission("PRESTATION", "VIEW")),
      canCreatePrestations: hasPermission(permissions, getPermission("PRESTATION", "CREATE")),
      canUpdatePrestations: hasPermission(permissions, getPermission("PRESTATION", "UPDATE")),
      canDeletePrestations: hasPermission(permissions, getPermission("PRESTATION", "DELETE")),

      canViewExperiences: hasPermission(permissions, getPermission("EXPERIENCE", "VIEW")),
      canCreateExperiences: hasPermission(permissions, getPermission("EXPERIENCE", "CREATE")),
      canUpdateExperiences: hasPermission(permissions, getPermission("EXPERIENCE", "UPDATE")),
      canDeleteExperiences: hasPermission(permissions, getPermission("EXPERIENCE", "DELETE")),

      canViewProfilSkills: hasPermission(permissions, getPermission("PROFILSKILL", "VIEW")),
      canCreateProfilSkills: hasPermission(permissions, getPermission("PROFILSKILL", "CREATE")),
      canUpdateProfilSkills: hasPermission(permissions, getPermission("PROFILSKILL", "UPDATE")),
      canDeleteProfilSkills: hasPermission(permissions, getPermission("PROFILSKILL", "DELETE")),

      canViewCandidatures: hasPermission(permissions, getPermission("CANDIDATURE", "VIEW")),
      canCreateCandidatures: hasPermission(permissions, getPermission("CANDIDATURE", "CREATE")),
      canUpdateCandidatures: hasPermission(permissions, getPermission("CANDIDATURE", "UPDATE")),
      canDeleteCandidatures: hasPermission(permissions, getPermission("CANDIDATURE", "DELETE")),

      canViewOffers: hasPermission(permissions, getPermission("OFFER", "VIEW")),
      canCreateOffers: hasPermission(permissions, getPermission("OFFER", "CREATE")),
      canUpdateOffers: hasPermission(permissions, getPermission("OFFER", "UPDATE")),
      canDeleteOffers: hasPermission(permissions, getPermission("OFFER", "DELETE")),

      canViewProfils: hasPermission(permissions, getPermission("PROFIL", "VIEW")),
      canCreateProfils: hasPermission(permissions, getPermission("PROFIL", "CREATE")),
      canUpdateProfils: hasPermission(permissions, getPermission("PROFIL", "UPDATE")),
      canDeleteProfils: hasPermission(permissions, getPermission("PROFIL", "DELETE")),

      canViewSkills: hasPermission(permissions, getPermission("SKILL", "VIEW")),
      canCreateSkills: hasPermission(permissions, getPermission("SKILL", "CREATE")),
      canUpdateSkills: hasPermission(permissions, getPermission("SKILL", "UPDATE")),
      canDeleteSkills: hasPermission(permissions, getPermission("SKILL", "DELETE")),

      canViewCompanies: hasPermission(permissions, getPermission("COMPANY", "VIEW")),
      canCreateCompanies: hasPermission(permissions, getPermission("COMPANY", "CREATE")),
      canUpdateCompanies: hasPermission(permissions, getPermission("COMPANY", "UPDATE")),
      canDeleteCompanies: hasPermission(permissions, getPermission("COMPANY", "DELETE")),

      canCreateProjects: hasPermission(
        permissions,
        getPermission("DEVSTREET_HUB_PROJECT", "CREATE")
      ),
      canStarProjects: hasPermission(
        permissions,
        getPermission("DEVSTREET_HUB_PROJECT", "STAR")
      ),

      isSuperAdmin: hasPermission(permissions, "*"),
      permissions,
    };
  }, [permissions, isAuthenticated]);
};
