import { create } from "zustand";
import type { GetFusionSchema } from "./schema";

interface FusionState {
  isCreateDialogOpen: boolean;
  selectedFusion: GetFusionSchema | null;
  isShowDialogOpen: boolean;
  isEditMode: boolean;
  openCreateDialog: () => void;
  closeCreateDialog: () => void;
  setSelectedFusion: (item: GetFusionSchema) => void;
  clearSelectedFusion: () => void;
  openShowDialog: () => void;
  closeShowDialog: () => void;
  enableEditMode: () => void;
  disableEditMode: () => void;
}

export const useFusionStore = create<FusionState>((set) => ({
  isCreateDialogOpen: false,
  selectedFusion: null,
  isShowDialogOpen: false,
  isEditMode: false,
  openCreateDialog: () => set({ isCreateDialogOpen: true }),
  closeCreateDialog: () => set({ isCreateDialogOpen: false }),
  setSelectedFusion: (item) => set({ selectedFusion: item }),
  clearSelectedFusion: () => set({ selectedFusion: null }),
  openShowDialog: () => set({ isShowDialogOpen: true }),
  closeShowDialog: () =>
    set({ isShowDialogOpen: false, isEditMode: false, selectedFusion: null }),
  enableEditMode: () => set({ isEditMode: true }),
  disableEditMode: () => set({ isEditMode: false }),
}));