export const ACTION_TYPES = [
  "create",
  "edit",
  "delete",
  "save",
  "close",
  "cancel",
] as const;
export type ActionType = (typeof ACTION_TYPES)[number];

export const BUTTON_VARIANTS = [
  "outline",
  "default",
  "ghost",
  "link",
  "destructive",
] as const;
export type ButtonVariant = (typeof BUTTON_VARIANTS)[number];

export const ACTION_CONFIG = {
  create: { icon: "Add" },
  edit: { icon: "Edit" },
  delete: { icon: "Delete" },
  save: { icon: "Save" },
  close: { icon: "Close" },
  cancel: { icon: "Cancel" },
} as const;

export const ACTION_TEXT_KEYS = {
  create: "actions.create",
  edit: "actions.edit",
  delete: "actions.delete",
  save: "actions.save",
  cancel: "actions.cancel",
  submitting: "actions.submitting",
  close: "actions.close",
} as const;
