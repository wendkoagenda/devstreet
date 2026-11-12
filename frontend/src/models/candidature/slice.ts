import { create } from "zustand";
import type { GetCandidatureSchema } from "./schema";

interface CandidatureState {
  isCreateDialogOpen: boolean;
  selectedCandidature: GetCandidatureSchema | null;
  isShowDialogOpen: boolean;
  isEditMode: boolean;
  openCreateDialog: () => void;
  closeCreateDialog: () => void;
  setSelectedCandidature: (item: GetCandidatureSchema) => void;
  clearSelectedCandidature: () => void;
  openShowDialog: () => void;
  closeShowDialog: () => void;
  enableEditMode: () => void;
  disableEditMode: () => void;
}

export const useCandidatureStore = create<CandidatureState>((set) => ({
  isCreateDialogOpen: false,
  selectedCandidature: null,
  isShowDialogOpen: false,
  isEditMode: false,
  openCreateDialog: () => set({ isCreateDialogOpen: true }),
  closeCreateDialog: () => set({ isCreateDialogOpen: false }),
  setSelectedCandidature: (item) => set({ selectedCandidature: item }),
  clearSelectedCandidature: () => set({ selectedCandidature: null }),
  openShowDialog: () => set({ isShowDialogOpen: true }),
  closeShowDialog: () =>
    set({ isShowDialogOpen: false, isEditMode: false, selectedCandidature: null }),
  enableEditMode: () => set({ isEditMode: true }),
  disableEditMode: () => set({ isEditMode: false }),
}));