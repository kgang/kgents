/**
 * Editor Stories
 *
 * STARK BIOME: MarkdownEditor with CodeMirror 6
 *
 * These stories showcase the markdown editing experience:
 * - MarkdownEditor: STARK BIOME-themed CodeMirror wrapper
 * - Ghost text completions (AGENTESE paths)
 * - Vim-like mode switching (readonly ↔ editable)
 * - Scroll navigation in NORMAL mode
 *
 * Philosophy: "The AI isn't a separate entity you talk to.
 * The AI is in your fingers—completing your thoughts before you finish thinking them."
 *
 * @see docs/skills/hypergraph-editor.md - Editor integration
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState, useRef, useCallback } from 'react';
import { MarkdownEditor, MarkdownEditorRef } from './MarkdownEditor';
import { AGENTESE_PATHS, matchAgentesePath } from './agentesePaths';

// Import component CSS
import './MarkdownEditor.css';
import './ghostText.css';

// =============================================================================
// Sample Content
// =============================================================================

const SAMPLE_MARKDOWN = `# K-Block: Witness Protocol

The witness protocol ensures all decisions leave traces.

## Core Concepts

- **Marks**: Immutable witnesses of actions
- **Crystals**: Compressed memory bundles
- **Trails**: Temporal sequences of marks

## AGENTESE Paths

Try typing these paths:
- \`self.brain.capture\` - Capture to brain
- \`world.entity.create\` - Create entity
- \`concept.categorical.probe\` - Probe laws

> "The proof IS the decision. The mark IS the witness."

## Code Example

\`\`\`python
mark = await witness.mark(
    action="decide",
    content={"choice": "SSE over WebSockets"},
    reasoning="Simpler ops, sufficient for unidirectional"
)
\`\`\`
`;

const SHORT_SAMPLE = `# Quick Note

This is a short markdown document for testing.

- Item one
- Item two
- Item three
`;

const AGENTESE_SAMPLE = `# AGENTESE Paths Demo

Type a path prefix and watch ghost text appear:

world.
self.
concept.
void.
time.

The AI suggests, never demands.
`;

// =============================================================================
// Decorators
// =============================================================================

const withDarkBackground = (Story: React.ComponentType) => (
  <div
    style={{
      padding: '2rem',
      background: '#0A0A0C',
      minHeight: '400px',
    }}
  >
    <Story />
  </div>
);

// =============================================================================
// Meta
// =============================================================================

const meta: Meta<typeof MarkdownEditor> = {
  title: 'Editor/MarkdownEditor',
  component: MarkdownEditor,
  tags: ['autodocs'],
  decorators: [withDarkBackground],
  parameters: {
    docs: {
      description: {
        component: `
## MarkdownEditor

A STARK BIOME-themed markdown editor built on CodeMirror 6.

### Features

| Feature | Description |
|---------|-------------|
| **Syntax Highlighting** | Markdown-aware with STARK BIOME colors |
| **Dynamic Readonly** | Switch NORMAL ↔ INSERT without remount |
| **Ghost Text** | AGENTESE path completions inline |
| **Scroll Navigation** | j/k/{/}/gg/G for keyboard reading |

### Mode Integration

The editor supports vim-like mode switching:
- **NORMAL mode**: \`readonly=true\`, keyboard scrolling
- **INSERT mode**: \`readonly=false\`, full editing
- Press \`i\` to enter INSERT, \`Escape\` to return to NORMAL

### Ghost Text Philosophy

> "The AI isn't a separate entity you talk to.
> The AI is in your fingers—completing your thoughts before you finish thinking them."

Ghost text appears at 40% opacity after 200ms pause.
Press \`Tab\` to accept, \`Escape\` to dismiss.
        `,
      },
    },
    layout: 'padded',
  },
  argTypes: {
    value: { control: 'text' },
    readonly: { control: 'boolean' },
    placeholder: { control: 'text' },
    autoFocus: { control: 'boolean' },
    enableGhostText: { control: 'boolean' },
    minHeight: { control: 'text' },
    maxHeight: { control: 'text' },
    fillHeight: { control: 'boolean' },
  },
};

export default meta;

type Story = StoryObj<typeof MarkdownEditor>;

// =============================================================================
// Basic Stories
// =============================================================================

export const Default: Story = {
  name: 'Default Editor',
  args: {
    value: SAMPLE_MARKDOWN,
    placeholder: 'Start typing...',
    minHeight: '300px',
    maxHeight: '500px',
  },
};

export const Empty: Story = {
  name: 'Empty with Placeholder',
  args: {
    value: '',
    placeholder: 'Start writing your K-Block here...',
    minHeight: '200px',
  },
};

export const Readonly: Story = {
  name: 'Readonly Mode (NORMAL)',
  args: {
    value: SAMPLE_MARKDOWN,
    readonly: true,
    minHeight: '300px',
    maxHeight: '500px',
  },
  parameters: {
    docs: {
      description: {
        story: `
In readonly mode (NORMAL), the editor displays content but doesn't allow editing.
This is the default state in the hypergraph editor.

The editor has slightly reduced opacity and a darker background to indicate readonly state.
        `,
      },
    },
  },
};


// =============================================================================
// Interactive Mode Switching
// =============================================================================

function ModeSwitchingDemo() {
  const [content, setContent] = useState(SHORT_SAMPLE);
  const [readonly, setReadonly] = useState(true);
  const editorRef = useRef<MarkdownEditorRef>(null);

  const toggleMode = useCallback(() => {
    setReadonly((prev) => !prev);
    if (readonly && editorRef.current) {
      // Switching to editable - focus after a brief delay
      setTimeout(() => editorRef.current?.focus(), 50);
    }
  }, [readonly]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {/* Mode indicator */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <button
          onClick={toggleMode}
          style={{
            padding: '0.5rem 1rem',
            background: readonly ? '#475569' : '#2E4A2E',
            color: 'white',
            border: 'none',
            borderRadius: '0.375rem',
            cursor: 'pointer',
            fontFamily: 'ui-monospace, monospace',
            fontSize: '0.875rem',
            fontWeight: 600,
            transition: 'all 150ms ease',
          }}
        >
          {readonly ? 'NORMAL' : 'INSERT'} mode
        </button>
        <span style={{ fontSize: '0.875rem', color: '#8A8A94' }}>
          Press <kbd style={kbdStyle}>{readonly ? 'i' : 'Esc'}</kbd> to{' '}
          {readonly ? 'edit' : 'exit'}
        </span>
      </div>

      {/* Editor */}
      <MarkdownEditor
        ref={editorRef}
        value={content}
        onChange={setContent}
        readonly={readonly}
        minHeight="250px"
        maxHeight="400px"
      />

      {/* Status */}
      <div style={{ fontSize: '0.75rem', color: '#5A5A64' }}>
        Content length: {content.length} characters
      </div>
    </div>
  );
}

const kbdStyle: React.CSSProperties = {
  display: 'inline-block',
  padding: '0.125rem 0.375rem',
  background: 'rgba(255, 255, 255, 0.1)',
  border: '1px solid rgba(255, 255, 255, 0.2)',
  borderRadius: '0.25rem',
  fontFamily: 'ui-monospace, monospace',
  fontSize: '0.75rem',
};

export const ModeSwitching: StoryObj = {
  name: 'Mode Switching (NORMAL ↔ INSERT)',
  render: () => <ModeSwitchingDemo />,
  parameters: {
    docs: {
      description: {
        story: `
Click the mode button to toggle between NORMAL (readonly) and INSERT (editable).

This demonstrates the dynamic readonly switching via CodeMirror Compartments.
The editor reconfigures without remounting, preserving scroll position and state.
        `,
      },
    },
  },
};

// =============================================================================
// Ghost Text Demo
// =============================================================================

function GhostTextDemo() {
  const [content, setContent] = useState(AGENTESE_SAMPLE);
  const [lastCompletion, setLastCompletion] = useState<string | null>(null);

  // Track what the user is typing
  const handleChange = useCallback((newValue: string) => {
    setContent(newValue);

    // Check if user just typed an AGENTESE path prefix
    const lines = newValue.split('\n');
    const lastLine = lines[lines.length - 1] || '';
    const match = lastLine.match(/[\w.]+$/);
    if (match) {
      const matches = matchAgentesePath(match[0]);
      if (matches.length > 0) {
        setLastCompletion(matches[0]);
      } else {
        setLastCompletion(null);
      }
    }
  }, []);

  return (
    <div style={{ display: 'flex', gap: '2rem' }}>
      {/* Editor */}
      <div style={{ flex: 1 }}>
        <MarkdownEditor
          value={content}
          onChange={handleChange}
          enableGhostText
          placeholder="Type an AGENTESE path prefix (e.g., 'world.')"
          minHeight="300px"
        />
        <p style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: '#5A5A64' }}>
          Ghost text enabled. Type a path prefix and pause for 200ms.
        </p>
      </div>

      {/* Path reference */}
      <div
        style={{
          width: '200px',
          padding: '1rem',
          background: '#141418',
          borderRadius: '0.5rem',
          border: '1px solid #28282F',
        }}
      >
        <h4 style={{ fontSize: '0.75rem', color: '#8A8A94', marginBottom: '0.5rem' }}>
          AGENTESE Contexts
        </h4>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          {['world.*', 'self.*', 'concept.*', 'void.*', 'time.*'].map((ctx) => (
            <code
              key={ctx}
              style={{
                fontSize: '0.75rem',
                color: '#4A6B4A',
                fontFamily: 'ui-monospace, monospace',
              }}
            >
              {ctx}
            </code>
          ))}
        </div>

        {lastCompletion && (
          <div style={{ marginTop: '1rem' }}>
            <h4 style={{ fontSize: '0.75rem', color: '#8A8A94', marginBottom: '0.25rem' }}>
              Suggested:
            </h4>
            <code
              style={{
                fontSize: '0.75rem',
                color: '#C4A77D',
                fontFamily: 'ui-monospace, monospace',
              }}
            >
              {lastCompletion}
            </code>
          </div>
        )}
      </div>
    </div>
  );
}

export const GhostText: StoryObj = {
  name: 'Ghost Text Completions',
  render: () => <GhostTextDemo />,
  parameters: {
    docs: {
      description: {
        story: `
Ghost text provides inline AGENTESE path completions.

**How it works:**
1. Type a path prefix (e.g., \`self.brain.\`)
2. After 200ms pause, ghost text appears at 40% opacity
3. Press \`Tab\` to accept the completion
4. Press \`Escape\` to dismiss

**Sources (prioritized):**
1. AGENTESE paths (highest priority)
2. Spec vocabulary (future)
3. Recent marks (future)

> "The AI is in your fingers—completing your thoughts before you finish thinking them."
        `,
      },
    },
  },
};

// =============================================================================
// Scroll Navigation Demo
// =============================================================================

const LONG_CONTENT = `# Scroll Navigation Demo

This is a long document to demonstrate keyboard scrolling in NORMAL mode.

## Section 1: Introduction

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.

## Section 2: Core Concepts

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident.

## Section 3: Implementation

Sunt in culpa qui officia deserunt mollit anim id est laborum. Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium.

## Section 4: Testing

Totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.

## Section 5: Deployment

Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.

## Section 6: Monitoring

Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem.

## Conclusion

At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident.
`;

function ScrollNavigationDemo() {
  const editorRef = useRef<MarkdownEditorRef>(null);
  const [lastAction, setLastAction] = useState<string>('');

  const handleScroll = useCallback((action: string, fn: () => void) => {
    fn();
    setLastAction(action);
    setTimeout(() => setLastAction(''), 500);
  }, []);

  const scrollControls = [
    { key: 'j', label: 'Line Down', action: () => editorRef.current?.scrollLines(1) },
    { key: 'k', label: 'Line Up', action: () => editorRef.current?.scrollLines(-1) },
    { key: '}', label: 'Para Down', action: () => editorRef.current?.scrollParagraph(1) },
    { key: '{', label: 'Para Up', action: () => editorRef.current?.scrollParagraph(-1) },
    { key: 'gg', label: 'Top', action: () => editorRef.current?.scrollToTop() },
    { key: 'G', label: 'Bottom', action: () => editorRef.current?.scrollToBottom() },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {/* Controls */}
      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
        {scrollControls.map(({ key, label, action }) => (
          <button
            key={key}
            onClick={() => handleScroll(label, action)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.375rem 0.75rem',
              background: lastAction === label ? '#4A6B4A' : '#28282F',
              color: 'white',
              border: 'none',
              borderRadius: '0.375rem',
              cursor: 'pointer',
              fontSize: '0.75rem',
              transition: 'all 150ms ease',
            }}
          >
            <kbd
              style={{
                padding: '0.125rem 0.25rem',
                background: 'rgba(0, 0, 0, 0.2)',
                borderRadius: '0.25rem',
                fontFamily: 'ui-monospace, monospace',
              }}
            >
              {key}
            </kbd>
            <span>{label}</span>
          </button>
        ))}
      </div>

      {/* Editor */}
      <MarkdownEditor
        ref={editorRef}
        value={LONG_CONTENT}
        readonly
        minHeight="250px"
        maxHeight="250px"
      />

      {/* Note */}
      <p style={{ fontSize: '0.75rem', color: '#5A5A64' }}>
        In NORMAL mode, use keyboard shortcuts for reading navigation.
        The scroll cursor (horizontal line) appears during scroll.
      </p>
    </div>
  );
}

export const ScrollNavigation: StoryObj = {
  name: 'Scroll Navigation (NORMAL mode)',
  render: () => <ScrollNavigationDemo />,
  parameters: {
    docs: {
      description: {
        story: `
In NORMAL mode (readonly), keyboard shortcuts enable reading navigation:

| Key | Action |
|-----|--------|
| \`j\` | Scroll down one line |
| \`k\` | Scroll up one line |
| \`}\` | Jump to next paragraph |
| \`{\` | Jump to previous paragraph |
| \`gg\` | Jump to top |
| \`G\` | Jump to bottom |

A horizontal scroll cursor appears briefly during keyboard scrolling
to show the current reading position.
        `,
      },
    },
  },
};

// =============================================================================
// Syntax Highlighting Demo
// =============================================================================

const CODE_HEAVY_MARKDOWN = `# Syntax Highlighting Demo

## Inline Elements

Here is some **bold text** and *italic text* and \`inline code\`.

## Code Blocks

### Python

\`\`\`python
async def witness_mark(action: str, content: dict) -> Mark:
    """Create a witness mark for an action."""
    mark = Mark(
        id=generate_id(),
        action=action,
        content=content,
        timestamp=datetime.now(),
    )
    await store.save(mark)
    return mark
\`\`\`

### TypeScript

\`\`\`typescript
interface KBlock {
  id: string;
  content: string;
  metadata: Record<string, unknown>;
  edges: Edge[];
}
\`\`\`

## Lists

- First item
- Second item
  - Nested item
  - Another nested
- Third item

## Links and Images

[AGENTESE Protocol](https://example.com/agentese)

## Blockquotes

> The proof IS the decision.
> The mark IS the witness.
`;

export const SyntaxHighlighting: StoryObj = {
  name: 'Syntax Highlighting',
  args: {
    value: CODE_HEAVY_MARKDOWN,
    minHeight: '400px',
    maxHeight: '500px',
  },
  parameters: {
    docs: {
      description: {
        story: `
The editor provides markdown syntax highlighting with STARK BIOME colors:

- **Headers**: Prominent, scaled by level
- **Bold/Italic**: Distinct styling
- **Code blocks**: Monospace with background
- **Links**: Accent color
- **Blockquotes**: Subtle border and background
- **Lists**: Proper indentation

The color palette follows STARK BIOME:
- Steel grays for structure
- Sage greens for code
- Amber for links
- Subtle backgrounds for blocks
        `,
      },
    },
  },
};

// =============================================================================
// Fill Height Demo
// =============================================================================

export const FillHeight: StoryObj = {
  name: 'Fill Parent Height',
  decorators: [
    (Story) => (
      <div
        style={{
          height: '400px',
          padding: '1rem',
          background: '#0A0A0C',
          border: '1px dashed #28282F',
        }}
      >
        <p style={{ fontSize: '0.75rem', color: '#5A5A64', marginBottom: '0.5rem' }}>
          Parent container: 400px height
        </p>
        <div style={{ height: 'calc(100% - 24px)' }}>
          <Story />
        </div>
      </div>
    ),
  ],
  args: {
    value: SAMPLE_MARKDOWN,
    fillHeight: true,
  },
  parameters: {
    docs: {
      description: {
        story: 'With `fillHeight=true`, the editor expands to fill its parent container.',
      },
    },
  },
};

// =============================================================================
// AGENTESE Path Reference
// =============================================================================

export const AgentesePaths: StoryObj = {
  name: 'AGENTESE Path Reference',
  render: () => {
    const contexts = [
      { name: 'world.*', description: 'The External (entities, environments, tools)', color: '#D4A574' },
      { name: 'self.*', description: 'The Internal (memory, capability, state)', color: '#4A6B4A' },
      { name: 'concept.*', description: 'The Abstract (platonics, definitions, logic)', color: '#6B8E8E' },
      { name: 'void.*', description: 'The Accursed Share (entropy, serendipity)', color: '#8B5A2B' },
      { name: 'time.*', description: 'The Temporal (traces, forecasts, schedules)', color: '#C4A77D' },
    ];

    return (
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '1rem',
          padding: '1rem',
        }}
      >
        {/* Context cards */}
        {contexts.map(({ name, description, color }) => {
          const prefix = name.replace('.*', '');
          const paths = AGENTESE_PATHS.filter((p) => p.startsWith(prefix + '.'));

          return (
            <div
              key={name}
              style={{
                padding: '1rem',
                background: '#141418',
                borderRadius: '0.5rem',
                border: '1px solid #28282F',
                borderLeft: `3px solid ${color}`,
              }}
            >
              <h3
                style={{
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  color,
                  marginBottom: '0.25rem',
                  fontFamily: 'ui-monospace, monospace',
                }}
              >
                {name}
              </h3>
              <p
                style={{
                  fontSize: '0.75rem',
                  color: '#8A8A94',
                  marginBottom: '0.75rem',
                }}
              >
                {description}
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.125rem' }}>
                {paths.slice(0, 6).map((path) => (
                  <code
                    key={path}
                    style={{
                      fontSize: '0.6875rem',
                      color: '#E5E7EB',
                      fontFamily: 'ui-monospace, monospace',
                    }}
                  >
                    {path}
                  </code>
                ))}
                {paths.length > 6 && (
                  <span style={{ fontSize: '0.625rem', color: '#5A5A64' }}>
                    +{paths.length - 6} more
                  </span>
                )}
              </div>
            </div>
          );
        })}

        {/* Philosophy card */}
        <div
          style={{
            gridColumn: 'span 2',
            padding: '1rem',
            background: 'rgba(74, 107, 74, 0.1)',
            borderRadius: '0.5rem',
            border: '1px solid #28282F',
          }}
        >
          <blockquote style={{ margin: 0 }}>
            <p
              style={{
                fontSize: '0.875rem',
                color: '#E5E7EB',
                fontStyle: 'italic',
                marginBottom: '0.5rem',
              }}
            >
              "The noun is a lie. There is only the rate of change."
            </p>
            <footer style={{ fontSize: '0.75rem', color: '#8A8A94' }}>
              — AGENTESE Philosophy
            </footer>
          </blockquote>
        </div>
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: `
All AGENTESE paths available for ghost text completion.

**Five Contexts:**
- **world.*** - The External (entities, environments, tools)
- **self.*** - The Internal (memory, capability, state)
- **concept.*** - The Abstract (platonics, definitions, logic)
- **void.*** - The Accursed Share (entropy, serendipity, gratitude)
- **time.*** - The Temporal (traces, forecasts, schedules)

These paths are the first-class citizens of the completion system.
        `,
      },
    },
  },
};

// =============================================================================
// Editor API Reference
// =============================================================================

export const EditorAPI: StoryObj = {
  name: 'Editor API Reference',
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
        MarkdownEditorRef API
      </h3>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={thStyle}>Method</th>
            <th style={thStyle}>Description</th>
          </tr>
        </thead>
        <tbody>
          {[
            { method: 'getValue()', desc: 'Get current content as string' },
            { method: 'setValue(value)', desc: 'Set content programmatically' },
            { method: 'focus()', desc: 'Focus the editor' },
            { method: 'isFocused()', desc: 'Check if editor has focus' },
            { method: 'setReadonly(bool)', desc: 'Toggle readonly dynamically' },
            { method: 'scrollLines(n)', desc: 'Scroll by N lines' },
            { method: 'scrollParagraph(dir)', desc: 'Jump to next/prev paragraph' },
            { method: 'scrollToTop()', desc: 'Scroll to document start' },
            { method: 'scrollToBottom()', desc: 'Scroll to document end' },
          ].map(({ method, desc }) => (
            <tr key={method}>
              <td style={tdStyle}>
                <code
                  style={{
                    fontSize: '0.8125rem',
                    color: '#4A6B4A',
                    fontFamily: 'ui-monospace, monospace',
                  }}
                >
                  {method}
                </code>
              </td>
              <td style={tdStyle}>{desc}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3
        style={{
          fontSize: '1rem',
          fontWeight: 600,
          color: '#E5E7EB',
          marginTop: '1.5rem',
          marginBottom: '1rem',
        }}
      >
        Props
      </h3>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={thStyle}>Prop</th>
            <th style={thStyle}>Type</th>
            <th style={thStyle}>Default</th>
          </tr>
        </thead>
        <tbody>
          {[
            { prop: 'value', type: 'string', def: '""' },
            { prop: 'onChange', type: '(value: string) => void', def: '-' },
            { prop: 'readonly', type: 'boolean', def: 'false' },
            { prop: 'enableGhostText', type: 'boolean', def: 'false' },
            { prop: 'placeholder', type: 'string', def: '""' },
            { prop: 'autoFocus', type: 'boolean', def: 'false' },
            { prop: 'fillHeight', type: 'boolean', def: 'false' },
          ].map(({ prop, type, def }) => (
            <tr key={prop}>
              <td style={tdStyle}>
                <code style={{ color: '#C4A77D', fontFamily: 'ui-monospace, monospace' }}>
                  {prop}
                </code>
              </td>
              <td style={{ ...tdStyle, fontSize: '0.75rem', color: '#8A8A94' }}>{type}</td>
              <td style={{ ...tdStyle, fontSize: '0.75rem' }}>{def}</td>
            </tr>
          ))}
        </tbody>
      </table>
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
