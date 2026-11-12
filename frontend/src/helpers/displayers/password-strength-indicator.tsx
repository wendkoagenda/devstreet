import { Check, X } from "lucide-react";
import { useTranslation } from "react-i18next";

export default function PasswordStrengthIndicator({
  password,
}: {
  password: string;
}) {
  const { t } = useTranslation();
  const criteria = [
    { label: t("at_least_12_characters"), check: password?.length >= 12 },
    {
      label: t("at_least_one_uppercase_letter"),
      check: /[A-Z]/.test(password || ""),
    },
    {
      label: t("at_least_one_lowercase_letter"),
      check: /[a-z]/.test(password || ""),
    },
    { label: t("at_least_one_digit"), check: /\d/.test(password || "") },
    {
      label: t("at_least_one_special_character"),
      check: /[!@#$%^&*(),.?":{}|<>]/.test(password || ""),
    },
  ];
  return (
    <div className="space-y-1 mt-2">
      {criteria.map((criterion, index) => (
        <div key={index} className="flex items-center gap-2 text-xs">
          {criterion.check ? (
            <Check className="h-3 w-3 text-green-600 dark:text-green-400" />
          ) : (
            <X className="h-3 w-3 text-muted-foreground" />
          )}
          {criterion.label}
        </div>
      ))}
    </div>
  );
}
