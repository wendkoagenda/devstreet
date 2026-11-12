import { create } from "zustand";
import type { GetAvailabilitySchema } from "./schema";

interface AvailabilityState {
  isCreateDialogOpen: boolean;
  selectedAvailability: GetAvailabilitySchema | null;
  isShowDialogOpen: boolean;
  isEditMode: boolean;
  openCreateDialog: () => void;
  closeCreateDialog: () => void;
  setSelectedAvailability: (item: GetAvailabilitySchema) => void;
  clearSelectedAvailability: () => void;
  openShowDialog: () => void;
  closeShowDialog: () => void;
  enableEditMode: () => void;
  disableEditMode: () => void;
}

export const useAvailabilityStore = create<AvailabilityState>((set) => ({
  isCreateDialogOpen: false,
  selectedAvailability: null,
  isShowDialogOpen: false,
  isEditMode: false,
  openCreateDialog: () => set({ isCreateDialogOpen: true }),
  closeCreateDialog: () => set({ isCreateDialogOpen: false }),
  setSelectedAvailability: (item) => set({ selectedAvailability: item }),
  clearSelectedAvailability: () => set({ selectedAvailability: null }),
  openShowDialog: () => set({ isShowDialogOpen: true }),
  closeShowDialog: () =>
    set({ isShowDialogOpen: false, isEditMode: false, selectedAvailability: null }),
  enableEditMode: () => set({ isEditMode: true }),
  disableEditMode: () => set({ isEditMode: false }),
}));