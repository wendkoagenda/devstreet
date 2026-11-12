import React, { useEffect, useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { Role } from "../schema";

type RoleFormData = {
  name: string;
  description: string;
};

interface RoleFormModalProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  editingRole: Role | null;
  formData: RoleFormData;
  onFormChange: (field: keyof RoleFormData, value: string) => void;
  onSubmit: () => Promise<void>;
  isLoading?: boolean;
}

const RoleFormModal: React.FC<RoleFormModalProps> = ({
  isOpen,
  onOpenChange,
  editingRole,
  formData,
  onFormChange,
  onSubmit,
  isLoading = false,
}) => {
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (isOpen) {
      setErrors({});
    }
  }, [isOpen]);

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.name.trim()) {
      newErrors.name = "Le nom est obligatoire";
    } else if (formData.name.length > 30) {
      newErrors.name = "Maximum 30 caractères";
    }

    if (formData.description && formData.description.length > 100) {
      newErrors.description = "Maximum 100 caractères";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      try {
        await onSubmit();
        onOpenChange(false);
      } catch {
        setErrors({ submit: "Erreur lors de la sauvegarde" });
      }
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    onFormChange(name as keyof RoleFormData, value);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>
              {editingRole ? "Modifier le rôle" : "Nouveau rôle"}
            </DialogTitle>
            <DialogDescription>
              {editingRole
                ? "Mettez à jour les détails du rôle"
                : "Remplissez les détails du nouveau rôle"}
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">Nom*</Label>
              <Input
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="Nom du rôle"
                className={errors.name ? "border-destructive" : ""}
              />
              {errors.name && (
                <p className="text-destructive text-xs mt-1">{errors.name}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                name="description"
                value={formData.description || ""}
                onChange={handleInputChange}
                placeholder="Description du rôle (optionnel)"
                className={errors.description ? "border-destructive" : ""}
              />
              {errors.description && (
                <p className="text-destructive text-xs mt-1">
                  {errors.description}
                </p>
              )}
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isLoading}
            >
              Annuler
            </Button>

            <Button type="submit" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {editingRole ? "Mise à jour..." : "Création..."}
                </>
              ) : editingRole ? (
                "Mettre à jour"
              ) : (
                "Créer"
              )}
            </Button>
          </DialogFooter>

          {errors.submit && (
            <p className="text-destructive text-xs text-center mt-2">
              {errors.submit}
            </p>
          )}
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default RoleFormModal;
