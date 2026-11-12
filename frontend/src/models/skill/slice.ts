import { create } from "zustand";
import type { GetSkillSchema } from "./schema";

interface SkillState {
  isCreateDialogOpen: boolean;
  selectedSkill: GetSkillSchema | null;
  isShowDialogOpen: boolean;
  isEditMode: boolean;
  openCreateDialog: () => void;
  closeCreateDialog: () => void;
  setSelectedSkill: (item: GetSkillSchema) => void;
  clearSelectedSkill: () => void;
  openShowDialog: () => void;
  closeShowDialog: () => void;
  enableEditMode: () => void;
  disableEditMode: () => void;
}

export const useSkillStore = create<SkillState>((set) => ({
  isCreateDialogOpen: false,
  selectedSkill: null,
  isShowDialogOpen: false,
  isEditMode: false,
  openCreateDialog: () => set({ isCreateDialogOpen: true }),
  closeCreateDialog: () => set({ isCreateDialogOpen: false }),
  setSelectedSkill: (item) => set({ selectedSkill: item }),
  clearSelectedSkill: () => set({ selectedSkill: null }),
  openShowDialog: () => set({ isShowDialogOpen: true }),
  closeShowDialog: () =>
    set({ isShowDialogOpen: false, isEditMode: false, selectedSkill: null }),
  enableEditMode: () => set({ isEditMode: true }),
  disableEditMode: () => set({ isEditMode: false }),
}));