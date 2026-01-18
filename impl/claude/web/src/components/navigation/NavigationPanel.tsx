/**
 * NavigationPanel — Dense file tree with AGENTESE paths
 *
 * Grounded in: spec/ui/severe-stark.md (Yahoo Japan Density)
 * "50+ links visible, 11px text, every pixel used."
 *
 * Shows:
 * - AGENTESE context hierarchy
 * - Recently accessed K-Blocks
 * - Lifecycle indicators per item
 */

import type { LifecycleStage } from '../../types';
import { LIFECYCLE_COLORS, LIFECYCLE_ICONS } from '../../types';

interface NavigationItem {
  /** AGENTESE path */
  path: string;

  /** Display title */
  title: string;

  /** Item type */
  type: 'folder' | 'kblock' | 'document';

  /** Children (for folders) */
  children?: NavigationItem[];

  /** Lifecycle stage (if available) */
  lifecycle?: LifecycleStage;

  /** Is expanded (for folders) */
  expanded?: boolean;
}

interface NavigationPanelProps {
  /** Navigation items */
  items: NavigationItem[];

  /** Currently selected path */
  selectedPath?: string;

  /** Handler for item selection */
  onSelect?: (path: string) => void;

  /** Handler for folder toggle */
  onToggle?: (path: string) => void;

  /** Collapsed mode (icons only) */
  collapsed?: boolean;
}

/**
 * Dense navigation panel with AGENTESE paths.
 */
export function NavigationPanel({
  items,
  selectedPath,
  onSelect,
  onToggle,
  collapsed = false,
}: NavigationPanelProps) {
  if (collapsed) {
    return (
      <nav className="navigation-panel navigation-panel--collapsed panel-severe">
        <CollapsedNav items={items} selectedPath={selectedPath} onSelect={onSelect} />
      </nav>
    );
  }

  return (
    <nav className="navigation-panel panel-severe">
      <h3 className="text-xs text-secondary">NAVIGATION</h3>
      <ul className="navigation-panel__list list-dense">
        {items.map((item) => (
          <NavigationNode
            key={item.path}
            item={item}
            selectedPath={selectedPath}
            onSelect={onSelect}
            onToggle={onToggle}
            depth={0}
          />
        ))}
      </ul>
    </nav>
  );
}

/**
 * Single navigation node (recursive).
 */
function NavigationNode({
  item,
  selectedPath,
  onSelect,
  onToggle,
  depth,
}: {
  item: NavigationItem;
  selectedPath?: string;
  onSelect?: (path: string) => void;
  onToggle?: (path: string) => void;
  depth: number;
}) {
  const isSelected = selectedPath === item.path;
  const isFolder = item.type === 'folder';
  const hasChildren = item.children && item.children.length > 0;

  const handleClick = () => {
    if (isFolder && hasChildren && onToggle) {
      onToggle(item.path);
    } else if (onSelect) {
      onSelect(item.path);
    }
  };

  const lifecycleColor = item.lifecycle ? LIFECYCLE_COLORS[item.lifecycle] : undefined;
  const lifecycleIcon = item.lifecycle ? LIFECYCLE_ICONS[item.lifecycle] : undefined;

  return (
    <li className="navigation-node">
      <button
        className={`navigation-node__link ${isSelected ? 'navigation-node__link--active' : ''}`}
        onClick={handleClick}
        style={{ paddingLeft: `${depth * 12 + 4}px` }}
      >
        {/* Folder toggle */}
        {isFolder && hasChildren && (
          <span className="navigation-node__toggle">{item.expanded ? '▼' : '▶'}</span>
        )}

        {/* Type icon */}
        <span className="navigation-node__icon">
          {isFolder ? '📁' : item.type === 'kblock' ? '◇' : '📄'}
        </span>

        {/* Title */}
        <span className="navigation-node__title">{item.title}</span>

        {/* Lifecycle indicator */}
        {lifecycleIcon && (
          <span
            className="navigation-node__lifecycle"
            style={{ color: lifecycleColor }}
            title={item.lifecycle}
          >
            {lifecycleIcon}
          </span>
        )}
      </button>

      {/* Children */}
      {isFolder && item.expanded && hasChildren && (
        <ul className="navigation-node__children list-dense">
          {item.children!.map((child) => (
            <NavigationNode
              key={child.path}
              item={child}
              selectedPath={selectedPath}
              onSelect={onSelect}
              onToggle={onToggle}
              depth={depth + 1}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

/**
 * Collapsed navigation (icons only).
 */
function CollapsedNav({
  items,
  selectedPath,
  onSelect,
}: {
  items: NavigationItem[];
  selectedPath?: string;
  onSelect?: (path: string) => void;
}) {
  // Show only root-level context items
  const contexts = items.filter((item) => item.type === 'folder');

  return (
    <ul className="navigation-collapsed list-dense">
      {contexts.map((ctx) => {
        const isActive = selectedPath?.startsWith(ctx.path);
        return (
          <li key={ctx.path}>
            <button
              className={`navigation-collapsed__item ${isActive ? 'navigation-collapsed__item--active' : ''}`}
              onClick={() => onSelect?.(ctx.path)}
              title={ctx.title}
            >
              {ctx.title.charAt(0).toUpperCase()}
            </button>
          </li>
        );
      })}
    </ul>
  );
}

/**
 * Create default AGENTESE context structure.
 */
export function createDefaultContexts(): NavigationItem[] {
  return [
    {
      path: 'world',
      title: 'world',
      type: 'folder',
      expanded: true,
      children: [
        { path: 'world.document', title: 'document', type: 'folder' },
        { path: 'world.entity', title: 'entity', type: 'folder' },
        { path: 'world.tool', title: 'tool', type: 'folder' },
      ],
    },
    {
      path: 'self',
      title: 'self',
      type: 'folder',
      expanded: false,
      children: [
        { path: 'self.constitution', title: 'constitution', type: 'folder' },
        { path: 'self.memory', title: 'memory', type: 'folder' },
        { path: 'self.capability', title: 'capability', type: 'folder' },
      ],
    },
    {
      path: 'concept',
      title: 'concept',
      type: 'folder',
      expanded: false,
      children: [
        { path: 'concept.axiom', title: 'axiom', type: 'folder' },
        { path: 'concept.definition', title: 'definition', type: 'folder' },
      ],
    },
    {
      path: 'void',
      title: 'void',
      type: 'folder',
      expanded: false,
      children: [
        { path: 'void.entropy', title: 'entropy', type: 'folder' },
        { path: 'void.serendipity', title: 'serendipity', type: 'folder' },
      ],
    },
    {
      path: 'time',
      title: 'time',
      type: 'folder',
      expanded: false,
      children: [
        { path: 'time.witness', title: 'witness', type: 'folder' },
        { path: 'time.trace', title: 'trace', type: 'folder' },
      ],
    },
  ];
}

export default NavigationPanel;
