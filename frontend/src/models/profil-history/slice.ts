import { create } from "zustand";
import type { GetProfilHistorySchema } from "./schema";

interface ProfilHistoryState {
  isCreateDialogOpen: boolean;
  selectedProfilHistory: GetProfilHistorySchema | null;
  isShowDialogOpen: boolean;
  isEditMode: boolean;
  openCreateDialog: () => void;
  closeCreateDialog: () => void;
  setSelectedProfilHistory: (item: GetProfilHistorySchema) => void;
  clearSelectedProfilHistory: () => void;
  openShowDialog: () => void;
  closeShowDialog: () => void;
  enableEditMode: () => void;
  disableEditMode: () => void;
}

export const useProfilHistoryStore = create<ProfilHistoryState>((set) => ({
  isCreateDialogOpen: false,
  selectedProfilHistory: null,
  isShowDialogOpen: false,
  isEditMode: false,
  openCreateDialog: () => set({ isCreateDialogOpen: true }),
  closeCreateDialog: () => set({ isCreateDialogOpen: false }),
  setSelectedProfilHistory: (item) => set({ selectedProfilHistory: item }),
  clearSelectedProfilHistory: () => set({ selectedProfilHistory: null }),
  openShowDialog: () => set({ isShowDialogOpen: true }),
  closeShowDialog: () =>
    set({ isShowDialogOpen: false, isEditMode: false, selectedProfilHistory: null }),
  enableEditMode: () => set({ isEditMode: true }),
  disableEditMode: () => set({ isEditMode: false }),
}));