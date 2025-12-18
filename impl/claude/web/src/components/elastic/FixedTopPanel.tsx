/**
 * FixedTopPanel: Fixed position top panel with collapse/expand behavior.
 *
 * Key Principles:
 * - **Fixed > Relative**: Stays anchored at top during scroll
 * - **Collapsed + Expanded states**: Toggle between summary and full panel
 * - **Glass effect**: Transparency with backdrop blur
 * - **Sibling awareness**: Exposes height for siblings (NavigationTree) to offset
 *
 * Physical constraints enforced:
 * - Touch targets: 48px minimum
 * - Collapsed height: 40px (single row summary)
 * - Glass effect: 82.5% opacity with backdrop blur
 *
 * Sheaf condition: nav.top = observer.bottom (NavigationTree must offset from this panel)
 *
 * @see docs/skills/elastic-ui-patterns.md (Fixed Top Panel Pattern)
 */

import {
  type ReactNode,
  type CSSProperties,
  useCallback,
} from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown } from 'lucide-react';
import {
  GLASS_EFFECT,
  Z_INDEX_LAYERS,
  TOP_PANEL_HEIGHTS,
  PHYSICAL_CONSTRAINTS,
  type GlassVariant,
  type Density,
} from './types';

export interface FixedTopPanelProps {
  /** Whether the panel is expanded */
  isExpanded: boolean;

  /** Callback when expansion changes */
  onExpandChange: (expanded: boolean) => void;

  /** Panel content (shown when expanded) */
  children: ReactNode;

  /** Collapsed content (summary view) - shown when collapsed */
  collapsedContent: ReactNode;

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
}

/**
 * FixedTopPanel component for persistent top UI (observer context, status bars).
 *
 * Usage:
 * ```tsx
 * <FixedTopPanel
 *   isExpanded={observerExpanded}
 *   onExpandChange={setObserverExpanded}
 *   collapsedContent={<CollapsedSummary />}
 * >
 *   <ExpandedContent />
 * </FixedTopPanel>
 * ```
 */
export function FixedTopPanel({
  isExpanded,
  onExpandChange,
  children,
  collapsedContent,
  density: _density = 'spacious', // Reserved for density-specific behavior
  glass = 'standard',
  animate = true,
  className = '',
  ariaLabel = 'Top panel',
}: FixedTopPanelProps) {
  // Get glass effect styles
  const glassStyles = GLASS_EFFECT[glass];

  const handleExpand = useCallback(() => {
    onExpandChange(true);
  }, [onExpandChange]);

  const touchTargetStyle: CSSProperties = {
    minWidth: PHYSICAL_CONSTRAINTS.minTouchTarget,
    minHeight: PHYSICAL_CONSTRAINTS.minTouchTarget,
  };

  // Animation variants for smooth height transitions
  const panelVariants = {
    collapsed: {
      height: TOP_PANEL_HEIGHTS.collapsed,
    },
    expanded: {
      height: TOP_PANEL_HEIGHTS.expanded,
    },
  };

  return (
    <motion.div
      className={`
        fixed top-0 left-0 right-0
        ${glassStyles.background} ${glassStyles.blur}
        border-b border-gray-700/50
        flex flex-col overflow-hidden
        ${className}
      `}
      style={{ zIndex: Z_INDEX_LAYERS.panel }}
      role="region"
      aria-label={ariaLabel}
      aria-expanded={isExpanded}
      initial={false}
      animate={isExpanded ? 'expanded' : 'collapsed'}
      variants={panelVariants}
      transition={{
        duration: animate ? 0.25 : 0,
        ease: [0.4, 0, 0.2, 1],
      }}
    >
      <AnimatePresence mode="wait" initial={false}>
        {isExpanded ? (
          <motion.div
            key="expanded"
            className="flex flex-col h-full"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: animate ? 0.15 : 0 }}
          >
            {/* Expanded content */}
            <div className="flex-1 overflow-auto min-h-0">
              {children}
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="collapsed"
            className="h-full"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: animate ? 0.15 : 0 }}
          >
            {/* Collapsed summary with expand button */}
            <button
              onClick={handleExpand}
              className="w-full h-full flex items-center justify-between hover:bg-gray-700/30 transition-colors"
              style={touchTargetStyle}
              aria-label="Expand panel"
            >
              <div className="flex-1">
                {collapsedContent}
              </div>
              <div className="px-3 flex items-center justify-center" style={touchTargetStyle}>
                <ChevronDown className="w-4 h-4 text-gray-400" />
              </div>
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

/**
 * Hook to calculate top offset for sibling components.
 * Ensures siblings (like NavigationTree) don't overlap the fixed top panel.
 *
 * Usage:
 * ```tsx
 * const topOffset = useTopPanelOffset(observerExpanded);
 * <aside style={{ top: topOffset }}>
 * ```
 */
export function useTopPanelOffset(isExpanded: boolean): string {
  return isExpanded ? `${TOP_PANEL_HEIGHTS.expanded}px` : `${TOP_PANEL_HEIGHTS.collapsed}px`;
}

/**
 * Get the raw pixel height of the top panel.
 * Useful for calculating offsets in non-string contexts.
 */
export function getTopPanelHeight(isExpanded: boolean): number {
  return isExpanded ? TOP_PANEL_HEIGHTS.expanded : TOP_PANEL_HEIGHTS.collapsed;
}

export default FixedTopPanel;
