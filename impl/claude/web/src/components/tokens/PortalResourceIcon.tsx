/**
 * PortalResourceIcon — Icon for portal resource types
 *
 * Shows visual indicator for different resource types:
 * - file: 📂
 * - chat: 💬
 * - turn: 🎯
 * - mark: 📝
 * - trace: 📜
 * - evidence: 📊
 * - constitutional: 🌈
 * - crystal: 💎
 * - node: 🔗
 *
 * See spec/protocols/portal-resource-system.md §2.2
 */

import type { PortalResourceType } from './types';

// =============================================================================
// Types
// =============================================================================

export interface PortalResourceIconProps {
  /** Resource type */
  type: PortalResourceType;
  /** Additional class name */
  className?: string;
}

// =============================================================================
// Constants
// =============================================================================

/** Icon mapping for resource types */
const RESOURCE_ICONS: Record<PortalResourceType, string> = {
  file: '📂',
  chat: '💬',
  turn: '🎯',
  mark: '📝',
  trace: '📜',
  evidence: '📊',
  constitutional: '🌈',
  crystal: '💎',
  node: '🔗',
} as const;

/** Accessible labels for resource types */
const RESOURCE_LABELS: Record<PortalResourceType, string> = {
  file: 'File',
  chat: 'Chat session',
  turn: 'Turn',
  mark: 'Mark',
  trace: 'Policy trace',
  evidence: 'Evidence bundle',
  constitutional: 'Constitutional scores',
  crystal: 'Memory crystal',
  node: 'AGENTESE node',
} as const;

// =============================================================================
// Component
// =============================================================================

/**
 * PortalResourceIcon — Visual indicator for resource type
 */
export function PortalResourceIcon({ type, className }: PortalResourceIconProps) {
  const icon = RESOURCE_ICONS[type];
  const label = RESOURCE_LABELS[type];

  return (
    <span
      className={`portal-resource-icon portal-resource-icon--${type} ${className || ''}`}
      role="img"
      aria-label={label}
      title={label}
    >
      {icon}
    </span>
  );
}

export default PortalResourceIcon;
