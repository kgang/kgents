/**
 * PortalTree - Expandable portal token visualization
 *
 * "You don't go to the document. The document comes to you."
 *
 * Renders a source file's portal tokens as an expandable tree.
 * Uses <details> elements for native collapse/expand behavior.
 * Styled with box-drawing characters for CLI parity.
 *
 * @see spec/protocols/portal-token.md Phase 5.1
 */

import { memo, useCallback, useState, useMemo } from 'react';
import {
  ChevronDown,
  ChevronRight,
  Loader2,
  AlertCircle,
  ArrowDownToLine,
  TestTube,
  ScrollText,
  Folder,
  Phone,
  Link,
  ArrowRight,
  FileCode,
  CheckCircle,
  XCircle,
} from 'lucide-react';
import { Breathe } from '@/components/joy';
import type { PortalNode, PortalState } from '@/api/portal';
import { PORTAL_EDGE_CONFIG } from '@/api/portal';

// =============================================================================
// Types
// =============================================================================

export interface PortalTreeProps {
  /** Root node of the portal tree */
  root: PortalNode;
  /** Callback when a portal is expanded */
  onExpand?: (path: string[], edgeType?: string) => Promise<void>;
  /** Callback when a portal is collapsed */
  onCollapse?: (path: string[]) => Promise<void>;
  /** Check if a path is currently expanding */
  isExpanding?: (path: string[]) => boolean;
  /** Custom class name */
  className?: string;
  /** Compact mode for smaller displays */
  compact?: boolean;
}

export interface PortalNodeProps {
  node: PortalNode;
  parentPath: string[];
  onExpand?: (path: string[], edgeType?: string) => Promise<void>;
  onCollapse?: (path: string[]) => Promise<void>;
  isExpanding?: (path: string[]) => boolean;
  isRoot?: boolean;
  isLast?: boolean;
  compact?: boolean;
}

// =============================================================================
// Icon Mapping
// =============================================================================

const EDGE_ICONS: Record<string, typeof ArrowDownToLine> = {
  imports: ArrowDownToLine,
  tests: TestTube,
  implements: ScrollText,
  contains: Folder,
  calls: Phone,
  related: Link,
  default: ArrowRight,
};

function getEdgeIcon(edgeType: string): typeof ArrowDownToLine {
  return EDGE_ICONS[edgeType] || EDGE_ICONS.default;
}

function getEdgeColor(edgeType: string): string {
  return PORTAL_EDGE_CONFIG[edgeType]?.color || PORTAL_EDGE_CONFIG.default.color;
}

// =============================================================================
// State Icons
// =============================================================================

const STATE_DISPLAY: Record<PortalState, { icon: typeof Loader2; color: string }> = {
  collapsed: { icon: ChevronRight, color: '#64748b' },
  loading: { icon: Loader2, color: '#3b82f6' },
  expanded: { icon: ChevronDown, color: '#22c55e' },
  error: { icon: AlertCircle, color: '#ef4444' },
};

// =============================================================================
// Main Component
// =============================================================================

export const PortalTree = memo(function PortalTree({
  root,
  onExpand,
  onCollapse,
  isExpanding,
  className = '',
  compact = false,
}: PortalTreeProps) {
  if (!root) {
    return (
      <div className={`flex flex-col items-center justify-center py-12 text-gray-500 ${className}`}>
        <FileCode className="w-12 h-12 mb-3 opacity-50" />
        <p className="text-sm">No portals loaded</p>
        <p className="text-xs mt-1">Select a file to explore its connections</p>
      </div>
    );
  }

  return (
    <div className={`font-mono text-sm ${className}`}>
      <PortalNodeComponent
        node={root}
        parentPath={[]}
        onExpand={onExpand}
        onCollapse={onCollapse}
        isExpanding={isExpanding}
        isRoot
        compact={compact}
      />
    </div>
  );
});

// =============================================================================
// Portal Node Component
// =============================================================================

const PortalNodeComponent = memo(function PortalNodeComponent({
  node,
  parentPath,
  onExpand,
  onCollapse,
  isExpanding,
  isRoot = false,
  isLast = true,
  compact = false,
}: PortalNodeProps) {
  // Track local open state for <details> element
  const [, setLocalOpen] = useState(node.expanded);

  // Build this node's path
  const nodePath = useMemo(() => {
    if (isRoot) return [];
    return [...parentPath, node.edge_type || node.path];
  }, [parentPath, node.edge_type, node.path, isRoot]);

  // Check if currently expanding
  const expanding = isExpanding?.(nodePath) ?? false;

  // Current state
  const state: PortalState = expanding ? 'loading' : (node.state || (node.expanded ? 'expanded' : 'collapsed'));

  // Handle toggle
  const handleToggle = useCallback(async () => {
    if (state === 'loading') return; // Prevent toggle while loading

    if (node.expanded) {
      // Collapse
      setLocalOpen(false);
      await onCollapse?.(nodePath);
    } else {
      // Expand
      setLocalOpen(true);
      await onExpand?.(nodePath, node.edge_type || undefined);
    }
  }, [state, node.expanded, node.edge_type, nodePath, onExpand, onCollapse]);

  // Render state icon
  const StateIcon = STATE_DISPLAY[state].icon;
  const stateColor = STATE_DISPLAY[state].color;

  // Get edge icon and color
  const EdgeIcon = node.edge_type ? getEdgeIcon(node.edge_type) : FileCode;
  const edgeColor = node.edge_type ? getEdgeColor(node.edge_type) : '#64748b';

  // Box-drawing prefix for tree structure
  const prefix = isRoot ? '' : (isLast ? '  ' : '  ');

  // Count children for display
  const childCount = node.children?.length ?? 0;
  const hasChildren = childCount > 0;

  return (
    <div className={`portal-node ${isRoot ? 'portal-root' : ''}`}>
      {/* Node Header */}
      <div
        className={`
          flex items-center gap-2 py-1 px-2 rounded cursor-pointer
          hover:bg-gray-800/50 transition-colors
          ${node.expanded ? 'bg-gray-800/30' : ''}
        `}
        onClick={handleToggle}
        role="button"
        aria-expanded={node.expanded}
        aria-label={`${node.expanded ? 'Collapse' : 'Expand'} ${node.path}`}
      >
        {/* Tree connector (for non-root) */}
        {!isRoot && (
          <span className="text-gray-600 select-none" style={{ minWidth: node.depth * 16 }}>
            {prefix}
          </span>
        )}

        {/* Expand/Collapse indicator */}
        <Breathe intensity={expanding ? 0.3 : 0} speed="fast">
          <StateIcon
            className={`w-4 h-4 flex-shrink-0 ${expanding ? 'animate-spin' : ''}`}
            style={{ color: stateColor }}
          />
        </Breathe>

        {/* Edge type badge */}
        {node.edge_type && (
          <span
            className="flex items-center gap-1 px-1.5 py-0.5 rounded text-xs"
            style={{ backgroundColor: `${edgeColor}20`, color: edgeColor }}
          >
            <EdgeIcon className="w-3 h-3" />
            {node.edge_type}
          </span>
        )}

        {/* Path/Name */}
        <span className={`truncate ${isRoot ? 'text-white font-medium' : 'text-gray-300'}`}>
          {formatPath(node.path, isRoot)}
        </span>

        {/* Child count indicator */}
        {hasChildren && !node.expanded && (
          <span className="text-gray-500 text-xs">
            ({childCount} {childCount === 1 ? 'item' : 'items'})
          </span>
        )}

        {/* Existence indicator */}
        {!isRoot && !hasChildren && (
          <span className="ml-auto">
            {node.state === 'error' ? (
              <XCircle className="w-3 h-3 text-red-500" />
            ) : (
              <CheckCircle className="w-3 h-3 text-green-600/50" />
            )}
          </span>
        )}
      </div>

      {/* Error Message */}
      {node.state === 'error' && node.error && (
        <div className="ml-8 px-2 py-1 text-xs text-red-400 bg-red-950/30 rounded">
          {node.error}
        </div>
      )}

      {/* Children (when expanded) */}
      {node.expanded && hasChildren && (
        <div className="portal-children">
          {node.children.map((child, index) => (
            <PortalNodeComponent
              key={`${child.edge_type || ''}-${child.path}`}
              node={child}
              parentPath={nodePath}
              onExpand={onExpand}
              onCollapse={onCollapse}
              isExpanding={isExpanding}
              isLast={index === node.children.length - 1}
              compact={compact}
            />
          ))}
        </div>
      )}

      {/* Content Preview (for expanded nodes with content) */}
      {node.expanded && node.content && !hasChildren && (
        <div
          className="ml-8 mt-1 mb-2 p-2 text-xs bg-gray-900/50 border border-gray-700 rounded overflow-x-auto"
          style={{ maxHeight: 200 }}
        >
          <pre className="text-gray-400 whitespace-pre-wrap">{truncateContent(node.content)}</pre>
        </div>
      )}
    </div>
  );
});

// =============================================================================
// Helpers
// =============================================================================

/**
 * Format a path for display.
 */
function formatPath(path: string, isRoot: boolean): string {
  if (isRoot) {
    // Show filename for root
    const parts = path.split('/');
    return parts[parts.length - 1] || path;
  }

  // Show last segment of AGENTESE path
  const parts = path.split('.');
  return parts[parts.length - 1] || path;
}

/**
 * Truncate content for preview.
 */
function truncateContent(content: string, maxLines = 10): string {
  const lines = content.split('\n');
  if (lines.length <= maxLines) {
    return content;
  }
  return lines.slice(0, maxLines).join('\n') + `\n... (${lines.length - maxLines} more lines)`;
}

// =============================================================================
// Exports
// =============================================================================

export default PortalTree;
