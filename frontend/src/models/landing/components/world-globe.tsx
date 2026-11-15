import { useEffect, useRef } from "react";
import { cn } from "@/lib/utils";
import {
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
const SAMPLE_COUNT = 9000;
const TILT = 0.32;
const INITIAL_ROTATION = -12 * DEG;
const AUTO_SPEED = (2 * Math.PI) / 70000;
const ARC_STEPS = 48;
const ARC_GROW_MS = 1400;
const ARC_HOLD_MS = 1800;
const ARC_FADE_MS = 900;
const ARC_LIFETIME_MS = ARC_GROW_MS + ARC_HOLD_MS + ARC_FADE_MS;
const ARC_SPAWN_MS = 1900;
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

function insidePolygon(lon: number, lat: number, polygon: LonLat[]) {
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

let landCache: Float32Array | null = null;

/** Échantillonnage de Fibonacci : une grille de points quasi uniforme sur la sphère. */
function landPoints() {
  if (landCache) return landCache;
  const golden = Math.PI * (3 - Math.sqrt(5));
  const coords: number[] = [];
  for (let i = 0; i < SAMPLE_COUNT; i++) {
    const y = 1 - (2 * (i + 0.5)) / SAMPLE_COUNT;
    const lat = Math.asin(y) / DEG;
    const lon = (((i * golden) % (2 * Math.PI)) - Math.PI) / DEG;
    if (isLand(lon, lat)) coords.push(...toVector(lat, lon));
  }
  landCache = Float32Array.from(coords);
  return landCache;
}

/** Arc de grand cercle surélevé au milieu, d'autant plus haut que les villes sont éloignées. */
function arcSamples(connection: GlobeConnection) {
  const a = toVector(connection.dev.lat, connection.dev.lon);
  const b = toVector(connection.company.lat, connection.company.lon);
  const dot = Math.min(1, Math.max(-1, a[0] * b[0] + a[1] * b[1] + a[2] * b[2]));
  const omega = Math.acos(dot);
  const sinOmega = Math.sin(omega) || 1;
  const lift = 0.06 + 0.28 * (omega / Math.PI);
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

export function WorldGlobe({
  className,
  onConnection,
}: {
  className?: string;
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
    const markers = GLOBE_MARKERS.map((marker, i) => ({
      kind: marker.kind,
      vector: toVector(marker.lat, marker.lon),
      phase: (i * 0.137) % 1,
    }));
    const arcs = GLOBE_CONNECTIONS.map(arcSamples);
    const endpoints = GLOBE_CONNECTIONS.map(
      (c) => [toVector(c.dev.lat, c.dev.lon), toVector(c.company.lat, c.company.lon)] as const
    );

    let palette = readPalette();
    let width = 0;
    let height = 0;
    let frame = 0;
    let rotation = INITIAL_ROTATION;
    let velocity = 0;
    let dragging = false;
    let lastPointerX = 0;
    let lastPointerTime = 0;
    let lastFrameTime = 0;
    let visible = false;
    let active: ActiveArc[] = [];
    let nextSpawn = 0;
    let nextIndex = 0;

    const facingZ = (v: Vec3) => {
      const z = -v[0] * Math.sin(rotation) + v[2] * Math.cos(rotation);
      return v[1] * Math.sin(TILT) + z * Math.cos(TILT);
    };

    if (reduceMotion) {
      active = endpoints
        .map((pair, index) => ({ index, ok: facingZ(pair[0]) > 0.15 && facingZ(pair[1]) > 0.15 }))
        .filter((entry) => entry.ok)
        .slice(0, 4)
        .map(({ index }) => ({ index, start: 0, frozen: true }));
    }

    const spawnArcs = (now: number) => {
      active = active.filter((arc) => now - arc.start < ARC_LIFETIME_MS);
      if (now < nextSpawn) return;
      for (let k = 0; k < endpoints.length; k++) {
        const index = (nextIndex + k) % endpoints.length;
        if (active.some((arc) => arc.index === index)) continue;
        const [from, to] = endpoints[index];
        if (facingZ(from) > 0.12 && facingZ(to) > 0.12) {
          active.push({ index, start: now });
          nextIndex = index + 1;
          nextSpawn = now + ARC_SPAWN_MS;
          onConnectionRef.current?.(GLOBE_CONNECTIONS[index]);
          return;
        }
      }
      nextSpawn = now + 400;
    };

    const draw = (now: number) => {
      if (!width || !height) return;
      ctx.clearRect(0, 0, width, height);

      const radius = Math.min(width, height) * 0.42;
      const cx = width / 2;
      const cy = height / 2;
      const cr = Math.cos(rotation);
      const sr = Math.sin(rotation);
      const ct = Math.cos(TILT);
      const st = Math.sin(TILT);

      const project = (x: number, y: number, z: number): Vec3 => {
        const rx = x * cr + z * sr;
        const rz = -x * sr + z * cr;
        return [rx, y * ct - rz * st, y * st + rz * ct];
      };

      const glow = ctx.createRadialGradient(cx, cy, radius * 0.8, cx, cy, radius * 1.32);
      glow.addColorStop(0, hsla(palette.brand, 0.24));
      glow.addColorStop(1, hsla(palette.brand, 0));
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(cx, cy, radius * 1.32, 0, Math.PI * 2);
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

      const dotRadius = Math.max(0.6, radius * 0.0078);
      const buckets = Array.from({ length: DEPTH_BUCKETS }, () => new Path2D());
      for (let i = 0; i < land.length; i += 3) {
        const [x, y, z] = project(land[i], land[i + 1], land[i + 2]);
        if (z <= 0) continue;
        const sx = cx + x * radius;
        const sy = cy - y * radius;
        const path = buckets[Math.min(DEPTH_BUCKETS - 1, Math.floor(z * DEPTH_BUCKETS))];
        path.moveTo(sx + dotRadius, sy);
        path.arc(sx, sy, dotRadius, 0, Math.PI * 2);
      }
      buckets.forEach((path, i) => {
        ctx.fillStyle = hsla(palette.foreground, 0.1 + (0.42 * (i + 1)) / DEPTH_BUCKETS);
        ctx.fill(path);
      });

      for (const arc of active) {
        const samples = arcs[arc.index];
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
        const gradient = ctx.createLinearGradient(
          cx + start[0] * radius,
          cy - start[1] * radius,
          cx + end[0] * radius,
          cy - end[1] * radius
        );
        gradient.addColorStop(0, hsla(palette.brand, 0.9 * alpha));
        gradient.addColorStop(1, hsla(palette.success, 0.9 * alpha));

        ctx.beginPath();
        let penDown = false;
        let headPoint: Vec3 | null = null;
        for (let s = 0; s <= lastStep; s++) {
          const [x, y, z] = project(samples[s * 3], samples[s * 3 + 1], samples[s * 3 + 2]);
          const shown = z > 0 || x * x + y * y > 1;
          if (!shown) {
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
        ctx.lineWidth = Math.max(1, radius * 0.0055);
        ctx.lineCap = "round";
        ctx.stroke();

        if (headPoint && head < 1) {
          ctx.beginPath();
          ctx.arc(headPoint[0], headPoint[1], Math.max(1.5, radius * 0.012), 0, Math.PI * 2);
          ctx.fillStyle = hsla(palette.brand, 1);
          ctx.fill();
        }
      }

      for (const marker of markers) {
        const [x, y, z] = project(...marker.vector);
        if (z <= 0.02) continue;
        const sx = cx + x * radius;
        const sy = cy - y * radius;
        const color = marker.kind === "dev" ? palette.brand : palette.success;
        const core = Math.max(1.6, radius * 0.011) * (0.65 + 0.35 * z);

        if (!reduceMotion) {
          const pulse = (now / PULSE_MS + marker.phase) % 1;
          ctx.beginPath();
          ctx.arc(sx, sy, core * (1.4 + pulse * 2.8), 0, Math.PI * 2);
          ctx.fillStyle = hsla(color, (1 - pulse) * 0.28 * z);
          ctx.fill();
        }

        ctx.beginPath();
        ctx.arc(sx, sy, core, 0, Math.PI * 2);
        ctx.fillStyle = hsla(color, 0.45 + 0.55 * z);
        ctx.fill();
      }
    };

    const tick = (now: number) => {
      frame = 0;
      const dt = lastFrameTime ? Math.min(64, now - lastFrameTime) : 16;
      lastFrameTime = now;

      if (!dragging) {
        if (Math.abs(velocity) > 0.000005) {
          rotation += velocity * dt;
          velocity *= Math.pow(0.94, dt / 16);
        } else {
          velocity = 0;
        }
        if (!reduceMotion) rotation += AUTO_SPEED * dt;
      }
      if (!reduceMotion) spawnArcs(now);
      draw(now);

      const animating = !reduceMotion || dragging || velocity !== 0;
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
      velocity = 0;
      lastPointerX = event.clientX;
      lastPointerTime = event.timeStamp;
      canvas.setPointerCapture(event.pointerId);
      schedule();
    };

    const handlePointerMove = (event: PointerEvent) => {
      if (!dragging) return;
      const radius = Math.min(width, height) * 0.42 || 1;
      const delta = (event.clientX - lastPointerX) / radius;
      const elapsed = Math.max(1, event.timeStamp - lastPointerTime);
      rotation += delta;
      velocity = delta / elapsed;
      lastPointerX = event.clientX;
      lastPointerTime = event.timeStamp;
      schedule();
    };

    const handlePointerUp = (event: PointerEvent) => {
      if (!dragging) return;
      dragging = false;
      if (canvas.hasPointerCapture(event.pointerId)) {
        canvas.releasePointerCapture(event.pointerId);
      }
      if (event.timeStamp - lastPointerTime > 80) velocity = 0;
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
      aria-label="Globe terrestre montrant des développeurs et des entreprises répartis sur tous les continents"
      className={cn("size-full cursor-grab touch-pan-y active:cursor-grabbing", className)}
    />
  );
}
