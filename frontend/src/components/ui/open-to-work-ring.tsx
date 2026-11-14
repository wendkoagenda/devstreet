import { useId } from "react";
import { cn } from "@/lib/utils";

/** Point d'un cercle de centre (50, 50), à `angle` degrés de part et d'autre du bas (6 h). */
function point(radius: number, angle: number, side: -1 | 1) {
  const rad = (angle * Math.PI) / 180;
  return `${(50 + side * radius * Math.sin(rad)).toFixed(2)} ${(50 + radius * Math.cos(rad)).toFixed(2)}`;
}

/** Arc du bas, de gauche à droite en passant par 6 h (sens inverse des aiguilles d'une montre à l'écran). */
function bottomArc(radius: number, angle: number) {
  return `M ${point(radius, angle, -1)} A ${radius} ${radius} 0 0 0 ${point(radius, angle, 1)}`;
}

const RING_RADIUS = 45; // milieu de la bande
const BAND_WIDTH = 12;
const ARC_ANGLE = 72; // demi-ouverture de l'arc, de part et d'autre du bas
const FONT_SIZE = 7.4;
// Le haut des lettres pointe vers le centre : la ligne de base est décalée vers l'extérieur
// d'une demi-hauteur de capitale pour que le texte soit centré dans la bande.
const TEXT_RADIUS = RING_RADIUS + FONT_SIZE * 0.36;

/**
 * Arc « Open to work » à poser sur une photo de profil, façon LinkedIn : une bande en demi-cercle en bas de la bulle,
 * avec le texte centré dans la bande. À placer dans un conteneur `relative` qui entoure l'avatar.
 * Couleur d'accent du thème (le texte prend la couleur lisible sur l'accent, en clair comme en sombre).
 */
export function OpenToWorkRing({ className, showText = true }: { className?: string; showText?: boolean }) {
  const id = useId().replace(/:/g, "");
  const textPathId = `otw-text-${id}`;

  return (
    <svg
      viewBox="0 0 100 100"
      role="img"
      aria-label="Ouvert aux opportunités"
      className={cn(
        "pointer-events-none absolute left-1/2 top-1/2 h-[116%] w-[116%] -translate-x-1/2 -translate-y-1/2 overflow-visible",
        className
      )}
    >
      <title>Ouvert aux opportunités</title>
      <defs>
        <path id={textPathId} d={bottomArc(TEXT_RADIUS, ARC_ANGLE)} />
      </defs>
      {/* Liseré de la couleur de fond : sépare nettement la bande de la photo */}
      <path
        d={bottomArc(RING_RADIUS, ARC_ANGLE)}
        fill="none"
        className="stroke-card"
        strokeWidth={BAND_WIDTH + 2.5}
        strokeLinecap="round"
      />
      <path
        d={bottomArc(RING_RADIUS, ARC_ANGLE)}
        fill="none"
        className="stroke-brand"
        strokeWidth={BAND_WIDTH}
        strokeLinecap="round"
      />
      {showText ? (
      <text
        className="fill-brand-foreground"
        fontSize={FONT_SIZE}
        fontWeight={700}
        letterSpacing={0.9}
        textAnchor="middle"
        style={{ fontFamily: "inherit" }}
      >
        <textPath href={`#${textPathId}`} startOffset="50%">
          OPEN TO WORK
        </textPath>
      </text>
      ) : null}
    </svg>
  );
}
