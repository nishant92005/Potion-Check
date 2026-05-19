import { Canvas, useFrame } from "@react-three/fiber";
import { Float } from "@react-three/drei";
import { useMemo, useRef } from "react";
import * as THREE from "three";

function CylinderBetween({ start, end }) {
  const ref = useRef();
  const { position, quaternion, length } = useMemo(() => {
    const s = new THREE.Vector3(...start);
    const e = new THREE.Vector3(...end);
    const mid = s.clone().add(e).multiplyScalar(0.5);
    const direction = e.clone().sub(s);
    const quat = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), direction.clone().normalize());
    return { position: mid, quaternion: quat, length: direction.length() };
  }, [start, end]);
  return (
    <mesh ref={ref} position={position} quaternion={quaternion}>
      <cylinderGeometry args={[0.025, 0.025, length, 12]} />
      <meshStandardMaterial color="#E8F4FD" transparent opacity={0.4} />
    </mesh>
  );
}

function Helix() {
  const group = useRef();
  const points = useMemo(() => {
    return Array.from({ length: 28 }).map((_, index) => {
      const t = index * 0.45;
      const y = (index - 14) * 0.18;
      return {
        a: [Math.cos(t) * 1.15, y, Math.sin(t) * 1.15],
        b: [Math.cos(t + Math.PI) * 1.15, y, Math.sin(t + Math.PI) * 1.15]
      };
    });
  }, []);
  useFrame(() => {
    group.current.rotation.y += 0.003;
    group.current.rotation.x += 0.001;
  });
  return (
    <Float speed={1} floatIntensity={0.35}>
      <group ref={group} scale={1.35}>
        {points.map((point, index) => (
          <group key={index}>
            <mesh position={point.a}>
              <sphereGeometry args={[0.085, 16, 16]} />
              <meshStandardMaterial color="#00FFB2" emissive="#00FFB2" emissiveIntensity={0.45} />
            </mesh>
            <mesh position={point.b}>
              <sphereGeometry args={[0.085, 16, 16]} />
              <meshStandardMaterial color="#7B61FF" emissive="#7B61FF" emissiveIntensity={0.38} />
            </mesh>
            <CylinderBetween start={point.a} end={point.b} />
          </group>
        ))}
      </group>
    </Float>
  );
}

export function DNAHelix() {
  return (
    <div className="pointer-events-none absolute inset-0 hidden opacity-55 md:block">
      <Canvas camera={{ position: [0, 0, 6], fov: 50 }}>
        <ambientLight intensity={0.65} />
        <pointLight color="#00FFB2" position={[0, 4, 4]} intensity={2} />
        <Helix />
      </Canvas>
    </div>
  );
}
