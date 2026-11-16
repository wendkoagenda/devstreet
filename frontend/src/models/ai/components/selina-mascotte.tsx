import {
  Component,
  Suspense,
  lazy,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { useTranslation } from "react-i18next";
import { Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

const SIZE_PX = {
  sm: 40,
  md: 96,
  lg: 168,
} as const;

export type SelinaMascotteSize = keyof typeof SIZE_PX;

export interface SelinaMascotteProps {
  size?: SelinaMascotteSize;
  interactive?: boolean;
  className?: string;
  ariaLabel?: string;
  onClick?: () => void;
}

const SelinaMascotteScene = lazy(() => import("./selina-mascotte-scene"));

function usePrefersReducedMotion(): boolean {
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined" || !window.matchMedia) return;
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setReduced(mq.matches);
    update();
    mq.addEventListener("change", update);
    return () => mq.removeEventListener("change", update);
  }, []);

  return reduced;
}

function MascotteFallback({
  px,
  className,
}: {
  px: number;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center justify-center rounded-full",
        "bg-gradient-to-tr from-brand to-brand-strong text-white shadow-sm",
        className
      )}
      style={{ width: px, height: px }}
      aria-hidden
    >
      <Sparkles className="size-[40%]" strokeWidth={1.75} />
    </span>
  );
}

class SceneErrorBoundary extends Component<
  { fallback: ReactNode; children: ReactNode },
  { hasError: boolean }
> {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) return this.props.fallback;
    return this.props.children;
  }
}

export function SelinaMascotte({
  size = "md",
  interactive = true,
  className,
  ariaLabel,
  onClick,
}: SelinaMascotteProps) {
  const { t } = useTranslation();
  const reducedMotion = usePrefersReducedMotion();
  const [hovering, setHovering] = useState(false);
  const px = SIZE_PX[size];
  const label = ariaLabel ?? t("selina.mascotte_aria");
  const clickable = typeof onClick === "function";
  const fallback = <MascotteFallback px={px} />;
  const clippedCircle = size === "sm";

  const sharedClassName = cn(
    "relative inline-flex shrink-0 items-center justify-center",
    clippedCircle
      ? "overflow-hidden rounded-full bg-gradient-to-b from-brand-soft/80 to-muted/40 ring-1 ring-border/50"
      : "overflow-visible bg-transparent",
    clickable &&
      "cursor-pointer transition hover:scale-[1.03] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/40",
    className
  );

  const hoverHandlers = {
    onPointerEnter: () => {
      if (interactive && !reducedMotion) setHovering(true);
    },
    onPointerLeave: () => setHovering(false),
    onFocus: () => {
      if (interactive && !reducedMotion) setHovering(true);
    },
    onBlur: () => setHovering(false),
  };

  const scene = (
    <SceneErrorBoundary fallback={fallback}>
      <Suspense fallback={fallback}>
        <SelinaMascotteScene
          hovering={hovering && interactive}
          reducedMotion={reducedMotion}
          px={px}
          fitSize={size}
        />
      </Suspense>
    </SceneErrorBoundary>
  );

  if (clickable) {
    return (
      <button
        type="button"
        aria-label={label}
        className={sharedClassName}
        style={{ width: px, height: px }}
        onClick={onClick}
        {...hoverHandlers}
      >
        {scene}
      </button>
    );
  }

  return (
    <div
      role="img"
      aria-label={label}
      className={sharedClassName}
      style={{ width: px, height: px }}
      {...hoverHandlers}
    >
      {scene}
    </div>
  );
}
