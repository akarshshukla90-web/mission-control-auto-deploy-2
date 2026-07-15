import re

path = r'c:\antigravity\mission-control\static\index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update Head to include Three.js and Outfit font
head_old = """<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" />"""

head_new = """<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" />
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>"""
html = html.replace(head_old, head_new)

# 2. Update CSS Tokens
tokens_old = """    [data-theme="dark"] {
      --bg: #0f172a;
      --surface: #1e293b;
      --surface2: #0f172a;
      --border: #334155;
      --border2: #475569;
      --text: #f1f5f9;
      --text2: #94a3b8;
      --text3: #64748b;
      --accent-soft: #1e1b4b;
      --green-soft: #064e3b;
      --orange-soft: #451a03;
      --red-soft: #450a0a;
      --purple-soft: #2e1065;
    }"""
tokens_new = """    [data-theme="dark"] {
      --bg: #060a12;
      --surface: rgba(12, 18, 32, 0.75);
      --surface2: rgba(20, 29, 48, 0.85);
      --border: rgba(255, 255, 255, 0.08);
      --border2: rgba(255, 255, 255, 0.15);
      --text: #ffffff;
      --text2: #a8c0d8;
      --text3: #6b829e;
      --accent: #00d2ff;
      --accent-hover: #0066ff;
      --accent-soft: rgba(0, 102, 255, 0.15);
      --green-soft: rgba(16, 185, 129, 0.15);
      --orange-soft: rgba(245, 158, 11, 0.15);
      --red-soft: rgba(239, 68, 68, 0.15);
      --purple-soft: rgba(139, 92, 246, 0.15);
    }
    
    .glass-card {
        background: var(--surface);
        border: 1px solid var(--border);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.5);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: var(--border2);
        border-radius: 4px;
        border: 2px solid var(--bg);
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent);
    }
    
    #bg-canvas {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: 0;
        pointer-events: none;
        opacity: 0.8;
    }"""
html = html.replace(tokens_old, tokens_new)

# 3. Add canvas right after body
html = html.replace('<body>', '<body>\n  <canvas id="bg-canvas"></canvas>')

# 4. Apply glass-card to Sidebar, Topbar, Modals, Drawers, Cards
html = html.replace('background: var(--surface);', 'background: var(--surface);\n      backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);')
html = html.replace('font-family: \'Inter\', system-ui, sans-serif;', 'font-family: \'Inter\', system-ui, sans-serif;') # keep inter for body
html = html.replace('font-weight: 700;', 'font-weight: 700; font-family: \'Outfit\', sans-serif;') # headers

# 5. Add Three.js Tech Globe code before closing script
threejs_code = """
// ─── THREE.JS TECH GLOBE ──────────────────────────────────────────────────────────
function initTechGlobe() {
  const canvas = document.getElementById('bg-canvas');
  if (!canvas) return;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.z = 5;
  camera.position.x = 2; // offset to right

  const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(window.devicePixelRatio);

  const group = new THREE.Group();
  
  // Base Wireframe Sphere
  const globeGeo = new THREE.SphereGeometry(1.8, 32, 32);
  const globeMat = new THREE.MeshBasicMaterial({ color: 0x00d2ff, wireframe: true, transparent: true, opacity: 0.08 });
  const globe = new THREE.Mesh(globeGeo, globeMat);
  group.add(globe);

  // Orbiting Data Rings
  const ringGeo = new THREE.RingGeometry(2.1, 2.11, 64);
  const ringMat = new THREE.MeshBasicMaterial({ color: 0x0066ff, side: THREE.DoubleSide, transparent: true, opacity: 0.3 });
  const ring1 = new THREE.Mesh(ringGeo, ringMat);
  ring1.rotation.x = Math.PI / 2.5;
  group.add(ring1);
  
  const ring2 = new THREE.Mesh(ringGeo, ringMat);
  ring2.rotation.y = Math.PI / 3;
  group.add(ring2);

  // Floating Nodes
  const particleCount = 60;
  const particleGeo = new THREE.BufferGeometry();
  const positions = new Float32Array(particleCount * 3);
  for (let i = 0; i < particleCount; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos((Math.random() * 2) - 1);
      const distance = 1.8 + Math.random() * 0.2;
      positions[i * 3] = distance * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = distance * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = distance * Math.cos(phi);
  }
  particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  const pointsMat = new THREE.PointsMaterial({ color: 0x00d2ff, size: 0.04, transparent: true, opacity: 0.8 });
  const points = new THREE.Points(particleGeo, pointsMat);
  group.add(points);

  scene.add(group);

  function animate() {
      requestAnimationFrame(animate);
      group.rotation.y += 0.002;
      group.rotation.x += 0.001;
      ring1.rotation.z -= 0.005;
      ring2.rotation.z += 0.003;
      renderer.render(scene, camera);
  }
  animate();

  window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
  });
}

// Call init after a short delay
setTimeout(initTechGlobe, 500);
// ─── END THREE.JS ────────────────────────────────────────────────────────────────
"""
html = html.replace('// ─── INIT ───────────────────────────────────────────────────────────────────', threejs_code + '\n// ─── INIT ───────────────────────────────────────────────────────────────────')

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print("UI successfully patched with premium-web-design!")
