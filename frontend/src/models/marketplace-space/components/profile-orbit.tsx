import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type PointerEvent as ReactPointerEvent,
  type ReactNode,
} from "react";
import { Link } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export type OrbitLeaf = {
  key: string;
  title: string;
  summary?: string;
  onSelect?: () => void;
};

export type OrbitNode = {
  key: string;
  title: string;
  /** Une ligne de résumé (« 5 compétences », « Occupé jusqu'au… »). */
  summary: string;
  icon: ReactNode;
  /** Élément à compléter : bordure en pointillés et pastille « À compléter ». */
  todo?: boolean;
  /** Ouvre un panneau d'édition. */
  onSelect?: () => void;
  /** Ou mène vers une autre page. */
  to?: string;
  /** Feuilles hors de la branche (compétences, expériences…). */
  children?: OrbitLeaf[];
};

type Point = { x: number; y: number };

type ProfileOrbitProps = {
  center: ReactNode;
  nodes: OrbitNode[];
  /** Clé localStorage pour mémoriser les positions déplacées. */
  storageKey?: string;
};

const RADIUS = 34;

function positionOf(index: number, count: number): Point {
  const angle = ((-90 + (360 / Math.max(count, 1)) * index) * Math.PI) / 180;
  return { x: 50 + RADIUS * Math.cos(angle), y: 50 + RADIUS * Math.sin(angle) };
}

function childPosition(parent: Point, index: number, count: number): Point {
  const dx = parent.x - 50;
  const dy = parent.y - 50;
  const len = Math.hypot(dx, dy) || 1;
  const ux = dx / len;
  const uy = dy / len;
  const px = -uy;
  const py = ux;
  const fan = count <= 1 ? 0 : (index - (count - 1) / 2) * 7;
  const extend = 16;
  return {
    x: Math.min(96, Math.max(4, parent.x + ux * extend + px * fan)),
    y: Math.min(96, Math.max(4, parent.y + uy * extend + py * fan)),
  };
}

function loadPositions(storageKey?: string): Record<string, Point> {
  if (!storageKey || typeof window === "undefined") return {};
  let parsed: unknown = null;
  try {
    const raw = window.localStorage.getItem(storageKey);
    if (!raw) return {};
    parsed = JSON.parse(raw);
  } catch (error) {
    console.warn("Positions de l'orbite illisibles, valeurs par défaut utilisées", error);
  }
  return parsed && typeof parsed === "object" ? (parsed as Record<string, Point>) : {};
}

function savePositions(storageKey: string | undefined, positions: Record<string, Point>) {
  if (!storageKey || typeof window === "undefined") return;
  try {
    window.localStorage.setItem(storageKey, JSON.stringify(positions));
  } catch (error) {
    console.warn("Positions de l'orbite non enregistrées (stockage plein ou bloqué)", error);
  }
}

const BRANCH_CLASSES =
  "group flex w-full items-center gap-3 rounded-xl border bg-card p-3 text-left shadow-sm transition-colors " +
  "hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring " +
  "xl:absolute xl:left-[var(--x)] xl:top-[var(--y)] xl:z-20 xl:w-44 xl:-translate-x-1/2 xl:-translate-y-1/2 " +
  "xl:cursor-grab xl:active:cursor-grabbing xl:touch-none";

const LEAF_CLASSES =
  "absolute z-10 flex w-36 -translate-x-1/2 -translate-y-1/2 items-center gap-2 rounded-lg border border-border bg-card px-2.5 py-2 text-left text-xs shadow-sm " +
  "hover:border-brand-soft-border hover:bg-brand-soft/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";

function BranchBody({ node }: { node: OrbitNode }) {
  return (
    <>
      <span
        className="flex size-9 shrink-0 items-center justify-center rounded-full border border-border bg-muted text-foreground"
        aria-hidden
      >
        {node.icon}
      </span>
      <span className="flex min-w-0 flex-1 flex-col gap-0.5">
        <span className="truncate text-sm font-semibold text-foreground">
          {node.title}
        </span>
        <span className="line-clamp-2 text-xs text-muted-foreground">
          {node.summary}
        </span>
        {node.todo ? (
          <Badge
            variant="outline"
            className="mt-0.5 w-fit px-1.5 py-0 text-[10px]"
          >
            À compléter
          </Badge>
        ) : null}
      </span>
    </>
  );
}

/**
 * Profil au centre + branches déplaçables.
 * Chaque compétence / expérience / entreprise crée une feuille plus loin sur l'arbre.
 */
export function ProfileOrbit({ center, nodes, storageKey }: ProfileOrbitProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const defaults = useMemo(
    () =>
      Object.fromEntries(
        nodes.map((node, index) => [node.key, positionOf(index, nodes.length)])
      ) as Record<string, Point>,
    [nodes]
  );
  const [overrides, setOverrides] = useState<Record<string, Point>>(() =>
    loadPositions(storageKey)
  );
  const dragRef = useRef<{
    key: string;
    pointerId: number;
  } | null>(null);
  const movedRef = useRef(false);

  useEffect(() => {
    setOverrides(loadPositions(storageKey));
  }, [storageKey]);

  const positions = useMemo(() => {
    const next: Record<string, Point> = { ...defaults };
    for (const [key, point] of Object.entries(overrides)) {
      if (next[key]) next[key] = point;
    }
    return next;
  }, [defaults, overrides]);

  const lines = useMemo(() => {
    const edges: Array<{ key: string; x1: number; y1: number; x2: number; y2: number }> =
      [];
    for (const node of nodes) {
      const parent = positions[node.key] ?? { x: 50, y: 50 };
      edges.push({
        key: `root-${node.key}`,
        x1: 50,
        y1: 50,
        x2: parent.x,
        y2: parent.y,
      });
      const kids = node.children ?? [];
      kids.forEach((leaf, index) => {
        const child = childPosition(parent, index, kids.length);
        edges.push({
          key: `leaf-${node.key}-${leaf.key}`,
          x1: parent.x,
          y1: parent.y,
          x2: child.x,
          y2: child.y,
        });
      });
    }
    return edges;
  }, [nodes, positions]);

  const onPointerDown = useCallback(
    (key: string, event: ReactPointerEvent<HTMLElement>) => {
      if (event.button !== 0) return;
      // Sur mobile (liste), pas de drag.
      if (window.matchMedia("(max-width: 1279px)").matches) return;
      movedRef.current = false;
      dragRef.current = { key, pointerId: event.pointerId };
      event.currentTarget.setPointerCapture(event.pointerId);
    },
    []
  );

  const onPointerMove = useCallback((event: ReactPointerEvent<HTMLElement>) => {
    const drag = dragRef.current;
    if (!drag || drag.pointerId !== event.pointerId) return;
    const box = containerRef.current?.getBoundingClientRect();
    if (!box || box.width <= 0 || box.height <= 0) return;
    movedRef.current = true;
    const x = ((event.clientX - box.left) / box.width) * 100;
    const y = ((event.clientY - box.top) / box.height) * 100;
    const clamped = {
      x: Math.min(94, Math.max(6, x)),
      y: Math.min(94, Math.max(6, y)),
    };
    setOverrides((prev) => {
      const next = { ...prev, [drag.key]: clamped };
      savePositions(storageKey, next);
      return next;
    });
  }, [storageKey]);

  const onPointerUp = useCallback((event: ReactPointerEvent<HTMLElement>) => {
    const drag = dragRef.current;
    if (!drag || drag.pointerId !== event.pointerId) return;
    dragRef.current = null;
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
  }, []);

  const handleBranchActivate = (node: OrbitNode) => {
    if (movedRef.current) {
      movedRef.current = false;
      return;
    }
    node.onSelect?.();
  };

  const hasLeaves = nodes.some((node) => (node.children?.length ?? 0) > 0);

  return (
    <div
      ref={containerRef}
      className={cn(
        "flex flex-col gap-6 xl:relative xl:mx-auto xl:block xl:aspect-square xl:w-full xl:gap-0",
        hasLeaves ? "xl:max-w-[960px]" : "xl:max-w-[800px]"
      )}
    >
      <svg
        className="pointer-events-none absolute inset-0 hidden h-full w-full text-border xl:block"
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        aria-hidden
      >
        {lines.map((line) => (
          <line
            key={line.key}
            x1={line.x1}
            y1={line.y1}
            x2={line.x2}
            y2={line.y2}
            stroke="currentColor"
            strokeWidth={1}
            strokeDasharray="2 4"
            vectorEffect="non-scaling-stroke"
          />
        ))}
      </svg>

      <div
        className="pointer-events-none absolute inset-[14%] hidden rounded-full border border-dashed border-border bg-muted/20 xl:block"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute inset-[30%] hidden rounded-full border border-dashed border-border xl:block"
        aria-hidden
      />

      <div className="xl:absolute xl:left-1/2 xl:top-1/2 xl:z-30 xl:w-64 xl:-translate-x-1/2 xl:-translate-y-1/2">
        {center}
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:contents">
        {nodes.map((node) => {
          const point = positions[node.key] ?? { x: 50, y: 50 };
          const style = {
            "--x": `${point.x}%`,
            "--y": `${point.y}%`,
          } as CSSProperties;
          const className = cn(
            BRANCH_CLASSES,
            node.todo
              ? "border-dashed border-muted-foreground"
              : "border-border"
          );

          const kids = node.children ?? [];

          return (
            <div key={node.key} className="contents">
              {node.to ? (
                <Link
                  to={node.to}
                  className={className}
                  style={style}
                  onPointerDown={(event) => onPointerDown(node.key, event)}
                  onPointerMove={onPointerMove}
                  onPointerUp={onPointerUp}
                  onClick={(event) => {
                    if (movedRef.current) {
                      event.preventDefault();
                      movedRef.current = false;
                    }
                  }}
                >
                  <BranchBody node={node} />
                </Link>
              ) : (
                <button
                  type="button"
                  className={className}
                  style={style}
                  onPointerDown={(event) => onPointerDown(node.key, event)}
                  onPointerMove={onPointerMove}
                  onPointerUp={onPointerUp}
                  onClick={() => handleBranchActivate(node)}
                >
                  <BranchBody node={node} />
                </button>
              )}

              {/* Feuilles desktop : hors de la branche */}
              {kids.map((leaf, index) => {
                const leafPoint = childPosition(point, index, kids.length);
                const leafStyle = {
                  left: `${leafPoint.x}%`,
                  top: `${leafPoint.y}%`,
                } as CSSProperties;
                return (
                  <button
                    key={`${node.key}-${leaf.key}`}
                    type="button"
                    className={cn(LEAF_CLASSES, "hidden xl:flex")}
                    style={leafStyle}
                    onClick={() => leaf.onSelect?.() ?? node.onSelect?.()}
                  >
                    <span className="min-w-0">
                      <span className="block truncate font-medium text-foreground">
                        {leaf.title}
                      </span>
                      {leaf.summary ? (
                        <span className="block truncate text-[10px] text-muted-foreground">
                          {leaf.summary}
                        </span>
                      ) : null}
                    </span>
                  </button>
                );
              })}

              {/* Feuilles mobile : sous la branche */}
              {kids.length > 0 ? (
                <ul className="ml-4 space-y-1.5 border-l border-dashed border-border pl-3 xl:hidden">
                  {kids.map((leaf) => (
                    <li key={leaf.key}>
                      <button
                        type="button"
                        className="w-full rounded-lg border border-border bg-card px-2.5 py-2 text-left text-xs hover:bg-muted"
                        onClick={() => leaf.onSelect?.() ?? node.onSelect?.()}
                      >
                        <span className="block font-medium text-foreground">
                          {leaf.title}
                        </span>
                        {leaf.summary ? (
                          <span className="text-muted-foreground">
                            {leaf.summary}
                          </span>
                        ) : null}
                      </button>
                    </li>
                  ))}
                </ul>
              ) : null}
            </div>
          );
        })}
      </div>
    </div>
  );
}
