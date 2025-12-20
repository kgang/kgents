/**
 * Chat Components
 *
 * UI components for the chat primitive (self.chat).
 * These provide AI metadata visibility and session controls.
 *
 * @see spec/protocols/chat.md
 * @see services/chat/node.py
 */

export { ModelSwitcher } from './ModelSwitcher';
export { useModelState } from './useModelState';
export { ContextGauge, ContextBreakdown } from './ContextGauge';

// Re-export types for convenience
export type { ModelSwitcherProps } from './ModelSwitcher';
export type { ContextGaugeProps, ContextBreakdownProps } from './ContextGauge';
