/**
 * Chat Components
 *
 * Real-time chat session components following spec/protocols/chat-web.md
 */

// Context and Confidence indicators (Part X.3, Part X.4)
export { ContextIndicator, type ContextIndicatorProps, type ChatEvidence } from './ContextIndicator';
export { ConfidenceIndicator, type ConfidenceIndicatorProps } from './ConfidenceIndicator';
export { ConfidenceBar, type ConfidenceBarProps } from './ConfidenceBar';

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

export { CrystallizationTrigger as CrystallizationTriggerComponent } from './CrystallizationTrigger';
export type { CrystallizationTriggerProps } from './CrystallizationTrigger';

// Tool transparency (Part VII)
export { ToolPanel } from './ToolPanel';
export type { ToolPanelProps } from './ToolPanel';

export { ActionPanel } from './ActionPanel';
export type { ActionPanelProps } from './ActionPanel';

export { TransparencySelector } from './TransparencySelector';
export type { TransparencySelectorProps } from './TransparencySelector';

export { MutationAcknowledger } from './MutationAcknowledger';
export type { MutationAcknowledgerProps } from './MutationAcknowledger';

// Export mutation types from store
export type { PendingMutation, MutationAcknowledgment } from './store';
