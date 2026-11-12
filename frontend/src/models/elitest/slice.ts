import { create } from "zustand";
import type { GetElitestSchema } from "./schema";

interface ElitestState {
  isCreateDialogOpen: boolean;
  selectedElitest: GetElitestSchema | null;
  isShowDialogOpen: boolean;
  isEditMode: boolean;
  openCreateDialog: () => void;
  closeCreateDialog: () => void;
  setSelectedElitest: (item: GetElitestSchema) => void;
  clearSelectedElitest: () => void;
  openShowDialog: () => void;
  closeShowDialog: () => void;
  enableEditMode: () => void;
  disableEditMode: () => void;
}

export const useElitestStore = create<ElitestState>((set) => ({
  isCreateDialogOpen: false,
  selectedElitest: null,
  isShowDialogOpen: false,
  isEditMode: false,
  openCreateDialog: () => set({ isCreateDialogOpen: true }),
  closeCreateDialog: () => set({ isCreateDialogOpen: false }),
  setSelectedElitest: (item) => set({ selectedElitest: item }),
  clearSelectedElitest: () => set({ selectedElitest: null }),
  openShowDialog: () => set({ isShowDialogOpen: true }),
  closeShowDialog: () =>
    set({ isShowDialogOpen: false, isEditMode: false, selectedElitest: null }),
  enableEditMode: () => set({ isEditMode: true }),
  disableEditMode: () => set({ isEditMode: false }),
}));