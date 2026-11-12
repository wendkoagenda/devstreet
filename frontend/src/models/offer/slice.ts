import { create } from "zustand";
import type { GetOfferSchema } from "./schema";

interface OfferState {
  isCreateDialogOpen: boolean;
  selectedOffer: GetOfferSchema | null;
  isShowDialogOpen: boolean;
  isEditMode: boolean;
  openCreateDialog: () => void;
  closeCreateDialog: () => void;
  setSelectedOffer: (item: GetOfferSchema) => void;
  clearSelectedOffer: () => void;
  openShowDialog: () => void;
  closeShowDialog: () => void;
  enableEditMode: () => void;
  disableEditMode: () => void;
}

export const useOfferStore = create<OfferState>((set) => ({
  isCreateDialogOpen: false,
  selectedOffer: null,
  isShowDialogOpen: false,
  isEditMode: false,
  openCreateDialog: () => set({ isCreateDialogOpen: true }),
  closeCreateDialog: () => set({ isCreateDialogOpen: false }),
  setSelectedOffer: (item) => set({ selectedOffer: item }),
  clearSelectedOffer: () => set({ selectedOffer: null }),
  openShowDialog: () => set({ isShowDialogOpen: true }),
  closeShowDialog: () =>
    set({ isShowDialogOpen: false, isEditMode: false, selectedOffer: null }),
  enableEditMode: () => set({ isEditMode: true }),
  disableEditMode: () => set({ isEditMode: false }),
}));