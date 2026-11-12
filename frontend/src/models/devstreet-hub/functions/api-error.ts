import type { FetchBaseQueryError } from "@reduxjs/toolkit/query";
import type { SerializedError } from "@reduxjs/toolkit";

/** Code HTTP d'une erreur RTK Query ; null pour une panne réseau ou une erreur locale. */
export const httpStatusOf = (
  error: FetchBaseQueryError | SerializedError | undefined | unknown
): number | null => {
  if (error && typeof error === "object" && "status" in error) {
    const status = (error as FetchBaseQueryError).status;
    return typeof status === "number" ? status : null;
  }
  return null;
};

/** Message `detail` renvoyé par l'API, s'il existe. */
export const apiDetailOf = (error: unknown): string | null => {
  if (error && typeof error === "object" && "data" in error) {
    const data = (error as { data?: unknown }).data;
    if (data && typeof data === "object" && "detail" in data) {
      const detail = (data as { detail?: unknown }).detail;
      return typeof detail === "string" ? detail : null;
    }
  }
  return null;
};
