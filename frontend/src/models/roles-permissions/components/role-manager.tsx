import React, { useCallback, useState, useMemo } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PlusCircle, Pencil, Trash2, Search, X, Users } from "lucide-react";
import { useTranslation } from "react-i18next";
import IconAndTextDisplayerAsTitle from "@/helpers/displayers/icon-and-text-displayer-as-title";
import { Icons } from "@/lib/constants/icons";
import { usePermissions } from "@/hooks/use-permissions";
import type { Role } from "../schema";

interface RoleManagerProps {
  roles: Role[];
  selectedRole: Role | null;
  onSelectRole: (role: Role) => void;
  onEditRole: (role: Role) => void;
  onDeleteRole: (id: number) => void;
  onOpenModal: () => void;
}

const RoleManager: React.FC<RoleManagerProps> = ({
  roles,
  selectedRole,
  onSelectRole,
  onEditRole,
  onDeleteRole,
  onOpenModal,
}) => {
  const { t } = useTranslation();
  const [searchTerm, setSearchTerm] = useState("");
  // Utilisation du hook pour obtenir les permissions
  const { canCreateRoles, canUpdateRoles, canDeleteRoles } = usePermissions();

  // Filtrage des rôles selon le terme de recherche
  const filteredRoles = useMemo(() => {
    if (!searchTerm.trim()) return roles;

    const searchLower = searchTerm.toLowerCase();
    return roles.filter(
      (role) =>
        role.name.toLowerCase().includes(searchLower) ||
        (role.description &&
          role.description.toLowerCase().includes(searchLower))
    );
  }, [roles, searchTerm]);

  const handleEdit = useCallback(
    (e: React.MouseEvent, role: Role) => {
      e.stopPropagation();
      onEditRole(role);
    },
    [onEditRole]
  );

  const handleDelete = useCallback(
    (e: React.MouseEvent, id: number) => {
      e.stopPropagation();
      onDeleteRole(id);
    },
    [onDeleteRole]
  );

  return (
    <Card className="w-2/3 h-full flex flex-col">
      <CardHeader className="flex-shrink-0 pb-4">
        <CardTitle className="flex justify-between items-center">
          <IconAndTextDisplayerAsTitle
            Icon={Icons.Roles}
            text={t("roleManagement.roles")}
          />

          {/* Bouton d'ajout conditionnel */}
          {canCreateRoles && (
            <Button
              onClick={onOpenModal}
              aria-label={t("roleManagement.addRole")}
              data-testid="add-role-button"
            >
              <PlusCircle className="h-4 w-4 mr-2" />
              {t("roleManagement.newRole")}
            </Button>
          )}
        </CardTitle>

        {/* Champ de recherche */}
        <div className="mt-4 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
          <Input
            type="text"
            placeholder={t("roleManagement.searchRoles", {
              defaultValue: "Rechercher des rôles...",
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
      </CardHeader>

      <CardContent className="flex-1 overflow-hidden p-0">
        {filteredRoles.length > 0 ? (
          <div className="overflow-y-auto h-full">
            <Table>
              <TableHeader className="sticky top-0 bg-background/95 backdrop-blur-sm z-10">
                <TableRow>
                  <TableHead className="px-6 py-3">
                    {t("roleManagement.roleName")}
                  </TableHead>
                  <TableHead className="px-6 py-3">
                    {t("roleManagement.roleDescription")}
                  </TableHead>
                  <TableHead className="text-right px-6 py-3">
                    {t("common.actions")}
                  </TableHead>
                </TableRow>
              </TableHeader>

              <TableBody>
                {filteredRoles.map((role) => (
                  <TableRow
                    key={role.id}
                    className={`cursor-pointer transition-colors hover:bg-muted/50 ${
                      selectedRole?.id === role.id ? "bg-secondary" : ""
                    }`}
                    onClick={() => onSelectRole(role)}
                    aria-selected={selectedRole?.id === role.id}
                    data-testid={`role-row-${role.id}`}
                  >
                    <TableCell className="px-6 py-4 font-medium">
                      {role.name}
                    </TableCell>
                    <TableCell className="px-6 py-4 text-muted-foreground">
                      {role.description || "-"}
                    </TableCell>

                    <TableCell className="text-right px-6 py-4">
                      <div className="flex justify-end gap-2">
                        {/* Bouton d'édition conditionnel */}
                        {canUpdateRoles ? (
                          <Button
                            size="icon"
                            variant="ghost"
                            aria-label={t("roleManagement.editRole")}
                            onClick={(e) => handleEdit(e, role)}
                            data-testid={`edit-role-${role.id}`}
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                        ) : (
                          <div className="w-10 text-center text-muted-foreground">
                            -
                          </div>
                        )}

                        {/* Bouton de suppression conditionnel */}
                        {canDeleteRoles ? (
                          <Button
                            size="icon"
                            variant="ghost"
                            aria-label={t("roleManagement.deleteRole")}
                            className="text-destructive hover:text-destructive hover:bg-destructive/10"
                            onClick={(e) => handleDelete(e, role.id)}
                            data-testid={`delete-role-${role.id}`}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        ) : (
                          <div className="w-10 text-center text-muted-foreground">
                            -
                          </div>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full py-12 text-center">
            <div className="bg-muted/50 p-6 rounded-full mb-6">
              <Users className="h-12 w-12 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-medium mb-2">
              {searchTerm
                ? t("roleManagement.noRolesFound", {
                    defaultValue: "Aucun rôle trouvé",
                  })
                : t("roleManagement.noRoles", {
                    defaultValue: "Aucun rôle disponible",
                  })}
            </h3>
            <p className="text-muted-foreground text-sm mb-4">
              {searchTerm
                ? t("roleManagement.tryDifferentSearch", {
                    defaultValue: "Essayez avec un autre terme de recherche",
                  })
                : t("roleManagement.createFirstRole", {
                    defaultValue: "Créez votre premier rôle pour commencer",
                  })}
            </p>
            {searchTerm ? (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setSearchTerm("")}
              >
                {t("roleManagement.clearSearch", {
                  defaultValue: "Effacer la recherche",
                })}
              </Button>
            ) : (
              canCreateRoles && (
                <Button onClick={onOpenModal}>
                  <PlusCircle className="h-4 w-4 mr-2" />
                  {t("roleManagement.createRole", {
                    defaultValue: "Créer un rôle",
                  })}
                </Button>
              )
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default React.memo(RoleManager);
