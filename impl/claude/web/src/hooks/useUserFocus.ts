/**
 * useUserFocus - Track user's focus point for agent cursor following.
 *
 * CLI v7 Phase 5: Integration & Polish.
 *
 * Provides:
 * - Mouse position tracking within the canvas
 * - Focused node detection (what node is the user looking at)
 * - Debounced updates to avoid performance issues
 * - Focus path for agents to follow
 *
 * Voice Anchor:
 * "Agents pretending to be there with their cursors moving,
 *  kinda following my cursor, kinda doing its own thing."
 *
 * Key Design:
 * - Tracks mouse position relative to canvas
 * - Detects which node the user is hovering over or near
 * - Broadcasts focus updates to the backend (for agent following)
 * - Subtle, non-intrusive - the tracking is invisible to the user
 *
 * @example
 * const { focusPath, mousePosition, updateFocus } = useUserFocus({
 *   nodes,
 *   onFocusChange: (path) => console.log('User focusing on:', path),
 * });
 */

import { useState, useCallback, useEffect, useRef, useMemo } from 'react';
import type { CanvasNode } from '@/components/canvas';

// =============================================================================
// Types
// =============================================================================

export interface MousePosition {
  x: number;
  y: number;
  /** Time of last update */
  timestamp: number;
}

export interface UseUserFocusOptions {
  /** Canvas nodes for proximity detection */
  nodes: CanvasNode[];
  /** Called when focus changes to a new node */
  onFocusChange?: (path: string | null) => void;
  /** Distance threshold for considering a node "focused" (pixels) */
  focusThreshold?: number;
  /** Debounce delay for focus updates (ms) */
  debounceDelay?: number;
  /** Whether tracking is enabled */
  enabled?: boolean;
}

export interface UseUserFocusReturn {
  /** Currently focused AGENTESE path (null if none) */
  focusPath: string | null;
  /** Current mouse position relative to canvas */
  mousePosition: MousePosition | null;
  /** Ref to attach to the canvas container */
  containerRef: React.RefObject<HTMLDivElement>;
  /** Manually set focus path (for keyboard navigation) */
  setFocusPath: (path: string | null) => void;
  /** Whether the mouse is currently over the canvas */
  isHovering: boolean;
  /** Time since last mouse movement (ms) */
  idleTime: number;
}

// =============================================================================
// Constants
// =============================================================================

const DEFAULT_FOCUS_THRESHOLD = 60; // pixels
const DEFAULT_DEBOUNCE_DELAY = 100; // ms
const IDLE_CHECK_INTERVAL = 1000; // ms

// =============================================================================
// Hook Implementation
// =============================================================================

export function useUserFocus(options: UseUserFocusOptions): UseUserFocusReturn {
  const {
    nodes,
    onFocusChange,
    focusThreshold = DEFAULT_FOCUS_THRESHOLD,
    debounceDelay = DEFAULT_DEBOUNCE_DELAY,
    enabled = true,
  } = options;

  // State
  const [focusPath, setFocusPathState] = useState<string | null>(null);
  const [mousePosition, setMousePosition] = useState<MousePosition | null>(null);
  const [isHovering, setIsHovering] = useState(false);
  const [idleTime, setIdleTime] = useState(0);

  // Refs
  const containerRef = useRef<HTMLDivElement>(null);
  const debounceTimeoutRef = useRef<number | null>(null);
  const lastFocusPathRef = useRef<string | null>(null);
  const onFocusChangeRef = useRef(onFocusChange);

  // Keep callback ref updated
  useEffect(() => {
    onFocusChangeRef.current = onFocusChange;
  }, [onFocusChange]);

  // Build node lookup for fast proximity detection
  const nodePositions = useMemo(() => {
    return nodes.map((node) => ({
      path: node.path,
      x: node.position.x,
      y: node.position.y,
    }));
  }, [nodes]);

  // Find nearest node to a position
  const findNearestNode = useCallback(
    (x: number, y: number): string | null => {
      let nearestPath: string | null = null;
      let nearestDistance = Infinity;

      for (const node of nodePositions) {
        const dx = node.x - x;
        const dy = node.y - y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < nearestDistance && distance <= focusThreshold) {
          nearestDistance = distance;
          nearestPath = node.path;
        }
      }

      return nearestPath;
    },
    [nodePositions, focusThreshold]
  );

  // Update focus path (debounced)
  const updateFocus = useCallback(
    (path: string | null) => {
      if (!enabled) return;

      // Clear existing timeout
      if (debounceTimeoutRef.current !== null) {
        window.clearTimeout(debounceTimeoutRef.current);
      }

      // Debounce the update
      debounceTimeoutRef.current = window.setTimeout(() => {
        if (path !== lastFocusPathRef.current) {
          lastFocusPathRef.current = path;
          setFocusPathState(path);
          onFocusChangeRef.current?.(path);
        }
      }, debounceDelay);
    },
    [enabled, debounceDelay]
  );

  // Handle mouse move
  const handleMouseMove = useCallback(
    (event: MouseEvent) => {
      if (!enabled || !containerRef.current) return;

      const rect = containerRef.current.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      const now = Date.now();

      setMousePosition({ x, y, timestamp: now });
      setIdleTime(0);

      // Find nearest node and update focus
      const nearestPath = findNearestNode(x, y);
      updateFocus(nearestPath);
    },
    [enabled, findNearestNode, updateFocus]
  );

  // Handle mouse enter/leave
  const handleMouseEnter = useCallback(() => {
    setIsHovering(true);
  }, []);

  const handleMouseLeave = useCallback(() => {
    setIsHovering(false);
    setMousePosition(null);
    updateFocus(null);
  }, [updateFocus]);

  // Set up event listeners
  useEffect(() => {
    const container = containerRef.current;
    if (!container || !enabled) return;

    container.addEventListener('mousemove', handleMouseMove);
    container.addEventListener('mouseenter', handleMouseEnter);
    container.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      container.removeEventListener('mousemove', handleMouseMove);
      container.removeEventListener('mouseenter', handleMouseEnter);
      container.removeEventListener('mouseleave', handleMouseLeave);

      // Clean up timeout
      if (debounceTimeoutRef.current !== null) {
        window.clearTimeout(debounceTimeoutRef.current);
      }
    };
  }, [enabled, handleMouseMove, handleMouseEnter, handleMouseLeave]);

  // Track idle time
  useEffect(() => {
    if (!enabled || !isHovering) return;

    const interval = window.setInterval(() => {
      if (mousePosition) {
        const elapsed = Date.now() - mousePosition.timestamp;
        setIdleTime(elapsed);
      }
    }, IDLE_CHECK_INTERVAL);

    return () => window.clearInterval(interval);
  }, [enabled, isHovering, mousePosition]);

  // Manual focus setter (for keyboard navigation)
  const setFocusPath = useCallback((path: string | null) => {
    lastFocusPathRef.current = path;
    setFocusPathState(path);
    onFocusChangeRef.current?.(path);
  }, []);

  return {
    focusPath,
    mousePosition,
    containerRef: containerRef as React.RefObject<HTMLDivElement>,
    setFocusPath,
    isHovering,
    idleTime,
  };
}

// =============================================================================
// Exports
// =============================================================================

export default useUserFocus;
