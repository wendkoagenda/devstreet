import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  useAssignPermissionToRoleMutation,
  useCreateRoleMutation,
  useDeleteRoleMutation,
  useGetPermissionsQuery,
  useGetRolesQuery,
  useUpdateRoleMutation,
} from "../Api";
import type { Role } from "../schema";

import { toast } from "sonner";

import PageTitleDisplayer from "@/helpers/displayers/page-title-displayer";
import { CardLoader } from "@/helpers/loaders/card-loader";
import { usePermissions } from "@/hooks/use-permissions";
import { useTranslation } from "react-i18next";
import PermissionAssignment from "../components/permission-assignement";
import RoleFormModal from "../components/role-form-modal";
import RoleManager from "../components/role-manager";

interface RoleFormData {
  name: string;
  description: string;
}

const RolePermissionManagement: React.FC = () => {
  const { t } = useTranslation();

  const { data: permissions = [], isLoading: permsLoading } =
    useGetPermissionsQuery();

  const {
    data: roles = [],
    isLoading: rolesLoading,
    refetch: refetchRoles,
  } = useGetRolesQuery();

  const [createRole] = useCreateRoleMutation();
  const [updateRole] = useUpdateRoleMutation();
  const [deleteRole] = useDeleteRoleMutation();
  const [assignPermissionToRole] = useAssignPermissionToRoleMutation();

  const [isRoleModalOpen, setIsRoleModalOpen] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [selectedRoleId, setSelectedRoleId] = useState<number | null>(null);
  const [selectedPermissions, setSelectedPermissions] = useState<number[]>([]);
  const [isSavingPermissions, setIsSavingPermissions] = useState(false);

  const [roleFormData, setRoleFormData] = useState<RoleFormData>({
    name: "",
    description: "",
  });

  const { canViewRoles, canCreateRoles } = usePermissions();

  useEffect(() => {
    if (selectedRoleId && roles.length > 0) {
      const foundRole = roles.find((role) => role.id === selectedRoleId);
      if (foundRole) {
        setSelectedRole(foundRole);
      } else if (selectedRole) {
        setSelectedRole(null);
        setSelectedRoleId(null);
        setSelectedPermissions([]);
      }
    }
  }, [roles, selectedRoleId, selectedRole]);

  useEffect(() => {
    if (selectedRole?.permissions) {
      setSelectedPermissions(selectedRole.permissions.map((p) => p.id));
    } else {
      setSelectedPermissions([]);
    }
  }, [selectedRole]);

  const handleSelectRole = useCallback((role: Role) => {
    setSelectedRole(role);
    setSelectedRoleId(role.id);
  }, []);

  const handleRoleChange = useCallback(
    (field: keyof RoleFormData, value: string) => {
      setRoleFormData((prev) => ({ ...prev, [field]: value }));
    },
    []
  );

  const handleRoleSubmit = useCallback(async () => {
    try {
      if (editingRole) {
        await updateRole({
          id: editingRole.id,
          ...roleFormData,
        }).unwrap();
        toast.success(t("roleManagement.roleUpdated"));
        refetchRoles();
      } else {
        const response = await createRole(roleFormData).unwrap();
        const newRoleId = response.id;
        if (newRoleId) {
          setSelectedRoleId(newRoleId);
        }
        toast.success(t("roleManagement.roleCreated"));
      }
      setIsRoleModalOpen(false);
      setEditingRole(null);
      setRoleFormData({ name: "", description: "" });
      refetchRoles();
    } catch (error: unknown) {
      const errorMessage =
        error && typeof error === "object" && "data" in error
          ? (error as { data?: { message?: string } }).data?.message
          : undefined;
      toast.error(errorMessage || t("roleManagement.error.updateRole"));
    }
  }, [editingRole, roleFormData, updateRole, createRole, refetchRoles, t]);

  const handleDeleteRole = useCallback(
    async (id: number) => {
      try {
        await deleteRole(id).unwrap();
        toast.success(t("roleManagement.roleDeleted"));

        if (selectedRole?.id === id) {
          setSelectedRole(null);
          setSelectedRoleId(null);
          setSelectedPermissions([]);
        }

        refetchRoles();
      } catch (error: unknown) {
        const errorMessage =
          error && typeof error === "object" && "data" in error
            ? (error as { data?: { message?: string } }).data?.message
            : undefined;
        toast.error(errorMessage || t("roleManagement.error.deleteRole"));
      }
    },
    [deleteRole, refetchRoles, selectedRole, t]
  );

  const handlePermissionToggle = useCallback((permissionId: number) => {
    setSelectedPermissions((prev) =>
      prev.includes(permissionId)
        ? prev.filter((id) => id !== permissionId)
        : [...prev, permissionId]
    );
  }, []);

  const handleAssignPermissions = useCallback(async () => {
    if (!selectedRole) return;

    try {
      setIsSavingPermissions(true);

      const permissionCodes = permissions
        .filter((p) => selectedPermissions.includes(p.id))
        .map((p) => p.code);

      await assignPermissionToRole({
        id: selectedRole.id,
        permission_codes: permissionCodes,
      }).unwrap();

      toast.success(t("roleManagement.permissionsAssigned"));

      // Refetch to get updated role with permissions
      refetchRoles();
    } catch (error: unknown) {
      const errorMessage =
        error && typeof error === "object" && "data" in error
          ? (error as { data?: { message?: string } }).data?.message
          : undefined;
      toast.error(errorMessage || t("roleManagement.error.assignPermissions"));
    } finally {
      setIsSavingPermissions(false);
    }
  }, [
    selectedRole,
    selectedPermissions,
    permissions,
    assignPermissionToRole,
    refetchRoles,
    t,
  ]);

  const handleClearSelection = useCallback(() => {
    setSelectedRole(null);
    setSelectedRoleId(null);
    setSelectedPermissions([]);
  }, []);

  const handleOpenCreateModal = useCallback(() => {
    setEditingRole(null);
    setRoleFormData({ name: "", description: "" });
    setIsRoleModalOpen(true);
  }, []);

  const handleOpenEditModal = useCallback((role: Role) => {
    setEditingRole(role);
    setRoleFormData({
      name: role.name,
      description: role.description || "",
    });
    setIsRoleModalOpen(true);
  }, []);

  const isLoading = useMemo(
    () => permsLoading || rolesLoading,
    [permsLoading, rolesLoading]
  );

  if (isLoading) {
    return <CardLoader />;
  }

  if (!canViewRoles) {
    return <div className="text-center my-32">{t("common.accessDenied")}</div>;
  }

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <div className="flex-shrink-0">
        <PageTitleDisplayer
          title={t("roles.name")}
          description={t("roles.description")}
        />
      </div>

      <div className="flex-1 p-6 flex gap-6 min-h-0">
        <RoleManager
          roles={roles}
          selectedRole={selectedRole}
          onSelectRole={handleSelectRole}
          onEditRole={handleOpenEditModal}
          onDeleteRole={handleDeleteRole}
          onOpenModal={handleOpenCreateModal}
        />

        {canCreateRoles ? (
          <PermissionAssignment
            permissions={permissions}
            selectedRole={selectedRole}
            selectedPermissions={selectedPermissions}
            onPermissionToggle={handlePermissionToggle}
            onAssignPermissions={handleAssignPermissions}
            onClearSelection={handleClearSelection}
            isSaving={isSavingPermissions}
            maintainRoleSelection={false}
          />
        ) : (
          <div></div>
        )}

        <RoleFormModal
          isOpen={isRoleModalOpen}
          onOpenChange={setIsRoleModalOpen}
          editingRole={editingRole}
          formData={roleFormData}
          onFormChange={handleRoleChange}
          onSubmit={handleRoleSubmit}
        />
      </div>
    </div>
  );
};

export default RolePermissionManagement;
