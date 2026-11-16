import {
  Suspense,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { useGLTF } from "@react-three/drei";
import {
  Box3,
  Color,
  MathUtils,
  Mesh,
  Vector3,
  type Group,
  type Material,
  type MeshStandardMaterial,
  type Object3D,
  type PerspectiveCamera,
} from "three";

export const CELINA_GLB = "/mascotte/celina.glb";

const FRAME_FILL = {
  sm: 0.7,
  md: 0.76,
  lg: 0.8,
} as const;

type FitSize = keyof typeof FRAME_FILL;

type SceneProps = {
  hovering: boolean;
  reducedMotion: boolean;
  px: number;
  fitSize: FitSize;
};

type FaceExpression = "idle" | "blink" | "hover";

type FaceParts = {
  happyEyes: Object3D[];
  wink: Object3D[];
  smiles: Object3D[];
  leftArm: Object3D | null;
  rightArm: Object3D | null;
};

function frameModel(
  root: Object3D,
  camera: PerspectiveCamera,
  fill: number
) {
  root.position.set(0, 0, 0);
  root.scale.set(1, 1, 1);
  root.rotation.set(0, 0, 0);
  root.updateWorldMatrix(true, true);

  const box = new Box3().setFromObject(root);
  const size = box.getSize(new Vector3());
  const center = box.getCenter(new Vector3());
  root.position.sub(center);

  const height = Math.max(size.y, 1e-6);
  const fov = (camera.fov * Math.PI) / 180;
  const distance = height / (2 * Math.tan(fov / 2) * fill);

  camera.position.set(0, height * 0.04, distance * 1.08);
  camera.near = Math.max(distance / 100, 0.05);
  camera.far = distance * 20;
  camera.lookAt(0, 0, 0);
  camera.updateProjectionMatrix();
}

function collectFaceParts(root: Object3D): FaceParts {
  const happyEyes: Object3D[] = [];
  const wink: Object3D[] = [];
  const smiles: Object3D[] = [];
  let leftArm: Object3D | null = null;
  let rightArm: Object3D | null = null;

  root.traverse((obj) => {
    const name = obj.name || "";
    if (name.startsWith("happy_eye")) happyEyes.push(obj);
    else if (name.startsWith("wink")) wink.push(obj);
    else if (name.startsWith("smile")) smiles.push(obj);
    else if (name === "Left_arm_pivot") leftArm = obj;
    else if (name === "Right_arm_pivot") rightArm = obj;
  });

  return { happyEyes, wink, smiles, leftArm, rightArm };
}

function setVisible(nodes: Object3D[], visible: boolean) {
  for (const node of nodes) {
    node.visible = visible;
    node.traverse((child) => {
      child.visible = visible;
    });
  }
}

/** Renforce le contraste des traits du visage (yeux / bouche). */
function boostFaceMaterials(root: Object3D) {
  root.traverse((obj) => {
    if (!(obj instanceof Mesh)) return;
    const name = obj.name || "";
    if (
      !name.startsWith("happy_eye") &&
      !name.startsWith("wink") &&
      !name.startsWith("smile")
    ) {
      return;
    }
    const materials: Material[] = Array.isArray(obj.material)
      ? obj.material
      : [obj.material];
    for (const mat of materials) {
      const std = mat as MeshStandardMaterial;
      if (!std || !("color" in std)) continue;
      const base = std.color?.clone?.() ?? new Color("#ffffff");
      std.emissive = base;
      std.emissiveIntensity = 0.55;
      std.needsUpdate = true;
    }
  });
}

/**
 * Visage du GLB :
 * - happy_eye* = œil droit (segments)
 * - wink* = œil gauche (forme clin d'œil du design)
 * - smile* = bouche
 * Idle = les trois visibles (comme le rendu Blender de référence).
 * Blink = on cache brièvement les deux yeux.
 */
function applyFaceExpression(parts: FaceParts, expression: FaceExpression) {
  const eyesOpen = expression !== "blink";
  setVisible(parts.happyEyes, eyesOpen);
  setVisible(parts.wink, eyesOpen);
  setVisible(parts.smiles, true);
}

function CelinaModel({
  hovering,
  reducedMotion,
  fitSize,
}: Omit<SceneProps, "px">) {
  const { camera, invalidate } = useThree();
  const rootRef = useRef<Group>(null);
  const modelRef = useRef<Group>(null);
  const partsRef = useRef<FaceParts | null>(null);
  const armBaseRef = useRef<{
    leftX: number;
    leftZ: number;
    rightX: number;
    rightZ: number;
  } | null>(null);
  const expressionRef = useRef<FaceExpression>("idle");
  const animRef = useRef({
    jump: 0,
    arm: 0,
    bobPhase: 0,
    activeUntil: 0,
  });

  const { scene } = useGLTF(CELINA_GLB);
  const cloned = useMemo(() => scene.clone(true), [scene]);
  const [ready, setReady] = useState(false);

  useLayoutEffect(() => {
    const node = modelRef.current;
    if (!node) return;
    frameModel(node, camera as PerspectiveCamera, FRAME_FILL[fitSize]);
    boostFaceMaterials(node);
    const parts = collectFaceParts(node);
    partsRef.current = parts;
    expressionRef.current = "idle";
    applyFaceExpression(parts, "idle");
    armBaseRef.current = {
      leftX: parts.leftArm?.rotation.x ?? 0,
      leftZ: parts.leftArm?.rotation.z ?? 0,
      rightX: parts.rightArm?.rotation.x ?? 0,
      rightZ: parts.rightArm?.rotation.z ?? 0,
    };
    setReady(true);
    invalidate();
  }, [cloned, fitSize, camera, invalidate]);

  // Clignement idle : bascule wink ~140ms puis retour idle (2 yeux).
  useEffect(() => {
    if (!ready || reducedMotion) return;

    let cancelled = false;
    let scheduleId = 0;
    let blinkOffId = 0;

    const scheduleBlink = () => {
      scheduleId = window.setTimeout(() => {
        if (cancelled) return;
        const parts = partsRef.current;
        if (!parts || hovering) {
          scheduleBlink();
          return;
        }
        expressionRef.current = "blink";
        applyFaceExpression(parts, "blink");
        animRef.current.activeUntil = performance.now() + 200;
        invalidate();

        blinkOffId = window.setTimeout(() => {
          if (cancelled) return;
          expressionRef.current = hovering ? "hover" : "idle";
          applyFaceExpression(parts, expressionRef.current);
          invalidate();
          scheduleBlink();
        }, 140);
      }, 3200 + Math.random() * 2400);
    };

    scheduleBlink();
    return () => {
      cancelled = true;
      window.clearTimeout(scheduleId);
      window.clearTimeout(blinkOffId);
      const parts = partsRef.current;
      if (parts) {
        expressionRef.current = "idle";
        applyFaceExpression(parts, "idle");
      }
    };
  }, [ready, reducedMotion, hovering, invalidate]);

  // Hover : expression happy + fenêtre d’anim corps.
  useEffect(() => {
    if (!ready || reducedMotion) return;
    const parts = partsRef.current;
    if (!parts) return;

    if (hovering) {
      if (expressionRef.current !== "blink") {
        expressionRef.current = "hover";
        applyFaceExpression(parts, "hover");
      }
      animRef.current.activeUntil = performance.now() + 1200;
    } else {
      if (expressionRef.current !== "blink") {
        expressionRef.current = "idle";
        applyFaceExpression(parts, "idle");
      }
      animRef.current.activeUntil = performance.now() + 600;
    }
    invalidate();
  }, [hovering, ready, reducedMotion, invalidate]);

  // Idle : ~20 fps pour le bob léger (évite always 60 fps).
  useEffect(() => {
    if (!ready || reducedMotion) return;
    const id = window.setInterval(() => invalidate(), 50);
    return () => window.clearInterval(id);
  }, [ready, reducedMotion, invalidate]);

  useFrame((_, delta) => {
    const root = rootRef.current;
    const parts = partsRef.current;
    const base = armBaseRef.current;
    if (!root) return;

    const now = performance.now();
    const anim = animRef.current;
    const dt = Math.min(delta, 0.05);

    // Bob idle permanent (léger).
    anim.bobPhase += dt * (hovering ? 5.5 : 2.2);
    const bob =
      reducedMotion || hovering
        ? 0
        : Math.sin(anim.bobPhase) * 0.018;

    // Saut hover.
    const jumpTarget = hovering && !reducedMotion ? 0.09 : 0;
    anim.jump = MathUtils.damp(anim.jump, jumpTarget, 12, dt);
    root.position.y = bob + anim.jump;

    // Squash / stretch sur le saut.
    const squash = anim.jump * 1.6;
    root.scale.set(1 + squash * 0.35, 1 - squash * 0.45, 1 + squash * 0.35);

    // Bras : légère ouverture + petit flap.
    const armTarget = hovering && !reducedMotion ? 1 : 0;
    anim.arm = MathUtils.damp(anim.arm, armTarget, 9, dt);
    if (parts && base) {
      const flap = hovering
        ? Math.sin(now / 160) * 0.12 * anim.arm
        : 0;
      const open = anim.arm * 0.55;
      if (parts.leftArm) {
        parts.leftArm.rotation.z = base.leftZ + open + flap;
        parts.leftArm.rotation.x = base.leftX - open * 0.25;
      }
      if (parts.rightArm) {
        parts.rightArm.rotation.z = base.rightZ - open - flap;
        parts.rightArm.rotation.x = base.rightX - open * 0.25;
      }
    }

    const settling =
      Math.abs(anim.jump - jumpTarget) > 0.001 ||
      Math.abs(anim.arm - armTarget) > 0.001;
    if (hovering || settling || now < anim.activeUntil) {
      invalidate();
    }
  });

  return (
    <group ref={rootRef} dispose={null}>
      <group ref={modelRef}>
        <primitive object={cloned} />
      </group>
    </group>
  );
}

export default function SelinaMascotteScene({
  hovering,
  reducedMotion,
  px,
  fitSize,
}: SceneProps) {
  return (
    <Canvas
      dpr={[1, 1.5]}
      gl={{ antialias: true, alpha: true, powerPreference: "low-power" }}
      camera={{ fov: 32, near: 0.1, far: 200, position: [0, 0, 3] }}
      style={{ width: px, height: px }}
      frameloop="demand"
      onCreated={({ invalidate }) => invalidate()}
    >
      <ambientLight intensity={1.05} />
      <directionalLight position={[2.4, 3.6, 2.8]} intensity={1.3} />
      <directionalLight position={[-2.4, 1.6, -0.4]} intensity={0.45} />
      <Suspense fallback={null}>
        <CelinaModel
          hovering={hovering}
          reducedMotion={reducedMotion}
          fitSize={fitSize}
        />
      </Suspense>
    </Canvas>
  );
}

useGLTF.preload(CELINA_GLB);
