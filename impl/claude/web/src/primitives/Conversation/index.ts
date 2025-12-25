/**
 * Conversation Primitive Exports
 *
 * Unified chat system exports.
 */

export { Conversation } from './Conversation';
export { SafetyGate } from './SafetyGate';
export { InputArea } from './InputArea';
export { BranchTree } from './BranchTree';
export { useBranching } from './useBranching';
export { useCrystallization } from './useCrystallization';

export type {
  ConversationProps,
  SafetyGateProps,
  SafetyMode,
  Turn,
  Message,
  Mention,
  ToolUse,
  EvidenceDelta,
  PendingMutation,
  PendingApproval,
} from './types';
