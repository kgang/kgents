/**
 * KgentsWidget ESM Renderer for anywidget (marimo/Jupyter)
 *
 * This module renders KgentsWidget JSON projections to DOM elements.
 * Uses vanilla JavaScript for AI-friendly code and broad compatibility.
 *
 * Supported widget types:
 * - agent_card: Full agent representation with glyph, sparkline, capability bar
 * - sparkline: Time-series mini-chart
 * - bar: Progress/capacity bar
 * - glyph: Single character with styling
 * - generic: JSON fallback for unknown types
 */

// Phase icons for agent cards
const PHASE_ICONS = {
  idle: "○",
  active: "◉",
  waiting: "◐",
  error: "◈",
  yielding: "◑",
  thinking: "◔",
  complete: "●",
};

// Sparkline characters (height levels)
const SPARK_CHARS = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"];

// Bar characters
const BAR_CHARS = {
  solid: { empty: "░", filled: "█", partial: "▓" },
  gradient: { empty: " ", filled: "█", partial: "▓" },
  segments: { empty: "○", filled: "●", partial: "◐" },
  dots: { empty: "·", filled: "◉", partial: "○" },
};

/**
 * Main render function called by anywidget.
 */
function render({ model, el }) {
  const container = document.createElement("div");
  container.className = "kgents-widget";

  function update() {
    const stateJson = model.get("_state_json") || "{}";
    const widgetType = model.get("_widget_type") || "generic";

    let state;
    try {
      state = JSON.parse(stateJson);
    } catch (e) {
      state = { error: "Failed to parse state JSON" };
    }

    // Clear container
    container.innerHTML = "";

    // Dispatch to type-specific renderer
    switch (widgetType) {
      case "agent_card":
        renderAgentCard(container, state);
        break;
      case "sparkline":
        renderSparkline(container, state);
        break;
      case "bar":
        renderBar(container, state);
        break;
      case "glyph":
        renderGlyph(container, state);
        break;
      case "yield_card":
        renderYieldCard(container, state);
        break;
      case "hgent_card":
        renderHgentCard(container, state);
        break;
      default:
        renderGeneric(container, state);
    }
  }

  // Subscribe to state changes
  model.on("change:_state_json", update);
  model.on("change:_widget_type", update);

  // Initial render
  update();
  el.appendChild(container);
}

/**
 * Render an agent card with header, sparkline body, and capability footer.
 */
function renderAgentCard(el, state) {
  const phase = state.phase || "idle";
  const name = state.name || "Agent";
  const agentId = state.agent_id || "";
  const capability = state.capability || 0;
  const breathing = state.breathing && phase === "active";
  const style = state.style || "full";

  // Card container
  const card = document.createElement("div");
  card.className = `kgents-agent-card kgents-phase-${phase}`;
  card.dataset.agentId = agentId;
  if (breathing) {
    card.classList.add("kgents-breathing");
  }

  // Header: phase icon + name
  const header = document.createElement("div");
  header.className = "kgents-card-header";

  const phaseIcon = document.createElement("span");
  phaseIcon.className = "kgents-phase-icon";
  phaseIcon.textContent = PHASE_ICONS[phase] || "○";
  header.appendChild(phaseIcon);

  const nameSpan = document.createElement("span");
  nameSpan.className = "kgents-agent-name";
  nameSpan.textContent = name;
  header.appendChild(nameSpan);

  card.appendChild(header);

  // Body: activity sparkline (if not minimal)
  if (style !== "minimal" && state.children?.activity) {
    const body = document.createElement("div");
    body.className = "kgents-card-body";
    const activityData = state.children.activity;
    if (activityData.values && activityData.values.length > 0) {
      body.innerHTML = renderSparklineSVG(activityData.values);
    }
    card.appendChild(body);
  }

  // Footer: capability bar (if full style)
  if (style === "full") {
    const footer = document.createElement("div");
    footer.className = "kgents-card-footer";
    footer.innerHTML = renderCapabilityBar(capability);
    card.appendChild(footer);
  }

  el.appendChild(card);
}

/**
 * Render a sparkline widget.
 */
function renderSparkline(el, state) {
  const container = document.createElement("div");
  container.className = "kgents-sparkline";

  const values = state.values || [];
  if (values.length === 0) {
    container.textContent = "─".repeat(10);
  } else {
    container.innerHTML = renderSparklineSVG(values);
  }

  // Add label if present
  if (state.label) {
    const wrapper = document.createElement("div");
    wrapper.className = "kgents-sparkline-container";
    const label = document.createElement("span");
    label.className = "kgents-sparkline-label";
    label.textContent = state.label + ": ";
    wrapper.appendChild(label);
    wrapper.appendChild(container);
    el.appendChild(wrapper);
  } else {
    el.appendChild(container);
  }
}

/**
 * Render sparkline as SVG for smooth rendering.
 */
function renderSparklineSVG(values) {
  if (!values || values.length === 0) return "";

  const width = 100;
  const height = 20;
  const padding = 1;

  // Generate SVG path points
  const points = values
    .map((v, i) => {
      const x = (i / Math.max(values.length - 1, 1)) * (width - 2 * padding) + padding;
      const y = height - padding - v * (height - 2 * padding);
      return `${x},${y}`;
    })
    .join(" ");

  return `
    <svg viewBox="0 0 ${width} ${height}" class="kgents-sparkline-svg" preserveAspectRatio="none">
      <polyline points="${points}" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `;
}

/**
 * Render capability bar as Unicode characters.
 */
function renderCapabilityBar(value, width = 10) {
  const filledCount = Math.floor(value * width);
  const partial = value * width - filledCount;
  let bar = "";

  for (let i = 0; i < width; i++) {
    if (i < filledCount) {
      bar += BAR_CHARS.solid.filled;
    } else if (i === filledCount && partial > 0.5) {
      bar += BAR_CHARS.solid.partial;
    } else {
      bar += BAR_CHARS.solid.empty;
    }
  }

  return `<span class="kgents-capability-bar">${bar}</span>`;
}

/**
 * Render a bar widget.
 */
function renderBar(el, state) {
  const container = document.createElement("div");
  container.className = "kgents-bar";

  const value = state.value || 0;
  const width = state.width || 10;
  const barStyle = state.style || "solid";
  const orientation = state.orientation || "horizontal";

  const chars = BAR_CHARS[barStyle] || BAR_CHARS.solid;
  const filledCount = Math.floor(value * width);
  const partial = value * width - filledCount;

  let bar = "";
  for (let i = 0; i < width; i++) {
    if (i < filledCount) {
      bar += chars.filled;
    } else if (i === filledCount && partial > 0.5) {
      bar += chars.partial || chars.filled;
    } else {
      bar += chars.empty;
    }
  }

  if (orientation === "vertical") {
    bar = bar.split("").join("<br>");
    container.classList.add("kgents-bar-vertical");
  }

  container.innerHTML = bar;

  // Add label if present
  if (state.label) {
    const wrapper = document.createElement("div");
    wrapper.className = "kgents-bar-container";
    const label = document.createElement("span");
    label.className = "kgents-bar-label";
    label.textContent = state.label + ": ";
    wrapper.appendChild(label);
    wrapper.appendChild(container);
    el.appendChild(wrapper);
  } else {
    el.appendChild(container);
  }
}

/**
 * Render a single glyph.
 */
function renderGlyph(el, state) {
  const span = document.createElement("span");
  span.className = "kgents-glyph";

  const char = state.char || "·";
  span.textContent = char;

  // Apply styling
  if (state.fg) {
    span.style.color = state.fg;
  }
  if (state.bg) {
    span.style.backgroundColor = state.bg;
  }

  // Apply distortion if present
  if (state.distortion) {
    const d = state.distortion;
    const transforms = [];
    if (d.skew) transforms.push(`skewX(${d.skew}deg)`);
    if (d.jitter_x || d.jitter_y) {
      transforms.push(`translate(${d.jitter_x || 0}px, ${d.jitter_y || 0}px)`);
    }
    if (transforms.length > 0) {
      span.style.transform = transforms.join(" ");
    }
    if (d.blur && d.blur > 1) {
      span.style.filter = `blur(${(d.blur - 1) * 2}px)`;
    }
  }

  // Animation class
  if (state.animate && state.animate !== "none") {
    span.classList.add(`kgents-glyph-${state.animate}`);
  }

  el.appendChild(span);
}

/**
 * Render a yield card (for async operations).
 */
function renderYieldCard(el, state) {
  const card = document.createElement("div");
  card.className = "kgents-yield-card";

  const status = state.status || "pending";
  card.classList.add(`kgents-yield-${status}`);

  // Operation name
  const header = document.createElement("div");
  header.className = "kgents-yield-header";
  header.textContent = state.operation || "Yield";
  card.appendChild(header);

  // Progress indicator
  if (status === "in_progress") {
    const progress = document.createElement("div");
    progress.className = "kgents-yield-progress";
    progress.textContent = "⟳";
    card.appendChild(progress);
  }

  el.appendChild(card);
}

/**
 * Render an H-gent card (handler agent).
 */
function renderHgentCard(el, state) {
  // Use agent card structure with custom styling
  const card = document.createElement("div");
  card.className = "kgents-hgent-card";

  const name = state.name || "H-gent";
  const handlerType = state.handler_type || "unknown";

  const header = document.createElement("div");
  header.className = "kgents-hgent-header";
  header.innerHTML = `<span class="kgents-hgent-icon">⚙</span> ${name}`;
  card.appendChild(header);

  const typeLabel = document.createElement("div");
  typeLabel.className = "kgents-hgent-type";
  typeLabel.textContent = handlerType;
  card.appendChild(typeLabel);

  el.appendChild(card);
}

/**
 * Render generic JSON for unknown types.
 */
function renderGeneric(el, state) {
  const pre = document.createElement("pre");
  pre.className = "kgents-generic";
  pre.textContent = JSON.stringify(state, null, 2);
  el.appendChild(pre);
}

export default { render };
