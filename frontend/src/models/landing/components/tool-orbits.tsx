import type { CSSProperties } from "react";
import { cn } from "@/lib/utils";
import { LEFT_TOOLS, RIGHT_TOOLS, type DevTool } from "../data/dev-tools";

const DIAMETER_REM = 24;
const DURATION_S = 90;

/** Logos d'outils en orbite de part et d'autre du titre (décoratif, grands écrans seulement). */
export function ToolOrbits() {
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 hidden xl:block">
      <Orbit tools={LEFT_TOOLS} className="left-[calc(50%-38rem)]" />
      <Orbit tools={RIGHT_TOOLS} className="left-[calc(50%+38rem)]" reverse />
    </div>
  );
}

function Orbit({
  tools,
  className,
  reverse = false,
}: {
  tools: DevTool[];
  className?: string;
  reverse?: boolean;
}) {
  const timing = (direction: boolean): CSSProperties => ({
    animationDuration: `${DURATION_S}s`,
    animationDirection: direction ? "reverse" : "normal",
  });

  return (
    <div
      className={cn("absolute top-1/2 -translate-x-1/2 -translate-y-1/2", className)}
      style={{ width: `${DIAMETER_REM}rem`, height: `${DIAMETER_REM}rem` }}
    >
      <div
        className="absolute inset-0 animate-spin rounded-full border border-foreground/[0.07] [animation-timing-function:linear] motion-reduce:animate-none"
        style={timing(reverse)}
      >
        {tools.map((tool, index) => {
          const angle = (360 / tools.length) * index;
          return (
            <div
              key={tool.name}
              className="absolute left-1/2 top-1/2"
              style={{
                transform: `rotate(${angle}deg) translateX(${DIAMETER_REM / 2}rem) rotate(${-angle}deg)`,
              }}
            >
              <div
                className="-ml-5 -mt-5 animate-spin [animation-timing-function:linear] motion-reduce:animate-none"
                style={timing(!reverse)}
              >
                <div className="flex size-10 items-center justify-center rounded-xl border border-border/60 bg-card shadow-sm">
                  <img
                    src={tool.logo}
                    alt={tool.name}
                    width={22}
                    height={22}
                    loading="lazy"
                    decoding="async"
                    className={cn("size-[1.375rem]", tool.mono && "dark:invert")}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
