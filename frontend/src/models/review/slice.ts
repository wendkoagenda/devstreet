import { create } from "zustand";
import type { GetReviewSchema } from "./schema";

interface ReviewState {
  isCreateDialogOpen: boolean;
  selectedReview: GetReviewSchema | null;
  isShowDialogOpen: boolean;
  isEditMode: boolean;
  openCreateDialog: () => void;
  closeCreateDialog: () => void;
  setSelectedReview: (item: GetReviewSchema) => void;
  clearSelectedReview: () => void;
  openShowDialog: () => void;
  closeShowDialog: () => void;
  enableEditMode: () => void;
  disableEditMode: () => void;
}

export const useReviewStore = create<ReviewState>((set) => ({
  isCreateDialogOpen: false,
  selectedReview: null,
  isShowDialogOpen: false,
  isEditMode: false,
  openCreateDialog: () => set({ isCreateDialogOpen: true }),
  closeCreateDialog: () => set({ isCreateDialogOpen: false }),
  setSelectedReview: (item) => set({ selectedReview: item }),
  clearSelectedReview: () => set({ selectedReview: null }),
  openShowDialog: () => set({ isShowDialogOpen: true }),
  closeShowDialog: () =>
    set({ isShowDialogOpen: false, isEditMode: false, selectedReview: null }),
  enableEditMode: () => set({ isEditMode: true }),
  disableEditMode: () => set({ isEditMode: false }),
}));