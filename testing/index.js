import * as THREE from "three/webgpu";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

//- Camera Config
const w = window.innerWidth;
const h = window.innerHeight;
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x101010);
const camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 1000);
camera.position.set(0, 0, 100);
camera.lookAt(0, 0, 0);

//- Renderer
const renderer = new THREE.WebGPURenderer({ antialias: true });
renderer.setSize(w, h);
document.body.appendChild(renderer.domElement);

const lineMaterial = new THREE.LineBasicMaterial({ vertexColors: true });

//- From a (0, 0, 0) origin to their respective axis
const points = new Float32Array([
  //. X Axis Line
  0, 0, 0,  10, 0, 0,

  //. Y Axis Line
  0, 0, 0,  0, 10, 0,

  //. Z Axis Line
  0, 0, 0,  0, 0, 10

]);

//- Formatting: R, G, B
const colors = new Float32Array([
  //. X Verticies
  1, 0, 0,  1, 0, 0,

  //. Y Verticies
  0, 1, 0,  0, 1, 0,

  //. Z Verticies
  0, 0, 1,  0, 0, 1
]);

//- Creating the lines
const lineGeometry = new THREE.BufferGeometry();
lineGeometry.setAttribute("position", new THREE.BufferAttribute(points, 3));
lineGeometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
const markings = new THREE.LineSegments(lineGeometry, lineMaterial);
scene.add(markings);

//- Cube
const boxLength = 30; //. In three.js the 3D space is in X (Width), Y (Height), and Z (Depth)
const boxGeometry = new THREE.BoxGeometry(boxLength, boxLength, boxLength);
const boxOffset = (boxLength / 2) - 0.1;
boxGeometry.translate(boxOffset, boxOffset, boxOffset);
const boxMaterial = new THREE.MeshBasicMaterial({ color: "white" });
const edgeGeometry = new THREE.EdgesGeometry(boxGeometry);
const outlineMaterial = new THREE.LineDashedMaterial({ color: "white", dashSize: 0.5, gapSize: 0.5, scale: 1 });
const outline = new THREE.LineSegments(edgeGeometry, outlineMaterial);
outline.computeLineDistances();
scene.add(outline);

//- Spheres
const sphereGeometry = new THREE.SphereGeometry(0.5, 16, 16);

for (let i = 0; i < 2125; i++) {
  const sphereMaterial = new THREE.MeshBasicMaterial();
  const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
  
  sphere.position.set(
    (boxLength / 2) + (Math.random() - 0.5) * boxLength,
    (boxLength / 2) + (Math.random() - 0.5) * boxLength,
    (boxLength / 2) + (Math.random() - 0.5) * boxLength
  );

  const x = sphere.position.x / boxLength;
  const y = sphere.position.y / boxLength;
  const z = sphere.position.z / boxLength;

  const hue = x;
  const saturation = 0.6 + z * 0.4;
  const light = 0.3 + y * 0.4;

  sphereMaterial.color.setHSL(hue, saturation, light);

  scene.add(sphere);
}

await renderer.init();

renderer.render(scene, camera);
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(boxLength / 2, boxLength / 2, boxLength / 2);
controls.update();

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}

animate();

