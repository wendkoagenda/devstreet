import { create } from "zustand";
import type { GetUserSchema } from "./schema";

interface UserState {
  isCreateUserDialogOpen: boolean;
  selectedUser: GetUserSchema | null;
  isShowUserDialogOpen: boolean;
  isEditMode: boolean;
  openCreateUserDialog: () => void;
  closeCreateUserDialog: () => void;
  setSelectedUser: (user: GetUserSchema) => void;
  clearSelectedUser: () => void;
  openShowUserDialog: () => void;
  closeShowUserDialog: () => void;
  enableEditMode: () => void;
  disableEditMode: () => void;
}

export const useUserStore = create<UserState>((set) => ({
  isCreateUserDialogOpen: false,
  selectedUser: null,
  isShowUserDialogOpen: false,
  isEditMode: false,
  openCreateUserDialog: () => set({ isCreateUserDialogOpen: true }),
  closeCreateUserDialog: () => set({ isCreateUserDialogOpen: false }),
  setSelectedUser: (user: GetUserSchema) => set({ selectedUser: user }),
  clearSelectedUser: () => set({ selectedUser: null }),
  openShowUserDialog: () => set({ isShowUserDialogOpen: true }),
  closeShowUserDialog: () =>
    set({ isShowUserDialogOpen: false, isEditMode: false }),
  enableEditMode: () => set({ isEditMode: true }),
  disableEditMode: () => set({ isEditMode: false }),
}));
