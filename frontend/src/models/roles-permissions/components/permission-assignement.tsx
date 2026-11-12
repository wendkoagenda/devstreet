import React, {
  useMemo,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Check, Key, Loader2, Search, X } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Permission, Role } from "../schema";

interface PermissionAssignmentProps {
  permissions: Permission[];
  selectedRole: Role | null;
  selectedPermissions: number[];
  onPermissionToggle: (permissionId: number) => void;
  onAssignPermissions: () => void;
  onClearSelection?: () => void;
  isSaving: boolean;
  maintainRoleSelection?: boolean;
}

const PermissionAssignment: React.FC<PermissionAssignmentProps> = ({
  permissions,
  selectedRole,
  selectedPermissions,
  onPermissionToggle,
  onAssignPermissions,
  isSaving,
}) => {
  const { t } = useTranslation();
  const wasSaving = useRef(false);
  const [searchTerm, setSearchTerm] = useState("");

  // Extraction des composants de permission avec séparateur "."
  const extractModel = useCallback((code: string) => code.split(".")[0], []);
  const extractAction = useCallback(
    (code: string) => code.split(".")[1] || code,
    []
  );

  // Traductions
  const translateModel = useCallback(
    (model: string) => t(`permissionModels.${model}`, { defaultValue: model }),
    [t]
  );

  const translateAction = useCallback(
    (action: string) =>
      t(`permissionActions.${action}`, { defaultValue: action }),
    [t]
  );

  // Regroupement des permissions par modèle avec filtrage
  const groupedPermissions = useMemo(() => {
    const groups: Record<string, Permission[]> = {};

    // Filtrer les permissions selon le terme de recherche
    const filteredPermissions = permissions.filter((permission) => {
      if (!searchTerm.trim()) return true;

      const model = extractModel(permission.code);
      const action = extractAction(permission.code);
      const modelTranslated = translateModel(model).toLowerCase();
      const actionTranslated = translateAction(action).toLowerCase();
      const searchLower = searchTerm.toLowerCase();

      return (
        model.toLowerCase().includes(searchLower) ||
        action.toLowerCase().includes(searchLower) ||
        modelTranslated.includes(searchLower) ||
        actionTranslated.includes(searchLower) ||
        permission.code.toLowerCase().includes(searchLower)
      );
    });

    filteredPermissions.forEach((permission) => {
      const model = extractModel(permission.code);
      if (!groups[model]) groups[model] = [];
      groups[model].push(permission);
    });

    return Object.entries(groups)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([model, perms]) => ({
        model,
        modelLabel: translateModel(model),
        permissions: perms.sort((a, b) => {
          const aTranslated = translateAction(extractAction(a.code));
          const bTranslated = translateAction(extractAction(b.code));
          return aTranslated.localeCompare(bTranslated);
        }),
      }));
  }, [
    permissions,
    searchTerm,
    extractModel,
    extractAction,
    translateModel,
    translateAction,
  ]);

  // Vérification de sélection
  const isPermissionSelected = useCallback(
    (id: number) => selectedPermissions.includes(id),
    [selectedPermissions]
  );

  // Détection des changements
  const hasChanges = useMemo(() => {
    if (!selectedRole?.permissions) return selectedPermissions.length > 0;

    const currentIds = selectedRole.permissions.map((p) => p.id);
    return (
      currentIds.length !== selectedPermissions.length ||
      currentIds.some((id) => !selectedPermissions.includes(id))
    );
  }, [selectedRole, selectedPermissions]);

  // Rechargement après sauvegarde
  useEffect(() => {
    // Vérifie si on vient de terminer une sauvegarde
    if (wasSaving.current && !isSaving) {
      window.location.reload();
    }

    // Mise à jour de la référence pour le prochain cycle
    wasSaving.current = isSaving;
  }, [isSaving]);

  return (
    <Card className="w-1/3 h-full flex flex-col">
      <CardHeader className="flex-shrink-0 pb-4">
        <CardTitle className="font-medium text-lg">
          {selectedRole
            ? `${t("roleManagement.assignPermissionsToRole")}: ${
                selectedRole.name
              }`
            : t("roleManagement.assignPermissions")}
        </CardTitle>
        <CardDescription>
          {selectedRole
            ? t("roleManagement.assignPermissionsDescription")
            : t("roleManagement.selectRoleFirst")}
        </CardDescription>

        {selectedRole && (
          <div className="mt-4 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input
              type="text"
              placeholder={t("roleManagement.searchPermissions", {
                defaultValue: "Rechercher des permissions...",
              })}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-10"
            />
            {searchTerm && (
              <Button
                variant="ghost"
                size="sm"
                className="absolute right-1 top-1/2 transform -translate-y-1/2 h-8 w-8 p-0"
                onClick={() => setSearchTerm("")}
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        )}
      </CardHeader>

      <CardContent className="flex-1 overflow-y-auto px-6 py-0">
        {selectedRole ? (
          groupedPermissions.length > 0 ? (
            <div className="space-y-6 pb-4">
              {groupedPermissions.map(({ model, modelLabel, permissions }) => (
                <div key={model} className="space-y-3">
                  <h3 className="font-medium text-base border-b pb-2 text-foreground sticky top-0 bg-background/95 backdrop-blur-sm z-10">
                    {modelLabel}
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {permissions.map((permission) => (
                      <div
                        key={permission.id}
                        className="flex items-start space-x-2 p-2 border rounded-md hover:bg-muted/30 transition-colors"
                      >
                        <Checkbox
                          id={`perm-${permission.id}`}
                          checked={isPermissionSelected(permission.id)}
                          onCheckedChange={() =>
                            onPermissionToggle(permission.id)
                          }
                          disabled={isSaving}
                        />
                        <Label
                          htmlFor={`perm-${permission.id}`}
                          className="font-medium cursor-pointer flex-1 text-sm leading-5"
                        >
                          {translateAction(extractAction(permission.code))}
                        </Label>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full py-12 text-center">
              <div className="bg-muted/50 p-6 rounded-full mb-6">
                <Search className="h-12 w-12 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-medium mb-2">
                {t("roleManagement.noPermissionsFound", {
                  defaultValue: "Aucune permission trouvée",
                })}
              </h3>
              <p className="text-muted-foreground text-sm mb-4">
                {t("roleManagement.tryDifferentSearch", {
                  defaultValue: "Essayez avec un autre terme de recherche",
                })}
              </p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setSearchTerm("")}
              >
                {t("roleManagement.clearSearch", {
                  defaultValue: "Effacer la recherche",
                })}
              </Button>
            </div>
          )
        ) : (
          <div className="flex flex-col items-center justify-center h-full py-12 text-center">
            <div className="bg-muted/50 p-6 rounded-full mb-6">
              <Key className="h-12 w-12 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-medium mb-2">
              {t("roleManagement.noRoleSelected")}
            </h3>
            <p className="text-muted-foreground text-sm">
              {t("roleManagement.selectRoleFirst")}
            </p>
          </div>
        )}
      </CardContent>

      {selectedRole && (
        <div className="flex-shrink-0 p-6 pt-4 bg-background border-t">
          <Button
            className="w-full"
            onClick={onAssignPermissions}
            disabled={isSaving || !hasChanges}
            variant={hasChanges ? "default" : "secondary"}
          >
            {isSaving ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                {t("roleManagement.savingPermissions")}
              </>
            ) : (
              <>
                <Check className="h-4 w-4 mr-2" />
                {hasChanges
                  ? t("roleManagement.savePermissions")
                  : t("roleManagement.permissionsSaved")}
              </>
            )}
          </Button>
        </div>
      )}
    </Card>
  );
};

export default React.memo(PermissionAssignment);
