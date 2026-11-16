import type { ReactNode } from "react";
import { cn } from "@/lib/utils";
import { useInView } from "../hooks/use-in-view";

const HIDDEN_CLASS = {
  up: "translate-y-8",
  left: "-translate-x-8",
  right: "translate-x-8",
  zoom: "scale-95",
} as const;

export function Reveal({
  children,
  className,
  delay = 0,
  from = "up",
}: {
  children: ReactNode;
  className?: string;
  delay?: number;
  from?: keyof typeof HIDDEN_CLASS;
}) {
  const { ref, inView } = useInView<HTMLDivElement>();

  return (
    <div
      ref={ref}
      style={{ transitionDelay: inView ? `${delay}ms` : "0ms" }}
      className={cn(
        "transition-[opacity,transform] duration-700 ease-[cubic-bezier(0.22,1,0.36,1)] motion-reduce:!translate-x-0 motion-reduce:!translate-y-0 motion-reduce:!scale-100 motion-reduce:!opacity-100 motion-reduce:transition-none",
        inView ? "translate-x-0 translate-y-0 scale-100 opacity-100" : cn("opacity-0", HIDDEN_CLASS[from]),
        className
      )}
    >
      {children}
    </div>
  );
}
