import React, { Suspense, useRef } from "react";
import { Canvas, useFrame, useLoader } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import * as THREE from "three";

import earthTexture from "../images/earth.jpg";

function Earth() {
  const meshRef = useRef();

  const texture = useLoader(
    THREE.TextureLoader,
    earthTexture
  );

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.0035; // smoother rotation
    }
  });

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[1.8, 64, 64]} />

      <meshStandardMaterial
        map={texture}
        metalness={0.15}
        roughness={0.8}
      />
    </mesh>
  );
}

export default function Earth3D() {
  return (
    <Canvas
      style={{
        width: "170px",
        height: "170px",
      }}
      camera={{
        position: [0, 0, 5],
        fov: 45,
      }}
    >
      {/* Lighting */}
      <ambientLight intensity={1.8} />

      <directionalLight
        position={[5, 3, 5]}
        intensity={2.8}
      />

      <pointLight
        position={[-4, 2, 4]}
        intensity={1.2}
        color="#60a5fa"
      />

      <Suspense fallback={null}>
        <Earth />
      </Suspense>

      <OrbitControls
        enableZoom={false}
        enablePan={false}
        enableRotate={false}
      />
    </Canvas>
  );
}