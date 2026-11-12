import { toast } from "sonner";

export function CreationSuccessSonner(message: string) {
  toast.success(message, {
    duration: 3000,
    position: "top-right",
  });
}

export function CreationErrorSonner(message: string) {
  toast.error(message, {
    duration: 3000,
    position: "top-right",
  });
}
