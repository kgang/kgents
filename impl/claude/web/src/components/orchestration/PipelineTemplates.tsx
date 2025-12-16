/**
 * PipelineTemplates: Pre-built pipeline configurations.
 *
 * Templates:
 * - Exploration: Scout >> Sage
 * - Build: Sage >> Spark >> Steady
 * - Full Cycle: Scout >> Sage >> Spark >> Steady >> Sync
 * - Parallel Research: Scout // Scout >> Sage
 */

import { cn } from '@/lib/utils';
import { ElasticCard } from '@/components/elastic';

/**
 * Simplified edge type for templates.
 * Uses string IDs for source/target instead of the full PipelineEdge format.
 */
interface TemplateEdge {
  id: string;
  source: string;
  target: string;
  sourcePort?: string;
  targetPort?: string;
}

interface TemplateNode {
  id: string;
  label: string;
  archetype: string;
  position: { x: number; y: number };
}

export interface PipelineTemplate {
  id: string;
  name: string;
  description: string;
  icon: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  nodes: TemplateNode[];
  edges: TemplateEdge[];
}

export interface PipelineTemplatesProps {
  onSelect: (template: PipelineTemplate) => void;
  onClose: () => void;
  className?: string;
}

const TEMPLATES: PipelineTemplate[] = [
  {
    id: 'exploration',
    name: 'Exploration',
    description: 'Scout discovers, Sage analyzes. Perfect for research tasks.',
    icon: '🔍',
    difficulty: 'beginner',
    nodes: [
      { id: 'scout', label: 'Scout', archetype: 'Builder', position: { x: 100, y: 200 } },
      { id: 'sage', label: 'Sage', archetype: 'Scholar', position: { x: 400, y: 200 } },
    ],
    edges: [
      { id: 'e1', source: 'scout', target: 'sage', sourcePort: 'output', targetPort: 'input' },
    ],
  },
  {
    id: 'build-cycle',
    name: 'Build Cycle',
    description: 'Design → Prototype → Refine. For creating tangible outputs.',
    icon: '🔨',
    difficulty: 'intermediate',
    nodes: [
      { id: 'sage', label: 'Sage', archetype: 'Scholar', position: { x: 100, y: 200 } },
      { id: 'spark', label: 'Spark', archetype: 'Trader', position: { x: 350, y: 200 } },
      { id: 'steady', label: 'Steady', archetype: 'Healer', position: { x: 600, y: 200 } },
    ],
    edges: [
      { id: 'e1', source: 'sage', target: 'spark', sourcePort: 'output', targetPort: 'input' },
      { id: 'e2', source: 'spark', target: 'steady', sourcePort: 'output', targetPort: 'input' },
    ],
  },
  {
    id: 'full-cycle',
    name: 'Full Cycle',
    description: 'Complete workflow: Explore → Design → Build → Refine → Integrate',
    icon: '🔄',
    difficulty: 'advanced',
    nodes: [
      { id: 'scout', label: 'Scout', archetype: 'Builder', position: { x: 50, y: 200 } },
      { id: 'sage', label: 'Sage', archetype: 'Scholar', position: { x: 200, y: 200 } },
      { id: 'spark', label: 'Spark', archetype: 'Trader', position: { x: 350, y: 200 } },
      { id: 'steady', label: 'Steady', archetype: 'Healer', position: { x: 500, y: 200 } },
      { id: 'sync', label: 'Sync', archetype: 'Watcher', position: { x: 650, y: 200 } },
    ],
    edges: [
      { id: 'e1', source: 'scout', target: 'sage', sourcePort: 'output', targetPort: 'input' },
      { id: 'e2', source: 'sage', target: 'spark', sourcePort: 'output', targetPort: 'input' },
      { id: 'e3', source: 'spark', target: 'steady', sourcePort: 'output', targetPort: 'input' },
      { id: 'e4', source: 'steady', target: 'sync', sourcePort: 'output', targetPort: 'input' },
    ],
  },
  {
    id: 'parallel-research',
    name: 'Parallel Research',
    description: 'Two Scouts explore independently, Sage synthesizes findings.',
    icon: '⚡',
    difficulty: 'intermediate',
    nodes: [
      { id: 'scout1', label: 'Scout A', archetype: 'Builder', position: { x: 100, y: 100 } },
      { id: 'scout2', label: 'Scout B', archetype: 'Builder', position: { x: 100, y: 300 } },
      { id: 'sage', label: 'Sage', archetype: 'Scholar', position: { x: 400, y: 200 } },
    ],
    edges: [
      { id: 'e1', source: 'scout1', target: 'sage', sourcePort: 'output', targetPort: 'input' },
      { id: 'e2', source: 'scout2', target: 'sage', sourcePort: 'output', targetPort: 'input' },
    ],
  },
  {
    id: 'review-loop',
    name: 'Review Loop',
    description: 'Spark creates, Steady reviews, loop until refined.',
    icon: '🔁',
    difficulty: 'advanced',
    nodes: [
      { id: 'spark', label: 'Spark', archetype: 'Trader', position: { x: 150, y: 200 } },
      { id: 'steady', label: 'Steady', archetype: 'Healer', position: { x: 400, y: 200 } },
    ],
    edges: [
      { id: 'e1', source: 'spark', target: 'steady', sourcePort: 'output', targetPort: 'input' },
      { id: 'e2', source: 'steady', target: 'spark', sourcePort: 'feedback', targetPort: 'input' },
    ],
  },
  {
    id: 'synthesis',
    name: 'Synthesis',
    description: 'Multiple inputs converge to Sync for integration.',
    icon: '🔗',
    difficulty: 'advanced',
    nodes: [
      { id: 'sage', label: 'Sage', archetype: 'Scholar', position: { x: 100, y: 100 } },
      { id: 'spark', label: 'Spark', archetype: 'Trader', position: { x: 100, y: 200 } },
      { id: 'steady', label: 'Steady', archetype: 'Healer', position: { x: 100, y: 300 } },
      { id: 'sync', label: 'Sync', archetype: 'Watcher', position: { x: 400, y: 200 } },
    ],
    edges: [
      { id: 'e1', source: 'sage', target: 'sync', sourcePort: 'output', targetPort: 'input' },
      { id: 'e2', source: 'spark', target: 'sync', sourcePort: 'output', targetPort: 'input' },
      { id: 'e3', source: 'steady', target: 'sync', sourcePort: 'output', targetPort: 'input' },
    ],
  },
];

export function PipelineTemplates({
  onSelect,
  onClose,
  className,
}: PipelineTemplatesProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div
        className={cn(
          'relative bg-town-bg border border-town-accent/30 rounded-xl shadow-2xl',
          'w-full max-w-4xl max-h-[80vh] overflow-hidden flex flex-col',
          className
        )}
      >
        {/* Header */}
        <div className="p-4 border-b border-town-accent/20 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold">Pipeline Templates</h2>
            <p className="text-sm text-gray-400">
              Choose a pre-built pipeline to get started quickly
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-town-accent/20 rounded-lg transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Templates Grid */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {TEMPLATES.map((template) => (
              <TemplateCard
                key={template.id}
                template={template}
                onSelect={() => onSelect(template)}
              />
            ))}
          </div>
        </div>

        {/* Footer hint */}
        <div className="p-4 border-t border-town-accent/20 text-center text-sm text-gray-500">
          Click a template to load it into the canvas, then customize as needed
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Template Card
// =============================================================================

interface TemplateCardProps {
  template: PipelineTemplate;
  onSelect: () => void;
}

function TemplateCard({ template, onSelect }: TemplateCardProps) {
  const difficultyConfig = getDifficultyConfig(template.difficulty);

  return (
    <ElasticCard
      onClick={onSelect}
      className="hover:border-town-highlight/50 transition-all cursor-pointer"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{template.icon}</span>
          <h3 className="font-semibold">{template.name}</h3>
        </div>
        <span
          className={cn(
            'px-2 py-0.5 rounded text-xs font-medium',
            difficultyConfig.bgColor,
            difficultyConfig.textColor
          )}
        >
          {difficultyConfig.label}
        </span>
      </div>

      {/* Description */}
      <p className="text-sm text-gray-400 mb-4">{template.description}</p>

      {/* Mini preview */}
      <div className="bg-town-surface/30 rounded-lg p-3 mb-3">
        <MiniPipelinePreview template={template} />
      </div>

      {/* Stats */}
      <div className="flex items-center gap-4 text-xs text-gray-500">
        <span>{template.nodes.length} nodes</span>
        <span>{template.edges.length} connections</span>
      </div>
    </ElasticCard>
  );
}

// =============================================================================
// Mini Preview
// =============================================================================

interface MiniPipelinePreviewProps {
  template: PipelineTemplate;
}

function MiniPipelinePreview({ template }: MiniPipelinePreviewProps) {
  // Calculate bounds
  const minX = Math.min(...template.nodes.map((n) => n.position.x));
  const maxX = Math.max(...template.nodes.map((n) => n.position.x));
  const minY = Math.min(...template.nodes.map((n) => n.position.y));
  const maxY = Math.max(...template.nodes.map((n) => n.position.y));

  const width = maxX - minX + 100;
  const height = maxY - minY + 60;

  return (
    <svg
      viewBox={`${minX - 20} ${minY - 20} ${width + 40} ${height + 40}`}
      className="w-full h-16"
      preserveAspectRatio="xMidYMid meet"
    >
      {/* Edges */}
      {template.edges.map((edge) => {
        const source = template.nodes.find((n) => n.id === edge.source);
        const target = template.nodes.find((n) => n.id === edge.target);
        if (!source || !target) return null;

        return (
          <line
            key={edge.id}
            x1={source.position.x + 40}
            y1={source.position.y + 15}
            x2={target.position.x}
            y2={target.position.y + 15}
            stroke="currentColor"
            strokeOpacity={0.3}
            strokeWidth={2}
            markerEnd="url(#arrow)"
          />
        );
      })}

      {/* Nodes */}
      {template.nodes.map((node) => (
        <g key={node.id} transform={`translate(${node.position.x}, ${node.position.y})`}>
          <rect
            width="80"
            height="30"
            rx="4"
            fill="currentColor"
            fillOpacity={0.1}
            stroke="currentColor"
            strokeOpacity={0.3}
          />
          <text
            x="40"
            y="19"
            textAnchor="middle"
            fontSize="10"
            fill="currentColor"
            opacity={0.7}
          >
            {node.label}
          </text>
        </g>
      ))}

      {/* Arrow marker */}
      <defs>
        <marker
          id="arrow"
          viewBox="0 0 10 10"
          refX="8"
          refY="5"
          markerWidth="6"
          markerHeight="6"
          orient="auto-start-reverse"
        >
          <path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor" opacity={0.3} />
        </marker>
      </defs>
    </svg>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function getDifficultyConfig(difficulty: PipelineTemplate['difficulty']) {
  switch (difficulty) {
    case 'beginner':
      return {
        label: 'Beginner',
        bgColor: 'bg-green-500/20',
        textColor: 'text-green-400',
      };
    case 'intermediate':
      return {
        label: 'Intermediate',
        bgColor: 'bg-amber-500/20',
        textColor: 'text-amber-400',
      };
    case 'advanced':
      return {
        label: 'Advanced',
        bgColor: 'bg-purple-500/20',
        textColor: 'text-purple-400',
      };
  }
}

export default PipelineTemplates;
