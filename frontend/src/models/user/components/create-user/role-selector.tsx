import { useGetRolesQuery } from "@/models/roles-permissions/Api";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Check } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { useUserStore } from "../../slice";

interface Role {
  id: number;
  name: string;
}

interface RoleSelectorProps {
  value?: string[];
  onChange?: (value: string[]) => void;
  initialSelectedRoles?: string[];
}

export default function RoleSelector({
  value = [],
  onChange,
  initialSelectedRoles = [],
}: RoleSelectorProps) {
  const { t } = useTranslation();
  const { selectedUser } = useUserStore();
  const { data: roles, isLoading, isError, refetch } = useGetRolesQuery();

  // État local pour gérer la sélection
  const [selectedRoles, setSelectedRoles] = useState<string[]>([]);

  // Ref pour éviter les appels multiples à onChange lors de l'initialisation
  const hasInitialized = useRef(false);

  // Initialisation une seule fois au montage ou quand selectedUser change
  useEffect(() => {
    if (!hasInitialized.current || selectedUser) {
      console.log("RoleSelector initialization:", {
        value,
        initialSelectedRoles,
        selectedUserRoles: selectedUser?.role_names,
      });

      let initialRoles: string[] = [];

      // Priorité 1: value si elle existe et n'est pas vide
      if (value && value.length > 0) {
        initialRoles = value;
      }
      // Priorité 2: rôles de l'utilisateur sélectionné
      else if (selectedUser?.role_names && selectedUser.role_names.length > 0) {
        // Les role_names sont déjà des strings selon le schéma GetUserSchema
        initialRoles = selectedUser.role_names;
        console.log("Setting roles from selectedUser:", initialRoles);
      }
      // Priorité 3: initialSelectedRoles
      else if (initialSelectedRoles && initialSelectedRoles.length > 0) {
        initialRoles = initialSelectedRoles;
        console.log("Setting initial roles:", initialSelectedRoles);
      }

      setSelectedRoles(initialRoles);
      hasInitialized.current = true;

      // Notifier le parent seulement si on a des rôles à définir
      // et que value est vide (pour éviter de surcharger le parent)
      if (
        initialRoles.length > 0 &&
        (!value || value.length === 0) &&
        onChange
      ) {
        onChange(initialRoles);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedUser]); // Seulement quand selectedUser change pour éviter les re-renders inutiles

  // Réinitialiser quand selectedUser change
  useEffect(() => {
    if (selectedUser) {
      hasInitialized.current = false; // Permettre une nouvelle initialisation
    }
  }, [selectedUser]);

  // Synchronisation avec value quand elle change (composant contrôlé)
  useEffect(() => {
    if (hasInitialized.current && value !== undefined) {
      console.log("Syncing with external value:", value);
      setSelectedRoles(value);
    }
  }, [value]);

  // Gestion du toggle des rôles
  const toggleRole = useCallback(
    (roleName: string) => {
      setSelectedRoles((prev) => {
        const newRoles = prev.includes(roleName)
          ? prev.filter((r) => r !== roleName)
          : [...prev, roleName];

        console.log("Role toggled:", { roleName, newRoles });

        // Notifier le parent du changement
        onChange?.(newRoles);
        return newRoles;
      });
    },
    [onChange]
  );

  // Mémoïsation des rôles pour éviter des re-rendus inutiles
  const roleItems = useMemo(() => {
    if (!roles || roles.length === 0) return null;

    return roles.map((role: Role) => {
      const isSelected = selectedRoles.includes(role.name);
      return (
        <Button
          key={role.id}
          type="button"
          variant={isSelected ? "default" : "outline"}
          size="sm"
          onClick={() => toggleRole(role.name)}
          className="gap-2"
          aria-pressed={isSelected}
        >
          {isSelected && <Check className="w-4 h-4" />}
          <span className="capitalize">{role.name}</span>
        </Button>
      );
    });
  }, [roles, selectedRoles, toggleRole]);

  // États de chargement
  if (isLoading) {
    return (
      <div className="space-y-2">
        <div className="flex flex-wrap gap-2">
          {[...Array(3)].map((_, i) => (
            <Skeleton key={i} className="w-24 h-10 rounded-lg" />
          ))}
        </div>
        <p className="text-xs text-muted-foreground">{t("loading_roles")}</p>
      </div>
    );
  }

  // États d'erreur
  if (isError) {
    return (
      <div className="space-y-2">
        <div className="text-sm text-destructive">
          {t("error_loading_roles")}
        </div>
        <Button size="sm" variant="outline" onClick={() => refetch()}>
          {t("retry")}
        </Button>
      </div>
    );
  }

  // Aucun rôle disponible
  if (!roles || roles.length === 0) {
    return (
      <div className="space-y-2">
        <div className="text-sm text-muted-foreground">
          {t("no_roles_available")}
        </div>
        <p className="text-xs text-muted-foreground">
          {t("contact_admin_to_add_roles")}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-2">{roleItems}</div>
      <p className="text-xs text-muted-foreground">
        {t("selected_roles_count", { count: selectedRoles.length })}
      </p>
    </div>
  );
}
