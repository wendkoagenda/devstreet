import { create } from "zustand";
import type { GetCompanySchema } from "./schema";

interface CompanyState {
  isCreateDialogOpen: boolean;
  selectedCompany: GetCompanySchema | null;
  isShowDialogOpen: boolean;
  isEditMode: boolean;
  openCreateDialog: () => void;
  closeCreateDialog: () => void;
  setSelectedCompany: (item: GetCompanySchema) => void;
  clearSelectedCompany: () => void;
  openShowDialog: () => void;
  closeShowDialog: () => void;
  enableEditMode: () => void;
  disableEditMode: () => void;
}

export const useCompanyStore = create<CompanyState>((set) => ({
  isCreateDialogOpen: false,
  selectedCompany: null,
  isShowDialogOpen: false,
  isEditMode: false,
  openCreateDialog: () => set({ isCreateDialogOpen: true }),
  closeCreateDialog: () => set({ isCreateDialogOpen: false }),
  setSelectedCompany: (item) => set({ selectedCompany: item }),
  clearSelectedCompany: () => set({ selectedCompany: null }),
  openShowDialog: () => set({ isShowDialogOpen: true }),
  closeShowDialog: () =>
    set({ isShowDialogOpen: false, isEditMode: false, selectedCompany: null }),
  enableEditMode: () => set({ isEditMode: true }),
  disableEditMode: () => set({ isEditMode: false }),
}));