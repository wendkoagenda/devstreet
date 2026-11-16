import { Suspense, useEffect, useMemo, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { useAnimations, useGLTF } from "@react-three/drei";
import type { Group } from "three";

export const CELINA_GLB = "/mascotte/celina.glb";

type SceneProps = {
  hovering: boolean;
  reducedMotion: boolean;
  px: number;
};

function CelinaModel({
  hovering,
  reducedMotion,
}: Omit<SceneProps, "px">) {
  const group = useRef<Group>(null);
  const { scene, animations } = useGLTF(CELINA_GLB);
  const cloned = useMemo(() => scene.clone(true), [scene]);
  const { actions, names } = useAnimations(animations, group);

  useEffect(() => {
    if (reducedMotion) {
      Object.values(actions).forEach((action) => action?.stop());
      return;
    }
    const clipName =
      names.find((n) => /bras|arm|wave|hover|idle/i.test(n)) ?? names[0];
    const action = clipName ? actions[clipName] : undefined;
    if (!action) return;

    if (hovering) {
      action.reset().fadeIn(0.2).play();
    } else {
      action.fadeOut(0.25);
    }
    return () => {
      action.fadeOut(0.1);
    };
  }, [actions, hovering, names, reducedMotion]);

  useFrame((_, delta) => {
    const node = group.current;
    if (!node || reducedMotion) return;
    if (names.length > 0 && hovering) return;
    node.rotation.y += delta * (hovering ? 1.1 : 0.3);
    node.position.y = Math.sin(performance.now() / 520) * (hovering ? 0.05 : 0.02);
  });

  return (
    <group ref={group} dispose={null}>
      <primitive
        object={cloned}
        scale={1.35}
        position={[0, -0.85, 0]}
        rotation={[0, Math.PI * 0.12, 0]}
      />
    </group>
  );
}

export default function SelinaMascotteScene({
  hovering,
  reducedMotion,
  px,
}: SceneProps) {
  return (
    <Canvas
      dpr={[1, 1.5]}
      gl={{ antialias: true, alpha: true, powerPreference: "low-power" }}
      camera={{ position: [0, 0.35, 2.4], fov: 32 }}
      style={{ width: px, height: px }}
      frameloop={reducedMotion ? "demand" : "always"}
    >
      <ambientLight intensity={0.85} />
      <directionalLight position={[2.5, 3, 2]} intensity={1.1} />
      <directionalLight position={[-2, 1, -1]} intensity={0.35} />
      <Suspense fallback={null}>
        <CelinaModel hovering={hovering} reducedMotion={reducedMotion} />
      </Suspense>
    </Canvas>
  );
}

useGLTF.preload(CELINA_GLB);
