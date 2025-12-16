/**
 * Onboarding Hints
 *
 * Contextual hints that appear once per user, stored in localStorage.
 * Helpful guidance without being intrusive.
 *
 * @see plans/web-refactor/phase5-continuation.md
 */

import { useState, useEffect, type ReactNode } from 'react';
import { createPortal } from 'react-dom';

// =============================================================================
// Hint Keys (localStorage)
// =============================================================================

export const HINT_KEYS = {
  TOWN_FIRST_VISIT: 'kgents_hint_town_first',
  TOWN_CITIZEN_CLICK: 'kgents_hint_citizen_click',
  WORKSHOP_FIRST_TASK: 'kgents_hint_workshop_task',
  INHABIT_FIRST_SESSION: 'kgents_hint_inhabit_session',
  PIPELINE_FIRST_BUILD: 'kgents_hint_pipeline_build',
  SHORTCUTS_DISCOVERY: 'kgents_hint_shortcuts',
} as const;

export type HintKey = (typeof HINT_KEYS)[keyof typeof HINT_KEYS];

// =============================================================================
// Types
// =============================================================================

interface OnboardingHintProps {
  /** Storage key for this hint */
  hintKey: HintKey;
  /** Position relative to children */
  position?: 'top' | 'bottom' | 'left' | 'right';
  /** Element to attach hint to */
  children: ReactNode;
  /** Hint content */
  content: ReactNode;
  /** Delay before showing (ms) */
  delay?: number;
  /** Force show (for testing) */
  forceShow?: boolean;
}

interface HintBubbleProps {
  position: 'top' | 'bottom' | 'left' | 'right';
  onDismiss: () => void;
  children: ReactNode;
}

// =============================================================================
// Helpers
// =============================================================================

/**
 * Check if a hint has been dismissed.
 */
export function isHintDismissed(key: HintKey): boolean {
  if (typeof window === 'undefined') return true;
  return localStorage.getItem(key) === 'true';
}

/**
 * Dismiss a hint permanently.
 */
export function dismissHint(key: HintKey): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(key, 'true');
  }
}

/**
 * Reset all hints (for testing/debugging).
 */
export function resetAllHints(): void {
  if (typeof window === 'undefined') return;
  Object.values(HINT_KEYS).forEach((key) => {
    localStorage.removeItem(key);
  });
}

// =============================================================================
// Components
// =============================================================================

/**
 * Hint bubble with dismiss button.
 */
function HintBubble({ position, onDismiss, children }: HintBubbleProps) {
  const positionClasses: Record<string, string> = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  };

  const arrowClasses: Record<string, string> = {
    top: 'top-full left-1/2 -translate-x-1/2 border-l-transparent border-r-transparent border-b-transparent border-t-town-highlight',
    bottom: 'bottom-full left-1/2 -translate-x-1/2 border-l-transparent border-r-transparent border-t-transparent border-b-town-highlight',
    left: 'left-full top-1/2 -translate-y-1/2 border-t-transparent border-b-transparent border-r-transparent border-l-town-highlight',
    right: 'right-full top-1/2 -translate-y-1/2 border-t-transparent border-b-transparent border-l-transparent border-r-town-highlight',
  };

  return (
    <div
      className={`absolute ${positionClasses[position]} z-50 hint-bubble`}
      role="tooltip"
    >
      {/* Bubble */}
      <div className="relative bg-town-highlight text-white text-sm px-4 py-3 rounded-lg shadow-lg max-w-xs hint-attention">
        {/* Content */}
        <div className="pr-6">{children}</div>

        {/* Dismiss button */}
        <button
          onClick={onDismiss}
          className="absolute top-2 right-2 text-white/70 hover:text-white transition-colors"
          aria-label="Dismiss hint"
        >
          <svg
            width="14"
            height="14"
            viewBox="0 0 14 14"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path d="M1 1L13 13M1 13L13 1" />
          </svg>
        </button>

        {/* Arrow */}
        <div
          className={`absolute w-0 h-0 border-[6px] ${arrowClasses[position]}`}
        />
      </div>
    </div>
  );
}

/**
 * Onboarding hint wrapper.
 *
 * Shows a hint bubble once per user. Dismisses when clicked or closed.
 *
 * @example
 * ```tsx
 * <OnboardingHint
 *   hintKey={HINT_KEYS.TOWN_CITIZEN_CLICK}
 *   position="bottom"
 *   content="Click any citizen to see their thoughts and history"
 * >
 *   <CitizenCard citizen={citizen} />
 * </OnboardingHint>
 * ```
 */
export function OnboardingHint({
  hintKey,
  position = 'bottom',
  children,
  content,
  delay = 1000,
  forceShow = false,
}: OnboardingHintProps) {
  const [dismissed, setDismissed] = useState(() =>
    forceShow ? false : isHintDismissed(hintKey)
  );
  const [visible, setVisible] = useState(false);

  // Show hint after delay
  useEffect(() => {
    if (dismissed) return;

    const timer = setTimeout(() => {
      setVisible(true);
    }, delay);

    return () => clearTimeout(timer);
  }, [dismissed, delay]);

  const handleDismiss = () => {
    dismissHint(hintKey);
    setDismissed(true);
    setVisible(false);
  };

  return (
    <div className="relative inline-block">
      {children}
      {visible && !dismissed && (
        <HintBubble position={position} onDismiss={handleDismiss}>
          {content}
        </HintBubble>
      )}
    </div>
  );
}

// =============================================================================
// Pre-configured Hints
// =============================================================================

interface ContextualHintProps {
  children: ReactNode;
}

/**
 * Town page first visit hint.
 */
export function TownFirstVisitHint({ children }: ContextualHintProps) {
  return (
    <OnboardingHint
      hintKey={HINT_KEYS.TOWN_FIRST_VISIT}
      position="bottom"
      content={
        <div>
          <strong>Welcome to Agent Town!</strong>
          <p className="mt-1 text-sm opacity-90">
            Watch as citizens live their daily routines and form connections.
          </p>
        </div>
      }
    >
      {children}
    </OnboardingHint>
  );
}

/**
 * Citizen click hint.
 */
export function CitizenClickHint({ children }: ContextualHintProps) {
  return (
    <OnboardingHint
      hintKey={HINT_KEYS.TOWN_CITIZEN_CLICK}
      position="right"
      delay={3000}
      content="Click any citizen to see their thoughts and history"
    >
      {children}
    </OnboardingHint>
  );
}

/**
 * Workshop task hint.
 */
export function WorkshopTaskHint({ children }: ContextualHintProps) {
  return (
    <OnboardingHint
      hintKey={HINT_KEYS.WORKSHOP_FIRST_TASK}
      position="bottom"
      content={
        <div>
          <strong>The Workshop is Ready</strong>
          <p className="mt-1 text-sm opacity-90">
            Describe a task and watch the builders collaborate.
          </p>
        </div>
      }
    >
      {children}
    </OnboardingHint>
  );
}

/**
 * Inhabit session hint.
 */
export function InhabitSessionHint({ children }: ContextualHintProps) {
  return (
    <OnboardingHint
      hintKey={HINT_KEYS.INHABIT_FIRST_SESSION}
      position="top"
      content={
        <div>
          <strong>Inhabiting a Citizen</strong>
          <p className="mt-1 text-sm opacity-90">
            Suggest actions, or gently force them if needed. The citizen may push back!
          </p>
        </div>
      }
    >
      {children}
    </OnboardingHint>
  );
}

/**
 * Pipeline build hint.
 */
export function PipelineHint({ children }: ContextualHintProps) {
  return (
    <OnboardingHint
      hintKey={HINT_KEYS.PIPELINE_FIRST_BUILD}
      position="bottom"
      content="Drag agents here to compose them into workflows"
    >
      {children}
    </OnboardingHint>
  );
}

/**
 * Shortcuts discovery hint (shown in header area).
 */
export function ShortcutsHint({ children }: ContextualHintProps) {
  return (
    <OnboardingHint
      hintKey={HINT_KEYS.SHORTCUTS_DISCOVERY}
      position="bottom"
      delay={5000}
      content={
        <div>
          <strong>Pro tip!</strong>
          <p className="mt-1 text-sm opacity-90">
            Press <kbd className="px-1.5 py-0.5 bg-white/20 rounded text-xs">?</kbd> to see keyboard shortcuts
          </p>
        </div>
      }
    >
      {children}
    </OnboardingHint>
  );
}

// =============================================================================
// Portal-based Floating Hint
// =============================================================================

interface FloatingHintProps {
  /** Target element ref */
  targetRef: React.RefObject<HTMLElement>;
  /** Hint key */
  hintKey: HintKey;
  /** Hint content */
  content: ReactNode;
  /** Position */
  position?: 'top' | 'bottom' | 'left' | 'right';
  /** Offset in pixels */
  offset?: number;
}

/**
 * Floating hint that positions itself relative to a target element.
 * Uses portal to render outside the DOM hierarchy.
 */
export function FloatingHint({
  targetRef,
  hintKey,
  content,
  position = 'bottom',
  offset = 8,
}: FloatingHintProps) {
  const [dismissed, setDismissed] = useState(() => isHintDismissed(hintKey));
  const [coords, setCoords] = useState({ top: 0, left: 0 });
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (dismissed || !targetRef.current) return;

    const updatePosition = () => {
      const rect = targetRef.current?.getBoundingClientRect();
      if (!rect) return;

      let top = 0;
      let left = 0;

      switch (position) {
        case 'top':
          top = rect.top - offset;
          left = rect.left + rect.width / 2;
          break;
        case 'bottom':
          top = rect.bottom + offset;
          left = rect.left + rect.width / 2;
          break;
        case 'left':
          top = rect.top + rect.height / 2;
          left = rect.left - offset;
          break;
        case 'right':
          top = rect.top + rect.height / 2;
          left = rect.right + offset;
          break;
      }

      setCoords({ top, left });
    };

    // Initial position
    updatePosition();

    // Show after brief delay
    const timer = setTimeout(() => setVisible(true), 1000);

    // Update on scroll/resize
    window.addEventListener('scroll', updatePosition);
    window.addEventListener('resize', updatePosition);

    return () => {
      clearTimeout(timer);
      window.removeEventListener('scroll', updatePosition);
      window.removeEventListener('resize', updatePosition);
    };
  }, [dismissed, targetRef, position, offset]);

  const handleDismiss = () => {
    dismissHint(hintKey);
    setDismissed(true);
  };

  if (dismissed || !visible) return null;

  return createPortal(
    <div
      className="fixed z-50 hint-bubble"
      style={{
        top: coords.top,
        left: coords.left,
        transform:
          position === 'top' || position === 'bottom'
            ? 'translateX(-50%)'
            : 'translateY(-50%)',
      }}
    >
      <div className="bg-town-highlight text-white text-sm px-4 py-3 rounded-lg shadow-lg max-w-xs hint-attention">
        <div className="pr-6">{content}</div>
        <button
          onClick={handleDismiss}
          className="absolute top-2 right-2 text-white/70 hover:text-white"
          aria-label="Dismiss"
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M1 1L13 13M1 13L13 1" />
          </svg>
        </button>
      </div>
    </div>,
    document.body
  );
}

export default OnboardingHint;
