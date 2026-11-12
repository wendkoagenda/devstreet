import { create } from "zustand";
import type { GetProfilSkillSchema } from "./schema";

interface ProfilSkillState {
  isCreateDialogOpen: boolean;
  selectedProfilSkill: GetProfilSkillSchema | null;
  isShowDialogOpen: boolean;
  isEditMode: boolean;
  openCreateDialog: () => void;
  closeCreateDialog: () => void;
  setSelectedProfilSkill: (item: GetProfilSkillSchema) => void;
  clearSelectedProfilSkill: () => void;
  openShowDialog: () => void;
  closeShowDialog: () => void;
  enableEditMode: () => void;
  disableEditMode: () => void;
}

export const useProfilSkillStore = create<ProfilSkillState>((set) => ({
  isCreateDialogOpen: false,
  selectedProfilSkill: null,
  isShowDialogOpen: false,
  isEditMode: false,
  openCreateDialog: () => set({ isCreateDialogOpen: true }),
  closeCreateDialog: () => set({ isCreateDialogOpen: false }),
  setSelectedProfilSkill: (item) => set({ selectedProfilSkill: item }),
  clearSelectedProfilSkill: () => set({ selectedProfilSkill: null }),
  openShowDialog: () => set({ isShowDialogOpen: true }),
  closeShowDialog: () =>
    set({ isShowDialogOpen: false, isEditMode: false, selectedProfilSkill: null }),
  enableEditMode: () => set({ isEditMode: true }),
  disableEditMode: () => set({ isEditMode: false }),
}));