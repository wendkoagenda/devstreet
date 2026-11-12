import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

export default function IconAndTextDisplayerAsTitle({
  Icon,
  text,
  displaySize = "md",
  bold = false,
  textColor = "text-primary",
  iconColor = "text-primary",
  uppercase = false,
}: {
  Icon: LucideIcon;
  text: string;
  displaySize?: "sm" | "md" | "lg";
  bold?: boolean;
  textColor?: string;
  iconColor?: string;
  uppercase?: boolean;
}) {
  // Détermine la classe de police selon bold
  const fontWeightClass = bold ? "font-bold" : "font-medium";
  const textClass = uppercase ? "uppercase" : "";
  if (displaySize === "sm") {
    return (
      <div className={cn("flex items-center gap-2")}>
        <Icon className={cn("h-4 w-4", iconColor)} />
        <span className={cn("text-sm", fontWeightClass, textColor, textClass)}>
          {text}
        </span>
      </div>
    );
  }
  if (displaySize === "md") {
    return (
      <div className={cn("flex items-center gap-2")}>
        <Icon className={cn("h-6 w-6", iconColor)} />
        <span className={cn("text-md", fontWeightClass, textColor, textClass)}>
          {text}
        </span>
      </div>
    );
  }
  if (displaySize === "lg") {
    return (
      <div className={cn("flex items-center gap-2")}>
        <Icon className={cn("h-8 w-8", iconColor)} />
        <span className={cn("text-lg", fontWeightClass, textColor, textClass)}>
          {text}
        </span>
      </div>
    );
  }
}
