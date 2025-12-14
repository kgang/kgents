// Stigmergic Field Widget - Interactive canvas rendering
// Earth theme colors
const COLORS = {
  idle: '#4a4a5c',
  waking: '#c97b84',
  active: '#e6a352',
  intense: '#f5d08a',
  void: '#6b4b8a',
  materializing: '#7d9c7a',
  background: '#1a1a2e',
  surface: '#252525',
  text: '#e0e0e0',
  progress: '#7d9c7a',
  conflict: '#c97b84',
  synthesis: '#6b4b8a',
  error: '#ff6b6b',
};

// Entity type to color mapping
const ENTITY_COLORS = {
  'I': COLORS.idle,      // ID
  'C': COLORS.active,    // COMPOSE
  'G': COLORS.waking,    // GROUND
  'J': COLORS.intense,   // JUDGE
  'X': COLORS.conflict,  // CONTRADICT
  'S': COLORS.synthesis, // SUBLATE
  'F': COLORS.materializing, // FIX
  '*': COLORS.intense,   // TASK
  '◊': COLORS.waking,    // HYPOTHESIS
  '□': COLORS.idle,      // ARTIFACT
};

// Pheromone type to color
const PHEROMONE_COLORS = {
  progress: 'rgba(125, 156, 122, 0.3)',
  conflict: 'rgba(201, 123, 132, 0.4)',
  synthesis: 'rgba(107, 75, 138, 0.3)',
  error: 'rgba(255, 107, 107, 0.5)',
};

function render({ model, el }) {
  // Create container
  const container = document.createElement('div');
  container.className = 'kgents-field-container';
  container.style.cssText = `
    position: relative;
    width: ${model.get('width') * model.get('cell_size')}px;
    height: ${model.get('height') * model.get('cell_size')}px;
    background: ${COLORS.background};
    border-radius: 4px;
    overflow: hidden;
    font-family: 'JetBrains Mono', monospace;
  `;

  // Create canvas for pheromones (bottom layer)
  const pheromoneCanvas = document.createElement('canvas');
  pheromoneCanvas.width = model.get('width') * model.get('cell_size');
  pheromoneCanvas.height = model.get('height') * model.get('cell_size');
  pheromoneCanvas.style.cssText = 'position: absolute; top: 0; left: 0;';
  container.appendChild(pheromoneCanvas);

  // Create container for entities (top layer)
  const entityLayer = document.createElement('div');
  entityLayer.style.cssText = 'position: absolute; top: 0; left: 0; width: 100%; height: 100%;';
  container.appendChild(entityLayer);

  // Create status bar
  const statusBar = document.createElement('div');
  statusBar.style.cssText = `
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 24px;
    background: ${COLORS.surface};
    color: ${COLORS.text};
    font-size: 11px;
    padding: 4px 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  `;
  container.appendChild(statusBar);

  el.appendChild(container);

  // Animation state
  let animationId = null;
  let entityElements = new Map();

  // Render pheromones on canvas
  function renderPheromones() {
    const ctx = pheromoneCanvas.getContext('2d');
    const cellSize = model.get('cell_size');
    ctx.clearRect(0, 0, pheromoneCanvas.width, pheromoneCanvas.height);

    const pheromones = model.get('pheromones') || [];
    const tick = model.get('tick') || 0;

    for (const p of pheromones) {
      const age = tick - (p.birth_tick || 0);
      const decayRates = { progress: 5, conflict: 2, synthesis: 3, error: 1 };
      const decayRate = decayRates[p.ptype] || 3;
      const intensity = p.intensity * Math.max(0, 1 - age / decayRate);

      if (intensity <= 0) continue;

      const cx = p.x * cellSize + cellSize / 2;
      const cy = p.y * cellSize + cellSize / 2;
      const radius = cellSize * 2 * intensity;

      const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius);
      const color = PHEROMONE_COLORS[p.ptype] || PHEROMONE_COLORS.progress;
      gradient.addColorStop(0, color);
      gradient.addColorStop(1, 'transparent');

      ctx.fillStyle = gradient;
      ctx.fillRect(cx - radius, cy - radius, radius * 2, radius * 2);
    }

    // Add entropy noise
    const entropy = model.get('entropy') || 0;
    if (entropy > 0.5) {
      const imageData = ctx.getImageData(0, 0, pheromoneCanvas.width, pheromoneCanvas.height);
      const data = imageData.data;
      const noiseLevel = (entropy - 0.5) * 0.1;
      for (let i = 0; i < data.length; i += 4) {
        if (Math.random() < noiseLevel) {
          data[i] = Math.min(255, data[i] + Math.random() * 30);
          data[i + 1] = Math.min(255, data[i + 1] + Math.random() * 20);
          data[i + 2] = Math.min(255, data[i + 2] + Math.random() * 40);
        }
      }
      ctx.putImageData(imageData, 0, 0);
    }
  }

  // Render entities as positioned divs
  function renderEntities() {
    const entities = model.get('entities') || [];
    const cellSize = model.get('cell_size');
    const focusId = model.get('focus_entity_id');

    const seenIds = new Set();

    for (const e of entities) {
      seenIds.add(e.id);

      let elem = entityElements.get(e.id);
      if (!elem) {
        elem = document.createElement('div');
        elem.className = 'kgents-entity';
        elem.style.cssText = `
          position: absolute;
          width: ${cellSize}px;
          height: ${cellSize}px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: ${cellSize * 0.7}px;
          cursor: pointer;
          transition: transform 0.1s ease-out, background 0.2s;
          border-radius: 2px;
        `;
        elem.addEventListener('click', () => {
          model.set('clicked_entity_id', e.id);
          model.set('focus_entity_id', e.id);
          model.save_changes();
        });
        entityLayer.appendChild(elem);
        entityElements.set(e.id, elem);
      }

      const jitter = model.get('entropy') * 2;
      const jx = (Math.random() - 0.5) * jitter;
      const jy = (Math.random() - 0.5) * jitter;
      elem.style.left = `${e.x * cellSize + jx}px`;
      elem.style.top = `${e.y * cellSize + jy}px`;

      const color = ENTITY_COLORS[e.symbol] || COLORS.text;
      const isFocused = e.id === focusId;
      elem.style.color = color;
      elem.style.background = isFocused ? COLORS.surface : 'transparent';
      elem.style.transform = isFocused ? 'scale(1.2)' : 'scale(1)';
      elem.style.zIndex = isFocused ? '10' : '1';
      elem.textContent = e.symbol;
      elem.title = `${e.id} (${e.phase})`;
    }

    for (const [id, elem] of entityElements) {
      if (!seenIds.has(id)) {
        elem.remove();
        entityElements.delete(id);
      }
    }
  }

  function updateStatus() {
    const tick = model.get('tick') || 0;
    const entropy = model.get('entropy') || 0;
    const heat = model.get('heat') || 0;
    const phase = model.get('dialectic_phase') || 'dormant';
    const entityCount = (model.get('entities') || []).length;

    statusBar.innerHTML = `
      <span>tick: ${tick} | entities: ${entityCount}</span>
      <span>entropy: ${(entropy * 100).toFixed(0)}% | heat: ${heat.toFixed(0)} | ${phase}</span>
    `;
  }

  function animate() {
    renderPheromones();
    renderEntities();
    updateStatus();
    animationId = requestAnimationFrame(animate);
  }

  animate();

  model.on('change:entities', renderEntities);
  model.on('change:pheromones', renderPheromones);
  model.on('change:tick', updateStatus);
  model.on('change:entropy', () => { renderPheromones(); renderEntities(); });

  return () => {
    if (animationId) cancelAnimationFrame(animationId);
    entityElements.clear();
  };
}

export default { render };
