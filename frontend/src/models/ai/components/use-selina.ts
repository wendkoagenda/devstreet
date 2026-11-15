import { useContext } from "react";
import { SelinaContext } from "./selina-context";

export function useSelina() {
  const context = useContext(SelinaContext);
  if (!context) {
    throw new Error("useSelina doit être utilisé dans SelinaProvider");
  }
  return context;
}
