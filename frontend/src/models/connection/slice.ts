import { create } from "zustand";
import type { GetConnectionSchema } from "./schema";

interface ConnectionState {
  isCreateDialogOpen: boolean;
  selectedConnection: GetConnectionSchema | null;
  isShowDialogOpen: boolean;
  isEditMode: boolean;
  openCreateDialog: () => void;
  closeCreateDialog: () => void;
  setSelectedConnection: (item: GetConnectionSchema) => void;
  clearSelectedConnection: () => void;
  openShowDialog: () => void;
  closeShowDialog: () => void;
  enableEditMode: () => void;
  disableEditMode: () => void;
}

export const useConnectionStore = create<ConnectionState>((set) => ({
  isCreateDialogOpen: false,
  selectedConnection: null,
  isShowDialogOpen: false,
  isEditMode: false,
  openCreateDialog: () => set({ isCreateDialogOpen: true }),
  closeCreateDialog: () => set({ isCreateDialogOpen: false }),
  setSelectedConnection: (item) => set({ selectedConnection: item }),
  clearSelectedConnection: () => set({ selectedConnection: null }),
  openShowDialog: () => set({ isShowDialogOpen: true }),
  closeShowDialog: () =>
    set({ isShowDialogOpen: false, isEditMode: false, selectedConnection: null }),
  enableEditMode: () => set({ isEditMode: true }),
  disableEditMode: () => set({ isEditMode: false }),
}));