import { create } from "zustand";
import type { GetSwipeSchema } from "./schema";

interface SwipeState {
  isCreateDialogOpen: boolean;
  selectedSwipe: GetSwipeSchema | null;
  isShowDialogOpen: boolean;
  isEditMode: boolean;
  openCreateDialog: () => void;
  closeCreateDialog: () => void;
  setSelectedSwipe: (item: GetSwipeSchema) => void;
  clearSelectedSwipe: () => void;
  openShowDialog: () => void;
  closeShowDialog: () => void;
  enableEditMode: () => void;
  disableEditMode: () => void;
}

export const useSwipeStore = create<SwipeState>((set) => ({
  isCreateDialogOpen: false,
  selectedSwipe: null,
  isShowDialogOpen: false,
  isEditMode: false,
  openCreateDialog: () => set({ isCreateDialogOpen: true }),
  closeCreateDialog: () => set({ isCreateDialogOpen: false }),
  setSelectedSwipe: (item) => set({ selectedSwipe: item }),
  clearSelectedSwipe: () => set({ selectedSwipe: null }),
  openShowDialog: () => set({ isShowDialogOpen: true }),
  closeShowDialog: () =>
    set({ isShowDialogOpen: false, isEditMode: false, selectedSwipe: null }),
  enableEditMode: () => set({ isEditMode: true }),
  disableEditMode: () => set({ isEditMode: false }),
}));