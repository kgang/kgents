/**
 * InteractiveTextGallery: Demonstrates the Interactive Text × Servo bridge.
 *
 * "The text IS the interface." - Interactive Text manifesto
 *
 * Pilots:
 * 1. AGENTESE Portal - Show interactive path tokens with hover/click
 * 2. Task Toggle - Show checkbox tokens with toggle interaction
 * 3. Code Region - Show code block tokens with syntax highlighting
 * 4. Badge Tokens - Show principle/requirement reference badges
 * 5. Mixed Document - Render a complete markdown as token stream
 * 6. Token Comparison - Show same content in different density modes
 *
 * @see protocols/agentese/projection/tokens_to_scene.py - Bridge
 * @see components/servo/MeaningTokenRenderer.tsx - Token renderer
 */

import { useState, useMemo, useCallback, useEffect } from 'react';
import { documentApi, type TaskToggleResponse, type DocumentParseResponse } from '@/api/client';
import {
  MeaningTokenRenderer,
  AGENTESEPortal,
  TaskToggle,
  CodeRegion,
  BadgeToken,
  type MeaningTokenContent,
  type MeaningTokenKind,
} from '@/components/servo/MeaningTokenRenderer';
import { SERVO_BG_CLASSES, SERVO_BORDER_CLASSES } from '@/components/servo/theme';
import { useWindowLayout } from '@/components/elastic';
import { PersonalityLoading } from '@/components/joy';

// =============================================================================
// Sample Data (from demos/interactive_text_demo.py)
// =============================================================================

const SAMPLE_AGENTESE_PATHS: MeaningTokenContent[] = [
  {
    token_type: 'agentese_path',
    source_text: '`self.brain.capture`',
    source_position: [0, 20],
    token_id: 'agentese:0:20',
    token_data: { path: 'self.brain.capture' },
    affordances: [
      { name: 'navigate', action: 'click', handler: 'navigate', enabled: true },
      { name: 'preview', action: 'hover', handler: 'preview', enabled: true },
    ],
  },
  {
    token_type: 'agentese_path',
    source_text: '`world.town.citizen`',
    source_position: [21, 42],
    token_id: 'agentese:21:42',
    token_data: { path: 'world.town.citizen' },
    affordances: [{ name: 'navigate', action: 'click', handler: 'navigate', enabled: true }],
  },
  {
    token_type: 'agentese_path',
    source_text: '`concept.design.operad`',
    source_position: [43, 66],
    token_id: 'agentese:43:66',
    token_data: { path: 'concept.design.operad', is_ghost: true },
    affordances: [],
  },
];

const SAMPLE_TASKS: MeaningTokenContent[] = [
  {
    token_type: 'task_checkbox',
    source_text: '- [x] Create tokens_to_scene bridge',
    source_position: [0, 35],
    token_id: 'task:0:35',
    token_data: { checked: true, description: 'Create tokens_to_scene bridge' },
    affordances: [{ name: 'toggle', action: 'click', handler: 'toggle', enabled: true }],
  },
  {
    token_type: 'task_checkbox',
    source_text: '- [x] Add MeaningTokenRenderer',
    source_position: [36, 66],
    token_id: 'task:36:66',
    token_data: { checked: true, description: 'Add MeaningTokenRenderer' },
    affordances: [{ name: 'toggle', action: 'click', handler: 'toggle', enabled: true }],
  },
  {
    token_type: 'task_checkbox',
    source_text: '- [ ] Wire up AGENTESE navigation',
    source_position: [67, 100],
    token_id: 'task:67:100',
    token_data: { checked: false, description: 'Wire up AGENTESE navigation' },
    affordances: [{ name: 'toggle', action: 'click', handler: 'toggle', enabled: true }],
  },
  {
    token_type: 'task_checkbox',
    source_text: '- [ ] Add hover state display',
    source_position: [101, 130],
    token_id: 'task:101:130',
    token_data: { checked: false, description: 'Add hover state display' },
    affordances: [{ name: 'toggle', action: 'click', handler: 'toggle', enabled: true }],
  },
];

const SAMPLE_CODE: MeaningTokenContent = {
  token_type: 'code_block',
  source_text:
    '```python\n# Example agent composition\npipeline = AgentA >> AgentB >> AgentC\nresult = await pipeline.invoke(input)\n```',
  source_position: [0, 120],
  token_id: 'code:0:120',
  token_data: {
    language: 'python',
    code: '# Example agent composition\npipeline = AgentA >> AgentB >> AgentC\nresult = await pipeline.invoke(input)',
  },
  affordances: [
    { name: 'run', action: 'dblclick', handler: 'execute', enabled: true },
    { name: 'copy', action: 'click', handler: 'copy', enabled: true },
  ],
};

const SAMPLE_BADGES: MeaningTokenContent[] = [
  {
    token_type: 'principle_ref',
    source_text: '[P1]',
    source_position: [0, 4],
    token_id: 'principle:0:4',
    token_data: { principle_number: 1 },
    affordances: [{ name: 'expand', action: 'click', handler: 'show_principle', enabled: true }],
  },
  {
    token_type: 'principle_ref',
    source_text: '[P5]',
    source_position: [5, 9],
    token_id: 'principle:5:9',
    token_data: { principle_number: 5 },
    affordances: [{ name: 'expand', action: 'click', handler: 'show_principle', enabled: true }],
  },
  {
    token_type: 'requirement_ref',
    source_text: '[R2.1]',
    source_position: [10, 16],
    token_id: 'requirement:10:16',
    token_data: { requirement_id: '2.1' },
    affordances: [{ name: 'expand', action: 'click', handler: 'show_requirement', enabled: true }],
  },
];

// Note: SAMPLE_MARKDOWN is available for future use when backend parsing is integrated
// const SAMPLE_MARKDOWN = `
// # Interactive Text Demo
// Check \`self.brain.capture\` for memory operations.
// - [x] Create bridge
// - [ ] Wire navigation
// See [P1] (Tasteful) and [R2.1] for design rationale.
// `;

// =============================================================================
// Pilot Components
// =============================================================================

interface PilotContainerProps {
  title: string;
  subtitle: string;
  children: React.ReactNode;
  fullWidth?: boolean;
}

function PilotContainer({ title, subtitle, children, fullWidth }: PilotContainerProps) {
  return (
    <div
      className={`rounded-lg border border-emerald-800/30 bg-stone-900/50 overflow-hidden ${fullWidth ? '' : 'max-w-fit'}`}
    >
      <div className="px-4 py-2 bg-emerald-900/30 border-b border-emerald-800/30">
        <h3 className="font-medium text-sm text-emerald-200">{title}</h3>
        <p className="text-xs text-emerald-400/70">{subtitle}</p>
      </div>
      <div className="p-4">{children}</div>
    </div>
  );
}

/**
 * Pilot 1: AGENTESE Portal - Interactive path navigation
 */
function AGENTESEPortalPilot() {
  const [hoveredPath, setHoveredPath] = useState<string | null>(null);
  const [selectedPath, setSelectedPath] = useState<string | null>(null);

  const handlePathClick = useCallback((content: MeaningTokenContent) => {
    const path = content.token_data?.path as string;
    if (path) {
      setSelectedPath(path);
      // In production: navigate(`/${path}`) or open preview modal
    }
  }, []);

  const handlePathHover = useCallback((content: MeaningTokenContent, hovering: boolean) => {
    setHoveredPath(hovering ? (content.token_data?.path as string) : null);
  }, []);

  return (
    <PilotContainer title="AGENTESE Portal" subtitle="Interactive path tokens with navigate/hover">
      <div className="space-y-4">
        <div className="flex flex-wrap gap-3">
          {SAMPLE_AGENTESE_PATHS.map((token) => (
            <div
              key={token.token_id}
              onMouseEnter={() => handlePathHover(token, true)}
              onMouseLeave={() => handlePathHover(token, false)}
            >
              <AGENTESEPortal
                content={token}
                isSelected={selectedPath === token.token_data?.path}
                onClick={() => handlePathClick(token)}
              />
            </div>
          ))}
        </div>

        {/* Interaction state display */}
        <div className="text-xs text-gray-500 border-t border-gray-800 pt-3 mt-3">
          <div className="grid grid-cols-2 gap-2">
            <div>
              <span className="text-gray-400">Selected: </span>
              <code className="text-emerald-400">{selectedPath ?? 'none'}</code>
            </div>
            <div>
              <span className="text-gray-400">Hovered: </span>
              <code className="text-emerald-400">{hoveredPath ?? 'none'}</code>
            </div>
          </div>
        </div>

        {/* Affordance explanation */}
        <div className="text-xs text-gray-500 space-y-1">
          <p>
            <span className="text-emerald-400">Click</span> to select a path (would navigate in
            production)
          </p>
          <p>
            <span className="text-gray-400 italic">Ghost paths</span> (dimmed) have no navigation
            target
          </p>
        </div>
      </div>
    </PilotContainer>
  );
}

/**
 * Pilot 2: Task Toggle - Backend-wired checkboxes
 *
 * Now calls documentApi.toggleTask() to demonstrate:
 * - Real backend mutation (in-memory for this demo)
 * - TraceWitness capture for each toggle
 * - File update status
 */
function TaskTogglePilot() {
  const [tasks, setTasks] = useState(SAMPLE_TASKS);
  const [lastToggle, setLastToggle] = useState<TaskToggleResponse | null>(null);
  const [isToggling, setIsToggling] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleToggle = useCallback(
    async (tokenId: string, lineNumber: number) => {
      setIsToggling(tokenId);
      setError(null);

      // Build markdown text from current tasks for backend toggle
      const taskText = tasks
        .map((t) => {
          const checked = t.token_data?.checked ? 'x' : ' ';
          return `- [${checked}] ${t.token_data?.description}`;
        })
        .join('\n');

      try {
        // Call backend - uses in-memory text mode
        const result = await documentApi.toggleTask({
          text: taskText,
          line_number: lineNumber,
        });

        setLastToggle(result);

        if (result.success) {
          // Update local state to match backend
          setTasks((prev) =>
            prev.map((task) =>
              task.token_id === tokenId
                ? {
                    ...task,
                    token_data: {
                      ...task.token_data,
                      checked: result.new_state,
                    },
                  }
                : task
            )
          );
        } else {
          setError(result.error ?? 'Toggle failed');
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Backend unavailable');
        // Fallback to local toggle for demo
        setTasks((prev) =>
          prev.map((task) =>
            task.token_id === tokenId
              ? {
                  ...task,
                  token_data: {
                    ...task.token_data,
                    checked: !task.token_data?.checked,
                  },
                }
              : task
          )
        );
      } finally {
        setIsToggling(null);
      }
    },
    [tasks]
  );

  const completedCount = tasks.filter((t) => t.token_data?.checked).length;

  return (
    <PilotContainer title="Task Toggle" subtitle="Backend-wired with TraceWitness">
      <div className="space-y-3">
        {tasks.map((task, idx) => (
          <div key={task.token_id} className="relative">
            <TaskToggle
              content={task}
              isSelected={false}
              onClick={() => handleToggle(task.token_id, idx + 1)}
            />
            {isToggling === task.token_id && (
              <div className="absolute right-2 top-1/2 -translate-y-1/2">
                <div className="w-3 h-3 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
              </div>
            )}
          </div>
        ))}

        {/* Progress indicator */}
        <div className="flex items-center gap-2 pt-2 border-t border-gray-800 mt-3">
          <div className="flex-1 h-1.5 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-emerald-500 transition-all duration-300"
              style={{ width: `${(completedCount / tasks.length) * 100}%` }}
            />
          </div>
          <span className="text-xs text-gray-400">
            {completedCount}/{tasks.length}
          </span>
        </div>

        {/* Backend response display */}
        {(lastToggle || error) && (
          <div className="pt-3 border-t border-gray-800 mt-3 space-y-2">
            <div className="text-xs text-gray-400 font-medium">Last Toggle Result:</div>
            {error ? (
              <div className="text-xs text-amber-400 bg-amber-900/20 px-2 py-1 rounded">
                ⚠️ {error} (local fallback)
              </div>
            ) : lastToggle ? (
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-gray-500">Task: </span>
                  <span className="text-gray-300">{lastToggle.task_description}</span>
                </div>
                <div>
                  <span className="text-gray-500">State: </span>
                  <span className={lastToggle.new_state ? 'text-emerald-400' : 'text-gray-400'}>
                    {lastToggle.new_state ? '✓ checked' : '○ unchecked'}
                  </span>
                </div>
                <div className="col-span-2">
                  <span className="text-gray-500">TraceWitness: </span>
                  <code className="text-purple-400 text-[10px]">
                    {lastToggle.trace_witness_id ?? 'none'}
                  </code>
                </div>
                <div>
                  <span className="text-gray-500">File Updated: </span>
                  <span className={lastToggle.file_updated ? 'text-emerald-400' : 'text-gray-500'}>
                    {lastToggle.file_updated ? 'yes' : 'no (in-memory)'}
                  </span>
                </div>
              </div>
            ) : null}
          </div>
        )}
      </div>
    </PilotContainer>
  );
}

/**
 * Pilot 3: Code Region - Syntax highlighted code blocks
 */
function CodeRegionPilot() {
  const [executionState, setExecutionState] = useState<'idle' | 'running' | 'success'>('idle');

  const handleRun = useCallback(() => {
    setExecutionState('running');
    setTimeout(() => setExecutionState('success'), 1000);
    setTimeout(() => setExecutionState('idle'), 2500);
  }, []);

  return (
    <PilotContainer title="Code Region" subtitle="Code block with run/copy affordances" fullWidth>
      <div className="space-y-3">
        <CodeRegion content={SAMPLE_CODE} isSelected={false} onClick={handleRun} />

        {/* Execution state */}
        <div className="flex items-center gap-2 text-xs">
          {executionState === 'running' && (
            <PersonalityLoading jewel="gestalt" size="sm" action="process" />
          )}
          {executionState === 'success' && (
            <div className="flex items-center gap-1 text-emerald-400">
              <span>Executed successfully</span>
            </div>
          )}
          {executionState === 'idle' && (
            <span className="text-gray-500">Double-click to execute</span>
          )}
        </div>
      </div>
    </PilotContainer>
  );
}

/**
 * Pilot 4: Badge Tokens - Principle/Requirement references
 */
function BadgeTokensPilot() {
  const [expanded, setExpanded] = useState<string | null>(null);

  const principleDescriptions: Record<number, string> = {
    1: 'Tasteful — Each agent serves a clear, justified purpose',
    5: 'Composable — Agents are morphisms in a category',
  };

  return (
    <PilotContainer title="Badge Tokens" subtitle="Principle & requirement reference badges">
      <div className="space-y-4">
        <div className="flex flex-wrap gap-2">
          {SAMPLE_BADGES.map((badge) => (
            <BadgeToken
              key={badge.token_id}
              content={badge}
              kind={badge.token_type === 'principle_ref' ? 'PRINCIPLE_ANCHOR' : 'REQUIREMENT_TRACE'}
              isSelected={expanded === badge.token_id}
              onClick={() => setExpanded(expanded === badge.token_id ? null : badge.token_id)}
            />
          ))}
        </div>

        {/* Expanded principle/requirement */}
        {expanded && (
          <div className="p-3 rounded bg-amber-900/20 border border-amber-700/30 text-sm">
            {SAMPLE_BADGES.find((b) => b.token_id === expanded)?.token_type === 'principle_ref' ? (
              <p className="text-amber-200">
                {principleDescriptions[
                  SAMPLE_BADGES.find((b) => b.token_id === expanded)?.token_data
                    ?.principle_number as number
                ] ?? 'Principle description...'}
              </p>
            ) : (
              <p className="text-purple-200">
                Requirement R
                {String(
                  SAMPLE_BADGES.find((b) => b.token_id === expanded)?.token_data?.requirement_id ??
                    '?'
                )}
                : Functional specification details...
              </p>
            )}
          </div>
        )}
      </div>
    </PilotContainer>
  );
}

// Token type for mixed document rendering
interface DocumentToken {
  kind: MeaningTokenKind;
  content: MeaningTokenContent | string;
  label: string;
}

/**
 * Pilot 5: Mixed Document - Full markdown with all token types
 */
function MixedDocumentPilot() {
  // Simulated parsed document (in production, this would come from the backend)
  const documentTokens = useMemo(
    (): DocumentToken[] => [
      // Title
      { kind: 'PLAIN_TEXT', content: '# Interactive Text Demo\n\n', label: 'title' },
      {
        kind: 'PLAIN_TEXT',
        content: 'This demonstrates the unified projection surface.\n\n',
        label: 'intro',
      },
      // AGENTESE paths section
      { kind: 'PLAIN_TEXT', content: '## AGENTESE Paths\n\nCheck ', label: 'section' },
      {
        kind: 'AGENTESE_PORTAL',
        content: SAMPLE_AGENTESE_PATHS[0],
        label: SAMPLE_AGENTESE_PATHS[0].token_data?.path as string,
      },
      { kind: 'PLAIN_TEXT', content: ' for memory.\n\n', label: 'text' },
      // Tasks
      { kind: 'PLAIN_TEXT', content: '## Tasks\n\n', label: 'section' },
      ...SAMPLE_TASKS.slice(0, 2).map(
        (t): DocumentToken => ({
          kind: 'TASK_TOGGLE',
          content: t,
          label: t.token_data?.description as string,
        })
      ),
      // References
      { kind: 'PLAIN_TEXT', content: '\n## References: ', label: 'section' },
      ...SAMPLE_BADGES.map(
        (b): DocumentToken => ({
          kind: b.token_type === 'principle_ref' ? 'PRINCIPLE_ANCHOR' : 'REQUIREMENT_TRACE',
          content: b,
          label: b.source_text,
        })
      ),
    ],
    []
  );

  return (
    <PilotContainer
      title="Mixed Document"
      subtitle="Full markdown rendered as token stream"
      fullWidth
    >
      <div className={`p-4 rounded ${SERVO_BG_CLASSES.paper} ${SERVO_BORDER_CLASSES.paper} border`}>
        <div className="prose prose-invert prose-sm max-w-none">
          {documentTokens.map((token, i) => (
            <span key={i} className="inline">
              <MeaningTokenRenderer kind={token.kind} content={token.content} label={token.label} />
            </span>
          ))}
        </div>
      </div>
    </PilotContainer>
  );
}

/**
 * Pilot 6: Density Comparison - Same content at different densities
 */
function DensityComparisonPilot() {
  const densities = ['COMPACT', 'COMFORTABLE', 'SPACIOUS'] as const;
  const [activeDensity, setActiveDensity] = useState<(typeof densities)[number]>('COMFORTABLE');

  const gapClasses: Record<(typeof densities)[number], string> = {
    COMPACT: 'gap-1',
    COMFORTABLE: 'gap-2',
    SPACIOUS: 'gap-4',
  };

  const paddingClasses: Record<(typeof densities)[number], string> = {
    COMPACT: 'p-2',
    COMFORTABLE: 'p-3',
    SPACIOUS: 'p-5',
  };

  return (
    <PilotContainer
      title="Density Comparison"
      subtitle="Same content at COMPACT / COMFORTABLE / SPACIOUS"
      fullWidth
    >
      <div className="space-y-4">
        {/* Density selector */}
        <div className="flex gap-2">
          {densities.map((density) => (
            <button
              key={density}
              onClick={() => setActiveDensity(density)}
              className={`
                px-3 py-1 rounded text-xs font-medium transition-all
                ${
                  activeDensity === density
                    ? 'bg-emerald-600 text-white'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }
              `}
            >
              {density}
            </button>
          ))}
        </div>

        {/* Content at selected density */}
        <div
          className={`rounded bg-stone-800/50 border border-stone-700/50 ${paddingClasses[activeDensity]}`}
        >
          <div className={`flex flex-wrap ${gapClasses[activeDensity]}`}>
            {SAMPLE_AGENTESE_PATHS.slice(0, 2).map((token) => (
              <AGENTESEPortal key={token.token_id} content={token} isSelected={false} />
            ))}
          </div>
          <div className={`mt-2 ${gapClasses[activeDensity]} flex flex-wrap`}>
            {SAMPLE_BADGES.map((badge) => (
              <BadgeToken
                key={badge.token_id}
                content={badge}
                kind={
                  badge.token_type === 'principle_ref' ? 'PRINCIPLE_ANCHOR' : 'REQUIREMENT_TRACE'
                }
                isSelected={false}
              />
            ))}
          </div>
        </div>

        {/* Density metrics */}
        <div className="text-xs text-gray-500 grid grid-cols-3 gap-2">
          <div className="text-center">
            <div className="text-gray-400">Gap</div>
            <div className="font-mono">
              {activeDensity === 'COMPACT'
                ? '4px'
                : activeDensity === 'COMFORTABLE'
                  ? '8px'
                  : '16px'}
            </div>
          </div>
          <div className="text-center">
            <div className="text-gray-400">Padding</div>
            <div className="font-mono">
              {activeDensity === 'COMPACT'
                ? '8px'
                : activeDensity === 'COMFORTABLE'
                  ? '12px'
                  : '20px'}
            </div>
          </div>
          <div className="text-center">
            <div className="text-gray-400">Mode</div>
            <div className="font-mono text-emerald-400">{activeDensity}</div>
          </div>
        </div>
      </div>
    </PilotContainer>
  );
}

/**
 * Live Parse Demo - Backend-powered token detection
 *
 * Now calls documentApi.parse() to demonstrate:
 * - Real backend parsing (not client-side regex)
 * - Token type breakdown from backend
 * - Debounced input for performance
 */
function LiveParsePilot() {
  const [input, setInput] = useState(
    'Check `self.brain.capture` and see [P1] (Tasteful).\n\n- [x] First task done\n- [ ] Second task pending'
  );
  const [parseResult, setParseResult] = useState<DocumentParseResponse | null>(null);
  const [isParsing, setIsParsing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [useBackend, setUseBackend] = useState(true);

  // Client-side fallback detection (for when backend unavailable)
  const clientDetectedTokens = useMemo(() => {
    const tokens: { type: string; text: string; start: number }[] = [];
    const pathRegex = /`([a-z]+\.[a-z.]+)`/g;
    let match;
    while ((match = pathRegex.exec(input)) !== null) {
      tokens.push({ type: 'agentese_path', text: match[0], start: match.index });
    }
    const principleRegex = /\[P(\d+)\]/g;
    while ((match = principleRegex.exec(input)) !== null) {
      tokens.push({ type: 'principle_ref', text: match[0], start: match.index });
    }
    const taskRegex = /- \[([ xX])\] (.+?)(?:\n|$)/g;
    while ((match = taskRegex.exec(input)) !== null) {
      tokens.push({ type: 'task_checkbox', text: match[0], start: match.index });
    }
    return tokens.sort((a, b) => a.start - b.start);
  }, [input]);

  // Debounced backend parse
  const parseWithBackend = useCallback(
    async (text: string) => {
      if (!useBackend || !text.trim()) {
        setParseResult(null);
        return;
      }
      setIsParsing(true);
      setError(null);
      try {
        const result = await documentApi.parse(text);
        setParseResult(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Parse failed');
        setParseResult(null);
      } finally {
        setIsParsing(false);
      }
    },
    [useBackend]
  );

  // Debounce input changes (300ms)
  const [debouncedInput, setDebouncedInput] = useState(input);
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedInput(input), 300);
    return () => clearTimeout(timer);
  }, [input]);

  // Parse when debounced input changes
  useEffect(() => {
    if (useBackend) {
      parseWithBackend(debouncedInput);
    }
  }, [debouncedInput, useBackend, parseWithBackend]);

  // Use backend results or client fallback
  const tokenTypes = parseResult?.token_types ?? {};
  const tokenCount = parseResult?.token_count ?? clientDetectedTokens.length;

  // Map token_types to display format
  const displayTokens =
    useBackend && parseResult
      ? Object.entries(tokenTypes).map(([type, count]) => ({ type, count: count as number }))
      : Object.entries(
          clientDetectedTokens.reduce(
            (acc, t) => ({ ...acc, [t.type]: (acc[t.type] || 0) + 1 }),
            {} as Record<string, number>
          )
        ).map(([type, count]) => ({ type, count }));

  const tokenColorClass = (type: string) => {
    if (type.includes('agentese')) return 'bg-emerald-800 text-emerald-200';
    if (type.includes('principle')) return 'bg-amber-800 text-amber-200';
    if (type.includes('task')) return 'bg-stone-700 text-stone-200';
    if (type.includes('code')) return 'bg-blue-800 text-blue-200';
    return 'bg-gray-700 text-gray-200';
  };

  return (
    <PilotContainer
      title="Live Parse"
      subtitle={
        useBackend ? 'Backend-powered via self.document.parse' : 'Client-side regex fallback'
      }
      fullWidth
    >
      <div className="grid md:grid-cols-2 gap-4">
        {/* Input */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-xs text-gray-400">Markdown Input</label>
            <button
              onClick={() => setUseBackend(!useBackend)}
              className={`text-xs px-2 py-0.5 rounded transition-colors ${
                useBackend ? 'bg-emerald-800/50 text-emerald-300' : 'bg-gray-700 text-gray-400'
              }`}
            >
              {useBackend ? '✓ Backend' : '○ Client'}
            </button>
          </div>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="w-full h-40 p-3 rounded bg-stone-800 border border-stone-700 text-gray-200 text-sm font-mono resize-none focus:outline-none focus:border-emerald-600"
            placeholder="Type markdown with AGENTESE paths, tasks, principles..."
          />
        </div>

        {/* Output */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-xs text-gray-400">
              Tokens ({tokenCount})
              {isParsing && <span className="ml-2 text-emerald-400">parsing...</span>}
            </label>
          </div>
          <div className="h-40 p-3 rounded bg-stone-800/50 border border-stone-700/50 overflow-auto">
            {error ? (
              <div className="text-amber-400 text-sm">⚠️ {error}</div>
            ) : displayTokens.length === 0 ? (
              <div className="text-gray-500 text-sm">No tokens detected...</div>
            ) : (
              <div className="space-y-2">
                {displayTokens.map(({ type, count }, i) => (
                  <div key={i} className="flex items-center justify-between text-sm">
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-medium ${tokenColorClass(type)}`}
                    >
                      {type}
                    </span>
                    <span className="text-gray-400 font-mono">×{count}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Backend status */}
      {useBackend && parseResult && (
        <div className="mt-3 pt-3 border-t border-gray-800 text-xs text-gray-500">
          <span className="text-gray-400">Scene nodes: </span>
          <span className="text-emerald-400 font-mono">{parseResult.token_count}</span>
          <span className="mx-2">|</span>
          <span className="text-gray-400">Source: </span>
          <code className="text-purple-400">self.document.parse</code>
        </div>
      )}
    </PilotContainer>
  );
}

// =============================================================================
// Main Page Component
// =============================================================================

export default function InteractiveTextGallery() {
  const { density } = useWindowLayout();

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col bg-stone-950 overflow-auto">
      {/* Header */}
      <div className="bg-emerald-900/30 border-b border-emerald-800/30 px-4 py-3">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold text-emerald-100">Interactive Text Gallery</h1>
            <p className="text-sm text-emerald-400/70">
              "The text IS the interface" — Token × Servo bridge demonstration
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500">Current density:</span>
            <span className="px-2 py-0.5 rounded text-xs bg-emerald-800/50 text-emerald-300 capitalize">
              {density}
            </span>
          </div>
        </div>
      </div>

      {/* Gallery content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Live Parse */}
          <section>
            <h2 className="text-sm font-semibold text-emerald-300 uppercase tracking-wider mb-4">
              Live Parsing
            </h2>
            <LiveParsePilot />
          </section>

          {/* Token Types */}
          <section>
            <h2 className="text-sm font-semibold text-emerald-300 uppercase tracking-wider mb-4">
              Token Types
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <AGENTESEPortalPilot />
              <TaskTogglePilot />
            </div>
          </section>

          {/* Code & Badges */}
          <section>
            <h2 className="text-sm font-semibold text-emerald-300 uppercase tracking-wider mb-4">
              Code & References
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <CodeRegionPilot />
              <BadgeTokensPilot />
            </div>
          </section>

          {/* Document Rendering */}
          <section>
            <h2 className="text-sm font-semibold text-emerald-300 uppercase tracking-wider mb-4">
              Document Rendering
            </h2>
            <MixedDocumentPilot />
          </section>

          {/* Density */}
          <section>
            <h2 className="text-sm font-semibold text-emerald-300 uppercase tracking-wider mb-4">
              Density Modes
            </h2>
            <DensityComparisonPilot />
          </section>

          {/* Architecture Reference */}
          <section>
            <h2 className="text-sm font-semibold text-emerald-300 uppercase tracking-wider mb-4">
              Architecture
            </h2>
            <PilotContainer
              title="Token → Scene → React Pipeline"
              subtitle="How Interactive Text flows to the screen"
              fullWidth
            >
              <div className="font-mono text-xs text-gray-400 space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-amber-400">Markdown</span>
                  <span className="text-gray-600">→</span>
                  <span className="text-emerald-400">parse_markdown()</span>
                  <span className="text-gray-600">→</span>
                  <span className="text-amber-400">ParsedDocument</span>
                </div>
                <div className="flex items-center gap-2 pl-8">
                  <span className="text-gray-600">→</span>
                  <span className="text-emerald-400">tokens_to_scene_graph()</span>
                  <span className="text-gray-600">→</span>
                  <span className="text-amber-400">SceneGraph</span>
                </div>
                <div className="flex items-center gap-2 pl-16">
                  <span className="text-gray-600">→</span>
                  <span className="text-emerald-400">ServoSceneRenderer</span>
                  <span className="text-gray-600">→</span>
                  <span className="text-amber-400">React</span>
                </div>
              </div>
              <div className="mt-4 text-xs text-gray-500">
                <strong>Key insight:</strong> Each MeaningToken becomes a SceneNode with its own
                affordances, enabling the same content to be interactive in different ways based on
                observer context.
              </div>
            </PilotContainer>
          </section>
        </div>
      </div>
    </div>
  );
}
