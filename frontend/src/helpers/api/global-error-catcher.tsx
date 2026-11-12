import { TFunction } from "i18next";
import {
  AlertCircle,
  StopCircle,
  Frown,
  ShieldAlert,
  WifiOff,
  Hourglass,
  ArrowBigRight,
} from "lucide-react";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import type { FetchBaseQueryError } from "@reduxjs/toolkit/query";

export const renderFetchBaseQueryError = (
  error: FetchBaseQueryError,
  t: TFunction
) => {
  let errorMessage = t("error.generic");
  let icon = <AlertCircle className="h-4 w-4" />;
  let validationErrors: string[] = [];

  if (error.status === 401) {
    errorMessage = t("error.unauthorized");
    icon = <StopCircle className="h-4 w-4" />;
  } else if (error.status === 400) {
    errorMessage = t("error.validation");
    const errorsData = error.data as Record<string, string[]>;
    const errorMapping: Record<string, string> = {
      username: t("validation.username.unique"),
      email: t("validation.email.unique"),
    };
    validationErrors = Object.entries(errorsData).flatMap(([key, msgs]) => {
      const customMsg = errorMapping[key];
      return customMsg ? [customMsg] : msgs;
    });
    icon = <Frown className="h-4 w-4" />;
  } else if (error.status === 404) {
    errorMessage = t("error.not_found");
    icon = <Frown className="h-4 w-4" />;
  } else if (error.status === 403) {
    errorMessage = t("error.forbidden");
    icon = <ShieldAlert className="h-4 w-4" />;
  } else if (error.status === "FETCH_ERROR") {
    errorMessage = t("error.network");
    icon = <WifiOff className="h-4 w-4" />;
  } else if (error.status === "TIMEOUT_ERROR") {
    errorMessage = t("error.timeout");
    icon = <Hourglass className="h-4 w-4" />;
  }

  return (
    <Alert variant="destructive">
      {icon}
      <AlertTitle>{t("error.title")}</AlertTitle>
      <AlertDescription>
        {errorMessage}
        {validationErrors.length > 0 && (
          <div className="mt-2 space-y-1">
            {validationErrors.map((msg, idx) => (
              <div key={idx} className="flex items-start">
                <ArrowBigRight className="mr-2 h-4 w-4" />
                <span>{msg}</span>
              </div>
            ))}
          </div>
        )}
      </AlertDescription>
    </Alert>
  );
};
