/**
 * Projection Component Library - Storybook Stories
 *
 * Unified rendering components for AGENTESE responses.
 * These widgets form the vocabulary of projected agent outputs,
 * providing consistent UI across CLI, Web, and marimo surfaces.
 *
 * STARK BIOME Philosophy:
 * - "90% Steel (cool industrial) / 10% Earned Glow (organic accents)"
 * - The frame is humble. The content glows.
 * - Sharp corners (2-4px) make warm elements pop against austerity.
 *
 * @see docs/skills/projection-target.md - Multi-target rendering
 * @see docs/skills/elastic-ui-patterns.md - Responsive patterns
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState, useEffect } from 'react';

// Import all projection components
import {
  TextWidget,
  TableWidget,
  GraphWidget,
  ProgressWidget,
  SelectWidget,
  ConfirmWidget,
  StreamWidget,
  ErrorPanel,
  RefusalPanel,
  CachedBadge,
  PilotCard,
  CategoryFilter,
  OverrideControls,
  ProjectionView,
} from '../../components/projection';

// Import types
import type {
  TextVariant,
  TableColumn,
  GraphType,
  ProgressStep,
  SelectOption,
  ErrorInfo,
  RefusalInfo,
  CacheMeta,
  ErrorCategory,
} from '../../components/projection';

import type { GalleryCategory, GalleryOverrides, PilotResponse } from '../../api/types.js';

// Import design system
import '../../design/tokens.css';

// =============================================================================
// Meta Configuration
// =============================================================================

const meta: Meta = {
  title: 'Journeys/Projection Widgets',
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: `
# Projection Widget Library

The projection layer renders AGENTESE responses into visual widgets.
Each widget is a universal primitive that works across all surfaces.

## Design Philosophy: STARK BIOME

> "The frame is humble. The content glows."

- **90% Steel**: Cool industrial backgrounds, borders, containers
- **10% Earned Glow**: Organic accents for success, focus, special states
- **Bare Edge**: Sharp corners (2-4px) maximize warmth contrast

## Widget Categories

| Category | Widgets | Purpose |
|----------|---------|---------|
| **Content** | TextWidget, TableWidget, GraphWidget | Display data |
| **Interaction** | SelectWidget, ConfirmWidget | Gather input |
| **Progress** | ProgressWidget, StreamWidget | Show activity |
| **Status** | ErrorPanel, RefusalPanel, CachedBadge | Chrome/metadata |
| **Gallery** | PilotCard, CategoryFilter, OverrideControls, ProjectionView | Component gallery |

## Usage Pattern

\`\`\`tsx
// All widgets accept data props + optional metadata
<TextWidget content="Hello, world!" variant="heading" />

// Status chrome wraps content when needed
{hasError(meta) && <ErrorPanel error={meta.error} onRetry={retry} />}
{isCached(meta) && <CachedBadge cache={meta.cache} />}
\`\`\`
        `,
      },
    },
  },
  tags: ['autodocs'],
};

export default meta;

// =============================================================================
// Mock Data Factories
// =============================================================================

const MOCK_TEXT_SAMPLES: Record<TextVariant, string> = {
  plain: `The quick brown fox jumps over the lazy dog.
This is a multi-line text sample that demonstrates plain text rendering.
Notice the default line spacing and typography.`,
  code: `function fibonacci(n: number): number {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}

// Usage
console.log(fibonacci(10)); // 55`,
  heading: 'Crown Jewels System Status',
  quote: `"The proof IS the decision. The mark IS the witness."
- Kent's Agents Philosophy`,
  markdown: `# kgents Architecture

The system consists of:

- **Brain**: Core intelligence
- **Town**: Citizen simulation
- **Witness**: Decision tracing

> Every agent is a fullstack agent.`,
};

const MOCK_TABLE_DATA: { columns: TableColumn[]; rows: Record<string, unknown>[] } = {
  columns: [
    { key: 'id', label: 'ID', sortable: true, width: '60px' },
    { key: 'name', label: 'Agent Name', sortable: true },
    { key: 'status', label: 'Status', sortable: true },
    { key: 'health', label: 'Health', sortable: true, align: 'right' },
    { key: 'lastSeen', label: 'Last Seen', sortable: true },
  ],
  rows: [
    { id: 1, name: 'Brain', status: 'active', health: 98, lastSeen: '2m ago' },
    { id: 2, name: 'Town', status: 'active', health: 87, lastSeen: '1m ago' },
    { id: 3, name: 'Witness', status: 'active', health: 100, lastSeen: '30s ago' },
    { id: 4, name: 'Park', status: 'dormant', health: 72, lastSeen: '5m ago' },
    { id: 5, name: 'Atelier', status: 'active', health: 95, lastSeen: '1m ago' },
    { id: 6, name: 'Garden', status: 'seeding', health: 45, lastSeen: '10m ago' },
    { id: 7, name: 'Liminal', status: 'dreaming', health: 88, lastSeen: '3m ago' },
    { id: 8, name: 'Membrane', status: 'active', health: 92, lastSeen: '45s ago' },
    { id: 9, name: 'Soul', status: 'reflecting', health: 100, lastSeen: '1m ago' },
    { id: 10, name: 'Cosmos', status: 'expanding', health: 78, lastSeen: '8m ago' },
    { id: 11, name: 'Forge', status: 'cooling', health: 65, lastSeen: '15m ago' },
    { id: 12, name: 'Cache', status: 'warm', health: 99, lastSeen: '10s ago' },
  ],
};

const MOCK_GRAPH_DATA: Record<GraphType, { labels: string[]; datasets: { label: string; data: number[] }[] }> = {
  line: {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      { label: 'Decisions', data: [12, 19, 15, 22, 18, 25, 30] },
      { label: 'Witnesses', data: [8, 15, 12, 18, 14, 20, 24] },
    ],
  },
  bar: {
    labels: ['Brain', 'Town', 'Witness', 'Atelier', 'Liminal'],
    datasets: [
      { label: 'Uptime %', data: [99.2, 87.5, 100, 95.3, 88.1] },
    ],
  },
  pie: {
    labels: ['Active', 'Dormant', 'Dreaming', 'Seeding'],
    datasets: [
      { label: 'Agent States', data: [42, 18, 25, 15] },
    ],
  },
  doughnut: {
    labels: ['Success', 'Refusal', 'Error', 'Cached'],
    datasets: [
      { label: 'Response Types', data: [156, 12, 8, 45] },
    ],
  },
  radar: {
    labels: ['Tasteful', 'Curated', 'Ethical', 'Joy-Inducing', 'Composable'],
    datasets: [
      { label: 'K-gent Principles', data: [92, 88, 100, 85, 78] },
    ],
  },
};

const MOCK_PROGRESS_STEPS: ProgressStep[] = [
  { label: 'Initialize', completed: true },
  { label: 'Analyze', completed: true },
  { label: 'Transform', completed: false, current: true },
  { label: 'Validate', completed: false },
  { label: 'Complete', completed: false },
];

const MOCK_SELECT_OPTIONS: SelectOption[] = [
  { value: 'brain', label: 'Brain (Core Intelligence)', group: 'Crown Jewels' },
  { value: 'town', label: 'Town (Citizen Simulation)', group: 'Crown Jewels' },
  { value: 'witness', label: 'Witness (Decision Tracing)', group: 'Crown Jewels' },
  { value: 'atelier', label: 'Atelier (Creative Workspace)', group: 'Crown Jewels' },
  { value: 'liminal', label: 'Liminal (Dream State)', group: 'Crown Jewels' },
  { value: 'normal', label: 'Normal Mode', group: 'Editor Modes' },
  { value: 'insert', label: 'Insert Mode', group: 'Editor Modes' },
  { value: 'edge', label: 'Edge Mode', group: 'Editor Modes' },
  { value: 'visual', label: 'Visual Mode', group: 'Editor Modes' },
  { value: 'witness-mode', label: 'Witness Mode', group: 'Editor Modes', disabled: true },
];

const MOCK_ERROR_BY_CATEGORY: Record<ErrorCategory, ErrorInfo> = {
  network: {
    category: 'network',
    code: 'ECONNREFUSED',
    message: 'Unable to connect to AGENTESE gateway',
    retryAfterSeconds: 5,
    fallbackAction: 'Check network connection or use offline mode',
    traceId: 'trace-abc123-network',
  },
  notFound: {
    category: 'notFound',
    code: 'AGENT_NOT_FOUND',
    message: 'Agent "cosmos.expand" not registered in gateway',
    retryAfterSeconds: null,
    fallbackAction: 'Check AGENTESE path spelling or register the agent',
    traceId: 'trace-def456-notfound',
  },
  permission: {
    category: 'permission',
    code: 'PERMISSION_DENIED',
    message: 'Insufficient privileges to invoke "self.soul.override"',
    retryAfterSeconds: null,
    fallbackAction: 'Request elevated permissions or use alternative path',
    traceId: 'trace-ghi789-permission',
  },
  timeout: {
    category: 'timeout',
    code: 'ETIMEDOUT',
    message: 'Agent invocation exceeded 30 second timeout',
    retryAfterSeconds: 15,
    fallbackAction: 'Consider breaking operation into smaller steps',
    traceId: 'trace-jkl012-timeout',
  },
  validation: {
    category: 'validation',
    code: 'SCHEMA_MISMATCH',
    message: 'Response schema does not match expected WidgetEnvelope',
    retryAfterSeconds: null,
    fallbackAction: 'Check agent implementation for schema compliance',
    traceId: 'trace-mno345-validation',
  },
  unknown: {
    category: 'unknown',
    code: 'INTERNAL_ERROR',
    message: 'An unexpected error occurred during projection',
    retryAfterSeconds: null,
    fallbackAction: 'Check system logs or contact support',
    traceId: 'trace-pqr678-unknown',
  },
};

const MOCK_REFUSAL: RefusalInfo = {
  reason: 'This action would violate the principle of tasteful design.',
  consentRequired: 'Explicit user acknowledgment of design trade-off',
  appealTo: 'self.soul.appeal',
  overrideCost: 25,
};

const MOCK_CACHE: CacheMeta = {
  isCached: true,
  cachedAt: new Date(Date.now() - 5 * 60 * 1000).toISOString(), // 5 minutes ago
  ttlSeconds: 300, // 5 minute TTL
  cacheKey: 'agentese:world.brain.status:architect',
  deterministic: true,
};

// =============================================================================
// 1. TextWidget Stories
// =============================================================================

export const TextWidgetStory: StoryObj = {
  name: '1. TextWidget - Text Display',
  render: () => {
    const variants: TextVariant[] = ['plain', 'code', 'heading', 'quote', 'markdown'];

    return (
      <div style={{ maxWidth: '800px' }}>
        <h2 style={{ color: 'var(--text-primary)', marginBottom: 'var(--space-lg)' }}>
          TextWidget: Multi-Variant Text Display
        </h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: 'var(--space-xl)' }}>
          Renders text content with support for variants, truncation, and highlighting.
        </p>

        {variants.map((variant) => (
          <div key={variant} style={{ marginBottom: 'var(--space-xl)' }}>
            <h3 style={{
              color: 'var(--text-secondary)',
              fontSize: 'var(--font-size-sm)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginBottom: 'var(--space-sm)',
            }}>
              variant="{variant}"
            </h3>
            <TextWidget content={MOCK_TEXT_SAMPLES[variant]} variant={variant} />
          </div>
        ))}

        {/* Truncation Demo */}
        <div style={{ marginTop: 'var(--space-2xl)' }}>
          <h3 style={{
            color: 'var(--text-secondary)',
            fontSize: 'var(--font-size-sm)',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            marginBottom: 'var(--space-sm)',
          }}>
            Truncation (truncateLines=2)
          </h3>
          <TextWidget
            content={MOCK_TEXT_SAMPLES.plain}
            variant="plain"
            truncateLines={2}
          />
        </div>

        {/* Highlight Demo */}
        <div style={{ marginTop: 'var(--space-xl)' }}>
          <h3 style={{
            color: 'var(--text-secondary)',
            fontSize: 'var(--font-size-sm)',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            marginBottom: 'var(--space-sm)',
          }}>
            Highlighting (highlight="fox|dog")
          </h3>
          <TextWidget
            content={MOCK_TEXT_SAMPLES.plain}
            variant="plain"
            highlight="fox|dog"
          />
        </div>
      </div>
    );
  },
};

// =============================================================================
// 2. TableWidget Stories
// =============================================================================

export const TableWidgetStory: StoryObj = {
  name: '2. TableWidget - Data Tables',
  render: () => {
    const [selectedKeys, setSelectedKeys] = useState<string[]>([]);
    const [clickedRow, setClickedRow] = useState<Record<string, unknown> | null>(null);

    return (
      <div style={{ maxWidth: '1000px' }}>
        <h2 style={{ color: 'var(--text-primary)', marginBottom: 'var(--space-lg)' }}>
          TableWidget: Sortable, Paginated Data Tables
        </h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: 'var(--space-xl)' }}>
          Features column sorting, pagination, and row selection.
        </p>

        {/* Basic Table */}
        <div style={{ marginBottom: 'var(--space-2xl)' }}>
          <h3 style={{
            color: 'var(--text-secondary)',
            marginBottom: 'var(--space-md)',
          }}>
            Basic Table (pageSize=5, sortable)
          </h3>
          <TableWidget
            columns={MOCK_TABLE_DATA.columns}
            rows={MOCK_TABLE_DATA.rows}
            pageSize={5}
            sortBy="health"
            sortDirection="desc"
          />
        </div>

        {/* Selectable Table */}
        <div style={{ marginBottom: 'var(--space-2xl)' }}>
          <h3 style={{
            color: 'var(--text-secondary)',
            marginBottom: 'var(--space-md)',
          }}>
            Selectable Table (selectable=true)
          </h3>
          <TableWidget
            columns={MOCK_TABLE_DATA.columns}
            rows={MOCK_TABLE_DATA.rows.slice(0, 5)}
            pageSize={0}
            selectable
            selectedKeys={selectedKeys}
            onSelectionChange={setSelectedKeys}
            onRowClick={setClickedRow}
          />
          {selectedKeys.length > 0 && (
            <p style={{ color: 'var(--text-muted)', marginTop: 'var(--space-md)' }}>
              Selected: {selectedKeys.join(', ')}
            </p>
          )}
          {clickedRow && (
            <p style={{ color: 'var(--text-muted)', marginTop: 'var(--space-sm)' }}>
              Clicked: {JSON.stringify(clickedRow)}
            </p>
          )}
        </div>
      </div>
    );
  },
};

// =============================================================================
// 3. GraphWidget Stories
// =============================================================================

export const GraphWidgetStory: StoryObj = {
  name: '3. GraphWidget - Data Visualization',
  render: () => {
    const chartTypes: GraphType[] = ['line', 'bar', 'pie', 'doughnut', 'radar'];

    return (
      <div style={{ maxWidth: '1000px' }}>
        <h2 style={{ color: 'var(--text-primary)', marginBottom: 'var(--space-lg)' }}>
          GraphWidget: Chart.js Visualization
        </h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: 'var(--space-xl)' }}>
          Supports line, bar, pie, doughnut, and radar charts.
          Currently renders placeholders (install chart.js for full interactivity).
        </p>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
          gap: 'var(--space-xl)',
        }}>
          {chartTypes.map((type) => (
            <div key={type}>
              <h3 style={{
                color: 'var(--text-secondary)',
                marginBottom: 'var(--space-md)',
                textTransform: 'capitalize',
              }}>
                {type} Chart
              </h3>
              <GraphWidget
                type={type}
                labels={MOCK_GRAPH_DATA[type].labels}
                datasets={MOCK_GRAPH_DATA[type].datasets}
                title={MOCK_GRAPH_DATA[type].datasets[0].label}
              />
            </div>
          ))}
        </div>
      </div>
    );
  },
};

// =============================================================================
// 4. ProgressWidget Stories
// =============================================================================

export const ProgressWidgetStory: StoryObj = {
  name: '4. ProgressWidget - Progress Indicators',
  render: () => {
    const [animatedProgress, setAnimatedProgress] = useState(0);

    useEffect(() => {
      const interval = setInterval(() => {
        setAnimatedProgress((p) => (p >= 100 ? 0 : p + 5));
      }, 200);
      return () => clearInterval(interval);
    }, []);

    return (
      <div style={{ maxWidth: '700px' }}>
        <h2 style={{ color: 'var(--text-primary)', marginBottom: 'var(--space-lg)' }}>
          ProgressWidget: Progress Bars & Step Indicators
        </h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: 'var(--space-xl)' }}>
          Two variants: bar (percentage) and steps (multi-step process).
        </p>

        {/* Progress Bar Variant */}
        <div style={{ marginBottom: 'var(--space-2xl)' }}>
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
            Bar Variant
          </h3>

          <div style={{ marginBottom: 'var(--space-lg)' }}>
            <ProgressWidget value={75} label="Agent Health" />
          </div>

          <div style={{ marginBottom: 'var(--space-lg)' }}>
            <ProgressWidget value={animatedProgress} label="Processing" />
          </div>

          <div style={{ marginBottom: 'var(--space-lg)' }}>
            <ProgressWidget indeterminate label="Loading agents..." />
          </div>
        </div>

        {/* Steps Variant */}
        <div style={{ marginBottom: 'var(--space-2xl)' }}>
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
            Steps Variant
          </h3>
          <ProgressWidget variant="steps" steps={MOCK_PROGRESS_STEPS} />
        </div>

        {/* All Steps Complete */}
        <div style={{ marginBottom: 'var(--space-xl)' }}>
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
            Steps Complete
          </h3>
          <ProgressWidget
            variant="steps"
            steps={MOCK_PROGRESS_STEPS.map((s) => ({ ...s, completed: true, current: false }))}
          />
        </div>
      </div>
    );
  },
};

// =============================================================================
// 5. SelectWidget Stories
// =============================================================================

export const SelectWidgetStory: StoryObj = {
  name: '5. SelectWidget - Selection Input',
  render: () => {
    const [singleValue, setSingleValue] = useState<string>('');
    const [multiValue, setMultiValue] = useState<string[]>([]);
    const [searchValue, setSearchValue] = useState<string>('');

    return (
      <div style={{ maxWidth: '500px' }}>
        <h2 style={{ color: 'var(--text-primary)', marginBottom: 'var(--space-lg)' }}>
          SelectWidget: Single/Multi Select
        </h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: 'var(--space-xl)' }}>
          Features single/multiple selection, searchable options, and grouped items.
        </p>

        {/* Single Select */}
        <div style={{ marginBottom: 'var(--space-xl)' }}>
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
            Single Select
          </h3>
          <SelectWidget
            options={MOCK_SELECT_OPTIONS}
            value={singleValue}
            onChange={(v) => setSingleValue(v as string)}
            placeholder="Choose an agent..."
          />
          {singleValue && (
            <p style={{ color: 'var(--text-muted)', marginTop: 'var(--space-sm)' }}>
              Selected: {singleValue}
            </p>
          )}
        </div>

        {/* Multiple Select */}
        <div style={{ marginBottom: 'var(--space-xl)' }}>
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
            Multiple Select
          </h3>
          <SelectWidget
            options={MOCK_SELECT_OPTIONS}
            value={multiValue}
            onChange={(v) => setMultiValue(v as string[])}
            multiple
            placeholder="Select multiple..."
          />
          {multiValue.length > 0 && (
            <p style={{ color: 'var(--text-muted)', marginTop: 'var(--space-sm)' }}>
              Selected: {multiValue.join(', ')}
            </p>
          )}
        </div>

        {/* Searchable */}
        <div style={{ marginBottom: 'var(--space-xl)' }}>
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
            Searchable Select
          </h3>
          <SelectWidget
            options={MOCK_SELECT_OPTIONS}
            value={searchValue}
            onChange={(v) => setSearchValue(v as string)}
            searchable
            placeholder="Search agents..."
          />
        </div>

        {/* Disabled */}
        <div style={{ marginBottom: 'var(--space-xl)' }}>
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
            Disabled Select
          </h3>
          <SelectWidget
            options={MOCK_SELECT_OPTIONS}
            value="brain"
            disabled
          />
        </div>
      </div>
    );
  },
};

// =============================================================================
// 6. ConfirmWidget Stories
// =============================================================================

export const ConfirmWidgetStory: StoryObj = {
  name: '6. ConfirmWidget - Binary Confirmation',
  render: () => {
    const [inlineResult, setInlineResult] = useState<string | null>(null);
    const [showModal, setShowModal] = useState(false);
    const [modalResult, setModalResult] = useState<string | null>(null);

    return (
      <div style={{ maxWidth: '600px' }}>
        <h2 style={{ color: 'var(--text-primary)', marginBottom: 'var(--space-lg)' }}>
          ConfirmWidget: Binary Confirmation
        </h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: 'var(--space-xl)' }}>
          Confirm/Cancel with keyboard support (Enter to confirm, Escape to cancel).
        </p>

        {/* Inline Variant */}
        <div style={{ marginBottom: 'var(--space-2xl)' }}>
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
            Inline Variant
          </h3>
          <ConfirmWidget
            message="Are you sure you want to crystallize this decision?"
            confirmLabel="Crystallize"
            cancelLabel="Cancel"
            onConfirm={() => setInlineResult('confirmed')}
            onCancel={() => setInlineResult('cancelled')}
          />
          {inlineResult && (
            <p style={{ color: 'var(--text-muted)', marginTop: 'var(--space-md)' }}>
              Result: {inlineResult}
            </p>
          )}
        </div>

        {/* Destructive Variant */}
        <div style={{ marginBottom: 'var(--space-2xl)' }}>
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
            Destructive Action
          </h3>
          <ConfirmWidget
            message="This will permanently delete all witness marks. This action cannot be undone."
            confirmLabel="Delete All"
            cancelLabel="Keep Marks"
            destructive
            onConfirm={() => alert('Deleted!')}
            onCancel={() => alert('Cancelled')}
          />
        </div>

        {/* Modal Trigger */}
        <div style={{ marginBottom: 'var(--space-xl)' }}>
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
            Modal Variant
          </h3>
          <button
            onClick={() => setShowModal(true)}
            style={{
              padding: 'var(--space-sm) var(--space-md)',
              background: 'var(--accent-primary)',
              color: 'var(--surface-0)',
              border: 'none',
              borderRadius: 'var(--radius-subtle)',
              cursor: 'pointer',
            }}
          >
            Open Modal Confirmation
          </button>
          {modalResult && (
            <p style={{ color: 'var(--text-muted)', marginTop: 'var(--space-sm)' }}>
              Modal result: {modalResult}
            </p>
          )}
        </div>

        {/* Modal */}
        {showModal && (
          <ConfirmWidget
            variant="modal"
            message="Override the agent's refusal? This will consume 25 tokens."
            confirmLabel="Override"
            cancelLabel="Respect Refusal"
            destructive
            onConfirm={() => {
              setModalResult('overridden');
              setShowModal(false);
            }}
            onCancel={() => {
              setModalResult('respected');
              setShowModal(false);
            }}
          />
        )}
      </div>
    );
  },
};

// =============================================================================
// 7. StreamWidget Stories
// =============================================================================

export const StreamWidgetStory: StoryObj = {
  name: '7. StreamWidget - Streaming Text',
  render: () => {
    const [textChunks, setTextChunks] = useState<string[]>([]);
    const [codeChunks, setCodeChunks] = useState<string[]>([]);
    const [isComplete, setIsComplete] = useState(false);

    const STREAM_TEXT = [
      'Analyzing codebase structure...\n',
      'Found 24 agents across 8 domains.\n',
      'Tracing AGENTESE invocation paths...\n',
      'Building projection graph...\n',
      'Optimizing widget selection...\n',
      '\nComplete! ',
      'Discovered 156 unique paths ',
      'with 98.2% coverage.\n',
    ];

    const STREAM_CODE = [
      'async function analyzeAgents() {\n',
      '  const agents = await gateway.discover();\n',
      '  const paths = agents.flatMap(a => a.paths);\n',
      '  \n',
      '  for (const path of paths) {\n',
      '    const result = await logos.invoke(path);\n',
      '    await witness.mark(result);\n',
      '  }\n',
      '  \n',
      '  return { agents, paths };\n',
      '}\n',
    ];

    useEffect(() => {
      let textIndex = 0;
      let codeIndex = 0;

      const textInterval = setInterval(() => {
        if (textIndex < STREAM_TEXT.length) {
          setTextChunks((prev) => [...prev, STREAM_TEXT[textIndex]]);
          textIndex++;
        } else {
          setIsComplete(true);
          clearInterval(textInterval);
        }
      }, 400);

      const codeInterval = setInterval(() => {
        if (codeIndex < STREAM_CODE.length) {
          setCodeChunks((prev) => [...prev, STREAM_CODE[codeIndex]]);
          codeIndex++;
        } else {
          clearInterval(codeInterval);
        }
      }, 300);

      return () => {
        clearInterval(textInterval);
        clearInterval(codeInterval);
      };
    }, []);

    const resetStream = () => {
      setTextChunks([]);
      setCodeChunks([]);
      setIsComplete(false);
      // Re-trigger the effect (hacky but works for demo)
      window.location.reload();
    };

    return (
      <div style={{ maxWidth: '700px' }}>
        <h2 style={{ color: 'var(--text-primary)', marginBottom: 'var(--space-lg)' }}>
          StreamWidget: Streaming Text Display
        </h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: 'var(--space-xl)' }}>
          Live streaming with blinking cursor and auto-scroll.
        </p>

        {/* Text Variant */}
        <div style={{ marginBottom: 'var(--space-2xl)' }}>
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
            Text Stream
          </h3>
          <StreamWidget
            chunks={textChunks}
            complete={isComplete}
            showCursor
            autoScroll
            maxHeight={200}
          />
        </div>

        {/* Code Variant */}
        <div style={{ marginBottom: 'var(--space-xl)' }}>
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
            Code Stream
          </h3>
          <StreamWidget
            chunks={codeChunks}
            complete={codeChunks.length >= STREAM_CODE.length}
            variant="code"
            showCursor
            autoScroll
            maxHeight={300}
          />
        </div>

        <button
          onClick={resetStream}
          style={{
            padding: 'var(--space-sm) var(--space-md)',
            background: 'var(--surface-2)',
            color: 'var(--text-primary)',
            border: '1px solid var(--surface-3)',
            borderRadius: 'var(--radius-subtle)',
            cursor: 'pointer',
          }}
        >
          Restart Streams
        </button>
      </div>
    );
  },
};

// =============================================================================
// 8. ErrorPanel Stories
// =============================================================================

export const ErrorPanelStory: StoryObj = {
  name: '8. ErrorPanel - Error Display',
  render: () => {
    const categories: ErrorCategory[] = ['network', 'notFound', 'permission', 'timeout', 'validation', 'unknown'];

    return (
      <div style={{ maxWidth: '700px' }}>
        <h2 style={{ color: 'var(--text-primary)', marginBottom: 'var(--space-lg)' }}>
          ErrorPanel: Technical Error Display
        </h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: 'var(--space-xl)' }}>
          Category-specific styling with retry affordance for network/timeout errors.
        </p>

        {categories.map((category) => (
          <div key={category} style={{ marginBottom: 'var(--space-lg)' }}>
            <ErrorPanel
              error={MOCK_ERROR_BY_CATEGORY[category]}
              onRetry={() => alert(`Retrying ${category}...`)}
            />
          </div>
        ))}

        {/* Without Retry */}
        <div style={{ marginTop: 'var(--space-2xl)' }}>
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
            With Retry Disabled
          </h3>
          <ErrorPanel
            error={MOCK_ERROR_BY_CATEGORY.network}
            showRetry={false}
          />
        </div>
      </div>
    );
  },
};

// =============================================================================
// 9. RefusalPanel Stories
// =============================================================================

export const RefusalPanelStory: StoryObj = {
  name: '9. RefusalPanel - Semantic Refusal',
  render: () => {
    const refusalVariants: RefusalInfo[] = [
      MOCK_REFUSAL,
      {
        reason: 'Accessing self.soul.core requires elevated trust level.',
        consentRequired: 'Multi-factor authentication',
        appealTo: 'self.soul.elevate',
        overrideCost: null,
      },
      {
        reason: 'This operation would exceed your daily token budget.',
        consentRequired: null,
        appealTo: 'world.billing.upgrade',
        overrideCost: 100,
      },
      {
        reason: 'Agent determined this path leads to suboptimal outcomes.',
        consentRequired: null,
        appealTo: null,
        overrideCost: null,
      },
    ];

    return (
      <div style={{ maxWidth: '700px' }}>
        <h2 style={{ color: 'var(--text-primary)', marginBottom: 'var(--space-lg)' }}>
          RefusalPanel: Semantic Refusal Display
        </h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: 'var(--space-xl)' }}>
          Distinct from errors - refusals are intentional agent decisions.
          Uses purple/magenta styling to differentiate.
        </p>

        {refusalVariants.map((refusal, i) => (
          <div key={i} style={{ marginBottom: 'var(--space-lg)' }}>
            <RefusalPanel
              refusal={refusal}
              onAppeal={() => alert(`Appealing to ${refusal.appealTo}...`)}
              onOverride={() => alert(`Overriding for ${refusal.overrideCost} tokens...`)}
            />
          </div>
        ))}

        {/* Without Actions */}
        <div style={{ marginTop: 'var(--space-2xl)' }}>
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
            Read-Only (no appeal/override)
          </h3>
          <RefusalPanel
            refusal={MOCK_REFUSAL}
            showAppeal={false}
            showOverride={false}
          />
        </div>
      </div>
    );
  },
};

// =============================================================================
// 10. CachedBadge Stories
// =============================================================================

export const CachedBadgeStory: StoryObj = {
  name: '10. CachedBadge - Cache Indicator',
  render: () => {
    const cacheVariants: CacheMeta[] = [
      {
        isCached: true,
        cachedAt: new Date(Date.now() - 30 * 1000).toISOString(), // 30 seconds ago
        ttlSeconds: 300,
        cacheKey: 'recent-cache',
        deterministic: true,
      },
      {
        isCached: true,
        cachedAt: new Date(Date.now() - 5 * 60 * 1000).toISOString(), // 5 minutes ago
        ttlSeconds: 300,
        cacheKey: 'medium-cache',
        deterministic: false,
      },
      {
        isCached: true,
        cachedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
        ttlSeconds: 3600,
        cacheKey: 'stale-cache',
        deterministic: true,
      },
      {
        isCached: true,
        cachedAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
        ttlSeconds: 86400,
        cacheKey: 'old-cache',
        deterministic: true,
      },
    ];

    return (
      <div style={{ maxWidth: '600px' }}>
        <h2 style={{ color: 'var(--text-primary)', marginBottom: 'var(--space-lg)' }}>
          CachedBadge: Cache Indicator
        </h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: 'var(--space-xl)' }}>
          Prominent [CACHED] badge with age tooltip. Amber/yellow styling.
        </p>

        {/* Inline Variants */}
        <div style={{ marginBottom: 'var(--space-2xl)' }}>
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
            Inline Position
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
            {cacheVariants.map((cache, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
                <CachedBadge cache={cache} position="inline" />
                <span style={{ color: 'var(--text-muted)', fontSize: 'var(--font-size-sm)' }}>
                  (hover for tooltip)
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Absolute Position */}
        <div style={{ marginBottom: 'var(--space-xl)' }}>
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
            Absolute Position (top-right of container)
          </h3>
          <div style={{
            position: 'relative',
            padding: 'var(--space-lg)',
            background: 'var(--surface-1)',
            border: '1px solid var(--surface-3)',
            borderRadius: 'var(--radius-bare)',
            minHeight: '100px',
          }}>
            <CachedBadge cache={MOCK_CACHE} position="absolute" />
            <p style={{ color: 'var(--text-secondary)' }}>
              Content area with absolute-positioned cache badge.
            </p>
          </div>
        </div>
      </div>
    );
  },
};

// =============================================================================
// 11. Gallery Components
// =============================================================================

export const GalleryComponentsStory: StoryObj = {
  name: '11. Gallery Components',
  render: () => {
    const [activeCategory, setActiveCategory] = useState<GalleryCategory | 'ALL'>('ALL');
    const [overrides, setOverrides] = useState<GalleryOverrides>({ entropy: 0 });

    const mockCategories: GalleryCategory[] = ['PRIMITIVES', 'CARDS', 'CHROME', 'STREAMING'];
    const mockCounts: Partial<Record<GalleryCategory, number>> = {
      PRIMITIVES: 5,
      CARDS: 3,
      CHROME: 2,
      STREAMING: 4,
    };

    const mockPilot: PilotResponse = {
      name: 'TextWidget Demo',
      description: 'Multi-variant text rendering with syntax highlighting and truncation.',
      category: 'PRIMITIVES',
      tags: ['text', 'code', 'markdown'],
      projections: {
        cli: '$ kg text --variant=code "const x = 42;"',
        html: '<div class="kgents-text-code"><code>const x = 42;</code></div>',
        json: { variant: 'code', content: 'const x = 42;' },
      },
    };

    return (
      <div style={{ maxWidth: '900px' }}>
        <h2 style={{ color: 'var(--text-primary)', marginBottom: 'var(--space-lg)' }}>
          Gallery Components
        </h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: 'var(--space-xl)' }}>
          Components for the Projection Component Gallery page.
        </p>

        {/* CategoryFilter */}
        <div style={{ marginBottom: 'var(--space-2xl)' }}>
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
            CategoryFilter
          </h3>
          <div style={{
            padding: 'var(--space-md)',
            background: 'var(--surface-1)',
            borderRadius: 'var(--radius-bare)',
          }}>
            <CategoryFilter
              categories={mockCategories}
              activeCategory={activeCategory}
              onChange={setActiveCategory}
              counts={mockCounts}
            />
          </div>
          <p style={{ color: 'var(--text-muted)', marginTop: 'var(--space-sm)' }}>
            Active: {activeCategory}
          </p>
        </div>

        {/* OverrideControls */}
        <div style={{ marginBottom: 'var(--space-2xl)' }}>
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
            OverrideControls
          </h3>
          <div style={{
            padding: 'var(--space-md)',
            background: 'var(--surface-1)',
            borderRadius: 'var(--radius-bare)',
          }}>
            <OverrideControls
              overrides={overrides}
              onChange={setOverrides}
            />
          </div>
          <p style={{ color: 'var(--text-muted)', marginTop: 'var(--space-sm)' }}>
            Overrides: {JSON.stringify(overrides)}
          </p>
        </div>

        {/* ProjectionView */}
        <div style={{ marginBottom: 'var(--space-2xl)' }}>
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
            ProjectionView (CLI/HTML/JSON tabs)
          </h3>
          <div style={{
            padding: 'var(--space-md)',
            background: 'var(--surface-1)',
            borderRadius: 'var(--radius-bare)',
            height: '200px',
          }}>
            <ProjectionView
              projections={mockPilot.projections}
              defaultTab="cli"
            />
          </div>
        </div>

        {/* PilotCard */}
        <div style={{ marginBottom: 'var(--space-xl)' }}>
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-md)' }}>
            PilotCard
          </h3>
          <div style={{ maxWidth: '400px' }}>
            <PilotCard
              pilot={mockPilot}
              onClick={() => alert('Clicked!')}
            />
          </div>
        </div>
      </div>
    );
  },
};

// =============================================================================
// 12. Combined Widget Demo
// =============================================================================

export const CombinedDemoStory: StoryObj = {
  name: '12. Combined Widget Demo',
  render: () => {
    const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error' | 'refusal'>('idle');
    const [progress, setProgress] = useState(0);

    const simulateInvocation = () => {
      setStatus('loading');
      setProgress(0);

      const interval = setInterval(() => {
        setProgress((p) => {
          if (p >= 100) {
            clearInterval(interval);
            // Randomly choose outcome
            const outcomes: ('success' | 'error' | 'refusal')[] = ['success', 'error', 'refusal'];
            setStatus(outcomes[Math.floor(Math.random() * outcomes.length)]);
            return 100;
          }
          return p + 10;
        });
      }, 200);
    };

    return (
      <div style={{ maxWidth: '700px' }}>
        <h2 style={{ color: 'var(--text-primary)', marginBottom: 'var(--space-lg)' }}>
          Combined Widget Demo
        </h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: 'var(--space-xl)' }}>
          Demonstrates how widgets compose together in a real invocation flow.
        </p>

        {/* Control */}
        <div style={{ marginBottom: 'var(--space-xl)' }}>
          <button
            onClick={simulateInvocation}
            disabled={status === 'loading'}
            style={{
              padding: 'var(--space-sm) var(--space-md)',
              background: status === 'loading' ? 'var(--surface-2)' : 'var(--accent-primary)',
              color: 'var(--surface-0)',
              border: 'none',
              borderRadius: 'var(--radius-subtle)',
              cursor: status === 'loading' ? 'not-allowed' : 'pointer',
            }}
          >
            {status === 'loading' ? 'Invoking...' : 'Invoke Agent'}
          </button>
          <button
            onClick={() => setStatus('idle')}
            style={{
              marginLeft: 'var(--space-sm)',
              padding: 'var(--space-sm) var(--space-md)',
              background: 'var(--surface-2)',
              color: 'var(--text-primary)',
              border: '1px solid var(--surface-3)',
              borderRadius: 'var(--radius-subtle)',
              cursor: 'pointer',
            }}
          >
            Reset
          </button>
        </div>

        {/* Status Display */}
        <div style={{
          padding: 'var(--space-lg)',
          background: 'var(--surface-1)',
          border: '1px solid var(--surface-3)',
          borderRadius: 'var(--radius-bare)',
          position: 'relative',
        }}>
          {status === 'idle' && (
            <TextWidget
              content="Ready to invoke agent. Click the button to start."
              variant="plain"
            />
          )}

          {status === 'loading' && (
            <ProgressWidget value={progress} label="Invoking world.brain.analyze..." />
          )}

          {status === 'success' && (
            <>
              <CachedBadge cache={MOCK_CACHE} position="absolute" />
              <TextWidget
                content="Analysis Complete"
                variant="heading"
              />
              <div style={{ marginTop: 'var(--space-md)' }}>
                <TableWidget
                  columns={MOCK_TABLE_DATA.columns.slice(0, 3)}
                  rows={MOCK_TABLE_DATA.rows.slice(0, 3)}
                  pageSize={0}
                />
              </div>
            </>
          )}

          {status === 'error' && (
            <ErrorPanel
              error={MOCK_ERROR_BY_CATEGORY.network}
              onRetry={simulateInvocation}
            />
          )}

          {status === 'refusal' && (
            <RefusalPanel
              refusal={MOCK_REFUSAL}
              onAppeal={() => alert('Appealing...')}
              onOverride={() => {
                setStatus('success');
              }}
            />
          )}
        </div>
      </div>
    );
  },
};
