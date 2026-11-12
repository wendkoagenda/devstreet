import type { CSSProperties, ReactNode } from "react";
import { Link } from "react-router-dom";
import { Badge } from "@/components/ui/badge";

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
};

type ProfileOrbitProps = {
  /** Le profil, au centre. */
  center: ReactNode;
  /** Les éléments liés au profil, répartis régulièrement en orbite (de préférence 6 à 10). */
  nodes: OrbitNode[];
};

/** Rayon de l'orbite, en pourcentage de la largeur du conteneur (carré). */
const RADIUS = 38;

/** Position (en %) du centre d'un satellite : le premier est en haut, puis dans le sens des aiguilles d'une montre. */
function positionOf(index: number, count: number) {
  const angle = ((-90 + (360 / count) * index) * Math.PI) / 180;
  return { x: 50 + RADIUS * Math.cos(angle), y: 50 + RADIUS * Math.sin(angle) };
}

const NODE_CLASSES =
  "group flex w-full items-center gap-3 rounded-xl border bg-card p-3 text-left shadow-sm transition-colors " +
  "hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring " +
  "xl:absolute xl:left-[var(--x)] xl:top-[var(--y)] xl:z-10 xl:w-44 xl:-translate-x-1/2 xl:-translate-y-1/2";

function NodeBody({ node }: { node: OrbitNode }) {
  return (
    <>
      <span
        className="flex size-9 shrink-0 items-center justify-center rounded-full border border-border bg-muted text-foreground"
        aria-hidden
      >
        {node.icon}
      </span>
      <span className="flex min-w-0 flex-1 flex-col gap-0.5">
        <span className="truncate text-sm font-semibold text-foreground">{node.title}</span>
        <span className="line-clamp-2 text-xs text-muted-foreground">{node.summary}</span>
        {node.todo ? (
          <Badge variant="outline" className="mt-0.5 w-fit px-1.5 py-0 text-[10px]">
            À compléter
          </Badge>
        ) : null}
      </span>
    </>
  );
}

/**
 * Le profil au centre et ses éléments liés en orbite autour (à partir de 1280 px de large) ; en dessous, le profil puis la liste
 * des éléments. Les anneaux tournent très lentement, sauf si l'utilisateur préfère réduire les animations.
 */
export function ProfileOrbit({ center, nodes }: ProfileOrbitProps) {
  const positions = nodes.map((_node, index) => positionOf(index, nodes.length));

  return (
    <div className="flex flex-col gap-6 xl:relative xl:mx-auto xl:block xl:aspect-square xl:w-full xl:max-w-[800px] xl:gap-0">
      {/* Orbites et fils reliant le profil à chaque satellite (très grand écran uniquement) */}
      <svg
        className="pointer-events-none absolute inset-0 hidden h-full w-full text-border xl:block"
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        aria-hidden
      >
        {positions.map((position, index) => (
          <line
            key={nodes[index].key}
            x1={50}
            y1={50}
            x2={position.x}
            y2={position.y}
            stroke="currentColor"
            strokeWidth={1}
            strokeDasharray="2 4"
            vectorEffect="non-scaling-stroke"
          />
        ))}
      </svg>
      <div
        className="pointer-events-none absolute inset-[12%] hidden rounded-full border border-dashed border-border bg-muted/20 xl:block xl:animate-spin xl:motion-reduce:animate-none xl:[animation-duration:180s]"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute inset-[28%] hidden rounded-full border border-dashed border-border xl:block xl:animate-spin xl:motion-reduce:animate-none xl:[animation-direction:reverse] xl:[animation-duration:120s]"
        aria-hidden
      />

      <div className="xl:absolute xl:left-1/2 xl:top-1/2 xl:z-10 xl:w-64 xl:-translate-x-1/2 xl:-translate-y-1/2">
        {center}
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:contents">
        {nodes.map((node, index) => {
          const style = { "--x": `${positions[index].x}%`, "--y": `${positions[index].y}%` } as CSSProperties;
          const className = `${NODE_CLASSES} ${node.todo ? "border-dashed border-muted-foreground" : "border-border"}`;
          return node.to ? (
            <Link key={node.key} to={node.to} className={className} style={style}>
              <NodeBody node={node} />
            </Link>
          ) : (
            <button key={node.key} type="button" onClick={node.onSelect} className={className} style={style}>
              <NodeBody node={node} />
            </button>
          );
        })}
      </div>
    </div>
  );
}
