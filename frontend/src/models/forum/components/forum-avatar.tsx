import { buildMediaUrl } from "@/helpers/displayers/media-url-builder";
import { cn } from "@/lib/utils";

function initialsOf(name: string) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");
}

type ForumAvatarProps = {
  name: string;
  photo?: string | null;
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
  tone?: "brand" | "soft" | "muted";
};

const sizeClasses = {
  sm: "h-8 w-8 text-[10px]",
  md: "h-10 w-10 text-xs",
  lg: "h-12 w-12 text-sm",
  xl: "h-16 w-16 text-base",
} as const;

const toneClasses = {
  brand: "bg-brand text-brand-foreground",
  soft: "bg-brand-soft text-brand-strong",
  muted: "bg-muted text-foreground",
} as const;

export function ForumAvatar({
  name,
  photo,
  size = "md",
  className,
  tone = "soft",
}: ForumAvatarProps) {
  const photoUrl = photo ? buildMediaUrl(photo) : null;

  if (photoUrl) {
    return (
      <img
        src={photoUrl}
        alt=""
        className={cn(
          "shrink-0 rounded-full object-cover",
          sizeClasses[size],
          className
        )}
      />
    );
  }

  return (
    <div
      aria-hidden
      className={cn(
        "flex shrink-0 items-center justify-center rounded-full font-semibold",
        sizeClasses[size],
        toneClasses[tone],
        className
      )}
    >
      {initialsOf(name) || "?"}
    </div>
  );
}
