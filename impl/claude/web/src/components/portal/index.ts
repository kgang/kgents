/**
 * Portal Components - Expandable portal token visualization
 *
 * "You don't go to the document. The document comes to you."
 *
 * @see spec/protocols/portal-token.md
 * @see spec/protocols/context-perception.md
 */

export { PortalTree, default } from './PortalTree';
export type { PortalTreeProps, PortalNodeProps } from './PortalTree';

// Presence indicators for agent collaboration
export {
  PresenceBadge,
  SingleCursorBadge,
  PresenceFooter,
  InlinePresence,
} from './PresenceBadge';
export type {
  PresenceBadgeProps,
  SingleCursorBadgeProps,
  PresenceFooterProps,
  InlinePresenceProps,
} from './PresenceBadge';

// Proposal overlays for collaborative editing (Phase 5C)
export {
  ProposalOverlay,
  ProposalList,
  ProposalBadge,
} from './ProposalOverlay';
export type {
  ProposalOverlayProps,
  ProposalListProps,
  ProposalBadgeProps,
} from './ProposalOverlay';

// Trail panel for exploration history (Phase 5D)
export {
  TrailPanel,
  TrailIndicator,
} from './TrailPanel';
export type {
  TrailPanelProps,
  CollaborationEvent,
  TrailIndicatorProps,
} from './TrailPanel';

// Evidence badge for computed evidence strength (Phase 5D)
export {
  EvidenceBadge,
  EvidenceProgress,
} from './EvidenceBadge';
export type {
  EvidenceBadgeProps,
  EvidenceProgressProps,
} from './EvidenceBadge';
