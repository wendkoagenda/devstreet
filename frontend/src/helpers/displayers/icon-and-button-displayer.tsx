import { Button } from "@/components/ui/button";
import { Icons } from "@/lib/constants/icons";
import {
  ActionType,
  ButtonVariant,
  ACTION_CONFIG,
} from "@/lib/constants/actions";
import { cn } from "@/lib/utils";

export default function IconAndButtonDisplayer({
  type = "create",
  text,
  onClick,
  variant = "default",
  style = "end",
}: {
  type: ActionType;
  text: string;
  onClick: () => void;
  variant?: ButtonVariant;
  style?: "end" | "start" | "center" | "none";
}) {
  const { icon } = ACTION_CONFIG[type];
  const ActionIcon = Icons[icon as keyof typeof Icons];

  return (
    <div
      className={cn(
        "flex gap-3",
        style !== "none" && "pt-4",
        style === "end" && "justify-end",
        style === "start" && "justify-start",
        style === "center" && "justify-center"
      )}
    >
      <Button
        variant={variant}
        className="flex items-center gap-2"
        onClick={onClick}
      >
        <ActionIcon className="h-4 w-4" />
        {text}
      </Button>
    </div>
  );
}
