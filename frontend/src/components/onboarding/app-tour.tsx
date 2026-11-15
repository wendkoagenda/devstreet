import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useState,
  type CSSProperties,
} from "react";
import { createPortal } from "react-dom";
import { useTranslation } from "react-i18next";
import { ArrowDown, ArrowLeft, ArrowRight, ArrowUp, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useSidebar } from "@/components/ui/sidebar";
import { cn } from "@/lib/utils";
import { useAuthSlice } from "@/models/auth/slice";
import { getTourSteps, tourStorageKey, type TourStep } from "./tour-steps";
import { useAccountType } from "@/models/auth/account-type/use-account-type";

type Spot = { top: number; left: number; width: number; height: number };

const PAD = 6;
// Sans stockage local (navigation privée, accès bloqué), le tour est considéré terminé : il ne se rouvre pas à chaque page.
const COMPLETED_WHEN_STORAGE_UNAVAILABLE = true;

function readCompleted(userId: number): boolean {
  try {
    return window.localStorage.getItem(tourStorageKey(userId)) === "1";
  } catch (error) {
    console.warn("Tour guidé : lecture du stockage local impossible", error);
    return COMPLETED_WHEN_STORAGE_UNAVAILABLE;
  }
}

function markCompleted(userId: number) {
  try {
    window.localStorage.setItem(tourStorageKey(userId), "1");
  } catch (error) {
    // stockage indisponible : le tour pourra se réafficher
    console.warn("Tour guidé : enregistrement dans le stockage local impossible", error);
  }
}

function measureTarget(tourId: string): Spot | null {
  const el = document.querySelector(`[data-tour="${tourId}"]`);
  if (!(el instanceof HTMLElement)) return null;
  el.scrollIntoView({ block: "nearest", inline: "nearest" });
  const r = el.getBoundingClientRect();
  if (r.width < 2 && r.height < 2) return null;
  return {
    top: r.top - PAD,
    left: r.left - PAD,
    width: r.width + PAD * 2,
    height: r.height + PAD * 2,
  };
}

function cardStyle(step: TourStep, spot: Spot | null): CSSProperties {
  if (!spot || step.placement === "center" || !step.target) {
    return {
      top: "50%",
      left: "50%",
      transform: "translate(-50%, -50%)",
    };
  }

  const gap = 14;
  const cardW = 300;
  const placement = step.placement ?? "right";

  if (placement === "right") {
    return {
      top: Math.max(12, spot.top + spot.height / 2 - 60),
      left: Math.min(window.innerWidth - cardW - 12, spot.left + spot.width + gap),
    };
  }
  if (placement === "left") {
    return {
      top: Math.max(12, spot.top + spot.height / 2 - 60),
      left: Math.max(12, spot.left - cardW - gap),
    };
  }
  if (placement === "top") {
    return {
      top: Math.max(12, spot.top - gap - 140),
      left: Math.min(
        window.innerWidth - cardW - 12,
        Math.max(12, spot.left + spot.width / 2 - cardW / 2)
      ),
    };
  }
  return {
    top: Math.min(window.innerHeight - 180, spot.top + spot.height + gap),
    left: Math.min(
      window.innerWidth - cardW - 12,
      Math.max(12, spot.left + spot.width / 2 - cardW / 2)
    ),
  };
}

function StepArrow({ placement }: { placement?: TourStep["placement"] }) {
  const cls = "size-4 shrink-0 text-brand";
  if (placement === "right") return <ArrowLeft className={cls} aria-hidden />;
  if (placement === "left") return <ArrowRight className={cls} aria-hidden />;
  if (placement === "top") return <ArrowDown className={cls} aria-hidden />;
  if (placement === "bottom") return <ArrowUp className={cls} aria-hidden />;
  return null;
}

export function AppTour() {
  const { t } = useTranslation();
  const userId = useAuthSlice((s) => s.user?.id ?? null);
  const isAuthenticated = useAuthSlice((s) => s.isAuthenticated);
  const isInitialized = useAuthSlice((s) => s.isInitialized);
  const { setOpen, setOpenMobile, isMobile } = useSidebar();

  const [active, setActive] = useState(false);
  const [index, setIndex] = useState(0);
  const [spot, setSpot] = useState<Spot | null>(null);

  const { isEntrepriseOnly } = useAccountType();
  const steps = useMemo(() => getTourSteps(isEntrepriseOnly), [isEntrepriseOnly]);
  const step = steps[index];

  useEffect(() => {
    if (!isInitialized || !isAuthenticated || userId == null) return;
    if (readCompleted(userId)) return;
    setActive(true);
    setIndex(0);
  }, [isInitialized, isAuthenticated, userId]);

  useEffect(() => {
    if (!active) return;
    setOpen(true);
    if (isMobile) setOpenMobile(true);
  }, [active, setOpen, setOpenMobile, isMobile]);

  const refreshSpot = useCallback(() => {
    if (!step?.target) {
      setSpot(null);
      return;
    }
    setSpot(measureTarget(step.target));
  }, [step]);

  useLayoutEffect(() => {
    if (!active) return;
    const id = window.requestAnimationFrame(refreshSpot);
    return () => window.cancelAnimationFrame(id);
  }, [active, index, refreshSpot]);

  useEffect(() => {
    if (!active) return;
    const onResize = () => refreshSpot();
    window.addEventListener("resize", onResize);
    window.addEventListener("scroll", onResize, true);
    return () => {
      window.removeEventListener("resize", onResize);
      window.removeEventListener("scroll", onResize, true);
    };
  }, [active, refreshSpot]);

  const finish = useCallback(() => {
    if (userId != null) markCompleted(userId);
    setActive(false);
    if (isMobile) setOpenMobile(false);
  }, [userId, isMobile, setOpenMobile]);

  const goNext = () => {
    if (index >= steps.length - 1) {
      finish();
      return;
    }
    setIndex((i) => i + 1);
  };

  const goPrev = () => {
    setIndex((i) => Math.max(0, i - 1));
  };

  if (!active || !step) return null;

  const total = steps.length;
  const isLast = index === total - 1;
  const isFirst = index === 0;

  return createPortal(
    <div className="fixed inset-0 z-[80]" role="dialog" aria-modal="true">
      {/* Bloque les clics pendant le tour */}
      <div className="absolute inset-0" aria-hidden />
      {spot ? (
        <div
          aria-hidden
          className="pointer-events-none absolute rounded-xl ring-2 ring-brand shadow-[0_0_0_9999px_hsl(var(--foreground)/0.5)]"
          style={{
            top: spot.top,
            left: spot.left,
            width: spot.width,
            height: spot.height,
          }}
        />
      ) : (
        <div className="pointer-events-none absolute inset-0 bg-foreground/50" aria-hidden />
      )}

      <div
        className={cn(
          "absolute z-[81] w-[min(20rem,calc(100vw-1.5rem))] rounded-2xl border border-border bg-card p-4 text-card-foreground shadow-xl"
        )}
        style={cardStyle(step, spot)}
      >
        <div className="mb-3 flex items-start justify-between gap-2">
          <div className="flex items-center gap-2">
            <StepArrow placement={step.placement} />
            <p className="text-sm font-semibold leading-snug">
              {t(step.titleKey)}
            </p>
          </div>
          <button
            type="button"
            onClick={finish}
            className="rounded-lg p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
            aria-label={t("tour.skip")}
          >
            <X className="size-4" />
          </button>
        </div>

        <p className="text-sm leading-relaxed text-muted-foreground">
          {t(step.bodyKey)}
        </p>

        <div className="mt-4 flex items-center justify-between gap-2">
          <span className="text-xs tabular-nums text-muted-foreground">
            {index + 1}/{total}
          </span>
          <div className="flex items-center gap-2">
            {!isFirst ? (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="h-8"
                onClick={goPrev}
              >
                {t("tour.back")}
              </Button>
            ) : (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="h-8"
                onClick={finish}
              >
                {t("tour.skip")}
              </Button>
            )}
            <Button
              type="button"
              size="sm"
              className="h-8 bg-foreground text-background hover:bg-foreground/90"
              onClick={goNext}
            >
              {isLast ? t("tour.finish") : t("tour.next")}
            </Button>
          </div>
        </div>
      </div>
    </div>,
    document.body
  );
}
