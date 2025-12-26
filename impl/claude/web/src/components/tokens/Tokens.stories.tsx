/**
 * Token Components Stories
 *
 * STARK BIOME Design System - Interactive Document Rendering
 *
 * These stories showcase the markdown rendering system:
 * - InteractiveDocument: Main SceneGraph renderer
 * - CodeBlockToken: Syntax-highlighted code blocks
 * - PortalToken: Expandable hyperedge references
 * - LinkToken: Clickable hyperlinks
 * - ImageToken: Images with AI analysis
 * - BlockquoteToken: Quoted text blocks
 * - MarkdownTableToken: GFM-style tables
 * - AGENTESEPathToken: AGENTESE path navigation
 * - PrincipleToken: Architectural principle references
 * - TaskCheckboxToken: Toggleable task items
 *
 * Philosophy: "Specs stop being documentation and become live control surfaces."
 *
 * @see spec/protocols/interactive-text.md
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState, useCallback } from 'react';

import { InteractiveDocument } from './InteractiveDocument';
import { CodeBlockToken } from './CodeBlockToken';
import { PortalToken } from './PortalToken';
import { LinkToken } from './LinkToken';
import { ImageToken } from './ImageToken';
import { BlockquoteToken } from './BlockquoteToken';
import { MarkdownTableToken } from './MarkdownTableToken';
import { AGENTESEPathToken } from './AGENTESEPathToken';
import { PrincipleToken } from './PrincipleToken';
import { TaskCheckboxToken } from './TaskCheckboxToken';
import { HorizontalRuleToken } from './HorizontalRuleToken';
import { TextSpan } from './TextSpan';
import type { SceneGraph, SceneNode, LayoutDirective } from './types';

// Import component CSS
import './tokens.css';

// =============================================================================
// Meta
// =============================================================================

const meta: Meta = {
  title: 'Tokens/Interactive Document',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: `
# Token Components - Interactive Document Rendering

The token system transforms markdown into interactive, semantically-rich components.

## Core Philosophy

**"The noun is a lie. There is only the rate of change."**

Every token is a meaning-bearing unit that can:
- Be navigated (AGENTESE paths)
- Be expanded (portals)
- Be toggled (tasks)
- Be copied (code)
- Be analyzed (images)

## STARK BIOME Design

- **Steel Foundation** (90%): Carbon backgrounds, gunmetal borders
- **Earned Glow** (10%): Life-sage for living elements, glow-spore for earned badges
- **Bare Edge**: Minimal border-radius (2-4px)
- **No Layout Shift**: Hover elements always in DOM, controlled via opacity

## Token Types

| Token | Purpose | Interaction |
|-------|---------|-------------|
| AGENTESEPath | Navigate the AGENTESE space | Click to navigate |
| Portal | Expand hyperedges inline | Toggle expand/collapse |
| CodeBlock | Display code with syntax | Copy to clipboard |
| Task | Track completion | Toggle checkbox |
| Link | Navigate to URLs | Click to open |
| Image | Display with AI analysis | Hover for description |
| Blockquote | Quoted text | Display only |
| Table | Structured data | Hover for info |
| Principle | Reference principles | Click to view |
        `,
      },
    },
  },
};

export default meta;

// =============================================================================
// Helper: Create SceneGraph
// =============================================================================

function createSceneGraph(nodes: Partial<SceneNode>[], title = 'Test Document'): SceneGraph {
  const layout: LayoutDirective = {
    direction: 'vertical',
    gap: 8,
    padding: 16,
    mode: 'COMFORTABLE',
  };

  return {
    id: `sg-${Date.now()}`,
    nodes: nodes.map((node, index) => ({
      id: `node-${index}`,
      kind: 'TEXT',
      content: '',
      label: '',
      style: {},
      flex: 1,
      min_width: null,
      min_height: null,
      interactions: [],
      section_index: null,
      metadata: {},
      ...node,
    })),
    edges: [],
    layout,
    title,
    metadata: {},
    created_at: new Date().toISOString(),
  };
}

// =============================================================================
// AGENTESEPathToken Stories
// =============================================================================

export const AGENTESEPathDefault: StoryObj = {
  name: 'AGENTESE Path - Default',
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <AGENTESEPathToken path="self.brain" exists={true} onClick={(p) => console.log('Navigate:', p)} />
      <AGENTESEPathToken path="world.house.manifest" exists={true} onClick={(p) => console.log('Navigate:', p)} />
      <AGENTESEPathToken path="concept.categorical.functor" exists={true} onClick={(p) => console.log('Navigate:', p)} />
      <AGENTESEPathToken path="time.traces.recent" exists={true} onClick={(p) => console.log('Navigate:', p)} />
      <AGENTESEPathToken path="void.serendipity.spark" exists={true} onClick={(p) => console.log('Navigate:', p)} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: `
AGENTESE paths are "places" in the semantic space. Each path follows the five-context ontology:
- \`self.*\` - The Internal (memory, capability, state)
- \`world.*\` - The External (entities, environments, tools)
- \`concept.*\` - The Abstract (platonics, definitions, logic)
- \`time.*\` - The Temporal (traces, forecasts, schedules)
- \`void.*\` - The Accursed Share (entropy, serendipity, gratitude)
        `,
      },
    },
  },
};

export const AGENTESEPathGhost: StoryObj = {
  name: 'AGENTESE Path - Ghost (Non-existent)',
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div>
        <span style={{ color: '#8A8A94', marginRight: '8px' }}>Exists:</span>
        <AGENTESEPathToken path="self.brain" exists={true} />
      </div>
      <div>
        <span style={{ color: '#8A8A94', marginRight: '8px' }}>Ghost:</span>
        <AGENTESEPathToken path="self.missing.node" exists={false} />
      </div>
      <div>
        <span style={{ color: '#8A8A94', marginRight: '8px' }}>Ghost:</span>
        <AGENTESEPathToken path="world.hypothetical.feature" exists={false} />
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Ghost state for non-existent paths shows wavy strikethrough and muted colors. These paths may be planned but not yet implemented.',
      },
    },
  },
};

// =============================================================================
// CodeBlockToken Stories
// =============================================================================

export const CodeBlockPython: StoryObj = {
  name: 'Code Block - Python',
  render: () => (
    <CodeBlockToken
      language="python"
      code={`from kgents.agents import PolyAgent

class BrainAgent(PolyAgent[BrainState, Message, Response]):
    """The central reasoning agent.

    "The soul is a mode machine."
    """

    async def process(self, message: Message) -> Response:
        # Apply constitutional principles
        scores = await self.evaluate_constitution(message)

        if scores.total >= 0.8:
            return await self.generate_response(message)
        else:
            return self.decline_with_reasoning(scores)`}
      sourceText=""
    />
  ),
  parameters: {
    docs: {
      description: {
        story: 'Python code block with syntax information. Hover to reveal the copy button.',
      },
    },
  },
};

export const CodeBlockTypeScript: StoryObj = {
  name: 'Code Block - TypeScript',
  render: () => (
    <CodeBlockToken
      language="typescript"
      code={`interface SceneGraph {
  id: string;
  nodes: SceneNode[];
  edges: SceneEdge[];
  layout: LayoutDirective;
  title: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export function InteractiveDocument({ sceneGraph, onNavigate }: Props) {
  const { nodes } = sceneGraph;

  return (
    <div className="interactive-document">
      {nodes.map((node) => (
        <SceneNodeRenderer
          key={node.id}
          node={node}
          onNavigate={onNavigate}
        />
      ))}
    </div>
  );
}`}
      sourceText=""
    />
  ),
};

export const CodeBlockBash: StoryObj = {
  name: 'Code Block - Bash Commands',
  render: () => (
    <CodeBlockToken
      language="bash"
      code={`# Start the kgents development environment
cd impl/claude

# Backend API
uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000

# Web UI (separate terminal)
cd web && npm run dev

# Verify before committing
uv run pytest -q && uv run mypy .
npm run typecheck && npm run lint`}
      sourceText=""
    />
  ),
};

export const CodeBlockLongCode: StoryObj = {
  name: 'Code Block - Long Content (Scroll)',
  render: () => (
    <CodeBlockToken
      language="python"
      code={`# Long code block to test horizontal scrolling
def extremely_long_function_name_that_demonstrates_horizontal_scrolling_behavior(very_long_parameter_one: SomeVeryLongTypeName, another_incredibly_long_parameter: AnotherVeryLongTypeName) -> ReturnTypeWithAVeryLongNameForTestingPurposes:
    """This docstring is intentionally very long to show how the code block handles overflow. It should scroll horizontally rather than wrapping."""

    result = some_function_call_with_many_arguments(arg1="value1", arg2="value2", arg3="value3", arg4="value4", arg5="value5", arg6="value6", arg7="value7", arg8="value8")

    return result

# Many lines to test vertical height
line_1 = "content"
line_2 = "content"
line_3 = "content"
line_4 = "content"
line_5 = "content"
line_6 = "content"
line_7 = "content"
line_8 = "content"
line_9 = "content"
line_10 = "content"
line_11 = "content"
line_12 = "content"
line_13 = "content"
line_14 = "content"
line_15 = "content"
line_16 = "content"
line_17 = "content"
line_18 = "content"
line_19 = "content"
line_20 = "content"`}
      sourceText=""
    />
  ),
  parameters: {
    docs: {
      description: {
        story: 'Long code blocks demonstrate proper horizontal scrolling and line count display.',
      },
    },
  },
};

// =============================================================================
// PortalToken Stories
// =============================================================================

export const PortalDefault: StoryObj = {
  name: 'Portal - Default (Collapsed)',
  render: () => (
    <PortalToken
      edgeType="implements"
      destinations={[
        { path: 'services/brain/core.py', title: 'Brain Core', preview: 'Central reasoning engine' },
        { path: 'services/brain/memory.py', title: 'Memory Service', preview: 'Crystal storage' },
        { path: 'services/brain/dialogue.py', title: 'Dialogue Manager', preview: 'Turn handling' },
      ]}
      onNavigate={(path) => console.log('Navigate to:', path)}
    />
  ),
  parameters: {
    docs: {
      description: {
        story: `
Portals are expandable hyperedges that bring documentation to you.

**"You don't go to the doc. The doc comes to you."**

Click to expand and see destinations inline.
        `,
      },
    },
  },
};

export const PortalExpanded: StoryObj = {
  name: 'Portal - Expanded',
  render: () => (
    <PortalToken
      edgeType="tests"
      destinations={[
        { path: 'tests/test_brain.py', title: 'Brain Tests', preview: 'Unit tests for core reasoning', exists: true },
        { path: 'tests/test_memory.py', title: 'Memory Tests', preview: 'Crystal storage tests', exists: true },
        { path: 'tests/test_integration.py', title: 'Integration Tests', preview: 'End-to-end flows', exists: true },
      ]}
      defaultExpanded={true}
      onNavigate={(path) => console.log('Navigate to:', path)}
    />
  ),
};

export const PortalWithMissing: StoryObj = {
  name: 'Portal - With Missing Destinations',
  render: () => (
    <PortalToken
      edgeType="references"
      destinations={[
        { path: 'spec/protocols/agentese.md', title: 'AGENTESE Protocol', exists: true },
        { path: 'spec/agents/brain.md', title: 'Brain Spec', exists: true },
        { path: 'spec/missing/file.md', title: 'Missing File', exists: false },
        { path: 'spec/deleted/old.md', title: 'Deleted Spec', exists: false },
      ]}
      defaultExpanded={true}
      onNavigate={(path) => console.log('Navigate to:', path)}
    />
  ),
  parameters: {
    docs: {
      description: {
        story: 'Missing destinations are shown with a "missing" badge and disabled navigation.',
      },
    },
  },
};

export const PortalUnparsed: StoryObj = {
  name: 'Portal - Unparsed (Natural Language)',
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <PortalToken
        edgeType={null}
        destinations={[]}
        authoringState="UNPARSED"
        naturalLanguage="what tests this component?"
        onCure={async () => {
          await new Promise<void>((r) => { setTimeout(r, 1000); });
          return { success: true, confidence: 0.85 };
        }}
      />
      <PortalToken
        edgeType={null}
        destinations={[]}
        authoringState="CURING"
        naturalLanguage="finding related specifications..."
      />
      <PortalToken
        edgeType={null}
        destinations={[]}
        authoringState="FAILED"
        naturalLanguage="something ambiguous"
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: `
Portal authoring states (from spec/protocols/portal-token.md):
- **UNPARSED**: Natural language query needing resolution
- **CURING**: LLM resolution in progress
- **FAILED**: Could not resolve the query
        `,
      },
    },
  },
};

export const PortalManyDestinations: StoryObj = {
  name: 'Portal - Many Destinations (Show More)',
  render: () => (
    <PortalToken
      edgeType="used-by"
      destinations={Array.from({ length: 12 }, (_, i) => ({
        path: `services/module_${i + 1}/handler.py`,
        title: `Module ${i + 1} Handler`,
        exists: true,
      }))}
      defaultExpanded={true}
      maxVisible={5}
      onNavigate={(path) => console.log('Navigate to:', path)}
    />
  ),
  parameters: {
    docs: {
      description: {
        story: 'When there are many destinations, a "show more" button appears. Default maxVisible is 5.',
      },
    },
  },
};

// =============================================================================
// LinkToken Stories
// =============================================================================

export const LinkTokenVariants: StoryObj = {
  name: 'Link Token - Variants',
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', color: '#B4B4BE' }}>
      <p>
        Check the <LinkToken text="kgents documentation" url="https://github.com/kgents/kgents" /> for more details.
      </p>
      <p>
        Internal link to <LinkToken text="spec/protocols/witness.md" url="spec/protocols/witness.md" onClick={(url) => console.log('Internal:', url)} />.
      </p>
      <p>
        External link to <LinkToken text="Anthropic Claude" url="https://www.anthropic.com/claude" /> opens in new tab.
      </p>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Links show URL preview on hover. External links (http/https) open in new tab with arrow indicator.',
      },
    },
  },
};

// =============================================================================
// ImageToken Stories
// =============================================================================

export const ImageTokenDefault: StoryObj = {
  name: 'Image Token - Default',
  render: () => (
    <ImageToken
      src="https://placekitten.com/400/300"
      alt="A sample kitten image"
      caption="Figure 1: Sample image with caption"
      onClick={(src) => console.log('Expand image:', src)}
    />
  ),
};

export const ImageTokenWithAI: StoryObj = {
  name: 'Image Token - With AI Description',
  render: () => (
    <ImageToken
      src="https://placekitten.com/500/350"
      alt="Architecture diagram"
      aiDescription="This diagram shows the kgents architecture with Brain at the center, connected to Town (multi-agent), Park (leisure), and Atelier (creation) services. Data flows through the Witness bus for constitutional alignment."
      onClick={(src) => console.log('Expand image:', src)}
    />
  ),
  parameters: {
    docs: {
      description: {
        story: 'When AI description is available, it shows on hover. "Images are meaning tokens, not decoration."',
      },
    },
  },
};

export const ImageTokenError: StoryObj = {
  name: 'Image Token - Load Error',
  render: () => (
    <ImageToken
      src="/nonexistent/image.png"
      alt="Missing image"
    />
  ),
  parameters: {
    docs: {
      description: {
        story: 'Graceful error state when image fails to load, showing the path for debugging.',
      },
    },
  },
};

// =============================================================================
// BlockquoteToken Stories
// =============================================================================

export const BlockquoteDefault: StoryObj = {
  name: 'Blockquote - Default',
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '600px' }}>
      <BlockquoteToken
        content="The noun is a lie. There is only the rate of change."
      />
      <BlockquoteToken
        content="Specs stop being documentation and become live control surfaces."
        attribution="spec/protocols/interactive-text.md"
      />
      <BlockquoteToken
        content="Daring, bold, creative, opinionated but not gaudy. The Mirror Test: Does K-gent feel like me on my best day?"
        attribution="Kent"
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Blockquotes with optional attribution. Used for philosophy quotes and important citations.',
      },
    },
  },
};

// =============================================================================
// MarkdownTableToken Stories
// =============================================================================

export const TableDefault: StoryObj = {
  name: 'Table - Default',
  render: () => (
    <MarkdownTableToken
      columns={[
        { header: 'System', alignment: 'left', index: 0 },
        { header: 'Status', alignment: 'center', index: 1 },
        { header: 'Coverage', alignment: 'right', index: 2 },
      ]}
      rows={[
        ['Brain', 'Complete', '100%'],
        ['Town', 'Active', '70%'],
        ['Witness', 'Complete', '98%'],
        ['Atelier', 'Active', '75%'],
        ['Liminal', 'Planned', '50%'],
      ]}
      sourceText=""
    />
  ),
  parameters: {
    docs: {
      description: {
        story: 'GFM-style markdown table with column alignment. Hover to see row/column count badge.',
      },
    },
  },
};

export const TableLarge: StoryObj = {
  name: 'Table - Large (Many Columns)',
  render: () => (
    <MarkdownTableToken
      columns={[
        { header: 'Agent', alignment: 'left', index: 0 },
        { header: 'Layer 0', alignment: 'center', index: 1 },
        { header: 'Layer 1', alignment: 'center', index: 2 },
        { header: 'Layer 2', alignment: 'center', index: 3 },
        { header: 'Layer 3', alignment: 'center', index: 4 },
        { header: 'Layer 4', alignment: 'center', index: 5 },
        { header: 'Layer 5', alignment: 'center', index: 6 },
        { header: 'Layer 6', alignment: 'center', index: 7 },
      ]}
      rows={[
        ['PolyAgent', 'Persist', 'Sheaf', 'Operad', 'Service', 'Node', 'Protocol', 'Project'],
        ['Citizen', 'DB', 'Local', 'Compose', 'Town', 'Register', 'AGENTESE', 'CLI/Web'],
        ['Brain', 'Memory', 'Crystals', 'LLM', 'K-gent', 'Soul', 'Dialogue', 'Chat'],
      ]}
      sourceText=""
    />
  ),
  parameters: {
    docs: {
      description: {
        story: 'Wide tables scroll horizontally. The metaphysical fullstack in table form.',
      },
    },
  },
};

// =============================================================================
// PrincipleToken Stories
// =============================================================================

export const PrincipleTokenVariants: StoryObj = {
  name: 'Principle Token - Categories',
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', color: '#B4B4BE' }}>
      <p>
        This follows <PrincipleToken principle="AD-009" /> which states that density and content should be isomorphic.
      </p>
      <p>
        The design is <PrincipleToken principle="Tasteful" /> and <PrincipleToken principle="Joy-Inducing" />.
      </p>
      <p>
        Components should be <PrincipleToken principle="Composable" /> like morphisms in a category.
      </p>
      <p>
        Custom principle: <PrincipleToken principle="CUSTOM-01" title="Custom Principle" description="User-defined architectural decision" category="operational" />
      </p>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: `
Principle tokens reference architectural decisions and core values:
- **Architectural** (gold): AD-XXX numbered decisions
- **Constitutional** (green): Core values (Tasteful, Composable, etc.)
- **Operational** (steel): Day-to-day patterns
        `,
      },
    },
  },
};

// =============================================================================
// TaskCheckboxToken Stories
// =============================================================================

export const TaskCheckboxInteractive: StoryObj = {
  name: 'Task Checkbox - Interactive',
  render: () => {
    const [tasks, setTasks] = useState([
      { id: '1', checked: false, description: 'Implement SceneGraph parser' },
      { id: '2', checked: true, description: 'Add syntax highlighting' },
      { id: '3', checked: false, description: 'Write Storybook stories' },
      { id: '4', checked: false, description: 'Test portal expansion' },
    ]);

    const handleToggle = useCallback(async (newState: boolean, taskId?: string) => {
      await new Promise<void>((r) => { setTimeout(r, 200); }); // Simulate API call
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? { ...t, checked: newState } : t))
      );
    }, []);

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {tasks.map((task) => (
          <TaskCheckboxToken
            key={task.id}
            checked={task.checked}
            description={task.description}
            taskId={task.id}
            onToggle={handleToggle}
          />
        ))}
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: `
Task checkboxes render markdown task lists as interactive elements:
- \`[ ]\` becomes unchecked
- \`[x]\` becomes checked

Toggle uses optimistic updates with rollback on error.
        `,
      },
    },
  },
};

// =============================================================================
// HorizontalRuleToken Story
// =============================================================================

export const HorizontalRuleDefault: StoryObj = {
  name: 'Horizontal Rule',
  render: () => (
    <div style={{ maxWidth: '600px' }}>
      <p style={{ color: '#B4B4BE' }}>Content before the rule.</p>
      <HorizontalRuleToken />
      <p style={{ color: '#B4B4BE' }}>Content after the rule.</p>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Visual section divider with subtle gradient. Minimal presence, organic feel.',
      },
    },
  },
};

// =============================================================================
// TextSpan Stories
// =============================================================================

export const TextSpanWithHeaders: StoryObj = {
  name: 'Text Span - Cosmetic Headers',
  render: () => (
    <div style={{ maxWidth: '600px' }}>
      <TextSpan content={`# H1 Header - Main Title

## H2 Header - Section

Some paragraph text with normal content.

### H3 Header - Subsection

More content here.

#### H4 Header - Minor Section

##### H5 Header
###### H6 Header`} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'TextSpan detects markdown headers and applies cosmetic styling without semantic HTML tags.',
      },
    },
  },
};

export const TextSpanWithHighlighting: StoryObj = {
  name: 'Text Span - Rich Highlighting',
  render: () => (
    <div style={{ maxWidth: '600px' }}>
      <TextSpan content={`Rich highlighting detects patterns:

- Strings: "hello world" and 'single quotes'
- Numbers: 42, 3.14159, -100
- Booleans: true, false, True, False
- Null: null, None, undefined
- UUIDs: 550e8400-e29b-41d4-a716-446655440000
- URLs: https://example.com/path?query=1
- IPs: 192.168.1.1, ::1
- Paths: /usr/local/bin, ./relative/path
- Function calls: doSomething() and calculate()`} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'TextSpan applies heuristic-based highlighting inspired by Rich\'s ReprHighlighter.',
      },
    },
  },
};

// =============================================================================
// InteractiveDocument - Full Document Stories
// =============================================================================

export const FullDocumentMixed: StoryObj = {
  name: 'Full Document - Mixed Content',
  render: () => {
    const sceneGraph = createSceneGraph([
      {
        id: 'header',
        kind: 'TEXT',
        content: '# kgents Interactive Document Demo\n\nThis demonstrates the full rendering system.',
      },
      {
        id: 'code-1',
        kind: 'CODE_REGION',
        content: {
          token_type: 'code_block',
          source_text: '',
          source_position: [0, 0] as [number, number],
          token_id: 'code-1',
          token_data: {
            language: 'python',
            code: `from kgents import Brain

async def main():
    brain = Brain()
    response = await brain.think("Hello, world!")
    print(response)`,
          },
          affordances: [],
        },
        metadata: { meaning_token_kind: 'CODE_REGION' },
      },
      {
        id: 'text-1',
        kind: 'TEXT',
        content: '\nThe system uses AGENTESE paths for navigation:',
      },
      {
        id: 'path-1',
        kind: 'AGENTESE_PORTAL',
        content: {
          token_type: 'agentese_path',
          source_text: 'self.brain.think',
          source_position: [0, 0] as [number, number],
          token_id: 'path-1',
          token_data: { path: 'self.brain.think', exists: true },
          affordances: [],
        },
        metadata: { meaning_token_kind: 'AGENTESE_PORTAL' },
      },
      {
        id: 'quote-1',
        kind: 'BLOCKQUOTE',
        content: {
          token_type: 'blockquote',
          source_text: '> The proof IS the decision.',
          source_position: [0, 0] as [number, number],
          token_id: 'quote-1',
          token_data: { content: 'The proof IS the decision. The mark IS the witness.' },
          affordances: [],
        },
        metadata: { meaning_token_kind: 'BLOCKQUOTE' },
      },
      {
        id: 'hr-1',
        kind: 'HORIZONTAL_RULE',
        content: '---',
        metadata: { meaning_token_kind: 'HORIZONTAL_RULE' },
      },
      {
        id: 'table-1',
        kind: 'MARKDOWN_TABLE',
        content: {
          token_type: 'markdown_table',
          source_text: '',
          source_position: [0, 0] as [number, number],
          token_id: 'table-1',
          token_data: {
            columns: [
              { header: 'Layer', alignment: 'left' as const, index: 0 },
              { header: 'Purpose', alignment: 'left' as const, index: 1 },
            ],
            rows: [
              ['Persistence', 'StorageProvider'],
              ['Sheaf', 'Local coherence'],
              ['Operad', 'Composition grammar'],
              ['Service', 'Crown Jewels'],
              ['AGENTESE', 'Universal protocol'],
              ['Projection', 'CLI/Web/JSON'],
            ],
          },
          affordances: [],
        },
        metadata: { meaning_token_kind: 'MARKDOWN_TABLE' },
      },
    ], 'kgents Demo Document');

    return (
      <div style={{ maxWidth: '800px', padding: '24px', background: '#141418', borderRadius: '4px' }}>
        <InteractiveDocument
          sceneGraph={sceneGraph}
          onNavigate={(path) => console.log('Navigate:', path)}
        />
      </div>
    );
  },
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        story: `
# Full Interactive Document

This story demonstrates a complete document with mixed token types:
- Headers (via TextSpan)
- Code blocks with syntax highlighting
- AGENTESE path tokens
- Blockquotes
- Horizontal rules
- Tables

The InteractiveDocument component receives a SceneGraph and renders each node using the appropriate token component.
        `,
      },
    },
  },
};

export const DocumentWithTasks: StoryObj = {
  name: 'Full Document - Task List',
  render: () => {
    const [taskStates, setTaskStates] = useState<Record<string, boolean>>({
      'task-1': true,
      'task-2': true,
      'task-3': false,
      'task-4': false,
      'task-5': false,
    });

    const handleToggle = async (newState: boolean, taskId?: string) => {
      if (taskId) {
        await new Promise((r) => setTimeout(r, 150));
        setTaskStates((prev) => ({ ...prev, [taskId]: newState }));
      }
    };

    const tasks = [
      { id: 'task-1', description: 'Design SceneGraph schema' },
      { id: 'task-2', description: 'Implement token renderers' },
      { id: 'task-3', description: 'Add portal expansion' },
      { id: 'task-4', description: 'Write documentation' },
      { id: 'task-5', description: 'Deploy to production' },
    ];

    const sceneGraph = createSceneGraph([
      {
        id: 'header',
        kind: 'TEXT',
        content: '# Sprint Tasks\n\nCurrent sprint progress:',
      },
      ...tasks.map((task) => ({
        id: task.id,
        kind: 'TASK_TOGGLE' as const,
        content: {
          token_type: 'task_checkbox',
          source_text: `- [${taskStates[task.id] ? 'x' : ' '}] ${task.description}`,
          source_position: [0, 0] as [number, number],
          token_id: task.id,
          token_data: {
            checked: taskStates[task.id],
            description: task.description,
          },
          affordances: [],
        },
        metadata: { meaning_token_kind: 'TASK_TOGGLE' },
      })),
    ], 'Sprint Tasks');

    return (
      <div style={{ maxWidth: '600px', padding: '24px', background: '#141418', borderRadius: '4px' }}>
        <InteractiveDocument
          sceneGraph={sceneGraph}
          onToggle={handleToggle}
        />
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Interactive task list where checkboxes can be toggled. State persists in the parent component.',
      },
    },
  },
};

export const DocumentWithPortals: StoryObj = {
  name: 'Full Document - Portals',
  render: () => {
    const sceneGraph = createSceneGraph([
      {
        id: 'header',
        kind: 'TEXT',
        content: '# Brain Agent Specification\n\nThe central reasoning engine.',
      },
      {
        id: 'portal-1',
        kind: 'PORTAL',
        content: {
          token_type: 'portal',
          source_text: '@[implements -> services/brain/]',
          source_position: [0, 0] as [number, number],
          token_id: 'portal-1',
          token_data: {
            edge_type: 'implements',
            destinations: [
              { path: 'services/brain/core.py', title: 'Core Logic', exists: true },
              { path: 'services/brain/memory.py', title: 'Memory', exists: true },
              { path: 'services/brain/dialogue.py', title: 'Dialogue', exists: true },
            ],
          },
          affordances: [],
        },
        metadata: { meaning_token_kind: 'PORTAL' },
      },
      {
        id: 'text-1',
        kind: 'TEXT',
        content: '\n## Testing\n\nThe Brain agent has comprehensive tests:',
      },
      {
        id: 'portal-2',
        kind: 'PORTAL',
        content: {
          token_type: 'portal',
          source_text: '@[tests -> tests/brain/]',
          source_position: [0, 0] as [number, number],
          token_id: 'portal-2',
          token_data: {
            edge_type: 'tests',
            destinations: [
              { path: 'tests/brain/test_core.py', title: 'Core Tests', exists: true },
              { path: 'tests/brain/test_memory.py', title: 'Memory Tests', exists: true },
              { path: 'tests/brain/test_integration.py', title: 'Integration', exists: true },
            ],
          },
          affordances: [],
        },
        metadata: { meaning_token_kind: 'PORTAL' },
      },
      {
        id: 'text-2',
        kind: 'TEXT',
        content: '\n## Related Specifications',
      },
      {
        id: 'portal-3',
        kind: 'PORTAL',
        content: {
          token_type: 'portal',
          source_text: '@[extends -> spec/agents/]',
          source_position: [0, 0] as [number, number],
          token_id: 'portal-3',
          token_data: {
            edge_type: 'extends',
            destinations: [
              { path: 'spec/agents/poly.md', title: 'PolyAgent Base', exists: true },
              { path: 'spec/agents/k-gent.md', title: 'K-gent (Soul)', exists: true },
              { path: 'spec/agents/m-gent.md', title: 'M-gent (Memory)', exists: false },
            ],
            is_discovered: true,
          },
          affordances: [],
        },
        metadata: { meaning_token_kind: 'PORTAL' },
      },
    ], 'Brain Specification');

    return (
      <div style={{ maxWidth: '700px', padding: '24px', background: '#141418', borderRadius: '4px' }}>
        <InteractiveDocument
          sceneGraph={sceneGraph}
          onNavigate={(path) => console.log('Navigate:', path)}
        />
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Document with expandable portals showing implementation, tests, and related specs. The last portal is auto-discovered (dashed border).',
      },
    },
  },
};

// =============================================================================
// Edge Cases & Stress Tests
// =============================================================================

export const EdgeCaseEmptyDocument: StoryObj = {
  name: 'Edge Case - Empty Document',
  render: () => {
    const sceneGraph = createSceneGraph([], 'Empty Document');
    return (
      <div style={{ maxWidth: '600px', padding: '24px', background: '#141418', borderRadius: '4px', minHeight: '100px' }}>
        <InteractiveDocument sceneGraph={sceneGraph} />
        <p style={{ color: '#5A5A64', fontStyle: 'italic', marginTop: '16px' }}>
          (Empty document renders nothing)
        </p>
      </div>
    );
  },
};

export const EdgeCaseLongContent: StoryObj = {
  name: 'Edge Case - Very Long Content',
  render: () => (
    <div style={{ maxWidth: '600px' }}>
      <BlockquoteToken
        content={`This is an extremely long blockquote that tests how the token handles overflow. The system should gracefully wrap text content without breaking the layout. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.`}
        attribution="Stress Test"
      />
      <div style={{ marginTop: '16px' }}>
        <LinkToken
          text="This is a very long link text that might overflow the container and should be handled gracefully"
          url="https://example.com/very/long/path/that/might/cause/overflow/issues"
        />
      </div>
    </div>
  ),
};

export const EdgeCaseSpecialCharacters: StoryObj = {
  name: 'Edge Case - Special Characters',
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <AGENTESEPathToken path="self.brain.think<T>" exists={true} />
      <AGENTESEPathToken path="concept.math.pi=3.14" exists={true} />
      <CodeBlockToken
        language="html"
        code={`<div class="test">
  <span>&amp; &lt; &gt; &quot;</span>
  <script>alert('xss')</script>
</div>`}
        sourceText=""
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Tests handling of special characters like angle brackets, ampersands, and potential XSS vectors.',
      },
    },
  },
};

// =============================================================================
// Composition Demo
// =============================================================================

export const CompositionAllTokens: StoryObj = {
  name: 'Composition - All Token Types',
  render: () => (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '24px',
        padding: '24px',
        background: '#141418',
        borderRadius: '4px',
        maxWidth: '800px',
      }}
    >
      <div>
        <h3 style={{ color: '#E5E7EB', marginBottom: '12px', fontSize: '14px' }}>AGENTESE Paths</h3>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <AGENTESEPathToken path="self.brain" exists={true} />
          <AGENTESEPathToken path="world.house" exists={true} />
          <AGENTESEPathToken path="void.missing" exists={false} />
        </div>
      </div>

      <HorizontalRuleToken />

      <div>
        <h3 style={{ color: '#E5E7EB', marginBottom: '12px', fontSize: '14px' }}>Principles</h3>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <PrincipleToken principle="AD-009" />
          <PrincipleToken principle="Tasteful" />
          <PrincipleToken principle="Composable" />
        </div>
      </div>

      <HorizontalRuleToken />

      <div>
        <h3 style={{ color: '#E5E7EB', marginBottom: '12px', fontSize: '14px' }}>Portal</h3>
        <PortalToken
          edgeType="implements"
          destinations={[
            { path: 'services/brain/core.py', exists: true },
            { path: 'services/brain/memory.py', exists: true },
          ]}
        />
      </div>

      <HorizontalRuleToken />

      <div>
        <h3 style={{ color: '#E5E7EB', marginBottom: '12px', fontSize: '14px' }}>Code Block</h3>
        <CodeBlockToken
          language="typescript"
          code={`const brain = new Brain();
await brain.think();`}
          sourceText=""
        />
      </div>

      <HorizontalRuleToken />

      <div>
        <h3 style={{ color: '#E5E7EB', marginBottom: '12px', fontSize: '14px' }}>Tasks</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <TaskCheckboxToken checked={true} description="Complete task" taskId="1" />
          <TaskCheckboxToken checked={false} description="Pending task" taskId="2" />
        </div>
      </div>

      <HorizontalRuleToken />

      <div>
        <h3 style={{ color: '#E5E7EB', marginBottom: '12px', fontSize: '14px' }}>Quote</h3>
        <BlockquoteToken
          content="The proof IS the decision. The mark IS the witness."
          attribution="spec/protocols/witness.md"
        />
      </div>

      <HorizontalRuleToken />

      <div>
        <h3 style={{ color: '#E5E7EB', marginBottom: '12px', fontSize: '14px' }}>Table</h3>
        <MarkdownTableToken
          columns={[
            { header: 'Token', alignment: 'left', index: 0 },
            { header: 'Purpose', alignment: 'left', index: 1 },
          ]}
          rows={[
            ['AGENTESE', 'Navigation'],
            ['Portal', 'Expansion'],
            ['Code', 'Display'],
          ]}
          sourceText=""
        />
      </div>

      <HorizontalRuleToken />

      <div>
        <h3 style={{ color: '#E5E7EB', marginBottom: '12px', fontSize: '14px' }}>Links</h3>
        <p style={{ color: '#B4B4BE' }}>
          See <LinkToken text="documentation" url="https://github.com/kgents" /> or{' '}
          <LinkToken text="local spec" url="spec/readme.md" />.
        </p>
      </div>
    </div>
  ),
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        story: `
# All Token Types Composition

A gallery of all available token types rendered together, demonstrating the cohesive STARK BIOME design system.

**Steel Foundation** (90%): Carbon backgrounds, gunmetal borders
**Earned Glow** (10%): Life-sage for living elements, glow-spore for earned badges
        `,
      },
    },
  },
};
