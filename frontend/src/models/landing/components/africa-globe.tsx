import { useEffect, useRef } from "react";
import { cn } from "@/lib/utils";
import {
  AFRICA_POLYGONS,
  ANTARCTIC_LATITUDE,
  INLAND_SEAS,
  LAND_POLYGONS,
  type LonLat,
} from "../data/land-polygons";
import {
  GLOBE_CONNECTIONS,
  GLOBE_MARKERS,
  type GlobeConnection,
} from "../data/showcase-profiles";

const DEG = Math.PI / 180;
const SAMPLE_COUNT = 16000;
const AFRICA_CENTER = { lat: 2, lon: 18 };
const TILT = 4 * DEG;
const BASE_ROTATION = -AFRICA_CENTER.lon * DEG;
const SWAY_AMPLITUDE = 11 * DEG;
const SWAY_PERIOD_MS = 20000;
const RETURN_MS = 380;
const GLOBE_SCALE = 0.45;
const ARC_STEPS = 48;
const ARC_GROW_MS = 1300;
const ARC_HOLD_MS = 2000;
const ARC_FADE_MS = 900;
const ARC_LIFETIME_MS = ARC_GROW_MS + ARC_HOLD_MS + ARC_FADE_MS;
const ARC_SPAWN_MS = 1700;
const PULSE_MS = 2400;
const DEPTH_BUCKETS = 4;

type Vec3 = [number, number, number];
type Palette = { brand: string; success: string; foreground: string; card: string; border: string };
type ActiveArc = { index: number; start: number; frozen?: boolean };

const FALLBACK_PALETTE: Palette = {
  brand: "265 22% 48%",
  success: "160 50% 32%",
  foreground: "250 10% 16%",
  card: "0 0% 100%",
  border: "270 10% 88%",
};

const hsla = (triplet: string, alpha: number) => `hsl(${triplet} / ${alpha})`;

function toVector(lat: number, lon: number): Vec3 {
  const cosLat = Math.cos(lat * DEG);
  return [cosLat * Math.sin(lon * DEG), Math.sin(lat * DEG), cosLat * Math.cos(lon * DEG)];
}

function insidePolygon(lon: number, lat: number, polygon: readonly LonLat[]) {
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const [xi, yi] = polygon[i];
    const [xj, yj] = polygon[j];
    if (yi > lat !== yj > lat && lon < ((xj - xi) * (lat - yi)) / (yj - yi) + xi) {
      inside = !inside;
    }
  }
  return inside;
}

function isLand(lon: number, lat: number) {
  if (lat < ANTARCTIC_LATITUDE) return true;
  if (INLAND_SEAS.some((sea) => insidePolygon(lon, lat, sea))) return false;
  return LAND_POLYGONS.some((polygon) => insidePolygon(lon, lat, polygon));
}

type LandSample = { positions: Float32Array; africa: Uint8Array };
let landCache: LandSample | null = null;

/** Échantillonnage de Fibonacci : une grille de points quasi uniforme sur la sphère. */
function landPoints(): LandSample {
  if (landCache) return landCache;
  const golden = Math.PI * (3 - Math.sqrt(5));
  const coords: number[] = [];
  const africa: number[] = [];
  for (let i = 0; i < SAMPLE_COUNT; i++) {
    const y = 1 - (2 * (i + 0.5)) / SAMPLE_COUNT;
    const lat = Math.asin(y) / DEG;
    const lon = (((i * golden) % (2 * Math.PI)) - Math.PI) / DEG;
    if (!isLand(lon, lat)) continue;
    coords.push(...toVector(lat, lon));
    africa.push(AFRICA_POLYGONS.some((polygon) => insidePolygon(lon, lat, polygon)) ? 1 : 0);
  }
  landCache = { positions: Float32Array.from(coords), africa: Uint8Array.from(africa) };
  return landCache;
}

/** Arc de grand cercle surélevé au milieu, d'autant plus haut que les villes sont éloignées. */
function arcSamples(connection: GlobeConnection) {
  const a = toVector(connection.dev.lat, connection.dev.lon);
  const b = toVector(connection.company.lat, connection.company.lon);
  const dot = Math.min(1, Math.max(-1, a[0] * b[0] + a[1] * b[1] + a[2] * b[2]));
  const omega = Math.acos(dot);
  const sinOmega = Math.sin(omega) || 1;
  const lift = 0.04 + 0.42 * (omega / Math.PI);
  const samples = new Float32Array((ARC_STEPS + 1) * 3);
  for (let s = 0; s <= ARC_STEPS; s++) {
    const t = s / ARC_STEPS;
    const wa = Math.sin((1 - t) * omega) / sinOmega;
    const wb = Math.sin(t * omega) / sinOmega;
    const height = 1 + lift * Math.sin(Math.PI * t);
    samples[s * 3] = (wa * a[0] + wb * b[0]) * height;
    samples[s * 3 + 1] = (wa * a[1] + wb * b[1]) * height;
    samples[s * 3 + 2] = (wa * a[2] + wb * b[2]) * height;
  }
  return samples;
}

function readPalette(): Palette {
  const style = getComputedStyle(document.documentElement);
  const read = (name: string, fallback: string) =>
    style.getPropertyValue(name).trim() || fallback;
  return {
    brand: read("--brand", FALLBACK_PALETTE.brand),
    success: read("--success", FALLBACK_PALETTE.success),
    foreground: read("--foreground", FALLBACK_PALETTE.foreground),
    card: read("--card", FALLBACK_PALETTE.card),
    border: read("--border", FALLBACK_PALETTE.border),
  };
}

export function AfricaGlobe({
  className,
  label,
  onConnection,
}: {
  className?: string;
  label: string;
  onConnection?: (connection: GlobeConnection) => void;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const onConnectionRef = useRef(onConnection);

  useEffect(() => {
    onConnectionRef.current = onConnection;
  });

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const land = landPoints();
    const fontFamily = getComputedStyle(canvas).fontFamily;
    const africaCenter = toVector(AFRICA_CENTER.lat, AFRICA_CENTER.lon);
    const markers = GLOBE_MARKERS.map((marker, i) => ({
      kind: marker.kind,
      vector: toVector(marker.lat, marker.lon),
      phase: (i * 0.137) % 1,
    }));
    const arcs = GLOBE_CONNECTIONS.map(arcSamples);

    let palette = readPalette();
    let width = 0;
    let height = 0;
    let frame = 0;
    let swayClock = 0;
    let dragOffset = 0;
    let dragging = false;
    let lastPointerX = 0;
    let lastFrameTime = 0;
    let visible = false;
    let active: ActiveArc[] = reduceMotion
      ? arcs.slice(0, 4).map((_, index) => ({ index, start: 0, frozen: true }))
      : [];
    let nextSpawn = 0;
    let nextIndex = 0;

    const rotation = () =>
      BASE_ROTATION +
      dragOffset +
      (reduceMotion ? 0 : SWAY_AMPLITUDE * Math.sin((2 * Math.PI * swayClock) / SWAY_PERIOD_MS));

    const spawnArcs = (now: number) => {
      active = active.filter((arc) => now - arc.start < ARC_LIFETIME_MS);
      if (now < nextSpawn) return;
      const index = nextIndex % arcs.length;
      active.push({ index, start: now });
      nextIndex = index + 1;
      nextSpawn = now + ARC_SPAWN_MS;
      onConnectionRef.current?.(GLOBE_CONNECTIONS[index]);
    };

    const drawLabel = (text: string, x: number, y: number, alpha: number) => {
      ctx.font = `500 11px ${fontFamily}`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.lineJoin = "round";
      ctx.lineWidth = 4;
      ctx.strokeStyle = hsla(palette.card, 0.92 * alpha);
      ctx.strokeText(text, x, y);
      ctx.fillStyle = hsla(palette.foreground, 0.9 * alpha);
      ctx.fillText(text, x, y);
    };

    const draw = (now: number) => {
      if (!width || !height) return;
      ctx.clearRect(0, 0, width, height);

      const radius = Math.min(width, height) * GLOBE_SCALE;
      const cx = width / 2;
      const cy = height / 2;
      const angle = rotation();
      const cr = Math.cos(angle);
      const sr = Math.sin(angle);
      const ct = Math.cos(TILT);
      const st = Math.sin(TILT);

      const project = (x: number, y: number, z: number): Vec3 => {
        const rx = x * cr + z * sr;
        const rz = -x * sr + z * cr;
        return [rx, y * ct - rz * st, y * st + rz * ct];
      };

      const glow = ctx.createRadialGradient(cx, cy, radius * 0.8, cx, cy, radius * 1.3);
      glow.addColorStop(0, hsla(palette.brand, 0.22));
      glow.addColorStop(1, hsla(palette.brand, 0));
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(cx, cy, radius * 1.3, 0, Math.PI * 2);
      ctx.fill();

      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.fillStyle = hsla(palette.card, 1);
      ctx.fill();
      const shade = ctx.createRadialGradient(
        cx - radius * 0.35,
        cy - radius * 0.4,
        radius * 0.05,
        cx,
        cy,
        radius
      );
      shade.addColorStop(0, hsla(palette.brand, 0.02));
      shade.addColorStop(1, hsla(palette.brand, 0.16));
      ctx.fillStyle = shade;
      ctx.fill();
      ctx.lineWidth = 1;
      ctx.strokeStyle = hsla(palette.border, 1);
      ctx.stroke();

      const [ax, ay] = project(...africaCenter);
      const spotlight = ctx.createRadialGradient(
        cx + ax * radius,
        cy - ay * radius,
        0,
        cx + ax * radius,
        cy - ay * radius,
        radius * 0.62
      );
      spotlight.addColorStop(0, hsla(palette.brand, 0.14));
      spotlight.addColorStop(1, hsla(palette.brand, 0));
      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.clip();
      ctx.fillStyle = spotlight;
      ctx.fillRect(cx - radius, cy - radius, radius * 2, radius * 2);
      ctx.restore();

      const dotRadius = Math.max(0.6, radius * 0.0066);
      const africaBuckets = Array.from({ length: DEPTH_BUCKETS }, () => new Path2D());
      const worldPath = new Path2D();
      const { positions, africa } = land;
      for (let i = 0, p = 0; i < positions.length; i += 3, p++) {
        const [x, y, z] = project(positions[i], positions[i + 1], positions[i + 2]);
        if (z <= 0) continue;
        const sx = cx + x * radius;
        const sy = cy - y * radius;
        const path = africa[p]
          ? africaBuckets[Math.min(DEPTH_BUCKETS - 1, Math.floor(z * DEPTH_BUCKETS))]
          : worldPath;
        path.moveTo(sx + dotRadius, sy);
        path.arc(sx, sy, dotRadius, 0, Math.PI * 2);
      }
      ctx.fillStyle = hsla(palette.foreground, 0.11);
      ctx.fill(worldPath);
      africaBuckets.forEach((path, i) => {
        ctx.fillStyle = hsla(palette.foreground, 0.3 + (0.5 * (i + 1)) / DEPTH_BUCKETS);
        ctx.fill(path);
      });

      const labels: { text: string; x: number; y: number; alpha: number }[] = [];

      for (const arc of active) {
        const samples = arcs[arc.index];
        const connection = GLOBE_CONNECTIONS[arc.index];
        const age = now - arc.start;
        const head = arc.frozen ? 1 : Math.min(1, age / ARC_GROW_MS);
        const fadeStart = ARC_GROW_MS + ARC_HOLD_MS;
        const alpha = arc.frozen || age < fadeStart ? 1 : Math.max(0, 1 - (age - fadeStart) / ARC_FADE_MS);
        const lastStep = Math.floor(head * ARC_STEPS);

        const start = project(samples[0], samples[1], samples[2]);
        const end = project(
          samples[ARC_STEPS * 3],
          samples[ARC_STEPS * 3 + 1],
          samples[ARC_STEPS * 3 + 2]
        );
        const startX = cx + start[0] * radius;
        const startY = cy - start[1] * radius;
        const endX = cx + end[0] * radius;
        const endY = cy - end[1] * radius;
        const gradient = ctx.createLinearGradient(startX, startY, endX, endY);
        gradient.addColorStop(0, hsla(palette.brand, 0.95 * alpha));
        gradient.addColorStop(1, hsla(palette.success, 0.95 * alpha));

        ctx.beginPath();
        let penDown = false;
        let headPoint: Vec3 | null = null;
        for (let s = 0; s <= lastStep; s++) {
          const [x, y, z] = project(samples[s * 3], samples[s * 3 + 1], samples[s * 3 + 2]);
          if (z <= 0 && x * x + y * y <= 1) {
            penDown = false;
            continue;
          }
          const sx = cx + x * radius;
          const sy = cy - y * radius;
          if (penDown) ctx.lineTo(sx, sy);
          else ctx.moveTo(sx, sy);
          penDown = true;
          if (s === lastStep) headPoint = [sx, sy, z];
        }
        ctx.strokeStyle = gradient;
        ctx.lineWidth = Math.max(1.2, radius * 0.006);
        ctx.lineCap = "round";
        ctx.stroke();

        if (headPoint && head < 1) {
          ctx.beginPath();
          ctx.arc(headPoint[0], headPoint[1], Math.max(1.8, radius * 0.013), 0, Math.PI * 2);
          ctx.fillStyle = hsla(palette.brand, 1);
          ctx.fill();
        }

        if (!arc.frozen && age > ARC_GROW_MS * 0.5) {
          const labelAlpha = alpha * Math.min(1, (age - ARC_GROW_MS * 0.5) / 400);
          labels.push({ text: connection.dev.city, x: startX, y: startY - 14, alpha: labelAlpha });
          labels.push({ text: connection.company.city, x: endX, y: endY + 15, alpha: labelAlpha });
        }
      }

      for (const marker of markers) {
        const [x, y, z] = project(...marker.vector);
        if (z <= 0.02) continue;
        const sx = cx + x * radius;
        const sy = cy - y * radius;
        const color = marker.kind === "dev" ? palette.brand : palette.success;
        const core = Math.max(1.6, radius * 0.0105) * (0.65 + 0.35 * z);

        if (!reduceMotion) {
          const pulse = (now / PULSE_MS + marker.phase) % 1;
          ctx.beginPath();
          ctx.arc(sx, sy, core * (1.4 + pulse * 2.8), 0, Math.PI * 2);
          ctx.fillStyle = hsla(color, (1 - pulse) * 0.3 * z);
          ctx.fill();
        }

        ctx.beginPath();
        ctx.arc(sx, sy, core, 0, Math.PI * 2);
        ctx.fillStyle = hsla(color, 0.5 + 0.5 * z);
        ctx.fill();
      }

      labels.forEach((item) => drawLabel(item.text, item.x, item.y, item.alpha));
    };

    const tick = (now: number) => {
      frame = 0;
      const dt = lastFrameTime ? Math.min(64, now - lastFrameTime) : 16;
      lastFrameTime = now;

      if (!dragging) {
        swayClock += dt;
        dragOffset *= Math.exp(-dt / RETURN_MS);
        if (Math.abs(dragOffset) < 0.0002) dragOffset = 0;
      }
      if (!reduceMotion) spawnArcs(now);
      draw(now);

      const animating = !reduceMotion || dragging || dragOffset !== 0;
      if (visible && animating) frame = requestAnimationFrame(tick);
    };

    const schedule = () => {
      if (frame) return;
      lastFrameTime = 0;
      frame = requestAnimationFrame(tick);
    };

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      width = rect.width;
      height = rect.height;
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      schedule();
    };

    const handlePointerDown = (event: PointerEvent) => {
      dragging = true;
      lastPointerX = event.clientX;
      canvas.setPointerCapture(event.pointerId);
      schedule();
    };

    const handlePointerMove = (event: PointerEvent) => {
      if (!dragging) return;
      const radius = Math.min(width, height) * GLOBE_SCALE || 1;
      dragOffset += (event.clientX - lastPointerX) / radius;
      lastPointerX = event.clientX;
      schedule();
    };

    const handlePointerUp = (event: PointerEvent) => {
      if (!dragging) return;
      dragging = false;
      if (canvas.hasPointerCapture(event.pointerId)) {
        canvas.releasePointerCapture(event.pointerId);
      }
      schedule();
    };

    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(canvas);

    const visibilityObserver = new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting;
      if (visible) schedule();
      else if (frame) {
        cancelAnimationFrame(frame);
        frame = 0;
      }
    });
    visibilityObserver.observe(canvas);

    const themeObserver = new MutationObserver(() => {
      palette = readPalette();
      schedule();
    });
    themeObserver.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class", "style"],
    });

    canvas.addEventListener("pointerdown", handlePointerDown);
    canvas.addEventListener("pointermove", handlePointerMove);
    canvas.addEventListener("pointerup", handlePointerUp);
    canvas.addEventListener("pointercancel", handlePointerUp);

    return () => {
      if (frame) cancelAnimationFrame(frame);
      resizeObserver.disconnect();
      visibilityObserver.disconnect();
      themeObserver.disconnect();
      canvas.removeEventListener("pointerdown", handlePointerDown);
      canvas.removeEventListener("pointermove", handlePointerMove);
      canvas.removeEventListener("pointerup", handlePointerUp);
      canvas.removeEventListener("pointercancel", handlePointerUp);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      role="img"
      aria-label={label}
      className={cn("size-full cursor-grab touch-pan-y active:cursor-grabbing", className)}
    />
  );
}
