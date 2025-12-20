/**
 * SceneNodeComponent - Dispatches SceneNode to appropriate component.
 *
 * WARP Phase 2: React Projection Layer.
 *
 * Maps SceneNodeKind → React Component:
 * - PANEL → PanelNode (container with borders)
 * - TRACE → TraceNode (timeline item)
 * - TEXT → TextNode (plain text)
 * - GROUP → GroupNode (structural grouping)
 * - INTENT → IntentNode (task/goal)
 * - OFFERING → OfferingNode (context indicator)
 * - COVENANT → CovenantNode (permission indicator)
 * - WALK → WalkNode (session progress)
 * - RITUAL → RitualNode (workflow phase)
 */

import React, { Fragment, type ReactElement, type CSSProperties } from 'react';
import type {
  SceneNodeKind,
  NodeStyle,
  SceneNodeProps,
} from '../../api/types/_generated/world-scenery';
import { Breathe } from '../joy/Breathe';

// =============================================================================
// Style Utilities
// =============================================================================

/**
 * Convert NodeStyle to React styles and wrappers.
 */
function useNodeStyle(style: NodeStyle): {
  className: string;
  inlineStyle: CSSProperties;
  Wrapper: React.ComponentType<{ children: React.ReactNode }>;
} {
  // Background mapping (semantic → Tailwind)
  const bgClasses: Record<string, string> = {
    soil: 'bg-amber-900/30',
    sage: 'bg-green-900/30',
    amber: 'bg-amber-800/30',
    living_green: 'bg-green-700/30',
    copper: 'bg-orange-800/30',
  };

  const classes: string[] = [];

  // Background
  if (style.background && bgClasses[style.background]) {
    classes.push(bgClasses[style.background]);
  }

  // Paper grain texture
  if (style.paper_grain) {
    classes.push('bg-gradient-to-br from-transparent via-white/5 to-transparent');
  }

  // Inline style for opacity
  const inlineStyle: CSSProperties = {};
  if (style.opacity < 1.0) {
    inlineStyle.opacity = style.opacity;
  }

  // Animation wrapper
  let Wrapper: React.ComponentType<{ children: React.ReactNode }> =
    Fragment as React.ComponentType<{ children: React.ReactNode }>;

  if (style.breathing) {
    Wrapper = ({ children }) => (
      <Breathe intensity={0.2} speed="slow">
        {children}
      </Breathe>
    );
  }
  // Note: unfurling could be added with an Unfurl component when available

  return {
    className: classes.join(' '),
    inlineStyle,
    Wrapper,
  };
}

// =============================================================================
// Individual Node Components
// =============================================================================

function PanelNode({ node, onClick }: SceneNodeProps): ReactElement {
  const { className, inlineStyle, Wrapper } = useNodeStyle(node.style);

  return (
    <Wrapper>
      <div
        className={`panel-node rounded-lg border border-gray-700 bg-gray-800/50 p-4 ${className}`}
        style={inlineStyle}
        onClick={() => onClick?.(node.id)}
        role={onClick ? 'button' : undefined}
        tabIndex={onClick ? 0 : undefined}
      >
        {node.label && <h3 className="text-sm font-medium text-gray-200 mb-2">{node.label}</h3>}
        {typeof node.content === 'string' && (
          <p className="text-sm text-gray-400">{node.content}</p>
        )}
      </div>
    </Wrapper>
  );
}

function TraceNode({ node, onClick }: SceneNodeProps): ReactElement {
  const { className, inlineStyle, Wrapper } = useNodeStyle(node.style);
  const content = node.content as Record<string, unknown> | undefined;

  return (
    <Wrapper>
      <div
        className={`trace-node rounded border-l-2 border-cyan-500 bg-gray-800/30 p-3 ${className}`}
        style={inlineStyle}
        onClick={() => onClick?.(node.id)}
        role={onClick ? 'button' : undefined}
        tabIndex={onClick ? 0 : undefined}
      >
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-cyan-500" />
          <span className="text-sm font-medium text-gray-200">{node.label}</span>
        </div>
        {content?.origin != null && (
          <span className="text-xs text-gray-500 ml-4">{String(content.origin)}</span>
        )}
      </div>
    </Wrapper>
  );
}

function TextNode({ node }: SceneNodeProps): ReactElement {
  const { className, inlineStyle, Wrapper } = useNodeStyle(node.style);

  return (
    <Wrapper>
      <div className={`text-node ${className}`} style={inlineStyle}>
        {node.label && <span className="text-xs text-gray-500 block">{node.label}</span>}
        <p className="text-sm text-gray-300">
          {typeof node.content === 'string' ? node.content : JSON.stringify(node.content)}
        </p>
      </div>
    </Wrapper>
  );
}

function GroupNode({ node }: SceneNodeProps): ReactElement {
  const { className, inlineStyle, Wrapper } = useNodeStyle(node.style);

  return (
    <Wrapper>
      <div className={`group-node flex flex-col gap-2 ${className}`} style={inlineStyle}>
        {node.label && (
          <span className="text-xs text-gray-500 uppercase tracking-wider">{node.label}</span>
        )}
        {/* Group children would be rendered here in a more complex implementation */}
      </div>
    </Wrapper>
  );
}

function IntentNode({ node, onClick }: SceneNodeProps): ReactElement {
  const { className, inlineStyle, Wrapper } = useNodeStyle(node.style);

  return (
    <Wrapper>
      <div
        className={`intent-node rounded border border-purple-700/50 bg-purple-900/20 p-3 ${className}`}
        style={inlineStyle}
        onClick={() => onClick?.(node.id)}
        role={onClick ? 'button' : undefined}
        tabIndex={onClick ? 0 : undefined}
      >
        <div className="flex items-center gap-2">
          <span className="text-purple-400">◆</span>
          <span className="text-sm font-medium text-gray-200">{node.label}</span>
        </div>
      </div>
    </Wrapper>
  );
}

function OfferingNode({ node }: SceneNodeProps): ReactElement {
  const { className, inlineStyle, Wrapper } = useNodeStyle(node.style);

  return (
    <Wrapper>
      <span
        className={`offering-node inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-900/30 text-amber-400 text-xs ${className}`}
        style={inlineStyle}
      >
        ✦ {node.label}
      </span>
    </Wrapper>
  );
}

function CovenantNode({ node }: SceneNodeProps): ReactElement {
  const { className, inlineStyle, Wrapper } = useNodeStyle(node.style);

  return (
    <Wrapper>
      <span
        className={`covenant-node inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-green-900/30 text-green-400 text-xs ${className}`}
        style={inlineStyle}
      >
        ✓ {node.label}
      </span>
    </Wrapper>
  );
}

function WalkNode({ node }: SceneNodeProps): ReactElement {
  const { className, inlineStyle, Wrapper } = useNodeStyle(node.style);

  return (
    <Wrapper>
      <div className={`walk-node flex items-center gap-3 p-2 ${className}`} style={inlineStyle}>
        <div className="flex-1 h-1 bg-gray-700 rounded-full overflow-hidden">
          <div className="h-full bg-blue-500 w-1/2" />
        </div>
        <span className="text-xs text-gray-400">{node.label}</span>
      </div>
    </Wrapper>
  );
}

function RitualNode({ node }: SceneNodeProps): ReactElement {
  const { className, inlineStyle, Wrapper } = useNodeStyle(node.style);

  return (
    <Wrapper>
      <div
        className={`ritual-node rounded border border-pink-700/50 bg-pink-900/20 p-3 ${className}`}
        style={inlineStyle}
      >
        <div className="flex items-center gap-2">
          <span className="text-pink-400">⟡</span>
          <span className="text-sm font-medium text-gray-200">{node.label}</span>
        </div>
      </div>
    </Wrapper>
  );
}

// Fallback for unknown node types
function UnknownNode({ node }: SceneNodeProps): ReactElement {
  return (
    <div className="unknown-node p-2 border border-dashed border-gray-600 rounded">
      <span className="text-xs text-gray-500">
        Unknown: {node.kind} - {node.label}
      </span>
    </div>
  );
}

// =============================================================================
// Component Dispatch Map
// =============================================================================

const NODE_COMPONENTS: Record<SceneNodeKind, React.ComponentType<SceneNodeProps>> = {
  PANEL: PanelNode,
  TRACE: TraceNode,
  TEXT: TextNode,
  GROUP: GroupNode,
  INTENT: IntentNode,
  OFFERING: OfferingNode,
  COVENANT: CovenantNode,
  WALK: WalkNode,
  RITUAL: RitualNode,
};

// =============================================================================
// Main Component
// =============================================================================

export function SceneNodeComponent({ node, onClick, onHover }: SceneNodeProps): ReactElement {
  const Component = NODE_COMPONENTS[node.kind] || UnknownNode;

  return (
    <div
      className="scene-node"
      data-node-id={node.id}
      data-node-kind={node.kind}
      style={{ flex: node.flex }}
      onMouseEnter={() => onHover?.(node.id, true)}
      onMouseLeave={() => onHover?.(node.id, false)}
    >
      <Component node={node} onClick={onClick} onHover={onHover} />
    </div>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default SceneNodeComponent;
export {
  PanelNode,
  TraceNode,
  TextNode,
  GroupNode,
  IntentNode,
  OfferingNode,
  CovenantNode,
  WalkNode,
  RitualNode,
  UnknownNode,
  useNodeStyle,
};
