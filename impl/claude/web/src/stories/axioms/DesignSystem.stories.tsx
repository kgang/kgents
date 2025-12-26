/**
 * kgents Design System - Axiom Stories
 *
 * The irreducible design primitives for the STARK BIOME aesthetic.
 * "90% Steel (cool industrial) / 10% Earned Glow (organic accents)"
 *
 * Philosophy: "Daring, bold, creative, opinionated but not gaudy"
 *
 * BOOKMARK THIS PAGE: Reference for all design tokens
 *
 * @see src/design/tokens.css - Single source of truth
 * @see src/design/README.md - Full documentation
 * @see src/styles/breathing.css - Motion system
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import React, { useState } from 'react';
import '../../design/tokens.css';
import '../../styles/breathing.css';
import { Mode, MODE_COLORS, MODE_DEFINITIONS, ALL_MODES } from '../../types/mode';
import { useBreathing, BREATHING_4_7_8 } from '../../hooks/useBreathing';

// =============================================================================
// Meta
// =============================================================================

const meta: Meta = {
  title: 'Axioms/Design System',
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: `
# kgents Design System

The irreducible design primitives for the **STARK BIOME** aesthetic.

> "The frame is humble. The content glows."

## Philosophy

- **90% Steel**: Cool industrial backgrounds, frames, containers
- **10% Earned Glow**: Organic accents that celebrate moments (success, focus, special states)
- **Bare Edge**: Sharp corners (2-4px) make warm elements pop against austerity
- **Breathing Motion**: Subtle 4-7-8 animation cycles, never frantic

## Token File

All tokens live in \`src/design/tokens.css\` - the single source of truth.

\`\`\`css
@import '../design/tokens.css';
\`\`\`
        `,
      },
    },
  },
  tags: ['autodocs'],
};

export default meta;

// =============================================================================
// Shared Styles
// =============================================================================

const swatchContainerStyle: React.CSSProperties = {
  display: 'grid',
  gap: 'var(--space-md)',
  gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
};

const swatchStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: 'var(--space-xs)',
};

const colorBoxStyle: React.CSSProperties = {
  width: '100%',
  height: '60px',
  borderRadius: 'var(--radius-bare)',
  border: '1px solid var(--surface-3)',
};

const labelStyle: React.CSSProperties = {
  fontFamily: 'var(--font-mono)',
  fontSize: 'var(--font-size-xs)',
  color: 'var(--text-secondary)',
};

const valueStyle: React.CSSProperties = {
  fontFamily: 'var(--font-mono)',
  fontSize: 'var(--font-size-xs)',
  color: 'var(--text-muted)',
};

const sectionTitleStyle: React.CSSProperties = {
  fontSize: 'var(--font-size-lg)',
  fontWeight: 'var(--font-weight-semibold)',
  color: 'var(--text-primary)',
  marginBottom: 'var(--space-md)',
  paddingBottom: 'var(--space-sm)',
  borderBottom: '1px solid var(--surface-3)',
};

const subsectionTitleStyle: React.CSSProperties = {
  fontSize: 'var(--font-size-md)',
  fontWeight: 'var(--font-weight-medium)',
  color: 'var(--text-secondary)',
  marginTop: 'var(--space-lg)',
  marginBottom: 'var(--space-sm)',
};

const annotationStyle: React.CSSProperties = {
  fontSize: 'var(--font-size-sm)',
  color: 'var(--accent-primary)',
  fontStyle: 'italic',
  marginBottom: 'var(--space-md)',
};

// =============================================================================
// Color Swatch Component
// =============================================================================

interface ColorSwatchProps {
  name: string;
  value: string;
  cssVar: string;
}

function ColorSwatch({ name, value, cssVar }: ColorSwatchProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(`var(${cssVar})`);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div style={swatchStyle}>
      <div
        style={{
          ...colorBoxStyle,
          background: value,
          cursor: 'pointer',
          transition: 'transform var(--transition-fast)',
        }}
        onClick={handleCopy}
        title={`Click to copy: var(${cssVar})`}
      />
      <span style={labelStyle}>{name}</span>
      <span style={valueStyle}>{copied ? 'Copied!' : cssVar}</span>
    </div>
  );
}

// =============================================================================
// 1. Color System - STARK BIOME
// =============================================================================

export const ColorSystem: StoryObj = {
  name: '1. Color System - STARK BIOME',
  render: () => (
    <div style={{ maxWidth: '1200px' }}>
      <h2 style={sectionTitleStyle}>Color System - STARK BIOME</h2>
      <p style={annotationStyle}>
        "90% steel / 10% earned glow" - The frame is humble. The content glows.
      </p>

      {/* Steel Foundation */}
      <h3 style={subsectionTitleStyle}>Steel Foundation (The 90%)</h3>
      <p style={{ ...valueStyle, marginBottom: 'var(--space-md)' }}>
        Cool industrial tones for backgrounds, frames, and containers.
      </p>
      <div style={swatchContainerStyle}>
        <ColorSwatch name="Obsidian" value="#0a0a0c" cssVar="--color-steel-obsidian" />
        <ColorSwatch name="Carbon" value="#141418" cssVar="--color-steel-carbon" />
        <ColorSwatch name="Slate" value="#1c1c22" cssVar="--color-steel-slate" />
        <ColorSwatch name="Gunmetal" value="#28282f" cssVar="--color-steel-gunmetal" />
        <ColorSwatch name="Zinc" value="#3a3a44" cssVar="--color-steel-zinc" />
      </div>

      {/* Numbered Steel Scale */}
      <h3 style={subsectionTitleStyle}>Steel Scale (Granular Control)</h3>
      <div style={swatchContainerStyle}>
        <ColorSwatch name="950" value="#0d0d0d" cssVar="--color-steel-950" />
        <ColorSwatch name="900" value="#1a1a1a" cssVar="--color-steel-900" />
        <ColorSwatch name="850" value="#1f1f1f" cssVar="--color-steel-850" />
        <ColorSwatch name="800" value="#252525" cssVar="--color-steel-800" />
        <ColorSwatch name="700" value="#333" cssVar="--color-steel-700" />
        <ColorSwatch name="600" value="#444" cssVar="--color-steel-600" />
        <ColorSwatch name="500" value="#666" cssVar="--color-steel-500" />
        <ColorSwatch name="400" value="#888" cssVar="--color-steel-400" />
        <ColorSwatch name="300" value="#a0a0a0" cssVar="--color-steel-300" />
        <ColorSwatch name="200" value="#ccc" cssVar="--color-steel-200" />
        <ColorSwatch name="100" value="#e0e0e0" cssVar="--color-steel-100" />
      </div>

      {/* Living Accents */}
      <h3 style={subsectionTitleStyle}>Living Accents (Organic Warmth)</h3>
      <div style={swatchContainerStyle}>
        <ColorSwatch name="Moss" value="#1a2e1a" cssVar="--color-life-moss" />
        <ColorSwatch name="Sage" value="#4a6b4a" cssVar="--color-life-sage" />
        <ColorSwatch name="Mint" value="#6b8b6b" cssVar="--color-life-mint" />
        <ColorSwatch name="Sprout" value="#8bab8b" cssVar="--color-life-sprout" />
      </div>

      {/* Bioluminescent Glow */}
      <h3 style={subsectionTitleStyle}>Bioluminescent Glow (The Earned 10%)</h3>
      <p style={{ ...valueStyle, marginBottom: 'var(--space-md)' }}>
        Special moments only. Success, focus, crystallization.
      </p>
      <div style={swatchContainerStyle}>
        <ColorSwatch name="Spore (Primary)" value="#c4a77d" cssVar="--color-glow-spore" />
        <ColorSwatch name="Amber (Hover)" value="#d4b88c" cssVar="--color-glow-amber" />
        <ColorSwatch name="Light" value="#e5c99d" cssVar="--color-glow-light" />
        <ColorSwatch name="Lichen (Secondary)" value="#8ba98b" cssVar="--color-glow-lichen" />
      </div>

      {/* Surface Hierarchy */}
      <h3 style={subsectionTitleStyle}>Surface Hierarchy</h3>
      <p style={{ ...valueStyle, marginBottom: 'var(--space-md)' }}>
        Semantic mappings for consistent surface elevation.
      </p>
      <div style={{ display: 'flex', gap: 'var(--space-sm)', marginBottom: 'var(--space-lg)' }}>
        {[0, 1, 2, 3, 4].map((level) => (
          <div
            key={level}
            style={{
              flex: 1,
              height: '80px',
              background: `var(--surface-${level})`,
              border: '1px solid var(--surface-3)',
              borderRadius: 'var(--radius-bare)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontFamily: 'var(--font-mono)',
              fontSize: 'var(--font-size-sm)',
              color: 'var(--text-secondary)',
            }}
          >
            --surface-{level}
          </div>
        ))}
      </div>

      {/* Text Hierarchy */}
      <h3 style={subsectionTitleStyle}>Text Hierarchy</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
        <div>
          <span style={{ color: 'var(--text-primary)', fontSize: 'var(--font-size-md)' }}>
            Primary: Headlines, important content
          </span>
          <code style={{ ...valueStyle, marginLeft: 'var(--space-sm)' }}>--text-primary</code>
        </div>
        <div>
          <span style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-md)' }}>
            Secondary: Body text, descriptions
          </span>
          <code style={{ ...valueStyle, marginLeft: 'var(--space-sm)' }}>--text-secondary</code>
        </div>
        <div>
          <span style={{ color: 'var(--text-muted)', fontSize: 'var(--font-size-md)' }}>
            Muted: Hints, timestamps, whispers
          </span>
          <code style={{ ...valueStyle, marginLeft: 'var(--space-sm)' }}>--text-muted</code>
        </div>
      </div>
    </div>
  ),
};

// =============================================================================
// 2. Spacing Scale
// =============================================================================

export const SpacingScale: StoryObj = {
  name: '2. Spacing Scale',
  render: () => {
    const spacings = [
      { name: 'xs', value: '0.2rem', pixels: '3.2px', use: 'Micro gaps, inline' },
      { name: 'sm', value: '0.4rem', pixels: '6.4px', use: 'Tight groupings' },
      { name: 'md', value: '0.85rem', pixels: '13.6px', use: 'Standard gaps (default)' },
      { name: 'lg', value: '1.25rem', pixels: '20px', use: 'Comfortable sections' },
      { name: 'xl', value: '1.75rem', pixels: '28px', use: 'Spacious areas' },
      { name: '2xl', value: '2.5rem', pixels: '40px', use: 'Major sections' },
    ];

    return (
      <div style={{ maxWidth: '800px' }}>
        <h2 style={sectionTitleStyle}>Spacing Scale</h2>
        <p style={annotationStyle}>"Tight Frame, Breathing Content"</p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
          {spacings.map(({ name, value, pixels, use }) => (
            <div key={name} style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-lg)' }}>
              <div
                style={{
                  width: `var(--space-${name})`,
                  height: '40px',
                  background: 'var(--accent-primary)',
                  borderRadius: 'var(--radius-bare)',
                  minWidth: '4px',
                }}
              />
              <div style={{ flex: 1 }}>
                <code style={{ ...labelStyle, display: 'block' }}>--space-{name}</code>
                <span style={valueStyle}>
                  {value} ({pixels}) - {use}
                </span>
              </div>
              <div
                style={{
                  padding: `var(--space-${name})`,
                  background: 'var(--surface-1)',
                  border: '1px solid var(--surface-3)',
                  borderRadius: 'var(--radius-bare)',
                }}
              >
                <span style={valueStyle}>Padding demo</span>
              </div>
            </div>
          ))}
        </div>

        <h3 style={subsectionTitleStyle}>Grid Demo</h3>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: 'var(--space-md)',
            marginTop: 'var(--space-md)',
          }}
        >
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div
              key={i}
              style={{
                padding: 'var(--space-md)',
                background: 'var(--surface-1)',
                border: '1px solid var(--surface-3)',
                borderRadius: 'var(--radius-bare)',
                textAlign: 'center',
                color: 'var(--text-secondary)',
              }}
            >
              Item {i}
            </div>
          ))}
        </div>
      </div>
    );
  },
};

// =============================================================================
// 3. Border Radius - Bare Edge
// =============================================================================

export const BorderRadius: StoryObj = {
  name: '3. Border Radius - Bare Edge',
  render: () => {
    const radii = [
      { name: 'none', value: '0px', use: 'Panels, canvas - invisible frame' },
      { name: 'bare', value: '2px', use: 'Cards, containers - just enough to not cut' },
      { name: 'subtle', value: '3px', use: 'Interactive surfaces - softened for touch' },
      { name: 'soft', value: '4px', use: 'Accent elements - use sparingly' },
      { name: 'pill', value: '9999px', use: 'Badges, tags - finite, precious' },
    ];

    return (
      <div style={{ maxWidth: '800px' }}>
        <h2 style={sectionTitleStyle}>Border Radius - Bare Edge System</h2>
        <p style={annotationStyle}>
          "The container is humble; the content glows." Sharp frames make warm elements pop.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
          {radii.map(({ name, value, use }) => (
            <div key={name} style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-lg)' }}>
              <div
                style={{
                  width: '80px',
                  height: '80px',
                  background: 'var(--surface-2)',
                  border: '2px solid var(--accent-primary)',
                  borderRadius: `var(--radius-${name})`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--text-muted)',
                  fontSize: 'var(--font-size-xs)',
                }}
              >
                {value}
              </div>
              <div style={{ flex: 1 }}>
                <code style={{ ...labelStyle, display: 'block' }}>--radius-{name}</code>
                <span style={valueStyle}>{use}</span>
              </div>
            </div>
          ))}
        </div>

        <h3 style={subsectionTitleStyle}>Common Patterns</h3>
        <div style={{ display: 'flex', gap: 'var(--space-md)', flexWrap: 'wrap' }}>
          <div
            style={{
              padding: 'var(--space-md)',
              background: 'var(--surface-1)',
              border: '1px solid var(--surface-3)',
              borderRadius: 'var(--radius-bare)',
            }}
          >
            Card (--radius-bare)
          </div>
          <button
            style={{
              padding: 'var(--space-sm) var(--space-md)',
              background: 'var(--surface-2)',
              border: '1px solid var(--surface-3)',
              borderRadius: 'var(--radius-subtle)',
              color: 'var(--text-primary)',
              cursor: 'pointer',
            }}
          >
            Button (--radius-subtle)
          </button>
          <span
            style={{
              padding: 'var(--space-xs) var(--space-sm)',
              background: 'var(--accent-success)',
              borderRadius: 'var(--radius-pill)',
              color: 'var(--surface-0)',
              fontSize: 'var(--font-size-xs)',
            }}
          >
            Badge (--radius-pill)
          </span>
        </div>
      </div>
    );
  },
};

// =============================================================================
// 4. Typography
// =============================================================================

export const Typography: StoryObj = {
  name: '4. Typography',
  render: () => {
    const sizes = [
      { name: 'xs', value: '0.625rem', pixels: '10px' },
      { name: 'sm', value: '0.75rem', pixels: '12px' },
      { name: 'md', value: '0.875rem', pixels: '14px' },
      { name: 'base', value: '1rem', pixels: '16px' },
      { name: 'lg', value: '1.25rem', pixels: '20px' },
      { name: 'xl', value: '1.5rem', pixels: '24px' },
      { name: '2xl', value: '2rem', pixels: '32px' },
    ];

    const weights = [
      { name: 'normal', value: 400 },
      { name: 'medium', value: 500 },
      { name: 'semibold', value: 600 },
      { name: 'bold', value: 700 },
    ];

    return (
      <div style={{ maxWidth: '800px' }}>
        <h2 style={sectionTitleStyle}>Typography</h2>

        {/* Font Families */}
        <h3 style={subsectionTitleStyle}>Font Families</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          <div>
            <span style={{ fontFamily: 'var(--font-sans)', fontSize: 'var(--font-size-lg)' }}>
              Inter - The quick brown fox jumps over the lazy dog
            </span>
            <code style={{ ...valueStyle, display: 'block' }}>--font-sans</code>
          </div>
          <div>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--font-size-lg)' }}>
              JetBrains Mono - const foo = () =&gt; 42;
            </span>
            <code style={{ ...valueStyle, display: 'block' }}>--font-mono</code>
          </div>
        </div>

        {/* Size Scale */}
        <h3 style={subsectionTitleStyle}>Size Scale</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
          {sizes.map(({ name, value, pixels }) => (
            <div key={name} style={{ display: 'flex', alignItems: 'baseline', gap: 'var(--space-md)' }}>
              <span
                style={{
                  fontSize: `var(--font-size-${name})`,
                  color: 'var(--text-primary)',
                  minWidth: '300px',
                }}
              >
                The quick brown fox
              </span>
              <code style={labelStyle}>--font-size-{name}</code>
              <span style={valueStyle}>
                {value} ({pixels})
              </span>
            </div>
          ))}
        </div>

        {/* Weight Scale */}
        <h3 style={subsectionTitleStyle}>Weight Scale</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
          {weights.map(({ name, value }) => (
            <div key={name} style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
              <span
                style={{
                  fontWeight: value,
                  fontSize: 'var(--font-size-lg)',
                  color: 'var(--text-primary)',
                  minWidth: '300px',
                }}
              >
                Weight {value}
              </span>
              <code style={labelStyle}>--font-weight-{name}</code>
            </div>
          ))}
        </div>

        {/* Line Heights */}
        <h3 style={subsectionTitleStyle}>Line Heights</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 'var(--space-md)' }}>
          {['tight', 'normal', 'relaxed'].map((name) => (
            <div
              key={name}
              style={{
                padding: 'var(--space-md)',
                background: 'var(--surface-1)',
                border: '1px solid var(--surface-3)',
                borderRadius: 'var(--radius-bare)',
              }}
            >
              <code style={{ ...labelStyle, display: 'block', marginBottom: 'var(--space-xs)' }}>
                --line-height-{name}
              </code>
              <p
                style={{
                  lineHeight: `var(--line-height-${name})`,
                  color: 'var(--text-secondary)',
                  margin: 0,
                }}
              >
                The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs.
              </p>
            </div>
          ))}
        </div>
      </div>
    );
  },
};

// =============================================================================
// 5. Shadows & Elevation
// =============================================================================

export const ShadowsAndElevation: StoryObj = {
  name: '5. Shadows & Elevation',
  render: () => {
    const shadows = [
      { name: 'none', use: 'Flat elements' },
      { name: 'sm', use: 'Subtle elevation - cards at rest' },
      { name: 'md', use: 'Clear elevation - card hover, dropdowns' },
      { name: 'lg', use: 'Strong elevation - modals, panels' },
      { name: 'xl', use: 'Dramatic separation - full-screen overlays' },
      { name: '2xl', use: 'Maximum depth' },
    ];

    const backdrops = [
      { name: 'light', value: 'blur(4px)', use: 'Subtle frosted glass' },
      { name: 'heavy', value: 'blur(8px)', use: 'Strong frosted glass' },
    ];

    return (
      <div style={{ maxWidth: '900px' }}>
        <h2 style={sectionTitleStyle}>Shadows & Elevation</h2>

        {/* Shadow Scale */}
        <h3 style={subsectionTitleStyle}>Shadow Scale</h3>
        <div style={{ display: 'flex', gap: 'var(--space-lg)', flexWrap: 'wrap' }}>
          {shadows.map(({ name, use }) => (
            <div
              key={name}
              style={{
                width: '140px',
                padding: 'var(--space-md)',
                background: 'var(--surface-1)',
                borderRadius: 'var(--radius-bare)',
                boxShadow: `var(--shadow-${name})`,
                textAlign: 'center',
              }}
            >
              <code style={{ ...labelStyle, display: 'block' }}>--shadow-{name}</code>
              <span style={{ ...valueStyle, fontSize: 'var(--font-size-xs)' }}>{use}</span>
            </div>
          ))}
        </div>

        {/* Backdrop Blur */}
        <h3 style={subsectionTitleStyle}>Backdrop Blur</h3>
        <div style={{ display: 'flex', gap: 'var(--space-lg)' }}>
          {backdrops.map(({ name, use }) => (
            <div key={name} style={{ position: 'relative', width: '200px', height: '120px' }}>
              {/* Background pattern */}
              <div
                style={{
                  position: 'absolute',
                  inset: 0,
                  background: `
                    linear-gradient(45deg, var(--accent-primary) 25%, transparent 25%),
                    linear-gradient(-45deg, var(--accent-primary) 25%, transparent 25%),
                    linear-gradient(45deg, transparent 75%, var(--accent-primary) 75%),
                    linear-gradient(-45deg, transparent 75%, var(--accent-primary) 75%)
                  `,
                  backgroundSize: '20px 20px',
                  backgroundPosition: '0 0, 0 10px, 10px -10px, -10px 0px',
                  opacity: 0.3,
                  borderRadius: 'var(--radius-bare)',
                }}
              />
              {/* Blur overlay */}
              <div
                style={{
                  position: 'absolute',
                  inset: '20px',
                  backdropFilter: `var(--backdrop-blur-${name})`,
                  background: 'var(--backdrop-overlay-light)',
                  borderRadius: 'var(--radius-bare)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexDirection: 'column',
                }}
              >
                <code style={labelStyle}>--backdrop-blur-{name}</code>
                <span style={valueStyle}>{use}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  },
};

// =============================================================================
// 6. Transition Timing
// =============================================================================

export const TransitionTiming: StoryObj = {
  name: '6. Transition Timing',
  render: () => {
    const durations = [
      { name: 'instant', value: '100ms', use: 'Immediate feedback' },
      { name: 'fast', value: '120ms', use: 'Most interactions' },
      { name: 'normal', value: '200ms', use: 'Smooth changes' },
      { name: 'slow', value: '320ms', use: 'Dramatic effects' },
    ];

    const easings = [
      { name: 'linear', desc: 'Constant speed' },
      { name: 'in', desc: 'Accelerate' },
      { name: 'out', desc: 'Decelerate' },
      { name: 'in-out', desc: 'Smooth both ends' },
      { name: 'out-expo', desc: 'Exponential deceleration' },
      { name: 'spring', desc: 'Bouncy spring (1.56)' },
      { name: 'spring-gentle', desc: 'Subtle spring (1.2)' },
    ];

    const [hoveredDuration, setHoveredDuration] = useState<string | null>(null);

    return (
      <div style={{ maxWidth: '800px' }}>
        <h2 style={sectionTitleStyle}>Transition Timing</h2>
        <p style={annotationStyle}>"Everything Breathes" - Subtle, organic motion</p>

        {/* Duration Scale */}
        <h3 style={subsectionTitleStyle}>Duration Scale</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          {durations.map(({ name, value, use }) => (
            <div
              key={name}
              style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-lg)' }}
              onMouseEnter={() => setHoveredDuration(name)}
              onMouseLeave={() => setHoveredDuration(null)}
            >
              <div
                style={{
                  width: '60px',
                  height: '40px',
                  background: hoveredDuration === name ? 'var(--accent-primary)' : 'var(--surface-2)',
                  borderRadius: 'var(--radius-bare)',
                  transition: `all var(--duration-${name}) var(--ease-out)`,
                  transform: hoveredDuration === name ? 'scale(1.1)' : 'scale(1)',
                }}
              />
              <div style={{ flex: 1 }}>
                <code style={{ ...labelStyle, display: 'block' }}>--duration-{name}</code>
                <span style={valueStyle}>
                  {value} - {use}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Easing Curves */}
        <h3 style={subsectionTitleStyle}>Easing Curves</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 'var(--space-md)' }}>
          {easings.map(({ name, desc }) => (
            <div
              key={name}
              style={{
                padding: 'var(--space-sm)',
                background: 'var(--surface-1)',
                border: '1px solid var(--surface-3)',
                borderRadius: 'var(--radius-bare)',
              }}
            >
              <code style={{ ...labelStyle, display: 'block' }}>--ease-{name}</code>
              <span style={valueStyle}>{desc}</span>
            </div>
          ))}
        </div>

        {/* Composite Transitions */}
        <h3 style={subsectionTitleStyle}>Composite Transitions (Duration + Easing)</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
          <code style={labelStyle}>--transition-instant: var(--duration-instant) var(--ease-out)</code>
          <code style={labelStyle}>--transition-fast: var(--duration-fast) var(--ease-out-expo)</code>
          <code style={labelStyle}>--transition-normal: var(--duration-normal) var(--ease-in-out-cubic)</code>
          <code style={labelStyle}>--transition-slow: var(--duration-slow) var(--ease-spring)</code>
        </div>
      </div>
    );
  },
};

// =============================================================================
// 7. Mode Colors
// =============================================================================

export const ModeColors: StoryObj = {
  name: '7. Mode Colors (Hypergraph Editor)',
  render: () => {
    const [activeMode, setActiveMode] = useState<Mode>('NORMAL');

    return (
      <div style={{ maxWidth: '800px' }}>
        <h2 style={sectionTitleStyle}>Mode Colors</h2>
        <p style={annotationStyle}>
          Six-mode editing system (vim-inspired). Click to preview mode transitions.
        </p>

        {/* Mode Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 'var(--space-md)' }}>
          {ALL_MODES.map((mode) => {
            const def = MODE_DEFINITIONS[mode];
            const color = MODE_COLORS[mode];
            const isActive = activeMode === mode;

            return (
              <div
                key={mode}
                onClick={() => setActiveMode(mode)}
                style={{
                  padding: 'var(--space-md)',
                  background: isActive ? color : 'var(--surface-1)',
                  border: `2px solid ${color}`,
                  borderRadius: 'var(--radius-bare)',
                  cursor: 'pointer',
                  transition: 'all var(--transition-fast)',
                  transform: isActive ? 'scale(1.02)' : 'scale(1)',
                }}
              >
                <div
                  style={{
                    fontSize: 'var(--font-size-lg)',
                    fontWeight: 'var(--font-weight-bold)',
                    color: isActive ? 'var(--surface-0)' : color,
                    marginBottom: 'var(--space-xs)',
                  }}
                >
                  {def.label}
                </div>
                <div
                  style={{
                    fontSize: 'var(--font-size-xs)',
                    color: isActive ? 'var(--surface-0)' : 'var(--text-secondary)',
                    marginBottom: 'var(--space-xs)',
                  }}
                >
                  Trigger: <kbd>{def.trigger}</kbd>
                </div>
                <div
                  style={{
                    fontSize: 'var(--font-size-sm)',
                    color: isActive ? 'var(--surface-0)' : 'var(--text-muted)',
                  }}
                >
                  {def.description}
                </div>
              </div>
            );
          })}
        </div>

        {/* CSS Variables */}
        <h3 style={subsectionTitleStyle}>CSS Variables</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
          <code style={labelStyle}>--status-normal: #4a9eff (Blue)</code>
          <code style={labelStyle}>--status-insert: #4caf50 (Green)</code>
          <code style={labelStyle}>--status-edge: #ff9800 (Orange)</code>
          <code style={labelStyle}>--status-visual: #9c27b0 (Purple)</code>
          <code style={labelStyle}>--status-witness: #e91e63 (Pink)</code>
          <code style={labelStyle}>--status-error: #f44336 (Red)</code>
        </div>
      </div>
    );
  },
};

// =============================================================================
// 8. Breathing Animation
// =============================================================================

export const BreathingAnimation: StoryObj = {
  name: '8. Breathing Animation (4-7-8)',
  render: () => {
    const { style: breathingStyle, isBreathing, pause, resume } = useBreathing({ enabled: true });
    const [showBreathing, setShowBreathing] = useState(true);

    return (
      <div style={{ maxWidth: '800px' }}>
        <h2 style={sectionTitleStyle}>Breathing Animation</h2>
        <p style={annotationStyle}>
          Motion Law M-01: Asymmetric breathing uses 4-7-8 timing (not symmetric).
        </p>

        {/* Timing Explanation */}
        <h3 style={subsectionTitleStyle}>4-7-8 Pattern ({BREATHING_4_7_8.period / 1000}s cycle)</h3>
        <div style={{ display: 'flex', gap: 'var(--space-md)', marginBottom: 'var(--space-lg)' }}>
          <div
            style={{
              flex: 4,
              padding: 'var(--space-md)',
              background: 'var(--color-life-sage)',
              borderRadius: 'var(--radius-bare)',
              textAlign: 'center',
              color: 'var(--surface-0)',
            }}
          >
            <strong>Inhale</strong>
            <br />
            4s (21%)
          </div>
          <div
            style={{
              flex: 7,
              padding: 'var(--space-md)',
              background: 'var(--accent-primary)',
              borderRadius: 'var(--radius-bare)',
              textAlign: 'center',
              color: 'var(--surface-0)',
            }}
          >
            <strong>Hold</strong>
            <br />
            7s (37%)
          </div>
          <div
            style={{
              flex: 8,
              padding: 'var(--space-md)',
              background: 'var(--color-life-moss)',
              borderRadius: 'var(--radius-bare)',
              textAlign: 'center',
              color: 'var(--text-primary)',
            }}
          >
            <strong>Exhale</strong>
            <br />
            8s (42%)
          </div>
        </div>

        {/* Live Demo */}
        <h3 style={subsectionTitleStyle}>Live Demo (useBreathing hook)</h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-lg)' }}>
          <div
            style={{
              ...breathingStyle,
              width: '100px',
              height: '100px',
              borderRadius: '50%',
              background: 'var(--accent-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--surface-0)',
              fontWeight: 'var(--font-weight-bold)',
            }}
          >
            {isBreathing ? 'Live' : 'Paused'}
          </div>
          <div>
            <button
              onClick={() => (isBreathing ? pause() : resume())}
              style={{
                padding: 'var(--space-sm) var(--space-md)',
                background: 'var(--surface-2)',
                border: '1px solid var(--surface-3)',
                borderRadius: 'var(--radius-subtle)',
                color: 'var(--text-primary)',
                cursor: 'pointer',
                marginRight: 'var(--space-sm)',
              }}
            >
              {isBreathing ? 'Pause' : 'Resume'}
            </button>
            <button
              onClick={() => setShowBreathing(!showBreathing)}
              style={{
                padding: 'var(--space-sm) var(--space-md)',
                background: 'var(--surface-2)',
                border: '1px solid var(--surface-3)',
                borderRadius: 'var(--radius-subtle)',
                color: 'var(--text-primary)',
                cursor: 'pointer',
              }}
            >
              {showBreathing ? 'Disable CSS Classes' : 'Enable CSS Classes'}
            </button>
          </div>
        </div>

        {/* CSS Classes */}
        <h3 style={subsectionTitleStyle}>CSS Classes</h3>
        <div style={{ display: 'flex', gap: 'var(--space-lg)', flexWrap: 'wrap' }}>
          {['breathe', 'breathe-subtle', 'breathe-intense'].map((className) => (
            <div
              key={className}
              className={showBreathing ? className : undefined}
              style={{
                width: '80px',
                height: '80px',
                background: 'var(--accent-primary)',
                borderRadius: 'var(--radius-bare)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <code style={{ ...valueStyle, fontSize: 'var(--font-size-xs)' }}>.{className}</code>
            </div>
          ))}
        </div>

        {/* Motion Laws */}
        <h3 style={subsectionTitleStyle}>Motion Laws</h3>
        <ul style={{ color: 'var(--text-secondary)', paddingLeft: 'var(--space-lg)' }}>
          <li>M-01: Asymmetric breathing (4-7-8, not symmetric)</li>
          <li>M-02: Default is still, animation is earned</li>
          <li>M-03: Mechanical precision for structure, organic life for content</li>
          <li>M-04: Respect prefers-reduced-motion</li>
          <li>M-05: Every animation has semantic reason</li>
        </ul>
      </div>
    );
  },
};

// =============================================================================
// 9. Z-Index Scale
// =============================================================================

export const ZIndexScale: StoryObj = {
  name: '9. Z-Index Scale',
  render: () => {
    const layers = [
      { name: 'base', value: 0, color: 'var(--color-steel-700)' },
      { name: 'sticky', value: 100, color: 'var(--color-steel-600)' },
      { name: 'dropdown', value: 200, color: 'var(--color-steel-500)' },
      { name: 'modal', value: 300, color: 'var(--color-steel-400)' },
      { name: 'toast', value: 400, color: 'var(--color-steel-300)' },
      { name: 'tooltip', value: 500, color: 'var(--accent-primary)' },
    ];

    return (
      <div style={{ maxWidth: '800px' }}>
        <h2 style={sectionTitleStyle}>Z-Index Scale</h2>
        <p style={annotationStyle}>"Everything has its place in the stack"</p>

        {/* Layer Visualization */}
        <div style={{ position: 'relative', height: '320px', marginTop: 'var(--space-lg)' }}>
          {layers.map(({ name, value, color }, index) => (
            <div
              key={name}
              style={{
                position: 'absolute',
                left: `${index * 30}px`,
                top: `${index * 40}px`,
                width: '200px',
                padding: 'var(--space-md)',
                background: color,
                border: '1px solid var(--surface-3)',
                borderRadius: 'var(--radius-bare)',
                zIndex: value,
              }}
            >
              <code style={{ ...labelStyle, color: 'var(--text-primary)' }}>--z-{name}</code>
              <span style={{ ...valueStyle, marginLeft: 'var(--space-sm)' }}>{value}</span>
            </div>
          ))}
        </div>

        {/* Usage Guide */}
        <h3 style={subsectionTitleStyle}>Usage Guide</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
          <code style={labelStyle}>--z-base (0): Normal document flow</code>
          <code style={labelStyle}>--z-sticky (100): Sticky headers, sidebars</code>
          <code style={labelStyle}>--z-dropdown (200): Dropdown menus, popovers</code>
          <code style={labelStyle}>--z-modal (300): Modal dialogs</code>
          <code style={labelStyle}>--z-toast (400): Toast notifications</code>
          <code style={labelStyle}>--z-tooltip (500): Tooltips (always on top)</code>
        </div>
      </div>
    );
  },
};

// =============================================================================
// 10. Health & Status Indicators
// =============================================================================

export const HealthIndicators: StoryObj = {
  name: '10. Health & Status Indicators',
  render: () => {
    const health = [
      { name: 'healthy', value: '#22c55e', threshold: '>= 80%' },
      { name: 'degraded', value: '#facc15', threshold: '60-80%' },
      { name: 'warning', value: '#f97316', threshold: '40-60%' },
      { name: 'critical', value: '#ef4444', threshold: '< 40%' },
    ];

    const severity = [
      { name: 'info', value: '#3b82f6' },
      { name: 'warning', value: '#f59e0b' },
      { name: 'critical', value: '#ef4444' },
    ];

    const strength = [
      { name: 'weak', value: '#6b7280' },
      { name: 'moderate', value: '#f59e0b' },
      { name: 'strong', value: '#3b82f6' },
      { name: 'definitive', value: '#22c55e' },
    ];

    return (
      <div style={{ maxWidth: '800px' }}>
        <h2 style={sectionTitleStyle}>Health & Status Indicators</h2>

        {/* Health */}
        <h3 style={subsectionTitleStyle}>Health/Confidence</h3>
        <div style={{ display: 'flex', gap: 'var(--space-md)' }}>
          {health.map(({ name, value, threshold }) => (
            <div key={name} style={{ flex: 1, textAlign: 'center' }}>
              <div
                style={{
                  width: '60px',
                  height: '60px',
                  borderRadius: '50%',
                  background: value,
                  margin: '0 auto var(--space-sm)',
                }}
              />
              <code style={{ ...labelStyle, display: 'block' }}>--health-{name}</code>
              <span style={valueStyle}>{threshold}</span>
            </div>
          ))}
        </div>

        {/* Severity */}
        <h3 style={subsectionTitleStyle}>Severity Levels</h3>
        <div style={{ display: 'flex', gap: 'var(--space-md)' }}>
          {severity.map(({ name, value }) => (
            <div
              key={name}
              style={{
                flex: 1,
                padding: 'var(--space-md)',
                background: value,
                borderRadius: 'var(--radius-bare)',
                textAlign: 'center',
                color: 'var(--surface-0)',
              }}
            >
              <code>--severity-{name}</code>
            </div>
          ))}
        </div>

        {/* Strength */}
        <h3 style={subsectionTitleStyle}>Strength Indicators</h3>
        <div style={{ display: 'flex', gap: 'var(--space-md)' }}>
          {strength.map(({ name, value }) => (
            <div
              key={name}
              style={{
                flex: 1,
                padding: 'var(--space-sm)',
                borderBottom: `4px solid ${value}`,
                background: 'var(--surface-1)',
                textAlign: 'center',
              }}
            >
              <code style={{ ...labelStyle, display: 'block' }}>--strength-{name}</code>
            </div>
          ))}
        </div>
      </div>
    );
  },
};
