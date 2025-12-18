/**
 * FixedBottomPanel: Fixed position bottom panel with collapse/expand behavior.
 *
 * Key Principles:
 * - **Fixed > Relative**: Stays anchored during scroll
 * - **Collapsed + Expanded states**: Toggle between header-only and full panel
 * - **Resize handle**: Desktop-only drag to resize
 * - **Glass effect**: Transparency with backdrop blur
 *
 * Physical constraints enforced:
 * - Touch targets: 48px minimum
 * - Collapsed height: 48px (single row)
 * - Glass effect: 82.5% opacity with backdrop blur
 *
 * @see docs/skills/elastic-ui-patterns.md (Fixed Bottom Panel Pattern)
 */

import {
  type ReactNode,
  type CSSProperties,
  useState,
  useRef,
  useEffect,
  useCallback,
} from 'react';
import { ChevronUp, ChevronDown } from 'lucide-react';
import {
  GLASS_EFFECT,
  Z_INDEX_LAYERS,
  BOTTOM_PANEL_HEIGHTS,
  PHYSICAL_CONSTRAINTS,
  type GlassVariant,
  type Density,
} from './types';

export interface FixedBottomPanelProps {
  /** Whether the panel is expanded */
  isExpanded: boolean;

  /** Callback when expansion changes */
  onExpandChange: (expanded: boolean) => void;

  /** Panel content (shown when expanded) */
  children: ReactNode;

  /** Collapsed content (e.g., input line) - always visible */
  collapsedContent?: ReactNode;

  /** Header content (title, actions) - shown when expanded */
  header?: ReactNode;

  /** Initial expanded height */
  defaultHeight?: number;

  /** Maximum height when expanded */
  maxHeight?: number;

  /** Whether panel is resizable (drag to resize) */
  resizable?: boolean;

  /** Current density for responsive behavior */
  density?: Density;

  /** Glass effect variant */
  glass?: GlassVariant;

  /** Whether to animate transitions */
  animate?: boolean;

  /** Custom class name */
  className?: string;

  /** Accessible label */
  ariaLabel?: string;

  /** Callback when height changes (via resize) */
  onHeightChange?: (height: number) => void;
}

/**
 * FixedBottomPanel component for persistent bottom UI (terminals, chat, REPL).
 *
 * Usage:
 * ```tsx
 * <FixedBottomPanel
 *   isExpanded={terminalExpanded}
 *   onExpandChange={setTerminalExpanded}
 *   resizable={isDesktop}
 *   header={<TerminalHeader />}
 *   collapsedContent={<TerminalInput />}
 * >
 *   <TerminalOutput />
 * </FixedBottomPanel>
 * ```
 */
export function FixedBottomPanel({
  isExpanded,
  onExpandChange,
  children,
  collapsedContent,
  header,
  defaultHeight = BOTTOM_PANEL_HEIGHTS.expanded,
  maxHeight = BOTTOM_PANEL_HEIGHTS.max,
  resizable = false,
  density: _density = 'spacious', // Reserved for density-specific behavior
  glass = 'standard',
  animate = true,
  className = '',
  ariaLabel = 'Bottom panel',
  onHeightChange,
}: FixedBottomPanelProps) {
  const [height, setHeight] = useState(defaultHeight);
  const [isDragging, setIsDragging] = useState(false);
  const resizeRef = useRef<HTMLDivElement>(null);

  // Get glass effect styles
  const glassStyles = GLASS_EFFECT[glass];

  // Current height based on state
  const currentHeight = isExpanded ? height : BOTTOM_PANEL_HEIGHTS.collapsed;

  // Handle resize drag
  useEffect(() => {
    if (!isDragging || !resizable) return;

    const handleMouseMove = (e: MouseEvent) => {
      const newHeight = window.innerHeight - e.clientY;
      const clampedHeight = Math.max(
        BOTTOM_PANEL_HEIGHTS.collapsed,
        Math.min(maxHeight, newHeight)
      );
      setHeight(clampedHeight);
      onHeightChange?.(clampedHeight);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, resizable, maxHeight, onHeightChange]);

  const handleResizeStart = useCallback((e: React.MouseEvent) => {
    if (!resizable) return;
    e.preventDefault();
    setIsDragging(true);
  }, [resizable]);

  const handleExpand = useCallback(() => {
    onExpandChange(true);
  }, [onExpandChange]);

  const handleCollapse = useCallback(() => {
    onExpandChange(false);
  }, [onExpandChange]);

  const panelStyle: CSSProperties = {
    height: currentHeight,
    zIndex: Z_INDEX_LAYERS.panel + 10, // Above sidebar panels
    transition: isDragging ? 'none' : (animate ? 'height 0.2s ease' : 'none'),
  };

  const touchTargetStyle: CSSProperties = {
    minWidth: PHYSICAL_CONSTRAINTS.minTouchTarget,
    minHeight: PHYSICAL_CONSTRAINTS.minTouchTarget,
  };

  return (
    <div
      className={`
        fixed bottom-0 left-0 right-0
        ${glassStyles.background} ${glassStyles.blur}
        border-t border-gray-700/50
        flex flex-col
        ${className}
      `}
      style={panelStyle}
      role="region"
      aria-label={ariaLabel}
      aria-expanded={isExpanded}
    >
      {/* Resize handle (desktop only, expanded only) */}
      {resizable && isExpanded && (
        <div
          ref={resizeRef}
          onMouseDown={handleResizeStart}
          className={`
            absolute top-0 left-0 right-0 h-1
            cursor-ns-resize
            hover:bg-cyan-500/50
            transition-colors
            ${isDragging ? 'bg-cyan-500/50' : ''}
          `}
          role="separator"
          aria-orientation="horizontal"
          aria-valuenow={height}
          aria-valuemin={BOTTOM_PANEL_HEIGHTS.collapsed}
          aria-valuemax={maxHeight}
        />
      )}

      {/* Header (shown when expanded) */}
      {isExpanded && header && (
        <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700/50 shrink-0">
          <div className="flex-1">{header}</div>
          <button
            onClick={handleCollapse}
            className="p-1.5 hover:bg-gray-700 rounded transition-colors"
            style={touchTargetStyle}
            title="Collapse"
            aria-label="Collapse panel"
          >
            <ChevronDown className="w-4 h-4 text-gray-400" />
          </button>
        </div>
      )}

      {/* Main content (shown when expanded) */}
      {isExpanded && (
        <div className="flex-1 overflow-auto min-h-0">
          {children}
        </div>
      )}

      {/* Collapsed content / footer (always visible) */}
      <div className={`
        shrink-0 px-4 py-2
        ${isExpanded ? 'border-t border-gray-700/50' : ''}
        flex items-center
      `}>
        {!isExpanded && (
          <button
            onClick={handleExpand}
            className="p-1.5 hover:bg-gray-700 rounded transition-colors mr-2"
            style={touchTargetStyle}
            title="Expand"
            aria-label="Expand panel"
          >
            <ChevronUp className="w-4 h-4 text-gray-400" />
          </button>
        )}
        <div className="flex-1">
          {collapsedContent}
        </div>
        {!isExpanded && (
          <button
            onClick={handleExpand}
            className="p-1.5 hover:bg-gray-700 rounded transition-colors ml-2"
            style={touchTargetStyle}
            title="Expand"
            aria-label="Expand panel"
          >
            <ChevronUp className="w-4 h-4 text-gray-400" />
          </button>
        )}
      </div>
    </div>
  );
}

/**
 * Hook to calculate main content padding for FixedBottomPanel.
 * Ensures content isn't occluded by the fixed panel.
 *
 * Usage:
 * ```tsx
 * const padding = useBottomPanelPadding(terminalExpanded, density);
 * <main className={`overflow-auto ${padding}`}>
 * ```
 */
export function useBottomPanelPadding(
  isExpanded: boolean,
  density: Density = 'spacious'
): string {
  if (density === 'compact') {
    return 'pb-20'; // FAB space
  }
  return isExpanded ? 'pb-[200px]' : 'pb-12';
}

export default FixedBottomPanel;
