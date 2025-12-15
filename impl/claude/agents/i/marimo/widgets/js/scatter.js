/**
 * Eigenvector Scatter Widget ESM (Phase 6 DEVELOP).
 *
 * Live SVG scatter plot with SSE integration for Agent Town visualization.
 *
 * Heritage:
 * - S1: stigmergic_field.js (entity layer pattern, model sync)
 * - S2: visualization.py (ScatterPoint schema, ProjectionMethod)
 * - S3: KgentsWidget base (EARTH_COLORS CSS variables)
 *
 * Laws:
 * - L1: SVG viewBox maintains 400x300 aspect ratio
 * - L2: Point transitions animate via CSS (transition: all 0.3s ease-out)
 * - L3: Click → model.set("clicked_citizen_id") → model.save_changes()
 * - L4: SSE disconnect → browser auto-reconnect via EventSource
 * - L5: Cleanup function closes EventSource on widget unmount
 */

// Earth theme colors (match base.py EARTH_COLORS)
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
  bridge: '#fbbf24',      // Gold for bridge nodes
  unaffiliated: '#6b7280', // Gray for no coalition
};

// Archetype to color mapping
const ARCHETYPE_COLORS = {
  builder: '#3b82f6',     // Blue
  trader: '#ef4444',      // Red
  healer: '#22c55e',      // Green
  sage: '#f59e0b',        // Amber
  explorer: '#8b5cf6',    // Purple
  witness: '#ec4899',     // Pink
  kgent: '#f5d08a',       // Gold
};

// Projection axis labels
const PROJECTION_LABELS = {
  PAIR_WT: ['Warmth', 'Trust'],
  PAIR_CC: ['Curiosity', 'Creativity'],
  PAIR_PR: ['Patience', 'Resilience'],
  PAIR_RA: ['Resilience', 'Ambition'],
  PCA: ['PC1', 'PC2'],
  TSNE: ['t-SNE1', 't-SNE2'],
  CUSTOM: ['Custom1', 'Custom2'],
};

// SVG dimensions (Law L1: maintain aspect ratio)
const SVG_WIDTH = 400;
const SVG_HEIGHT = 300;
const MARGIN = { top: 30, right: 20, bottom: 40, left: 50 };
const PLOT_WIDTH = SVG_WIDTH - MARGIN.left - MARGIN.right;
const PLOT_HEIGHT = SVG_HEIGHT - MARGIN.top - MARGIN.bottom;

/**
 * Get 2D coordinates from a point based on projection method.
 */
function getProjectedCoords(point, projection) {
  const ev = point.eigenvectors || {};

  switch (projection) {
    case 'PAIR_WT':
      return [ev.warmth || 0, ev.trust || 0];
    case 'PAIR_CC':
      return [ev.curiosity || 0, ev.creativity || 0];
    case 'PAIR_PR':
      return [ev.patience || 0, ev.resilience || 0];
    case 'PAIR_RA':
      return [ev.resilience || 0, ev.ambition || 0];
    case 'PCA':
    case 'TSNE':
    case 'CUSTOM':
      // Use pre-computed x, y (normalized to 0-1 range)
      return [point.x || ev.warmth || 0, point.y || ev.trust || 0];
    default:
      return [ev.warmth || 0, ev.trust || 0];
  }
}

/**
 * Get color for a point.
 */
function getPointColor(point, showCoalitionColors) {
  if (!showCoalitionColors) {
    return ARCHETYPE_COLORS[point.archetype?.toLowerCase()] || COLORS.text;
  }

  // Use point's color (set by visualization.py based on coalition)
  return point.color || COLORS.unaffiliated;
}

/**
 * Main render function (anywidget entry point).
 */
function render({ model, el }) {
  // Create container
  const container = document.createElement('div');
  container.className = 'kgents-scatter-container';
  container.style.cssText = `
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    background: ${COLORS.background};
    color: ${COLORS.text};
    border-radius: 4px;
    padding: 8px;
    position: relative;
  `;

  // Create SVG
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', `0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`);
  svg.setAttribute('width', '100%');
  svg.setAttribute('height', 'auto');
  svg.style.cssText = 'display: block; max-width: 600px;';

  // Create layers
  const defsEl = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
  const axisGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  axisGroup.setAttribute('class', 'axis-layer');
  const pointGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  pointGroup.setAttribute('class', 'point-layer');
  pointGroup.setAttribute('transform', `translate(${MARGIN.left}, ${MARGIN.top})`);
  const labelGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  labelGroup.setAttribute('class', 'label-layer');
  labelGroup.setAttribute('transform', `translate(${MARGIN.left}, ${MARGIN.top})`);

  svg.appendChild(defsEl);
  svg.appendChild(axisGroup);
  svg.appendChild(pointGroup);
  svg.appendChild(labelGroup);
  container.appendChild(svg);

  // Create status bar
  const statusBar = document.createElement('div');
  statusBar.style.cssText = `
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 8px;
    background: ${COLORS.surface};
    border-radius: 0 0 4px 4px;
    font-size: 11px;
    margin-top: 4px;
  `;
  container.appendChild(statusBar);

  // Create tooltip
  const tooltip = document.createElement('div');
  tooltip.style.cssText = `
    position: absolute;
    background: ${COLORS.surface};
    border: 1px solid ${COLORS.idle};
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 11px;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.2s;
    z-index: 100;
    max-width: 200px;
  `;
  container.appendChild(tooltip);

  el.appendChild(container);

  // Point element cache
  const pointElements = new Map();
  const labelElements = new Map();

  // EventSource for SSE
  let eventSource = null;

  /**
   * Render axes and labels.
   */
  function renderAxes() {
    const projection = model.get('projection') || 'PAIR_WT';
    const [xLabel, yLabel] = PROJECTION_LABELS[projection] || ['X', 'Y'];

    axisGroup.innerHTML = '';

    // Plot background
    const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    bg.setAttribute('x', MARGIN.left);
    bg.setAttribute('y', MARGIN.top);
    bg.setAttribute('width', PLOT_WIDTH);
    bg.setAttribute('height', PLOT_HEIGHT);
    bg.setAttribute('fill', COLORS.surface);
    bg.setAttribute('rx', '4');
    axisGroup.appendChild(bg);

    // X axis line
    const xAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    xAxis.setAttribute('x1', MARGIN.left);
    xAxis.setAttribute('y1', MARGIN.top + PLOT_HEIGHT);
    xAxis.setAttribute('x2', MARGIN.left + PLOT_WIDTH);
    xAxis.setAttribute('y2', MARGIN.top + PLOT_HEIGHT);
    xAxis.setAttribute('stroke', COLORS.idle);
    xAxis.setAttribute('stroke-width', '1');
    axisGroup.appendChild(xAxis);

    // Y axis line
    const yAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    yAxis.setAttribute('x1', MARGIN.left);
    yAxis.setAttribute('y1', MARGIN.top);
    yAxis.setAttribute('x2', MARGIN.left);
    yAxis.setAttribute('y2', MARGIN.top + PLOT_HEIGHT);
    yAxis.setAttribute('stroke', COLORS.idle);
    yAxis.setAttribute('stroke-width', '1');
    axisGroup.appendChild(yAxis);

    // X axis label
    const xText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    xText.setAttribute('x', MARGIN.left + PLOT_WIDTH / 2);
    xText.setAttribute('y', SVG_HEIGHT - 8);
    xText.setAttribute('text-anchor', 'middle');
    xText.setAttribute('fill', COLORS.text);
    xText.setAttribute('font-size', '12');
    xText.textContent = xLabel;
    axisGroup.appendChild(xText);

    // Y axis label
    const yText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    yText.setAttribute('x', 12);
    yText.setAttribute('y', MARGIN.top + PLOT_HEIGHT / 2);
    yText.setAttribute('text-anchor', 'middle');
    yText.setAttribute('fill', COLORS.text);
    yText.setAttribute('font-size', '12');
    yText.setAttribute('transform', `rotate(-90, 12, ${MARGIN.top + PLOT_HEIGHT / 2})`);
    yText.textContent = yLabel;
    axisGroup.appendChild(yText);

    // Title
    const title = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    title.setAttribute('x', SVG_WIDTH / 2);
    title.setAttribute('y', 18);
    title.setAttribute('text-anchor', 'middle');
    title.setAttribute('fill', COLORS.text);
    title.setAttribute('font-size', '14');
    title.setAttribute('font-weight', 'bold');
    title.textContent = `Eigenvector Space (${xLabel[0]}${yLabel[0]})`;
    axisGroup.appendChild(title);
  }

  /**
   * Render scatter points.
   */
  function renderPoints() {
    const points = model.get('points') || [];
    const projection = model.get('projection') || 'PAIR_WT';
    const selectedId = model.get('selected_citizen_id');
    const hoveredId = model.get('hovered_citizen_id');
    const showLabels = model.get('show_labels');
    const showCoalitionColors = model.get('show_coalition_colors');
    const showEvolvingOnly = model.get('show_evolving_only');
    const archetypeFilter = model.get('archetype_filter') || [];
    const coalitionFilter = model.get('coalition_filter');
    const animate = model.get('animate_transitions');

    const seenIds = new Set();

    for (const point of points) {
      // Apply filters
      if (showEvolvingOnly && !point.is_evolving) continue;
      if (archetypeFilter.length > 0 && !archetypeFilter.includes(point.archetype)) continue;
      if (coalitionFilter && !point.coalition_ids?.includes(coalitionFilter)) continue;

      seenIds.add(point.citizen_id);

      // Get projected coordinates
      const [xVal, yVal] = getProjectedCoords(point, projection);

      // Map to plot coordinates (0-1 range → pixel coords)
      const cx = xVal * PLOT_WIDTH;
      const cy = (1 - yVal) * PLOT_HEIGHT; // Invert Y

      // Get or create circle element
      let circle = pointElements.get(point.citizen_id);
      if (!circle) {
        circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('class', 'scatter-point');
        circle.style.cssText = animate
          ? 'transition: all 0.3s ease-out; cursor: pointer;'
          : 'cursor: pointer;';

        // Click handler (Law L3)
        circle.addEventListener('click', () => {
          model.set('clicked_citizen_id', point.citizen_id);
          model.set('selected_citizen_id', point.citizen_id);
          model.save_changes();
        });

        // Hover handlers
        circle.addEventListener('mouseenter', (e) => {
          model.set('hovered_citizen_id', point.citizen_id);
          model.save_changes();
          showTooltip(e, point);
        });
        circle.addEventListener('mouseleave', () => {
          model.set('hovered_citizen_id', '');
          model.save_changes();
          hideTooltip();
        });

        pointGroup.appendChild(circle);
        pointElements.set(point.citizen_id, circle);
      }

      // Update circle attributes
      const isSelected = point.citizen_id === selectedId;
      const isHovered = point.citizen_id === hoveredId;
      const baseRadius = point.is_evolving ? 6 : 5;
      const radius = isSelected ? baseRadius * 1.5 : isHovered ? baseRadius * 1.2 : baseRadius;
      const color = getPointColor(point, showCoalitionColors);

      circle.setAttribute('cx', cx);
      circle.setAttribute('cy', cy);
      circle.setAttribute('r', radius);
      circle.setAttribute('fill', color);
      circle.setAttribute('stroke', isSelected ? COLORS.intense : isHovered ? COLORS.text : 'none');
      circle.setAttribute('stroke-width', isSelected ? '2' : '1');
      circle.setAttribute('opacity', point.is_evolving ? '1' : '0.8');

      // Update label
      if (showLabels) {
        let label = labelElements.get(point.citizen_id);
        if (!label) {
          label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
          label.setAttribute('class', 'scatter-label');
          label.setAttribute('font-size', '9');
          label.setAttribute('fill', COLORS.text);
          label.setAttribute('pointer-events', 'none');
          label.style.cssText = animate ? 'transition: all 0.3s ease-out;' : '';
          labelGroup.appendChild(label);
          labelElements.set(point.citizen_id, label);
        }

        label.setAttribute('x', cx + radius + 3);
        label.setAttribute('y', cy + 3);
        label.textContent = point.citizen_name?.substring(0, 8) || '';
        label.style.opacity = isSelected || isHovered ? '1' : '0.6';
      }
    }

    // Remove stale elements
    for (const [id, elem] of pointElements) {
      if (!seenIds.has(id)) {
        elem.remove();
        pointElements.delete(id);
      }
    }
    for (const [id, elem] of labelElements) {
      if (!seenIds.has(id)) {
        elem.remove();
        labelElements.delete(id);
      }
    }
  }

  /**
   * Show tooltip for a point.
   */
  function showTooltip(event, point) {
    const ev = point.eigenvectors || {};
    tooltip.innerHTML = `
      <div style="font-weight: bold; margin-bottom: 4px;">${point.citizen_name}</div>
      <div>Archetype: ${point.archetype}</div>
      <div>Evolving: ${point.is_evolving ? 'Yes' : 'No'}</div>
      <div style="margin-top: 4px; font-size: 10px; opacity: 0.8;">
        W:${(ev.warmth || 0).toFixed(2)} C:${(ev.curiosity || 0).toFixed(2)} T:${(ev.trust || 0).toFixed(2)}
      </div>
    `;

    const rect = container.getBoundingClientRect();
    tooltip.style.left = `${event.clientX - rect.left + 10}px`;
    tooltip.style.top = `${event.clientY - rect.top - 10}px`;
    tooltip.style.opacity = '1';
  }

  /**
   * Hide tooltip.
   */
  function hideTooltip() {
    tooltip.style.opacity = '0';
  }

  /**
   * Update status bar.
   */
  function updateStatus() {
    const points = model.get('points') || [];
    const sseConnected = model.get('sse_connected');
    const sseError = model.get('sse_error');
    const townId = model.get('town_id');

    const visibleCount = points.filter(p => {
      const showEvolvingOnly = model.get('show_evolving_only');
      const archetypeFilter = model.get('archetype_filter') || [];
      if (showEvolvingOnly && !p.is_evolving) return false;
      if (archetypeFilter.length > 0 && !archetypeFilter.includes(p.archetype)) return false;
      return true;
    }).length;

    const evolvingCount = points.filter(p => p.is_evolving).length;

    const sseStatus = sseConnected
      ? '<span style="color: #22c55e;">● SSE</span>'
      : sseError
        ? `<span style="color: #ef4444;">● ${sseError.substring(0, 20)}</span>`
        : '<span style="color: #6b7280;">○ SSE</span>';

    statusBar.innerHTML = `
      <span>Citizens: ${visibleCount}/${points.length} (${evolvingCount} evolving)</span>
      <span>${townId ? `Town: ${townId.substring(0, 8)}` : 'No town'} | ${sseStatus}</span>
    `;
  }

  /**
   * Connect to SSE endpoint.
   */
  function connectSSE() {
    const townId = model.get('town_id');
    const apiBase = model.get('api_base');

    // Close existing connection
    if (eventSource) {
      eventSource.close();
      eventSource = null;
    }

    if (!townId) {
      model.set('sse_connected', false);
      model.save_changes();
      return;
    }

    const url = `${apiBase}/${townId}/events`;

    try {
      eventSource = new EventSource(url);

      eventSource.onopen = () => {
        model.set('sse_connected', true);
        model.set('sse_error', '');
        model.save_changes();
        updateStatus();
      };

      eventSource.onerror = (e) => {
        model.set('sse_connected', false);
        model.set('sse_error', 'Connection error');
        model.save_changes();
        updateStatus();
        // Law L4: Browser auto-reconnects via EventSource
      };

      // Handle eigenvector drift events
      eventSource.addEventListener('town.eigenvector.drift', (e) => {
        try {
          const data = JSON.parse(e.data);
          // Update the specific point's eigenvectors
          const points = model.get('points') || [];
          const updatedPoints = points.map(p => {
            if (p.citizen_id === data.citizen_id) {
              return {
                ...p,
                eigenvectors: data.new,
                x: data.new?.x || p.x,
                y: data.new?.y || p.y,
              };
            }
            return p;
          });
          model.set('points', updatedPoints);
          model.save_changes();
        } catch (err) {
          console.error('Error parsing eigenvector drift:', err);
        }
      });

      // Handle status events
      eventSource.addEventListener('town.status', (e) => {
        updateStatus();
      });

    } catch (err) {
      model.set('sse_connected', false);
      model.set('sse_error', err.message);
      model.save_changes();
    }
  }

  // Initial render
  renderAxes();
  renderPoints();
  updateStatus();

  // Connect SSE if town_id is set
  if (model.get('town_id')) {
    connectSSE();
  }

  // Model change handlers
  model.on('change:points', renderPoints);
  model.on('change:projection', () => { renderAxes(); renderPoints(); });
  model.on('change:selected_citizen_id', renderPoints);
  model.on('change:hovered_citizen_id', renderPoints);
  model.on('change:show_labels', renderPoints);
  model.on('change:show_coalition_colors', renderPoints);
  model.on('change:show_evolving_only', () => { renderPoints(); updateStatus(); });
  model.on('change:archetype_filter', () => { renderPoints(); updateStatus(); });
  model.on('change:coalition_filter', renderPoints);
  model.on('change:town_id', connectSSE);
  model.on('change:sse_connected', updateStatus);
  model.on('change:sse_error', updateStatus);

  // Cleanup function (Law L5)
  return () => {
    if (eventSource) {
      eventSource.close();
    }
    pointElements.clear();
    labelElements.clear();
  };
}

export default { render };
