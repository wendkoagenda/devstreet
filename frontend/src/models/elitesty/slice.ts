import { create } from "zustand";
import type { GetElitestySchema } from "./schema";

interface ElitestyState {
  isCreateDialogOpen: boolean;
  selectedElitesty: GetElitestySchema | null;
  isShowDialogOpen: boolean;
  isEditMode: boolean;
  openCreateDialog: () => void;
  closeCreateDialog: () => void;
  setSelectedElitesty: (item: GetElitestySchema) => void;
  clearSelectedElitesty: () => void;
  openShowDialog: () => void;
  closeShowDialog: () => void;
  enableEditMode: () => void;
  disableEditMode: () => void;
}

export const useElitestyStore = create<ElitestyState>((set) => ({
  isCreateDialogOpen: false,
  selectedElitesty: null,
  isShowDialogOpen: false,
  isEditMode: false,
  openCreateDialog: () => set({ isCreateDialogOpen: true }),
  closeCreateDialog: () => set({ isCreateDialogOpen: false }),
  setSelectedElitesty: (item) => set({ selectedElitesty: item }),
  clearSelectedElitesty: () => set({ selectedElitesty: null }),
  openShowDialog: () => set({ isShowDialogOpen: true }),
  closeShowDialog: () =>
    set({ isShowDialogOpen: false, isEditMode: false, selectedElitesty: null }),
  enableEditMode: () => set({ isEditMode: true }),
  disableEditMode: () => set({ isEditMode: false }),
}));