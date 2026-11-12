import { create } from "zustand";
import type { GetExperienceSchema } from "./schema";

interface ExperienceState {
  isCreateDialogOpen: boolean;
  selectedExperience: GetExperienceSchema | null;
  isShowDialogOpen: boolean;
  isEditMode: boolean;
  openCreateDialog: () => void;
  closeCreateDialog: () => void;
  setSelectedExperience: (item: GetExperienceSchema) => void;
  clearSelectedExperience: () => void;
  openShowDialog: () => void;
  closeShowDialog: () => void;
  enableEditMode: () => void;
  disableEditMode: () => void;
}

export const useExperienceStore = create<ExperienceState>((set) => ({
  isCreateDialogOpen: false,
  selectedExperience: null,
  isShowDialogOpen: false,
  isEditMode: false,
  openCreateDialog: () => set({ isCreateDialogOpen: true }),
  closeCreateDialog: () => set({ isCreateDialogOpen: false }),
  setSelectedExperience: (item) => set({ selectedExperience: item }),
  clearSelectedExperience: () => set({ selectedExperience: null }),
  openShowDialog: () => set({ isShowDialogOpen: true }),
  closeShowDialog: () =>
    set({ isShowDialogOpen: false, isEditMode: false, selectedExperience: null }),
  enableEditMode: () => set({ isEditMode: true }),
  disableEditMode: () => set({ isEditMode: false }),
}));