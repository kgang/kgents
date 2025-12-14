// Dialectic Widget - Three-panel thesis/antithesis/synthesis
const COLORS = {
  thesis: '#e6a352',
  antithesis: '#c97b84',
  synthesis: '#7d9c7a',
  background: '#1a1a2e',
  surface: '#252525',
  text: '#e0e0e0',
  muted: '#6a6a7c',
};

function render({ model, el }) {
  const container = document.createElement('div');
  container.className = 'kgents-dialectic';
  container.style.cssText = `
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 8px;
    padding: 12px;
    background: ${COLORS.background};
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    min-height: 200px;
  `;

  const panels = ['thesis', 'antithesis', 'synthesis'].map(type => {
    const panel = document.createElement('div');
    panel.className = `dialectic-panel ${type}`;
    panel.style.cssText = `
      background: ${COLORS.surface};
      border-radius: 4px;
      padding: 12px;
      border-top: 3px solid ${COLORS[type]};
      display: flex;
      flex-direction: column;
      gap: 8px;
      transition: transform 0.2s, box-shadow 0.2s;
    `;

    const header = document.createElement('div');
    header.className = 'panel-header';
    header.style.cssText = `
      color: ${COLORS[type]};
      font-weight: bold;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 1px;
    `;
    header.textContent = type;

    const content = document.createElement('div');
    content.className = 'panel-content';
    content.style.cssText = `
      color: ${COLORS.text};
      font-size: 14px;
      flex: 1;
      overflow: auto;
      white-space: pre-wrap;
    `;

    const meta = document.createElement('div');
    meta.className = 'panel-meta';
    meta.style.cssText = `
      color: ${COLORS.muted};
      font-size: 10px;
      border-top: 1px solid ${COLORS.muted}33;
      padding-top: 8px;
      margin-top: auto;
    `;

    panel.appendChild(header);
    panel.appendChild(content);
    panel.appendChild(meta);

    return { panel, content, meta, type };
  });

  panels.forEach(p => container.appendChild(p.panel));

  const progressBar = document.createElement('div');
  progressBar.style.cssText = `
    grid-column: 1 / -1;
    height: 4px;
    background: ${COLORS.surface};
    border-radius: 2px;
    overflow: hidden;
  `;
  const progressFill = document.createElement('div');
  progressFill.style.cssText = `
    height: 100%;
    background: linear-gradient(90deg, ${COLORS.thesis}, ${COLORS.antithesis}, ${COLORS.synthesis});
    width: 0%;
    transition: width 0.3s ease-out;
  `;
  progressBar.appendChild(progressFill);
  container.appendChild(progressBar);

  el.appendChild(container);

  function update() {
    const thesis = model.get('thesis') || '';
    const antithesis = model.get('antithesis') || '';
    const synthesis = model.get('synthesis') || '';
    const progress = model.get('synthesis_progress') || 0;
    const phase = model.get('phase') || 'dormant';

    panels[0].content.textContent = thesis || '(awaiting thesis...)';
    panels[1].content.textContent = antithesis || '(awaiting antithesis...)';
    panels[2].content.textContent = synthesis || '(synthesis pending...)';

    const thesisMeta = model.get('thesis_source') || '';
    const antithesisMeta = model.get('antithesis_source') || '';
    const synthesisMeta = model.get('synthesis_confidence')
      ? `confidence: ${(model.get('synthesis_confidence') * 100).toFixed(0)}%`
      : '';

    panels[0].meta.textContent = thesisMeta;
    panels[1].meta.textContent = antithesisMeta;
    panels[2].meta.textContent = synthesisMeta;

    progressFill.style.width = `${progress * 100}%`;

    panels.forEach((p, i) => {
      const isActive = (
        (phase === 'thesis' && i === 0) ||
        (phase === 'antithesis' && i === 1) ||
        (phase === 'synthesis' && i === 2)
      );
      p.panel.style.transform = isActive ? 'translateY(-4px)' : '';
      p.panel.style.boxShadow = isActive
        ? `0 4px 12px ${COLORS[p.type]}44`
        : '';
    });
  }

  update();

  model.on('change:thesis', update);
  model.on('change:antithesis', update);
  model.on('change:synthesis', update);
  model.on('change:synthesis_progress', update);
  model.on('change:phase', update);
  model.on('change:thesis_source', update);
  model.on('change:antithesis_source', update);
  model.on('change:synthesis_confidence', update);
}

export default { render };
