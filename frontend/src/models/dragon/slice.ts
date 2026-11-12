import { create } from "zustand";
import type { GetDragonSchema } from "./schema";

interface DragonState {
  isCreateDialogOpen: boolean;
  selectedDragon: GetDragonSchema | null;
  isShowDialogOpen: boolean;
  isEditMode: boolean;
  openCreateDialog: () => void;
  closeCreateDialog: () => void;
  setSelectedDragon: (item: GetDragonSchema) => void;
  clearSelectedDragon: () => void;
  openShowDialog: () => void;
  closeShowDialog: () => void;
  enableEditMode: () => void;
  disableEditMode: () => void;
}

export const useDragonStore = create<DragonState>((set) => ({
  isCreateDialogOpen: false,
  selectedDragon: null,
  isShowDialogOpen: false,
  isEditMode: false,
  openCreateDialog: () => set({ isCreateDialogOpen: true }),
  closeCreateDialog: () => set({ isCreateDialogOpen: false }),
  setSelectedDragon: (item) => set({ selectedDragon: item }),
  clearSelectedDragon: () => set({ selectedDragon: null }),
  openShowDialog: () => set({ isShowDialogOpen: true }),
  closeShowDialog: () =>
    set({ isShowDialogOpen: false, isEditMode: false, selectedDragon: null }),
  enableEditMode: () => set({ isEditMode: true }),
  disableEditMode: () => set({ isEditMode: false }),
}));