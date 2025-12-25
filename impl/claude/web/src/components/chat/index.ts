/**
 * Chat Components
 *
 * Real-time chat session components following spec/protocols/chat-web.md
 */

// Context and Confidence indicators (Part X.3, Part X.4)
export { ContextIndicator, type ContextIndicatorProps, type ChatEvidence } from './ContextIndicator';
export { ConfidenceIndicator, type ConfidenceIndicatorProps } from './ConfidenceIndicator';

// Constitutional visualization
export { ConstitutionalBadge, type ConstitutionalBadgeProps } from './ConstitutionalBadge';
export { ConstitutionalRadar, type ConstitutionalRadarProps } from './ConstitutionalRadar';
export type { PrincipleScore } from '../../types/chat';

// @mention system (Part VI)
export { MentionPicker } from './MentionPicker';
export type { MentionPickerProps, MentionType, MentionSuggestion } from './MentionPicker';

export { MentionCard } from './MentionCard';
export type { MentionCardProps, Mention } from './MentionCard';

export { useMentions } from './useMentions';
export type { UseMentionsResult, ResolvedContent } from './useMentions';

// Input area (Part X)
export { InputArea } from './InputArea';
export type { InputAreaProps } from './InputArea';

// Branching system (Part IV, Part X.2)
export { BranchTree } from './BranchTree';
export type { BranchTreeProps } from './BranchTree';

export { BranchControls } from './BranchControls';
export type { BranchControlsProps } from './BranchControls';

export { ForkModal } from './ForkModal';
export type { ForkModalProps } from './ForkModal';

export { useBranching } from './useBranching';
export type {
  UseBranchingResult,
  Branch,
  BranchTreeNode,
  MergeStrategy,
} from './useBranching';

// Crystallization system (Part IX.4, Part IX.4b)
export { TrailingSession } from './TrailingSession';
export type { TrailingSessionProps } from './TrailingSession';

export { SessionCrystal as SessionCrystalView } from './SessionCrystal';
export type { SessionCrystalProps } from './SessionCrystal';

// Export types from store
export type { Turn, SessionCrystal, TrailingSessionData } from './store';

export { useCrystallization } from './useCrystallization';
export type {
  UseCrystallizationOptions,
  UseCrystallizationResult,
  CrystallizationTrigger,
} from './useCrystallization';

// Tool transparency (Part VII)
export { ActionPanel } from './ActionPanel';
export type { ActionPanelProps } from './ActionPanel';

// Portal emissions (inline content access)
export { ChatPortal } from './ChatPortal';
export type { ChatPortalProps } from './ChatPortal';

// Export mutation types from store
export type { PendingMutation, MutationAcknowledgment } from './store';

// Export portal types from types
export type { PortalEmission } from '../../types/chat';

// Main chat components
export { ChatPanel } from './ChatPanel';
export type { ChatPanelProps } from './ChatPanel';

export { ChatSidebar } from './ChatSidebar';
export type { ChatSidebarProps } from './ChatSidebar';
