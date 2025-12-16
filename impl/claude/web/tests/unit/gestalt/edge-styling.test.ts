/**
 * Edge Styling Tests
 *
 * Tests for the edge styling configuration and utility functions.
 *
 * @see plans/_continuations/gestalt-visual-showcase-chunk3.md
 */

import { describe, it, expect } from 'vitest';
import {
  EDGE_STYLES,
  getEdgeStyle,
  getHighlightedStyle,
  getDimmedStyle,
  getFlowConfig,
  DEFAULT_FLOW_CONFIG,
  VIOLATION_FLOW_CONFIG,
  calculatePulseOpacity,
  calculatePulseGlow,
  type EdgeStyle,
  type EdgeType,
} from '../../../src/components/gestalt/EdgeStyles';

// =============================================================================
// EDGE_STYLES Configuration Tests
// =============================================================================

describe('EDGE_STYLES', () => {
  it('defines style for import edges', () => {
    const style = EDGE_STYLES.import;
    expect(style).toBeDefined();
    expect(style.color).toBe('#6b7280');
    expect(style.dash).toBe(false);
    expect(style.width).toBe(1);
    expect(style.opacity).toBe(0.25);
    expect(style.animated).toBe(false);
  });

  it('defines style for violation edges', () => {
    const style = EDGE_STYLES.violation;
    expect(style).toBeDefined();
    expect(style.color).toBe('#ef4444');
    expect(style.dash).toBe(false);
    expect(style.width).toBe(2.5);
    expect(style.opacity).toBe(0.9);
    expect(style.animated).toBe(true);
    expect(style.glowColor).toBe('#ef4444');
    expect(style.glowIntensity).toBeGreaterThan(0);
  });

  it('violations are more prominent than imports', () => {
    const importStyle = EDGE_STYLES.import;
    const violationStyle = EDGE_STYLES.violation;

    expect(violationStyle.width).toBeGreaterThan(importStyle.width);
    expect(violationStyle.opacity).toBeGreaterThan(importStyle.opacity);
  });

  it('defines future infrastructure edge types', () => {
    const futureTypes: EdgeType[] = ['reads', 'writes', 'calls', 'publishes', 'subscribes', 'extends', 'implements'];

    futureTypes.forEach((type) => {
      expect(EDGE_STYLES[type]).toBeDefined();
      expect(EDGE_STYLES[type].color).toBeDefined();
      expect(EDGE_STYLES[type].width).toBeGreaterThan(0);
      expect(EDGE_STYLES[type].opacity).toBeGreaterThan(0);
    });
  });

  it('uses semantic colors for different edge types', () => {
    // Event types (pub/sub) should share a color
    expect(EDGE_STYLES.publishes.color).toBe(EDGE_STYLES.subscribes.color);

    // Type relationships should share a color
    expect(EDGE_STYLES.extends.color).toBe(EDGE_STYLES.implements.color);

    // Data flow types have distinct colors
    expect(EDGE_STYLES.reads.color).not.toBe(EDGE_STYLES.writes.color);
  });

  it('marks animated edge types correctly', () => {
    expect(EDGE_STYLES.violation.animated).toBe(true);
    expect(EDGE_STYLES.reads.animated).toBe(true);
    expect(EDGE_STYLES.publishes.animated).toBe(true);
    expect(EDGE_STYLES.import.animated).toBe(false);
  });
});

// =============================================================================
// getEdgeStyle Tests
// =============================================================================

describe('getEdgeStyle', () => {
  it('returns violation style when isViolation is true', () => {
    const style = getEdgeStyle(true);
    expect(style).toBe(EDGE_STYLES.violation);
  });

  it('returns import style when isViolation is false and no type specified', () => {
    const style = getEdgeStyle(false);
    expect(style).toBe(EDGE_STYLES.import);
  });

  it('returns specific type style when provided', () => {
    const style = getEdgeStyle(false, 'reads');
    expect(style).toBe(EDGE_STYLES.reads);
  });

  it('violation flag overrides edge type', () => {
    const style = getEdgeStyle(true, 'reads');
    expect(style).toBe(EDGE_STYLES.violation);
  });

  it('falls back to import for unknown edge type', () => {
    const style = getEdgeStyle(false, 'unknownType');
    expect(style).toBe(EDGE_STYLES.import);
  });
});

// =============================================================================
// getHighlightedStyle Tests
// =============================================================================

describe('getHighlightedStyle', () => {
  it('increases opacity', () => {
    const base: EdgeStyle = { color: '#fff', dash: false, width: 1, opacity: 0.5 };
    const highlighted = getHighlightedStyle(base);
    expect(highlighted.opacity).toBeGreaterThan(base.opacity);
  });

  it('caps opacity at 1.0', () => {
    const base: EdgeStyle = { color: '#fff', dash: false, width: 1, opacity: 0.9 };
    const highlighted = getHighlightedStyle(base);
    expect(highlighted.opacity).toBeLessThanOrEqual(1.0);
  });

  it('increases width', () => {
    const base: EdgeStyle = { color: '#fff', dash: false, width: 1, opacity: 0.5 };
    const highlighted = getHighlightedStyle(base);
    expect(highlighted.width).toBeGreaterThan(base.width);
  });

  it('increases glow intensity', () => {
    const base: EdgeStyle = { color: '#fff', dash: false, width: 1, opacity: 0.5, glowIntensity: 0.2 };
    const highlighted = getHighlightedStyle(base);
    expect(highlighted.glowIntensity).toBeGreaterThan(base.glowIntensity!);
  });

  it('preserves other properties', () => {
    const base: EdgeStyle = { color: '#ff0000', dash: true, width: 2, opacity: 0.5 };
    const highlighted = getHighlightedStyle(base);
    expect(highlighted.color).toBe(base.color);
    expect(highlighted.dash).toBe(base.dash);
  });
});

// =============================================================================
// getDimmedStyle Tests
// =============================================================================

describe('getDimmedStyle', () => {
  it('decreases opacity', () => {
    const base: EdgeStyle = { color: '#fff', dash: false, width: 1, opacity: 0.5 };
    const dimmed = getDimmedStyle(base);
    expect(dimmed.opacity).toBeLessThan(base.opacity);
  });

  it('decreases width slightly', () => {
    const base: EdgeStyle = { color: '#fff', dash: false, width: 2, opacity: 0.5 };
    const dimmed = getDimmedStyle(base);
    expect(dimmed.width).toBeLessThan(base.width);
  });

  it('disables animation', () => {
    const base: EdgeStyle = { color: '#fff', dash: false, width: 1, opacity: 0.5, animated: true };
    const dimmed = getDimmedStyle(base);
    expect(dimmed.animated).toBe(false);
  });

  it('preserves other properties', () => {
    const base: EdgeStyle = { color: '#ff0000', dash: true, width: 2, opacity: 0.5 };
    const dimmed = getDimmedStyle(base);
    expect(dimmed.color).toBe(base.color);
    expect(dimmed.dash).toBe(base.dash);
  });
});

// =============================================================================
// Flow Animation Config Tests
// =============================================================================

describe('getFlowConfig', () => {
  it('returns default config for non-violations', () => {
    const config = getFlowConfig(false);
    expect(config).toBe(DEFAULT_FLOW_CONFIG);
  });

  it('returns violation config for violations', () => {
    const config = getFlowConfig(true);
    expect(config).toBe(VIOLATION_FLOW_CONFIG);
  });
});

describe('DEFAULT_FLOW_CONFIG', () => {
  it('has reasonable particle count', () => {
    expect(DEFAULT_FLOW_CONFIG.particleCount).toBeGreaterThanOrEqual(1);
    expect(DEFAULT_FLOW_CONFIG.particleCount).toBeLessThanOrEqual(10);
  });

  it('has positive particle radius', () => {
    expect(DEFAULT_FLOW_CONFIG.particleRadius).toBeGreaterThan(0);
    expect(DEFAULT_FLOW_CONFIG.particleRadius).toBeLessThan(1);
  });

  it('has positive base speed', () => {
    expect(DEFAULT_FLOW_CONFIG.baseSpeed).toBeGreaterThan(0);
  });
});

describe('VIOLATION_FLOW_CONFIG', () => {
  it('has larger particles than default', () => {
    expect(VIOLATION_FLOW_CONFIG.particleRadius).toBeGreaterThan(DEFAULT_FLOW_CONFIG.particleRadius);
  });

  it('has slower speed than default', () => {
    expect(VIOLATION_FLOW_CONFIG.baseSpeed).toBeLessThan(DEFAULT_FLOW_CONFIG.baseSpeed);
  });
});

// =============================================================================
// Pulse Animation Tests
// =============================================================================

describe('calculatePulseOpacity', () => {
  it('returns value around base opacity', () => {
    const baseOpacity = 0.8;
    // Test at multiple time points
    for (let t = 0; t < 10; t += 0.5) {
      const opacity = calculatePulseOpacity(t, baseOpacity);
      expect(opacity).toBeGreaterThan(baseOpacity * 0.5);
      expect(opacity).toBeLessThanOrEqual(baseOpacity * 1.2);
    }
  });

  it('oscillates over time', () => {
    const baseOpacity = 0.8;
    const opacities = [0, 0.5, 1, 1.5, 2].map((t) => calculatePulseOpacity(t, baseOpacity));

    // Should have some variation
    const min = Math.min(...opacities);
    const max = Math.max(...opacities);
    expect(max - min).toBeGreaterThan(0.01);
  });
});

describe('calculatePulseGlow', () => {
  it('returns value in valid range', () => {
    for (let t = 0; t < 10; t += 0.5) {
      const glow = calculatePulseGlow(t);
      expect(glow).toBeGreaterThan(0);
      expect(glow).toBeLessThanOrEqual(1);
    }
  });

  it('oscillates over time', () => {
    const glows = [0, 0.5, 1, 1.5, 2].map((t) => calculatePulseGlow(t));

    // Should have some variation
    const min = Math.min(...glows);
    const max = Math.max(...glows);
    expect(max - min).toBeGreaterThan(0.01);
  });
});

// =============================================================================
// Animation Toggle Integration Tests
// =============================================================================

describe('Animation Toggle Integration', () => {
  it('dimmed style disables animation', () => {
    const animatedBase = EDGE_STYLES.violation;
    expect(animatedBase.animated).toBe(true);

    const dimmed = getDimmedStyle(animatedBase);
    expect(dimmed.animated).toBe(false);
  });

  it('highlighted style preserves animation capability', () => {
    const animatedBase = EDGE_STYLES.violation;
    const highlighted = getHighlightedStyle(animatedBase);

    // animated property should be preserved (not explicitly set to false)
    expect(highlighted.animated).toBe(animatedBase.animated);
  });
});
