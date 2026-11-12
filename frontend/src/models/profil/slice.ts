import { create } from "zustand";
import type { GetProfilSchema } from "./schema";

interface ProfilState {
  isCreateDialogOpen: boolean;
  selectedProfil: GetProfilSchema | null;
  isShowDialogOpen: boolean;
  isEditMode: boolean;
  openCreateDialog: () => void;
  closeCreateDialog: () => void;
  setSelectedProfil: (item: GetProfilSchema) => void;
  clearSelectedProfil: () => void;
  openShowDialog: () => void;
  closeShowDialog: () => void;
  enableEditMode: () => void;
  disableEditMode: () => void;
}

export const useProfilStore = create<ProfilState>((set) => ({
  isCreateDialogOpen: false,
  selectedProfil: null,
  isShowDialogOpen: false,
  isEditMode: false,
  openCreateDialog: () => set({ isCreateDialogOpen: true }),
  closeCreateDialog: () => set({ isCreateDialogOpen: false }),
  setSelectedProfil: (item) => set({ selectedProfil: item }),
  clearSelectedProfil: () => set({ selectedProfil: null }),
  openShowDialog: () => set({ isShowDialogOpen: true }),
  closeShowDialog: () =>
    set({ isShowDialogOpen: false, isEditMode: false, selectedProfil: null }),
  enableEditMode: () => set({ isEditMode: true }),
  disableEditMode: () => set({ isEditMode: false }),
}));