import { create } from "zustand";
import type { GetPrestationSchema } from "./schema";

interface PrestationState {
  isCreateDialogOpen: boolean;
  selectedPrestation: GetPrestationSchema | null;
  isShowDialogOpen: boolean;
  isEditMode: boolean;
  openCreateDialog: () => void;
  closeCreateDialog: () => void;
  setSelectedPrestation: (item: GetPrestationSchema) => void;
  clearSelectedPrestation: () => void;
  openShowDialog: () => void;
  closeShowDialog: () => void;
  enableEditMode: () => void;
  disableEditMode: () => void;
}

export const usePrestationStore = create<PrestationState>((set) => ({
  isCreateDialogOpen: false,
  selectedPrestation: null,
  isShowDialogOpen: false,
  isEditMode: false,
  openCreateDialog: () => set({ isCreateDialogOpen: true }),
  closeCreateDialog: () => set({ isCreateDialogOpen: false }),
  setSelectedPrestation: (item) => set({ selectedPrestation: item }),
  clearSelectedPrestation: () => set({ selectedPrestation: null }),
  openShowDialog: () => set({ isShowDialogOpen: true }),
  closeShowDialog: () =>
    set({ isShowDialogOpen: false, isEditMode: false, selectedPrestation: null }),
  enableEditMode: () => set({ isEditMode: true }),
  disableEditMode: () => set({ isEditMode: false }),
}));