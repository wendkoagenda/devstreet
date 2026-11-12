import { Button } from "@/components/ui/button";
import { Icons } from "@/lib/constants/icons";
import { useTranslation } from "react-i18next";
import {
  ActionType,
  ACTION_CONFIG,
  ACTION_TEXT_KEYS,
} from "@/lib/constants/actions";

interface ActionsLayoutProps {
  type: ActionType;
  onSubmit: () => void;
  onCancel?: () => void;
  isSubmitting?: boolean;
}

export default function ActionsLayout({
  type,
  onSubmit,
  onCancel,
  isSubmitting = false,
}: ActionsLayoutProps) {
  const { t } = useTranslation();

  const { icon } = ACTION_CONFIG[type];
  const text = t(ACTION_TEXT_KEYS[type]);
  const ActionIcon = Icons[icon as keyof typeof Icons];

  return (
    <div className="flex gap-3 pt-4 justify-end">
      {onCancel && (
        <Button
          type="button"
          variant="outline"
          disabled={isSubmitting}
          onClick={onCancel}
        >
          <Icons.Cancel className="h-4 w-4" />
          {t(ACTION_TEXT_KEYS.cancel)}
        </Button>
      )}
      <Button onClick={onSubmit} disabled={isSubmitting}>
        {isSubmitting ? (
          <>
            <Icons.Loading className="mr-2 h-4 w-4 animate-spin" />
            {t(ACTION_TEXT_KEYS.submitting)}
          </>
        ) : (
          <>
            <ActionIcon className="h-4 w-4" />
            {text}
          </>
        )}
      </Button>
    </div>
  );
}
