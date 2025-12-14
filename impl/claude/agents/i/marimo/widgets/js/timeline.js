// Timeline Widget - Horizontal scrollable timeline with state snapshots
const COLORS = {
  background: '#1a1a2e',
  surface: '#252525',
  text: '#e0e0e0',
  muted: '#6a6a7c',
  init: '#7d9c7a',
  synthesis: '#6b4b8a',
  error: '#ff6b6b',
  decay: '#4a4a5c',
  cooling: '#87ceeb',
  demo: '#e6a352',
  default: '#c97b84',
};

function render({ model, el }) {
  const container = document.createElement('div');
  container.className = 'kgents-timeline';
  container.style.cssText = `
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 12px;
    background: ${COLORS.background};
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    min-height: 100px;
  `;

  const controls = document.createElement('div');
  controls.style.cssText = `
    display: flex;
    align-items: center;
    gap: 8px;
    color: ${COLORS.text};
    font-size: 12px;
  `;

  const playBtn = document.createElement('button');
  playBtn.textContent = '▶';
  playBtn.style.cssText = `
    background: ${COLORS.surface};
    border: none;
    color: ${COLORS.text};
    padding: 4px 8px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
  `;
  playBtn.onclick = () => {
    model.set('playing', !model.get('playing'));
    model.save_changes();
  };

  const tickLabel = document.createElement('span');
  tickLabel.className = 'tick-label';

  const zoomControls = document.createElement('div');
  zoomControls.style.cssText = 'margin-left: auto; display: flex; gap: 4px;';

  const zoomIn = document.createElement('button');
  zoomIn.textContent = '+';
  zoomIn.style.cssText = playBtn.style.cssText;
  zoomIn.onclick = () => {
    model.set('zoom', Math.min(4, model.get('zoom') + 0.5));
    model.save_changes();
  };

  const zoomOut = document.createElement('button');
  zoomOut.textContent = '-';
  zoomOut.style.cssText = playBtn.style.cssText;
  zoomOut.onclick = () => {
    model.set('zoom', Math.max(0.5, model.get('zoom') - 0.5));
    model.save_changes();
  };

  zoomControls.appendChild(zoomOut);
  zoomControls.appendChild(zoomIn);

  controls.appendChild(playBtn);
  controls.appendChild(tickLabel);
  controls.appendChild(zoomControls);
  container.appendChild(controls);

  const track = document.createElement('div');
  track.className = 'timeline-track';
  track.style.cssText = `
    position: relative;
    height: 40px;
    background: ${COLORS.surface};
    border-radius: 4px;
    overflow-x: auto;
    overflow-y: hidden;
  `;

  const trackInner = document.createElement('div');
  trackInner.className = 'track-inner';
  trackInner.style.cssText = `
    position: relative;
    height: 100%;
    min-width: 100%;
  `;

  const cursor = document.createElement('div');
  cursor.className = 'cursor';
  cursor.style.cssText = `
    position: absolute;
    top: 0;
    bottom: 0;
    width: 2px;
    background: ${COLORS.text};
    z-index: 10;
    pointer-events: none;
  `;
  trackInner.appendChild(cursor);

  track.appendChild(trackInner);
  container.appendChild(track);

  const preview = document.createElement('div');
  preview.className = 'timeline-preview';
  preview.style.cssText = `
    display: none;
    position: absolute;
    background: ${COLORS.surface};
    border: 1px solid ${COLORS.muted};
    border-radius: 4px;
    padding: 8px;
    font-size: 11px;
    color: ${COLORS.text};
    max-width: 250px;
    z-index: 100;
    pointer-events: none;
  `;
  container.appendChild(preview);

  el.appendChild(container);

  let markers = [];

  function update() {
    const events = model.get('events') || [];
    const currentTick = model.get('current_tick') || 0;
    const zoom = model.get('zoom') || 1;
    const playing = model.get('playing') || false;

    playBtn.textContent = playing ? '⏸' : '▶';
    tickLabel.textContent = `tick: ${currentTick} / ${events.length ? events[events.length - 1].tick : 0}`;

    const maxTick = events.length ? Math.max(...events.map(e => e.tick)) : 100;
    const trackWidth = Math.max(track.clientWidth, maxTick * zoom * 10);
    trackInner.style.width = `${trackWidth}px`;

    markers.forEach(m => m.remove());
    markers = [];

    events.forEach(event => {
      const marker = document.createElement('div');
      marker.className = 'event-marker';
      const color = COLORS[event.type] || COLORS.default;
      marker.style.cssText = `
        position: absolute;
        left: ${event.tick * zoom * 10}px;
        top: 8px;
        width: 8px;
        height: 24px;
        background: ${color};
        border-radius: 2px;
        cursor: pointer;
        transition: transform 0.1s;
      `;
      marker.title = `[${event.tick}] ${event.type}: ${event.message}`;

      marker.onmouseenter = (e) => {
        marker.style.transform = 'scaleY(1.2)';
        preview.innerHTML = `
          <div style="color: ${color}; font-weight: bold;">${event.type}</div>
          <div>tick: ${event.tick}</div>
          <div style="color: ${COLORS.muted};">${event.source}</div>
          <div style="margin-top: 4px;">${event.message}</div>
        `;
        preview.style.display = 'block';
        preview.style.left = `${e.clientX - container.getBoundingClientRect().left}px`;
        preview.style.top = '60px';
      };

      marker.onmouseleave = () => {
        marker.style.transform = '';
        preview.style.display = 'none';
      };

      marker.onclick = () => {
        model.set('current_tick', event.tick);
        model.set('clicked_event', event);
        model.save_changes();
      };

      trackInner.appendChild(marker);
      markers.push(marker);
    });

    cursor.style.left = `${currentTick * zoom * 10}px`;

    if (playing) {
      const cursorLeft = currentTick * zoom * 10;
      if (cursorLeft > track.scrollLeft + track.clientWidth * 0.8) {
        track.scrollLeft = cursorLeft - track.clientWidth * 0.5;
      }
    }
  }

  update();

  model.on('change:events', update);
  model.on('change:current_tick', update);
  model.on('change:zoom', update);
  model.on('change:playing', update);
}

export default { render };
