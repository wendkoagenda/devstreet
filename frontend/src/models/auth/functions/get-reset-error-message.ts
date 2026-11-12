import type { TFunction } from "i18next";
import type { FetchBaseQueryError } from "@reduxjs/toolkit/query";

/**
 * Message à afficher pour une erreur des routes « mot de passe oublié ».
 * Le backend renvoie `{ "error": "..." }` en 400 et un 429 quand la limite de débit est atteinte.
 */
export const getResetErrorMessage = (error: unknown, t: TFunction): string => {
  const fetchError = error as FetchBaseQueryError | undefined;

  if (fetchError && typeof fetchError === "object" && "status" in fetchError) {
    if (fetchError.status === 429) {
      return t("forgot_password.too_many_requests");
    }
    const data = fetchError.data as { error?: unknown } | undefined;
    if (data && typeof data.error === "string") {
      return data.error;
    }
  }

  return t("forgot_password.generic_error");
};
