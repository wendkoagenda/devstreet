import { create } from "zustand";
import type { GetGadoSchema } from "./schema";

interface GadoState {
  isCreateDialogOpen: boolean;
  selectedGado: GetGadoSchema | null;
  isShowDialogOpen: boolean;
  isEditMode: boolean;
  openCreateDialog: () => void;
  closeCreateDialog: () => void;
  setSelectedGado: (item: GetGadoSchema) => void;
  clearSelectedGado: () => void;
  openShowDialog: () => void;
  closeShowDialog: () => void;
  enableEditMode: () => void;
  disableEditMode: () => void;
}

export const useGadoStore = create<GadoState>((set) => ({
  isCreateDialogOpen: false,
  selectedGado: null,
  isShowDialogOpen: false,
  isEditMode: false,
  openCreateDialog: () => set({ isCreateDialogOpen: true }),
  closeCreateDialog: () => set({ isCreateDialogOpen: false }),
  setSelectedGado: (item) => set({ selectedGado: item }),
  clearSelectedGado: () => set({ selectedGado: null }),
  openShowDialog: () => set({ isShowDialogOpen: true }),
  closeShowDialog: () =>
    set({ isShowDialogOpen: false, isEditMode: false, selectedGado: null }),
  enableEditMode: () => set({ isEditMode: true }),
  disableEditMode: () => set({ isEditMode: false }),
}));