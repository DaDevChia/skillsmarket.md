import React from 'react';
import * as THREE from 'three';
import type { IndexedResumeSkill } from '../types';

function webglAvailable(): boolean {
  try {
    const canvas = document.createElement('canvas');
    return !!(
      window.WebGLRenderingContext &&
      (canvas.getContext('webgl') || canvas.getContext('experimental-webgl'))
    );
  } catch {
    return false;
  }
}

function colorFor(skill: IndexedResumeSkill): number {
  const price = skill.price;
  if (price == null) return 0x55708a; // unmatched — dim
  if (price >= 120) return 0x00ff9c; // scarce — phosphor green
  if (price >= 100) return 0x4de3ff; // at baseline — cyan
  if (price >= 70) return 0xf4c542; // common — amber
  return 0xff5c7a; // very common — muted red
}

// Rotating orbital cluster of skills. Node size maps to price, colour to status.
// Plain three.js (imperative) so it is robust under React 19; degrades to a
// terminal list when WebGL is unavailable.
export function SkillsGlobe({
  skills,
  onSelect,
}: {
  skills: IndexedResumeSkill[];
  onSelect: (skill: IndexedResumeSkill) => void;
}) {
  const mountRef = React.useRef<HTMLDivElement>(null);
  const onSelectRef = React.useRef(onSelect);
  onSelectRef.current = onSelect;
  const [supported] = React.useState(webglAvailable);

  const dataKey = skills.map((s) => `${s.name}:${s.price ?? 'x'}`).join('|');

  React.useEffect(() => {
    if (!supported || !mountRef.current) return;
    const mount = mountRef.current;
    const width = mount.clientWidth || 320;
    const height = mount.clientHeight || 320;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 100);
    camera.position.z = 4.4;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(width, height);
    mount.appendChild(renderer.domElement);

    const group = new THREE.Group();
    group.rotation.x = 0.2;
    scene.add(group);

    const wire = new THREE.Mesh(
      new THREE.SphereGeometry(1.55, 26, 26),
      new THREE.MeshBasicMaterial({ color: 0x1d4a4f, wireframe: true, transparent: true, opacity: 0.25 }),
    );
    group.add(wire);

    const nodes: THREE.Mesh[] = [];
    const count = Math.max(skills.length, 1);
    skills.forEach((skill, i) => {
      const phi = Math.acos(1 - (2 * (i + 0.5)) / count);
      const theta = Math.PI * (1 + Math.sqrt(5)) * i;
      const radius = 1.55;
      const price = skill.price ?? 60;
      const size = 0.13 + (Math.min(price, 360) / 360) * 0.3;
      const color = colorFor(skill);
      const mesh = new THREE.Mesh(
        new THREE.SphereGeometry(size, 20, 20),
        new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 0.45, roughness: 0.35, metalness: 0.1 }),
      );
      mesh.position.set(
        radius * Math.sin(phi) * Math.cos(theta),
        radius * Math.sin(phi) * Math.sin(theta),
        radius * Math.cos(phi),
      );
      mesh.userData = { skill };
      group.add(mesh);
      nodes.push(mesh);
    });

    const point = new THREE.PointLight(0xffffff, 1.3);
    point.position.set(5, 5, 5);
    scene.add(point);
    scene.add(new THREE.AmbientLight(0x4de3ff, 0.45));

    const raycaster = new THREE.Raycaster();
    const pointer = new THREE.Vector2();
    function onClick(event: MouseEvent) {
      const rect = renderer.domElement.getBoundingClientRect();
      pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(pointer, camera);
      const hits = raycaster.intersectObjects(nodes);
      if (hits.length) onSelectRef.current((hits[0].object.userData as { skill: IndexedResumeSkill }).skill);
    }
    renderer.domElement.addEventListener('click', onClick);
    renderer.domElement.style.cursor = 'pointer';

    let raf = 0;
    function animate() {
      group.rotation.y += 0.0035;
      renderer.render(scene, camera);
      raf = requestAnimationFrame(animate);
    }
    animate();

    function onResize() {
      const w = mount.clientWidth || width;
      const h = mount.clientHeight || height;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    }
    window.addEventListener('resize', onResize);

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener('resize', onResize);
      renderer.domElement.removeEventListener('click', onClick);
      renderer.dispose();
      if (renderer.domElement.parentNode === mount) mount.removeChild(renderer.domElement);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [supported, dataKey]);

  return (
    <section className="globe panel" data-testid="skills-globe">
      <header className="panel-head">
        <h2>Skills globe</h2>
        <span className="panel-tag">size = price · colour = scarcity</span>
      </header>
      {supported ? (
        <div className="globe-canvas" ref={mountRef} />
      ) : (
        <ul className="globe-fallback" data-testid="skills-globe-fallback">
          {skills.map((skill) => (
            <li key={skill.name}>
              <button type="button" onClick={() => onSelect(skill)}>
                <span className={`dot status-${skill.status}`} />
                {skill.name} · {skill.price == null ? 'unpriced' : `${skill.price.toFixed(0)} pts`}
              </button>
            </li>
          ))}
        </ul>
      )}
      <div className="globe-legend">
        <span><i className="dot scarce" /> scarce</span>
        <span><i className="dot baseline" /> baseline</span>
        <span><i className="dot common" /> common</span>
      </div>
    </section>
  );
}
