import type { ReactNode } from "react";
import type { FieldValues, Path, UseFormReturn } from "react-hook-form";
import type { TFunction } from "i18next";
import type { FetchBaseQueryError } from "@reduxjs/toolkit/query";
import { renderFetchBaseQueryError } from "@/helpers/api/global-error-catcher";

/**
 * Affiche une erreur d'API sous les champs concernés (réponse 400 `{champ: [messages]}`),
 * ou, à défaut, dans un bandeau global (`{error: "message"}`, 403, 500…).
 */
export function applySubmitError<T extends FieldValues>(
  err: unknown,
  form: UseFormReturn<T>,
  t: TFunction
): ReactNode {
  const error = err as FetchBaseQueryError;
  const fieldNames = Object.keys(form.getValues());
  let matched = false;

  if (error.status === 400 && error.data && typeof error.data === "object") {
    Object.entries(error.data as Record<string, unknown>).forEach(
      ([field, messages]) => {
        if (
          fieldNames.includes(field) &&
          Array.isArray(messages) &&
          messages.length > 0
        ) {
          form.setError(field as Path<T>, { message: String(messages[0]) });
          matched = true;
        }
      }
    );
  }
  return matched ? null : renderFetchBaseQueryError(error, t);
}
