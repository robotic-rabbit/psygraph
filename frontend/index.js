const particleConfig = {
  particleCount: 24,
  maxSpeed: 0.2,
  particlesPerArea: 1 / 6500,
  minParticles: 14,
  maxParticles: 70,
  particleRadius: 2,
  connectFactor: 1.5,
  minConnectDistance: 55,
  maxConnectDistance: 150,
  CrowdA: "#534ab7",
  CrowdB: "#7f77dd",
  lineColor: "175, 169, 236"
}

function createParticle(w, h) {
  const angle = Math.random() * Math.PI * 2;
  rawSpeed = Math.max(0.1, Math.random() * particleConfig.maxSpeed);
  return {
    x: Math.random() * w,
    y: Math.random() * h,
    vx: Math.cos(angle) * rawSpeed,
    vy: Math.sin(angle) * rawSpeed,
    color: Math.random() < 0.5 ? particleConfig.CrowdA : particleConfig.CrowdB
  };
}

function initializeParticleField(canvas) {
  const ctx = canvas.getContext("2d");
  let w, h, particles;
  let rafId = null;

  function resize() {
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    w = rect.width;
    h = rect.height;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const area = w * h;
    const rawCount = Math.round(area * particleConfig.particlesPerArea);
    particleConfig.particleCount = Math.min(particleConfig.maxParticles, (Math.max(particleConfig.minParticles, rawCount)));

    const avgSpacing = Math.sqrt(area / particleConfig.particleCount);
    const rawConnectDistance = avgSpacing * particleConfig.connectFactor;
    particleConfig.connectDistance = Math.min(particleConfig.maxConnectDistance, (Math.max(particleConfig.minConnectDistance, rawConnectDistance)));
 }

 function seed() {
  particles = Array.from({ length: particleConfig.particleCount }, () => 
    createParticle(w, h)
  );
 }

 function step() {
  particles.forEach(p => {
    p.x += p.vx;
    p.y += p.vy;

    if (p.x < 0 || p.x > w) p.vx *= -1;
    if (p.y < 0 || p.y > h) p.vy *= -1;
  });
 }

 function drawConnections() {
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      const a = particles[i], b = particles[j];
      const dx = a.x - b.x, dy = a.y - b.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < particleConfig.connectDistance) {
        const alpha = 1 - dist / particleConfig.connectDistance;

        ctx.strokeStyle = `rgba(${particleConfig.lineColor}, ${(alpha * 0.35).toFixed(3)})`;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.stroke();
      }
    }
  }
 }

 function drawParticles() {
  particles.forEach(p => {
    ctx.beginPath();
    ctx.arc(p.x, p.y, particleConfig.particleRadius, 0, Math.PI * 2);
    ctx.fillStyle = p.color;
    ctx.fill();
  });
 }

 function render() {
  ctx.clearRect(0, 0, w, h);
  drawConnections();
  drawParticles();
 }

 function loop() {
  step();
  render();
  rafId = requestAnimationFrame(loop);
 }

 resize();
 seed();

  const prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;
 
  if (prefersReducedMotion) {
    render();
  } else {
    loop();
  }

 window.addEventListener("resize", () => {
  resize();
  seed();
 });

 return { stop: () => rafId && cancelAnimationFrame(rafId) };

}

document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("dotField");
  if (!canvas) return;
  initializeParticleField(canvas);
  console.log("Particle field initialized");
});