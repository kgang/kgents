/**
 * GraphSidebar — Living Canvas graph visualization sidebar
 *
 * "The map IS the territory—when the map is alive."
 *
 * Wraps AstronomicalChart with sidebar behavior:
 * - Slides in from right edge
 * - Resizable via drag handle
 * - Bidirectional selection sync with editor
 * - 'g' keybinding to toggle
 */

import { useRef, useState, useEffect, useCallback } from 'react';
import { AstronomicalChart } from '../components/chart/AstronomicalChart';

import './GraphSidebar.css';

// =============================================================================
// Types
// =============================================================================

export interface GraphSidebarProps {
  /** Whether sidebar is open */
  isOpen: boolean;
  /** Sidebar width in pixels */
  width: number;
  /** Currently focused node path (from editor) */
  focusedPath?: string | null;
  /** Callback when close button clicked */
  onClose: () => void;
  /** Callback when node clicked in graph */
  onNodeClick?: (path: string) => void;
  /** Callback when width changes (via resize) */
  onWidthChange?: (width: number) => void;
}

// =============================================================================
// Component
// =============================================================================

export function GraphSidebar({
  isOpen,
  width,
  focusedPath,
  onClose,
  onNodeClick,
  onWidthChange,
}: GraphSidebarProps) {
  const sidebarRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const dragStartRef = useRef<{ x: number; startWidth: number } | null>(null);

  // Handle resize drag
  const handleResizeStart = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
    dragStartRef.current = {
      x: e.clientX,
      startWidth: width,
    };
  }, [width]);

  const handleResizeMove = useCallback((e: MouseEvent) => {
    if (!isDragging || !dragStartRef.current) return;

    const delta = dragStartRef.current.x - e.clientX;
    const newWidth = dragStartRef.current.startWidth + delta;
    onWidthChange?.(newWidth);
  }, [isDragging, onWidthChange]);

  const handleResizeEnd = useCallback(() => {
    setIsDragging(false);
    dragStartRef.current = null;
  }, []);

  // Attach global drag listeners
  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleResizeMove);
      window.addEventListener('mouseup', handleResizeEnd);
      return () => {
        window.removeEventListener('mousemove', handleResizeMove);
        window.removeEventListener('mouseup', handleResizeEnd);
      };
    }
  }, [isDragging, handleResizeMove, handleResizeEnd]);

  // Prevent cursor jank during drag
  useEffect(() => {
    if (isDragging) {
      document.body.style.cursor = 'ew-resize';
      document.body.style.userSelect = 'none';
    } else {
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    }
  }, [isDragging]);

  return (
    <>
      {/* Sidebar */}
      <div
        ref={sidebarRef}
        className={`graph-sidebar ${isOpen ? 'graph-sidebar--open' : ''}`}
        style={{ width: `${width}px` }}
      >
        {/* Resize Handle */}
        <div
          className={`graph-sidebar__resize-handle ${isDragging ? 'graph-sidebar__resize-handle--dragging' : ''}`}
          onMouseDown={handleResizeStart}
        />

        {/* Header */}
        <div className="graph-sidebar__header">
          <div className="graph-sidebar__title">Living Canvas</div>
          <button
            className="graph-sidebar__close"
            onClick={onClose}
            title="Close graph (press 'g' to toggle)"
          >
            ×
          </button>
        </div>

        {/* Content (AstronomicalChart) */}
        <div className="graph-sidebar__content">
          <AstronomicalChart
            onNodeClick={onNodeClick}
            focusedNodePath={focusedPath}
            showControls={true}
            showLegend={true}
            limit={100}
          />
        </div>
      </div>

      {/* Hint (when closed) */}
      {!isOpen && (
        <div className="graph-sidebar__hint graph-sidebar__hint--visible">
          Show graph
          <kbd>gs</kbd>
        </div>
      )}
    </>
  );
}
