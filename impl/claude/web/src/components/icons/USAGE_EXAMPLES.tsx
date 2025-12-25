/**
 * GLYPH SYSTEM USAGE EXAMPLES
 *
 * Practical examples demonstrating the kgents glyph system in real components.
 * Copy these patterns into your components.
 */

import React from 'react';
import { Glyph } from './Glyph';

/**
 * EXAMPLE 1: Status Badge Component
 *
 * Replace colored dots with semantic glyphs
 */
export const StatusBadge: React.FC<{ status: 'healthy' | 'degraded' | 'dormant' | 'error' }> = ({ status }) => {
  return (
    <div className={`status-badge status-badge--${status}`}>
      <Glyph name={`status.${status}`} size="sm" className={`glyph--${status}`} breathing={status === 'healthy'} />
      <span>{status}</span>
    </div>
  );
};

/**
 * EXAMPLE 2: Action Button with Glyph
 *
 * Use glyphs instead of Lucide icons for proof-engine operations
 */
export const WitnessButton: React.FC<{ onClick: () => void }> = ({ onClick }) => {
  return (
    <button className="btn-base btn-primary" onClick={onClick}>
      <Glyph name="actions.witness" size="sm" />
      Witness
    </button>
  );
};

/**
 * EXAMPLE 3: AGENTESE Path Display
 *
 * Show context glyphs for AGENTESE paths
 */
export const AgentesePath: React.FC<{ context: string; path: string }> = ({ context, path }) => {
  const contextGlyph = context as 'world' | 'self' | 'concept' | 'void' | 'time';

  return (
    <div className="agentese-path">
      <Glyph name={`contexts.${contextGlyph}`} size="sm" className="glyph--life" />
      <code>{context}.{path}</code>
    </div>
  );
};

/**
 * EXAMPLE 4: Crown Jewel Indicator
 *
 * Living jewel icon with breathing animation
 */
export const JewelIndicator: React.FC<{ jewel: 'brain' | 'witness' | 'atelier' | 'liminal'; active: boolean }> = ({
  jewel,
  active,
}) => {
  return (
    <div className={`jewel-indicator jewel-indicator--${jewel}`}>
      <Glyph name={`jewels.${jewel}`} size="lg" breathing={active} className="glyph--glow" />
      <span className="jewel-indicator__label">{jewel}</span>
    </div>
  );
};

/**
 * EXAMPLE 5: File Tree with Type Glyphs
 *
 * Use file glyphs instead of Lucide icons
 */
export const FileTreeItem: React.FC<{
  name: string;
  type: 'file' | 'folder' | 'spec' | 'code';
  expanded?: boolean;
}> = ({ name, type, expanded }) => {
  const glyphName = type === 'folder' && expanded ? 'navigation.expand' : `files.${type}`;

  return (
    <div className="file-tree-item">
      <Glyph name={glyphName} size="sm" className="glyph--steel" />
      <span className="file-tree-item__name">{name}</span>
    </div>
  );
};

/**
 * EXAMPLE 6: Hypergraph Mode Indicator
 *
 * Modal editing state with mode glyphs
 */
export const ModeIndicator: React.FC<{ mode: 'normal' | 'insert' | 'edge' | 'visual' | 'witness' }> = ({ mode }) => {
  const modeColors = {
    normal: 'glyph--steel',
    insert: 'glyph--life',
    edge: 'glyph--warning',
    visual: 'glyph--glow',
    witness: 'glyph--critical',
  };

  return (
    <div className="mode-indicator">
      <Glyph name={`modes.${mode}`} size="md" className={modeColors[mode]} />
      <kbd>{mode}</kbd>
    </div>
  );
};

/**
 * EXAMPLE 7: Principle Badge
 *
 * Display axioms/principles with glyphs
 */
export const PrincipleBadge: React.FC<{
  principle: 'entity' | 'morphism' | 'mirror' | 'tasteful' | 'composable' | 'heterarchical' | 'generative';
}> = ({ principle }) => {
  return (
    <div className="principle-badge">
      <Glyph name={`axioms.${principle}`} size="sm" className="glyph--glow" />
      <span>{principle}</span>
    </div>
  );
};

/**
 * EXAMPLE 8: Health Monitor with Breathing
 *
 * System health with breathing indicator
 */
export const HealthMonitor: React.FC<{ health: number }> = ({ health }) => {
  const getStatus = (health: number) => {
    if (health >= 80) return 'healthy';
    if (health >= 60) return 'degraded';
    if (health >= 40) return 'warning';
    return 'critical';
  };

  const status = getStatus(health);
  const isHealthy = status === 'healthy';

  return (
    <div className="health-monitor">
      <Glyph
        name={`status.${status === 'critical' ? 'error' : status}`}
        size="md"
        breathing={isHealthy}
        className={`glyph--${status}`}
      />
      <div className="health-monitor__info">
        <span className="health-monitor__value">{health}%</span>
        <span className="health-monitor__label">{status}</span>
      </div>
    </div>
  );
};

/**
 * EXAMPLE 9: Action Menu
 *
 * Menu with action glyphs
 */
export const ActionMenu: React.FC = () => {
  const actions = [
    { id: 'witness', label: 'Witness', glyph: 'actions.witness' },
    { id: 'decide', label: 'Decide', glyph: 'actions.decide' },
    { id: 'compose', label: 'Compose', glyph: 'actions.compose' },
    { id: 'analyze', label: 'Analyze', glyph: 'actions.analyze' },
  ];

  return (
    <div className="action-menu">
      {actions.map((action) => (
        <button key={action.id} className="action-menu__item">
          <Glyph name={action.glyph} size="sm" className="glyph--hover-glow" />
          <span>{action.label}</span>
        </button>
      ))}
    </div>
  );
};

/**
 * EXAMPLE 10: Navigation with Directional Glyphs
 *
 * Replace Lucide arrows with glyph arrows
 */
export const NavigationControls: React.FC = () => {
  return (
    <div className="navigation-controls">
      <button className="btn-base btn-ghost btn-icon" aria-label="Back">
        <Glyph name="navigation.back" size="md" />
      </button>
      <button className="btn-base btn-ghost btn-icon" aria-label="Forward">
        <Glyph name="navigation.forward" size="md" />
      </button>
      <button className="btn-base btn-ghost btn-icon" aria-label="Up">
        <Glyph name="navigation.up" size="md" />
      </button>
      <button className="btn-base btn-ghost btn-icon" aria-label="Down">
        <Glyph name="navigation.down" size="md" />
      </button>
    </div>
  );
};

/**
 * CSS for Examples (add to your component styles)
 */
export const EXAMPLE_STYLES = `
/* Status Badge */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.6rem;
  background: var(--steel-850);
  border: 1px solid var(--steel-700);
  border-radius: var(--radius-bare);
  font-size: 0.85em;
}

/* Jewel Indicator */
.jewel-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
}

.jewel-indicator__label {
  font-size: 0.75em;
  color: var(--steel-400);
  text-transform: lowercase;
}

/* File Tree Item */
.file-tree-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.3rem 0.5rem;
  cursor: pointer;
  transition: background 0.15s ease;
}

.file-tree-item:hover {
  background: var(--steel-850);
}

/* Mode Indicator */
.mode-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.6rem;
  background: var(--steel-900);
  border: 1px solid var(--steel-700);
  border-radius: var(--radius-bare);
}

/* Health Monitor */
.health-monitor {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.5rem 0.75rem;
  background: var(--steel-900);
  border: 1px solid var(--steel-700);
  border-radius: var(--radius-bare);
}

.health-monitor__info {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.health-monitor__value {
  font-size: 0.9em;
  font-weight: 600;
  color: var(--steel-100);
}

.health-monitor__label {
  font-size: 0.7em;
  color: var(--steel-500);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Action Menu */
.action-menu {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  padding: 0.4rem;
  background: var(--steel-900);
  border: 1px solid var(--steel-700);
  border-radius: var(--radius-bare);
}

.action-menu__item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: transparent;
  border: none;
  border-radius: var(--radius-bare);
  color: var(--steel-300);
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: var(--font-mono);
  font-size: 0.85em;
}

.action-menu__item:hover {
  background: var(--steel-850);
  color: var(--steel-100);
}

/* Navigation Controls */
.navigation-controls {
  display: flex;
  gap: 0.4rem;
}
`;
