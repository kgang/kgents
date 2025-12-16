/**
 * ContextMenu: Right-click context menu for pipeline nodes and edges.
 *
 * Features:
 * - Position-aware (stays within viewport)
 * - Keyboard accessible
 * - Node-specific and edge-specific actions
 * - Styled via globals.css (.context-menu classes)
 *
 * @see plans/web-refactor/interaction-patterns.md
 */

import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactNode,
  type KeyboardEvent,
} from 'react';
import { createPortal } from 'react-dom';
import { cn } from '@/lib/utils';

// =============================================================================
// Types
// =============================================================================

export interface ContextMenuItem {
  /** Unique identifier */
  id: string;

  /** Display label */
  label: string;

  /** Optional icon */
  icon?: ReactNode;

  /** Click handler */
  onClick: () => void;

  /** Whether item is disabled */
  disabled?: boolean;

  /** Whether item is destructive (red styling) */
  destructive?: boolean;

  /** Keyboard shortcut hint */
  shortcut?: string;
}

export interface ContextMenuSection {
  /** Section label (optional) */
  label?: string;

  /** Menu items */
  items: ContextMenuItem[];
}

export interface ContextMenuProps {
  /** Position to render at */
  position: { x: number; y: number };

  /** Menu sections */
  sections: ContextMenuSection[];

  /** Called when menu should close */
  onClose: () => void;

  /** Additional class names */
  className?: string;
}

// =============================================================================
// Hook: useContextMenu
// =============================================================================

export interface UseContextMenuReturn {
  /** Whether menu is open */
  isOpen: boolean;

  /** Current position */
  position: { x: number; y: number } | null;

  /** Context data passed when opening */
  context: unknown;

  /** Open the menu at a position with context */
  open: (x: number, y: number, context?: unknown) => void;

  /** Close the menu */
  close: () => void;
}

export function useContextMenu<T = unknown>(): UseContextMenuReturn & { context: T | null } {
  const [isOpen, setIsOpen] = useState(false);
  const [position, setPosition] = useState<{ x: number; y: number } | null>(null);
  const [context, setContext] = useState<T | null>(null);

  const open = useCallback((x: number, y: number, ctx?: unknown) => {
    setPosition({ x, y });
    setContext(ctx as T);
    setIsOpen(true);
  }, []);

  const close = useCallback(() => {
    setIsOpen(false);
    setPosition(null);
    setContext(null);
  }, []);

  return { isOpen, position, context, open, close };
}

// =============================================================================
// Component
// =============================================================================

export function ContextMenu({
  position,
  sections,
  onClose,
  className,
}: ContextMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null);
  const [adjustedPosition, setAdjustedPosition] = useState(position);
  const [focusedIndex, setFocusedIndex] = useState(-1);

  // Flatten items for keyboard navigation
  const allItems = sections.flatMap((s) => s.items.filter((i) => !i.disabled));

  // ==========================================================================
  // Position Adjustment (keep within viewport)
  // ==========================================================================

  useEffect(() => {
    if (!menuRef.current) {
      setAdjustedPosition(position);
      return;
    }

    const rect = menuRef.current.getBoundingClientRect();
    const padding = 8;

    let x = position.x;
    let y = position.y;

    // Adjust horizontal
    if (x + rect.width > window.innerWidth - padding) {
      x = window.innerWidth - rect.width - padding;
    }
    if (x < padding) {
      x = padding;
    }

    // Adjust vertical
    if (y + rect.height > window.innerHeight - padding) {
      y = window.innerHeight - rect.height - padding;
    }
    if (y < padding) {
      y = padding;
    }

    setAdjustedPosition({ x, y });
  }, [position]);

  // ==========================================================================
  // Click Outside to Close
  // ==========================================================================

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        onClose();
      }
    };

    const handleEscape = (e: globalThis.KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    // Delay to prevent immediate close from the same click that opened
    const timer = setTimeout(() => {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleEscape);
    }, 0);

    return () => {
      clearTimeout(timer);
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [onClose]);

  // ==========================================================================
  // Keyboard Navigation
  // ==========================================================================

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLDivElement>) => {
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setFocusedIndex((i) => (i + 1) % allItems.length);
          break;
        case 'ArrowUp':
          e.preventDefault();
          setFocusedIndex((i) => (i - 1 + allItems.length) % allItems.length);
          break;
        case 'Enter':
        case ' ':
          e.preventDefault();
          if (focusedIndex >= 0 && focusedIndex < allItems.length) {
            allItems[focusedIndex].onClick();
            onClose();
          }
          break;
        case 'Escape':
          e.preventDefault();
          onClose();
          break;
      }
    },
    [allItems, focusedIndex, onClose]
  );

  // ==========================================================================
  // Render
  // ==========================================================================

  const menu = (
    <div
      ref={menuRef}
      className={cn('context-menu', className)}
      style={{
        left: adjustedPosition.x,
        top: adjustedPosition.y,
      }}
      role="menu"
      aria-orientation="vertical"
      tabIndex={0}
      onKeyDown={handleKeyDown}
    >
      {sections.map((section, sectionIndex) => (
        <div key={sectionIndex}>
          {/* Section separator (except first) */}
          {sectionIndex > 0 && <div className="context-menu-separator" role="separator" />}

          {/* Section label */}
          {section.label && (
            <div className="context-menu-label">{section.label}</div>
          )}

          {/* Items */}
          {section.items.map((item, itemIndex) => {
            // Calculate global index for focus
            const globalIndex = sections
              .slice(0, sectionIndex)
              .reduce((sum, s) => sum + s.items.filter((i) => !i.disabled).length, 0) +
              section.items.slice(0, itemIndex).filter((i) => !i.disabled).length;

            const isFocused = globalIndex === focusedIndex && !item.disabled;

            return (
              <button
                key={item.id}
                className={cn(
                  'context-menu-item',
                  item.destructive && 'destructive',
                  isFocused && 'bg-town-accent/20'
                )}
                onClick={() => {
                  if (!item.disabled) {
                    item.onClick();
                    onClose();
                  }
                }}
                disabled={item.disabled}
                aria-disabled={item.disabled}
                role="menuitem"
              >
                {item.icon && <span className="w-4 h-4">{item.icon}</span>}
                <span className="flex-1">{item.label}</span>
                {item.shortcut && (
                  <span className="text-xs text-gray-500 ml-4">{item.shortcut}</span>
                )}
              </button>
            );
          })}
        </div>
      ))}
    </div>
  );

  // Render in portal at document.body
  return createPortal(menu, document.body);
}

// =============================================================================
// Pre-built Menus
// =============================================================================

export interface NodeContextMenuProps {
  position: { x: number; y: number };
  nodeId: string;
  nodeType: 'agent' | 'operation' | 'input' | 'output';
  onClose: () => void;
  onDelete?: (nodeId: string) => void;
  onDuplicate?: (nodeId: string) => void;
  onEdit?: (nodeId: string) => void;
  onInspect?: (nodeId: string) => void;
}

export function NodeContextMenu({
  position,
  nodeId,
  nodeType,
  onClose,
  onDelete,
  onDuplicate,
  onEdit,
  onInspect,
}: NodeContextMenuProps) {
  const sections: ContextMenuSection[] = [
    {
      items: [
        {
          id: 'inspect',
          label: 'Inspect',
          icon: <InspectIcon />,
          onClick: () => onInspect?.(nodeId),
          shortcut: 'I',
        },
        ...(nodeType === 'agent'
          ? [
              {
                id: 'edit',
                label: 'Edit Agent',
                icon: <EditIcon />,
                onClick: () => onEdit?.(nodeId),
                shortcut: 'E',
              },
            ]
          : []),
        {
          id: 'duplicate',
          label: 'Duplicate',
          icon: <DuplicateIcon />,
          onClick: () => onDuplicate?.(nodeId),
          shortcut: 'Ctrl+D',
        },
      ],
    },
    {
      items: [
        {
          id: 'delete',
          label: 'Delete',
          icon: <DeleteIcon />,
          onClick: () => onDelete?.(nodeId),
          destructive: true,
          shortcut: 'Del',
        },
      ],
    },
  ];

  return <ContextMenu position={position} sections={sections} onClose={onClose} />;
}

export interface EdgeContextMenuProps {
  position: { x: number; y: number };
  edgeId: string;
  onClose: () => void;
  onDelete?: (edgeId: string) => void;
  onInspect?: (edgeId: string) => void;
}

export function EdgeContextMenu({
  position,
  edgeId,
  onClose,
  onDelete,
  onInspect,
}: EdgeContextMenuProps) {
  const sections: ContextMenuSection[] = [
    {
      items: [
        {
          id: 'inspect',
          label: 'Inspect Connection',
          icon: <InspectIcon />,
          onClick: () => onInspect?.(edgeId),
        },
      ],
    },
    {
      items: [
        {
          id: 'delete',
          label: 'Remove Connection',
          icon: <DeleteIcon />,
          onClick: () => onDelete?.(edgeId),
          destructive: true,
          shortcut: 'Del',
        },
      ],
    },
  ];

  return <ContextMenu position={position} sections={sections} onClose={onClose} />;
}

// =============================================================================
// Icons
// =============================================================================

function InspectIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
      />
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
      />
    </svg>
  );
}

function EditIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
      />
    </svg>
  );
}

function DuplicateIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
      />
    </svg>
  );
}

function DeleteIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
      />
    </svg>
  );
}

export default ContextMenu;
