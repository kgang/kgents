/**
 * Mode System Stories
 *
 * STARK BIOME: Six-Mode Modal Editing
 *
 * These stories showcase the vim-inspired modal editing system:
 * - ModeIndicator: Visual display of current mode
 * - Mode transitions with keyboard shortcuts
 * - All 6 modes: NORMAL, INSERT, EDGE, VISUAL, COMMAND, WITNESS
 *
 * Philosophy: "The modal interface honors the unix tradition.
 * Each mode is a context. Context reduces cognitive load."
 *
 * @see docs/skills/hypergraph-editor.md - Six-mode modal editing
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState, useCallback, useEffect } from 'react';
import { ModeIndicator, ModeIndicatorProps } from './ModeIndicator';
import { ModeProvider } from '@/context/ModeContext';
import { useMode } from '@/hooks/useMode';
import type { Mode } from '@/types/mode';
import { MODE_DEFINITIONS, MODE_COLORS, ALL_MODES } from '@/types/mode';

// Import component CSS
import './ModeIndicator.css';

// =============================================================================
// Decorators
// =============================================================================

/**
 * ModeProvider decorator for stories that need mode context
 */
const withModeProvider = (initialMode: Mode = 'NORMAL', enableKeyboard = false) => {
  return (Story: React.ComponentType) => (
    <ModeProvider initialMode={initialMode} enableKeyboard={enableKeyboard}>
      <Story />
    </ModeProvider>
  );
};

// =============================================================================
// Meta
// =============================================================================

const meta: Meta<typeof ModeIndicator> = {
  title: 'Mode/ModeIndicator',
  component: ModeIndicator,
  tags: ['autodocs'],
  decorators: [withModeProvider('NORMAL', false)],
  parameters: {
    docs: {
      description: {
        component: `
## Six-Mode Modal Editing

Inspired by vim, the hypergraph editor uses six modes:

| Mode | Trigger | Color | Purpose |
|------|---------|-------|---------|
| **NORMAL** | \`Escape\` | Steel | Navigation, selection, primary mode |
| **INSERT** | \`i\` | Moss | Create new K-Blocks (nodes) |
| **EDGE** | \`e\` | Amber | Create relationships between nodes |
| **VISUAL** | \`v\` | Sage | Multi-select for batch operations |
| **COMMAND** | \`:\` | Rust | Execute slash commands |
| **WITNESS** | \`w\` | Gold | Commit changes with witness marks |

### Vim Philosophy

> "Editing is thinking. Modes are contexts. Context reduces cognitive load."

The modal interface means:
- **NORMAL mode is home** - always return here with Escape
- **Each mode has a single purpose** - no mode does everything
- **Keyboard-driven** - single keys for mode transitions
- **Visual feedback** - the ModeIndicator always shows current state
        `,
      },
    },
    layout: 'centered',
  },
  argTypes: {
    variant: {
      control: 'select',
      options: ['pill', 'badge'],
      description: 'Display variant: pill (fixed overlay) or badge (inline)',
    },
    showHint: {
      control: 'boolean',
      description: 'Show keyboard hint (Esc to exit)',
    },
    position: {
      control: 'select',
      options: ['bottom-left', 'bottom-right', 'top-left', 'top-right'],
    },
    compact: {
      control: 'boolean',
      description: 'Compact mode (smaller, no description)',
    },
  },
};

export default meta;

type Story = StoryObj<typeof ModeIndicator>;

// =============================================================================
// Basic Stories
// =============================================================================

export const Default: Story = {
  name: 'Default (NORMAL mode)',
  args: {
    variant: 'pill',
    showHint: true,
    position: 'bottom-left',
    compact: false,
  },
};

export const Compact: Story = {
  name: 'Compact Variant',
  args: {
    variant: 'pill',
    showHint: true,
    position: 'bottom-left',
    compact: true,
  },
};

export const Badge: Story = {
  name: 'Badge Variant',
  args: {
    variant: 'badge',
  },
};

export const BadgeAllModes: Story = {
  name: 'Badge - All 6 Modes',
  render: () => (
    <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
      {(['NORMAL', 'INSERT', 'EDGE', 'VISUAL', 'COMMAND', 'WITNESS'] as Mode[]).map((mode) => (
        <ModeProvider key={mode} initialMode={mode}>
          <ModeIndicator variant="badge" />
        </ModeProvider>
      ))}
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: `
All six modes rendered as inline badges. Perfect for compact UI contexts
like footers, status bars, or inline in text.
        `,
      },
    },
  },
};

export const BadgeInContext: Story = {
  name: 'Badge - In Context (Footer Example)',
  render: () => (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        padding: '0.5rem 1rem',
        background: '#1a1a2e',
        borderRadius: '4px',
        color: '#888',
        fontSize: '0.75rem',
      }}
    >
      <span>3 events</span>
      <span>•</span>
      <span>Last sync: 2s ago</span>
      <div style={{ marginLeft: 'auto' }}>
        <ModeIndicator variant="badge" />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: `
Badge variant in a realistic footer context. The badge adapts to inline
layouts and integrates seamlessly with other status information.
        `,
      },
    },
  },
};

export const VariantComparison: Story = {
  name: 'Pill vs Badge Comparison',
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div>
        <h4 style={{ color: '#888', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
          Pill Variant (fixed position disabled for demo)
        </h4>
        <div style={{ position: 'relative', height: '80px', background: '#1a1a2e', borderRadius: '8px' }}>
          <ModeIndicator variant="pill" position="bottom-left" />
        </div>
      </div>
      <div>
        <h4 style={{ color: '#888', marginBottom: '0.5rem', fontSize: '0.875rem' }}>Badge Variant (inline)</h4>
        <ModeIndicator variant="badge" />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: `
Side-by-side comparison of the two ModeIndicator variants:

**Pill**: Fixed-position overlay (default for hypergraph editor)
**Badge**: Inline component (for footers, status bars, toolbars)
        `,
      },
    },
  },
};

// =============================================================================
// All Modes Display
// =============================================================================

/**
 * Helper component to display mode indicator in a specific mode
 */
function ModeDisplay({ mode, compact = false }: { mode: Mode; compact?: boolean }) {
  const definition = MODE_DEFINITIONS[mode];
  const color = MODE_COLORS[mode];

  return (
    <div style={{ textAlign: 'center', minWidth: '140px' }}>
      {/* Static mode indicator (not using context, just visual) */}
      <div
        style={{
          display: 'flex',
          flexDirection: compact ? 'row' : 'column',
          gap: compact ? '0.5rem' : '0.25rem',
          padding: compact ? '0.375rem 0.625rem' : '0.5rem 0.75rem',
          background: color,
          color: 'white',
          borderRadius: '9999px',
          boxShadow: `0 2px 8px rgba(0, 0, 0, 0.2), 0 0 12px ${color}`,
          fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
          fontSize: '0.75rem',
          lineHeight: 1.2,
          alignItems: compact ? 'center' : 'flex-start',
        }}
      >
        <div style={{ fontWeight: 700, fontSize: '0.875rem', letterSpacing: '0.05em' }}>
          {definition.label}
        </div>
        {!compact && (
          <div style={{ fontSize: '0.6875rem', opacity: 0.9 }}>
            {definition.description}
          </div>
        )}
      </div>
      {/* Trigger key */}
      <p style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: '#8A8A94' }}>
        <kbd
          style={{
            display: 'inline-block',
            padding: '0.125rem 0.375rem',
            background: 'rgba(255, 255, 255, 0.1)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '0.25rem',
            fontFamily: 'inherit',
          }}
        >
          {definition.trigger}
        </kbd>
      </p>
    </div>
  );
}

export const AllModes: StoryObj = {
  name: 'All 6 Modes',
  render: () => (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '2rem',
        padding: '2rem',
      }}
    >
      {ALL_MODES.map((mode) => (
        <ModeDisplay key={mode} mode={mode} />
      ))}
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: `
All six modes with their trigger keys and descriptions.

**Color Palette (Living Earth):**
- NORMAL: Steel (#475569) - Cool, neutral, home base
- INSERT: Moss (#2E4A2E) - Creation, growth
- EDGE: Amber (#D4A574) - Connection, relationship
- VISUAL: Sage (#4A6B4A) - Selection, attention
- COMMAND: Rust (#8B5A2B) - Authority, execution
- WITNESS: Gold (#E8C4A0) - Commitment, truth
        `,
      },
    },
  },
};

export const AllModesCompact: StoryObj = {
  name: 'All 6 Modes (Compact)',
  render: () => (
    <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', padding: '1rem' }}>
      {ALL_MODES.map((mode) => (
        <ModeDisplay key={mode} mode={mode} compact />
      ))}
    </div>
  ),
};

// =============================================================================
// Position Variants
// =============================================================================

export const Positions: StoryObj = {
  name: 'Position Variants',
  render: () => (
    <div
      style={{
        position: 'relative',
        width: '400px',
        height: '300px',
        background: '#141418',
        borderRadius: '8px',
        border: '1px solid #28282F',
      }}
    >
      <ModeProvider initialMode="NORMAL">
        <div
          style={{
            position: 'absolute',
            bottom: '1rem',
            left: '1rem',
          }}
        >
          <ModeIndicatorStatic position="bottom-left" />
        </div>
      </ModeProvider>
      <ModeProvider initialMode="INSERT">
        <div
          style={{
            position: 'absolute',
            bottom: '1rem',
            right: '1rem',
          }}
        >
          <ModeIndicatorStatic position="bottom-right" />
        </div>
      </ModeProvider>
      <ModeProvider initialMode="EDGE">
        <div
          style={{
            position: 'absolute',
            top: '1rem',
            left: '1rem',
          }}
        >
          <ModeIndicatorStatic position="top-left" />
        </div>
      </ModeProvider>
      <ModeProvider initialMode="VISUAL">
        <div
          style={{
            position: 'absolute',
            top: '1rem',
            right: '1rem',
          }}
        >
          <ModeIndicatorStatic position="top-right" />
        </div>
      </ModeProvider>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Mode indicators can be positioned in any corner of the viewport.',
      },
    },
  },
};

/**
 * Non-fixed position indicator for position demo
 */
function ModeIndicatorStatic({ position }: { position: ModeIndicatorProps['position'] }) {
  const { label, description, color } = useMode();

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '0.25rem',
        padding: '0.5rem 0.75rem',
        background: color,
        color: 'white',
        borderRadius: '9999px',
        boxShadow: `0 2px 8px rgba(0, 0, 0, 0.2), 0 0 12px ${color}`,
        fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
        fontSize: '0.75rem',
      }}
      data-position={position}
    >
      <div style={{ fontWeight: 700, fontSize: '0.875rem', letterSpacing: '0.05em' }}>
        {label}
      </div>
      <div style={{ fontSize: '0.6875rem', opacity: 0.9 }}>{description}</div>
    </div>
  );
}

// =============================================================================
// Interactive Mode Switching
// =============================================================================

/**
 * Interactive mode switcher component
 */
function InteractiveModeDemo() {
  const {
    mode,
    toNormal,
    toInsert,
    toEdge,
    toVisual,
    toCommand,
    toWitness,
    history,
  } = useMode();

  const transitions = [
    { label: 'NORMAL', key: 'Esc', action: toNormal, mode: 'NORMAL' as Mode },
    { label: 'INSERT', key: 'i', action: toInsert, mode: 'INSERT' as Mode },
    { label: 'EDGE', key: 'e', action: toEdge, mode: 'EDGE' as Mode },
    { label: 'VISUAL', key: 'v', action: toVisual, mode: 'VISUAL' as Mode },
    { label: 'COMMAND', key: ':', action: toCommand, mode: 'COMMAND' as Mode },
    { label: 'WITNESS', key: 'w', action: toWitness, mode: 'WITNESS' as Mode },
  ];

  return (
    <div style={{ display: 'flex', gap: '2rem', alignItems: 'flex-start' }}>
      {/* Mode buttons */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <p style={{ fontSize: '0.875rem', color: '#8A8A94', marginBottom: '0.5rem' }}>
          Click to switch modes:
        </p>
        {transitions.map(({ label, key, action, mode: targetMode }) => (
          <button
            key={label}
            onClick={action}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '1rem',
              padding: '0.5rem 1rem',
              background: mode === targetMode ? MODE_COLORS[targetMode] : '#28282F',
              color: mode === targetMode ? 'white' : '#E5E7EB',
              border: 'none',
              borderRadius: '0.375rem',
              cursor: 'pointer',
              fontFamily: 'inherit',
              fontSize: '0.875rem',
              transition: 'all 150ms ease',
              minWidth: '140px',
            }}
          >
            <span>{label}</span>
            <kbd
              style={{
                padding: '0.125rem 0.375rem',
                background: 'rgba(0, 0, 0, 0.2)',
                borderRadius: '0.25rem',
                fontSize: '0.75rem',
                fontFamily: 'ui-monospace, monospace',
              }}
            >
              {key}
            </kbd>
          </button>
        ))}
      </div>

      {/* Current indicator */}
      <div style={{ position: 'relative', width: '200px', height: '200px' }}>
        <ModeIndicator showHint />
      </div>

      {/* History */}
      <div style={{ minWidth: '180px' }}>
        <p style={{ fontSize: '0.875rem', color: '#8A8A94', marginBottom: '0.5rem' }}>
          Transition history:
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          {history.slice(0, 5).map((t, i) => (
            <div
              key={i}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                fontSize: '0.75rem',
                color: '#8A8A94',
              }}
            >
              <span style={{ color: MODE_COLORS[t.from] }}>{t.from}</span>
              <span>{'->'}</span>
              <span style={{ color: MODE_COLORS[t.to] }}>{t.to}</span>
            </div>
          ))}
          {history.length === 0 && (
            <p style={{ fontSize: '0.75rem', color: '#5A5A64', fontStyle: 'italic' }}>
              No transitions yet
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export const Interactive: StoryObj = {
  name: 'Interactive Mode Switching',
  decorators: [withModeProvider('NORMAL', false)],
  render: () => <InteractiveModeDemo />,
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        story: `
Click buttons to switch between modes. The indicator updates in real-time
with smooth color transitions. History shows recent mode changes.

**Try it:** Click different modes and watch the indicator animate.
        `,
      },
    },
  },
};

// =============================================================================
// Keyboard Navigation Demo
// =============================================================================

function KeyboardDemo() {
  const { mode, label, color, history } = useMode();
  const [lastKey, setLastKey] = useState<string | null>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      setLastKey(e.key);
      setTimeout(() => setLastKey(null), 500);
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '2rem',
        padding: '2rem',
      }}
    >
      {/* Instructions */}
      <div
        style={{
          padding: '1rem 2rem',
          background: '#1C1C22',
          borderRadius: '0.5rem',
          border: '1px solid #28282F',
          textAlign: 'center',
        }}
      >
        <p style={{ fontSize: '0.875rem', color: '#E5E7EB', marginBottom: '0.5rem' }}>
          Press keyboard shortcuts to switch modes
        </p>
        <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center' }}>
          {['i', 'e', 'v', ':', 'w', 'Esc'].map((key) => (
            <kbd
              key={key}
              style={{
                padding: '0.25rem 0.5rem',
                background: lastKey === key ? MODE_COLORS[mode] : '#28282F',
                border: '1px solid #3A3A42',
                borderRadius: '0.25rem',
                color: lastKey === key ? 'white' : '#8A8A94',
                fontSize: '0.875rem',
                fontFamily: 'ui-monospace, monospace',
                transition: 'all 150ms ease',
              }}
            >
              {key}
            </kbd>
          ))}
        </div>
      </div>

      {/* Large mode display */}
      <div
        style={{
          width: '200px',
          height: '200px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          background: color,
          borderRadius: '1rem',
          boxShadow: `0 4px 24px ${color}`,
          transition: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
        }}
      >
        <span
          style={{
            fontSize: '2rem',
            fontWeight: 700,
            color: 'white',
            letterSpacing: '0.1em',
          }}
        >
          {label}
        </span>
      </div>

      {/* Last transition */}
      {history.length > 0 && (
        <p style={{ fontSize: '0.75rem', color: '#8A8A94' }}>
          Last: {history[0].from} {'->'} {history[0].to}
          {history[0].reason && ` (${history[0].reason})`}
        </p>
      )}
    </div>
  );
}

export const KeyboardNavigation: StoryObj = {
  name: 'Keyboard Navigation (Interactive)',
  decorators: [withModeProvider('NORMAL', true)],
  render: () => <KeyboardDemo />,
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        story: `
**Focus this story and press keys:**
- \`i\` - INSERT mode (create K-Blocks)
- \`e\` - EDGE mode (create relationships)
- \`v\` - VISUAL mode (multi-select)
- \`:\` - COMMAND mode (slash commands)
- \`w\` - WITNESS mode (commit changes)
- \`Escape\` - Return to NORMAL

The large indicator shows current mode with animated transitions.
        `,
      },
    },
  },
};

// =============================================================================
// Mode Properties
// =============================================================================

export const ModeProperties: StoryObj = {
  name: 'Mode Properties Reference',
  render: () => (
    <div
      style={{
        padding: '1.5rem',
        background: '#141418',
        borderRadius: '0.5rem',
        border: '1px solid #28282F',
        maxWidth: '600px',
      }}
    >
      <h3
        style={{
          fontSize: '1rem',
          fontWeight: 600,
          color: '#E5E7EB',
          marginBottom: '1rem',
        }}
      >
        Mode Properties
      </h3>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={thStyle}>Mode</th>
            <th style={thStyle}>Captures Input</th>
            <th style={thStyle}>Blocks Nav</th>
            <th style={thStyle}>Color</th>
          </tr>
        </thead>
        <tbody>
          {ALL_MODES.map((mode) => {
            const def = MODE_DEFINITIONS[mode];
            return (
              <tr key={mode}>
                <td style={tdStyle}>
                  <span style={{ color: MODE_COLORS[mode], fontWeight: 600 }}>
                    {mode}
                  </span>
                </td>
                <td style={tdStyle}>{def.capturesInput ? 'Yes' : '-'}</td>
                <td style={tdStyle}>{def.blocksNavigation ? 'Yes' : '-'}</td>
                <td style={tdStyle}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <div
                      style={{
                        width: '16px',
                        height: '16px',
                        borderRadius: '4px',
                        background: MODE_COLORS[mode],
                      }}
                    />
                    <code style={{ fontSize: '0.75rem', color: '#8A8A94' }}>
                      {def.colorKey}
                    </code>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <div style={{ marginTop: '1rem', fontSize: '0.75rem', color: '#5A5A64' }}>
        <p>
          <strong>Captures Input:</strong> Mode intercepts all keyboard input
        </p>
        <p>
          <strong>Blocks Nav:</strong> Mode prevents hypergraph navigation
        </p>
      </div>
    </div>
  ),
};

const thStyle: React.CSSProperties = {
  textAlign: 'left',
  padding: '0.5rem',
  borderBottom: '1px solid #28282F',
  fontSize: '0.75rem',
  color: '#8A8A94',
  fontWeight: 500,
};

const tdStyle: React.CSSProperties = {
  padding: '0.5rem',
  borderBottom: '1px solid #1C1C22',
  fontSize: '0.875rem',
  color: '#E5E7EB',
};

// =============================================================================
// Transition Animation
// =============================================================================

function TransitionAnimationDemo() {
  const [currentMode, setCurrentMode] = useState<Mode>('NORMAL');
  const [isTransitioning, setIsTransitioning] = useState(false);

  const triggerTransition = useCallback((to: Mode) => {
    setIsTransitioning(true);
    setTimeout(() => {
      setCurrentMode(to);
      setIsTransitioning(false);
    }, 150);
  }, []);

  const color = MODE_COLORS[currentMode];
  const def = MODE_DEFINITIONS[currentMode];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2rem' }}>
      {/* Mode selector */}
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        {ALL_MODES.map((mode) => (
          <button
            key={mode}
            onClick={() => triggerTransition(mode)}
            style={{
              padding: '0.5rem 1rem',
              background: currentMode === mode ? MODE_COLORS[mode] : '#28282F',
              color: 'white',
              border: 'none',
              borderRadius: '0.375rem',
              cursor: 'pointer',
              fontSize: '0.75rem',
              fontWeight: 600,
              transition: 'all 150ms ease',
            }}
          >
            {mode}
          </button>
        ))}
      </div>

      {/* Animated indicator */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '0.25rem',
          padding: '0.75rem 1.25rem',
          background: color,
          color: 'white',
          borderRadius: '9999px',
          boxShadow: `0 2px 8px rgba(0, 0, 0, 0.2), 0 0 16px ${color}`,
          fontFamily: 'ui-monospace, monospace',
          transform: isTransitioning ? 'scale(1.05)' : 'scale(1)',
          opacity: isTransitioning ? 0.8 : 1,
          transition: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
        }}
      >
        <div style={{ fontWeight: 700, fontSize: '1rem', letterSpacing: '0.05em' }}>
          {def.label}
        </div>
        <div style={{ fontSize: '0.75rem', opacity: 0.9 }}>{def.description}</div>
      </div>

      <p style={{ fontSize: '0.75rem', color: '#8A8A94' }}>
        Click modes to see transition animation (300ms ease-out)
      </p>
    </div>
  );
}

export const TransitionAnimation: StoryObj = {
  name: 'Transition Animation',
  render: () => <TransitionAnimationDemo />,
  parameters: {
    docs: {
      description: {
        story: `
Mode transitions use a 300ms cubic-bezier ease for smooth animation.
The indicator pulses slightly on mode change for visual feedback.

Animation properties:
- Color transition: 300ms
- Box-shadow glow: 300ms (matches mode color)
- Scale pulse: 1.0 -> 1.05 -> 1.0
        `,
      },
    },
  },
};

// =============================================================================
// Philosophy Story
// =============================================================================

export const VimPhilosophy: StoryObj = {
  name: 'The Vim Philosophy',
  render: () => (
    <div
      style={{
        padding: '2rem',
        background: '#141418',
        borderRadius: '0.5rem',
        border: '1px solid #28282F',
        maxWidth: '600px',
      }}
    >
      <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#E5E7EB', marginBottom: '1.5rem' }}>
        Why Modal Editing?
      </h2>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {[
          {
            title: 'Context is Power',
            description:
              'Each mode has a single purpose. NORMAL for navigation, INSERT for creation, EDGE for relationships. No mode tries to do everything.',
            icon: '🎯',
          },
          {
            title: 'Keyboard-First',
            description:
              'Single-key transitions: i, e, v, :, w. Your hands never leave the keyboard. Escape is always home.',
            icon: '⌨️',
          },
          {
            title: 'Muscle Memory',
            description:
              'After learning, mode switching becomes unconscious. The interface disappears; only the thought remains.',
            icon: '🧠',
          },
          {
            title: 'Composability',
            description:
              'Modes compose with operations. VISUAL + delete = multi-delete. EDGE + select = relationship. Grammar emerges.',
            icon: '🔗',
          },
        ].map(({ title, description, icon }) => (
          <div key={title} style={{ display: 'flex', gap: '1rem' }}>
            <span style={{ fontSize: '1.5rem' }}>{icon}</span>
            <div>
              <h3 style={{ fontSize: '0.875rem', fontWeight: 600, color: '#E5E7EB', marginBottom: '0.25rem' }}>
                {title}
              </h3>
              <p style={{ fontSize: '0.8125rem', color: '#8A8A94', lineHeight: 1.5 }}>
                {description}
              </p>
            </div>
          </div>
        ))}
      </div>

      <blockquote
        style={{
          marginTop: '1.5rem',
          padding: '1rem',
          borderLeft: '3px solid #4A6B4A',
          background: 'rgba(74, 107, 74, 0.1)',
          borderRadius: '0 0.25rem 0.25rem 0',
        }}
      >
        <p style={{ fontSize: '0.875rem', color: '#E5E7EB', fontStyle: 'italic', margin: 0 }}>
          "Editing is thinking. Modes are contexts. Context reduces cognitive load."
        </p>
        <footer style={{ fontSize: '0.75rem', color: '#8A8A94', marginTop: '0.5rem' }}>
          — The kgents philosophy
        </footer>
      </blockquote>
    </div>
  ),
  parameters: {
    layout: 'centered',
  },
};
