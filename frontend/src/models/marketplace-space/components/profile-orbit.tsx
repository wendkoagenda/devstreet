import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type PointerEvent as ReactPointerEvent,
  type ReactNode,
} from "react";
import { Link } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { OpenToWorkRing } from "@/components/ui/open-to-work-ring";
import { ForumAvatar } from "@/models/forum/components/forum-avatar";
import { cn } from "@/lib/utils";

export type OrbitNode = {
  key: string;
  title: string;
  /** Une ligne de résumé (« 5 compétences », « Occupé jusqu'au… »). */
  summary: string;
  icon: ReactNode;
  /** Élément à compléter : bordure en pointillés et pastille « À compléter ». */
  todo?: boolean;
  /** Ouvre un panneau d'édition ou une autre vue. */
  onSelect?: () => void;
  /** Ou mène vers une autre page. */
  to?: string;
};

type Point = { x: number; y: number };

type ProfileOrbitProps = {
  center: ReactNode;
  nodes: OrbitNode[];
  /** Clé localStorage pour mémoriser les positions déplacées. */
  storageKey?: string;
  /** Les branches se déplacent à la souris (désactivé pour un visiteur : il ne modifie pas la présentation). */
  draggable?: boolean;
};

const RADIUS = 34;

function positionOf(index: number, count: number): Point {
  const angle = ((-90 + (360 / Math.max(count, 1)) * index) * Math.PI) / 180;
  return { x: 50 + RADIUS * Math.cos(angle), y: 50 + RADIUS * Math.sin(angle) };
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

/**
 * Largeur minimale (px) du conteneur pour afficher l'orbite complète. En dessous (colonne étroite, petit écran),
 * les branches s'affichent en grille de cartes. La mesure se fait sur le conteneur lui-même, pas sur l'écran :
 * l'orbite s'adapte à la place réellement disponible, par exemple à côté du menu de la page de profil.
 */
const ORBIT_MIN_WIDTH = 720;

const BRANCH_CLASSES =
  "group flex w-full items-center gap-3 rounded-xl border bg-card p-3 text-left shadow-sm transition-colors " +
  "hover:border-brand hover:bg-brand-soft focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";

const BRANCH_ORBIT_CLASSES =
  "absolute left-[var(--x)] top-[var(--y)] z-20 w-44 -translate-x-1/2 -translate-y-1/2";

const BRANCH_DRAG_CLASSES = "cursor-grab active:cursor-grabbing touch-none";

/** Carte centrale du profil : photo, nom, accroche et statut « ouvert aux opportunités » — rien d'autre. */
export function ProfileOrbitCenter({
  name,
  photo,
  headline,
  headlinePlaceholder,
  openToWork,
}: {
  name: string;
  photo?: string | null;
  headline?: string;
  /** Texte affiché quand l'accroche est vide (ex. invitation à la renseigner sur mon propre profil). */
  headlinePlaceholder?: string;
  openToWork: boolean;
}) {
  const tagline = headline || headlinePlaceholder;
  return (
    <section
      aria-label={`Profil de ${name}`}
      className="flex flex-col items-center gap-2.5 rounded-2xl border border-brand-soft-border bg-card p-4 text-center shadow-md ring-4 ring-brand-soft"
    >
      {/* Statut « ouvert aux opportunités » : arc façon LinkedIn sur la photo */}
      <div className="relative mb-1.5">
        <ForumAvatar
          name={name}
          photo={photo}
          tone="brand"
          className="!h-24 !w-24 !text-2xl"
        />
        {openToWork ? <OpenToWorkRing /> : null}
      </div>
      <div className="flex min-w-0 flex-col gap-1">
        <h2 className="truncate text-lg font-semibold text-foreground">{name}</h2>
        {tagline ? <p className="text-xs text-muted-foreground">{tagline}</p> : null}
      </div>
    </section>
  );
}

function BranchBody({ node }: { node: OrbitNode }) {
  return (
    <>
      <span
        className="flex size-9 shrink-0 items-center justify-center rounded-full border border-brand-soft-border bg-brand-soft text-brand-strong"
        aria-hidden
      >
        {node.icon}
      </span>
      <span className="flex min-w-0 flex-1 flex-col gap-0.5">
        <span className="truncate text-sm font-semibold text-foreground">{node.title}</span>
        <span className="line-clamp-2 text-xs text-muted-foreground">{node.summary}</span>
        {node.todo ? (
          <Badge
            variant="outline"
            className="mt-0.5 w-fit border-brand px-1.5 py-0 text-[10px] text-brand-strong"
          >
            À compléter
          </Badge>
        ) : null}
      </span>
    </>
  );
}

/**
 * Profil au centre + résumé en branches : chaque branche donne un compte ou un état (« 12 compétences »),
 * le détail s'ouvre au clic. Les branches sont déplaçables (positions mémorisées) quand `draggable` est actif.
 */
export function ProfileOrbit({ center, nodes, storageKey, draggable = true }: ProfileOrbitProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [orbital, setOrbital] = useState(false);
  const orbitalRef = useRef(false);
  orbitalRef.current = orbital;
  const defaults = useMemo(
    () =>
      Object.fromEntries(
        nodes.map((node, index) => [node.key, positionOf(index, nodes.length)])
      ) as Record<string, Point>,
    [nodes]
  );
  const [overrides, setOverrides] = useState<Record<string, Point>>(() =>
    draggable ? loadPositions(storageKey) : {}
  );
  const dragRef = useRef<{ key: string; pointerId: number } | null>(null);
  const movedRef = useRef(false);

  useEffect(() => {
    setOverrides(draggable ? loadPositions(storageKey) : {});
  }, [storageKey, draggable]);

  // Orbite complète si le conteneur est assez large, grille de cartes sinon
  useLayoutEffect(() => {
    const node = containerRef.current;
    if (!node) return;
    const update = () => setOrbital(node.getBoundingClientRect().width >= ORBIT_MIN_WIDTH);
    update();
    if (typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(update);
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  const positions = useMemo(() => {
    const next: Record<string, Point> = { ...defaults };
    for (const [key, point] of Object.entries(overrides)) {
      if (next[key]) next[key] = point;
    }
    return next;
  }, [defaults, overrides]);

  const onPointerDown = useCallback(
    (key: string, event: ReactPointerEvent<HTMLElement>) => {
      if (event.button !== 0 || !draggable) return;
      // En grille de cartes, pas de drag.
      if (!orbitalRef.current) return;
      movedRef.current = false;
      dragRef.current = { key, pointerId: event.pointerId };
      event.currentTarget.setPointerCapture(event.pointerId);
    },
    [draggable]
  );

  const onPointerMove = useCallback(
    (event: ReactPointerEvent<HTMLElement>) => {
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
    },
    [storageKey]
  );

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

  const lines = useMemo(
    () =>
      nodes.map((node) => {
        const point = positions[node.key] ?? { x: 50, y: 50 };
        return { key: node.key, x2: point.x, y2: point.y };
      }),
    [nodes, positions]
  );

  return (
    <div
      ref={containerRef}
      className={cn(
        "w-full",
        orbital ? "relative mx-auto block aspect-square max-w-[800px]" : "flex flex-col gap-6"
      )}
    >
      {orbital ? (
        <>
          <svg
            className="pointer-events-none absolute inset-0 h-full w-full text-brand-soft-border"
            viewBox="0 0 100 100"
            preserveAspectRatio="none"
            aria-hidden
          >
            {lines.map((line) => (
              <line
                key={line.key}
                x1={50}
                y1={50}
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
            className="pointer-events-none absolute inset-[14%] rounded-full border border-dashed border-brand-soft-border bg-brand-soft/40"
            aria-hidden
          />
          <div
            className="pointer-events-none absolute inset-[30%] rounded-full border border-dashed border-brand-soft-border"
            aria-hidden
          />
        </>
      ) : null}

      <div
        className={cn(
          orbital && "absolute left-1/2 top-1/2 z-30 w-64 -translate-x-1/2 -translate-y-1/2"
        )}
      >
        {center}
      </div>

      <div className={cn(orbital ? "contents" : "grid gap-3 sm:grid-cols-2")}>
        {nodes.map((node) => {
          const point = positions[node.key] ?? { x: 50, y: 50 };
          const style = {
            "--x": `${point.x}%`,
            "--y": `${point.y}%`,
          } as CSSProperties;
          const className = cn(
            BRANCH_CLASSES,
            orbital && BRANCH_ORBIT_CLASSES,
            orbital && draggable && BRANCH_DRAG_CLASSES,
            node.todo ? "border-dashed border-brand" : "border-brand-soft-border"
          );

          return node.to ? (
            <Link
              key={node.key}
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
              key={node.key}
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
          );
        })}
      </div>
    </div>
  );
}
