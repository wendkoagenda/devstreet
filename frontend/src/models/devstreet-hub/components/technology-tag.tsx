import { cn } from "@/lib/utils";

/** Pastilles de couleur des technologies, attribuées de façon stable à partir de l'ID. */
const DOT_CLASSES = [
  "bg-chart-1",
  "bg-chart-2",
  "bg-chart-3",
  "bg-chart-4",
  "bg-chart-5",
] as const;

interface TechnologyTagProps {
  id: number;
  label: string;
  className?: string;
}

export function TechnologyTag({ id, label, className }: TechnologyTagProps) {
  return (
    <span
      className={cn(
        "inline-flex h-6 items-center gap-1.5 rounded border border-border bg-secondary px-2 font-mono text-[11px] text-secondary-foreground",
        className
      )}
    >
      <span
        aria-hidden
        className={cn(
          "h-1.5 w-1.5 shrink-0 rounded-full",
          DOT_CLASSES[Math.abs(id) % DOT_CLASSES.length]
        )}
      />
      {label}
    </span>
  );
}
