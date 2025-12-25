/**
 * Conversation Primitive Types
 *
 * Unified types for the consolidated chat system.
 * Merges ChatPanel, MutationAcknowledger, and PreExecutionGate into one coherent primitive.
 */

// =============================================================================
// Core Types
// =============================================================================

export interface Turn {
  turn_number: number;
  user_message: Message;
  assistant_response: Message;
  tools_used: ToolUse[];
  evidence_delta: EvidenceDelta;
  confidence: number;
  started_at: string;
  completed_at: string;
}

export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  mentions: Mention[];
  linearity_tag: 'required' | 'preserved' | 'droppable';
}

export interface Mention {
  type: 'file' | 'symbol' | 'spec' | 'witness' | 'web' | 'terminal' | 'project';
  query: string;
  resolved_path?: string;
}

export interface ToolUse {
  name: string;
  input: Record<string, unknown>;
  output: unknown;
  success: boolean;
  duration_ms: number;
}

export interface EvidenceDelta {
  tools_executed: number;
  tools_succeeded: number;
  confidence_change: number;
}

// =============================================================================
// Safety Gate Types
// =============================================================================

/**
 * Safety mode for tool execution.
 *
 * - 'gate': Pre-execution approval required (blocks execution)
 * - 'acknowledge': Post-execution acknowledgment (mutation awareness)
 * - 'trust': Tools run freely, minimal UI
 */
export type SafetyMode = 'gate' | 'acknowledge' | 'trust';

/**
 * Pending mutation requiring acknowledgment (post-execution).
 */
export interface PendingMutation {
  id: string;
  tool_name: string;
  description: string;
  target?: string;
  is_destructive: boolean;
  timestamp: string;
}

/**
 * Pending approval for destructive operation (pre-execution).
 */
export interface PendingApproval {
  request_id: string;
  tool_name: string;
  input_preview: string;
  is_destructive: boolean;
  timeout_seconds: number;
  timestamp: string;
}

// =============================================================================
// Conversation Props
// =============================================================================

export interface ConversationProps {
  /** Chat turns to display */
  turns: Turn[];

  /** Send message handler */
  onMessage: (content: string) => void;

  /** Branch/fork handler */
  onBranch?: (turnId: string) => void;

  /** Crystallize session handler */
  onCrystallize?: (selection: string[]) => void;

  /** Rewind to turn handler */
  onRewind?: (turnId: string) => void;

  /** Safety mode for tool execution */
  safetyMode: SafetyMode;

  /** Current streaming state */
  isStreaming?: boolean;

  /** Error message if any */
  error?: string | null;

  /** Pending mutations (post-execution acknowledgment) */
  pendingMutations?: PendingMutation[];

  /** Pending approvals (pre-execution gate) */
  pendingApprovals?: PendingApproval[];

  /** Acknowledge mutation callback */
  onAcknowledgeMutation?: (id: string, mode: 'click' | 'keyboard' | 'timeout_accept') => void;

  /** Approve tool execution callback */
  onApproveExecution?: (requestId: string, alwaysAllow: boolean) => void;

  /** Deny tool execution callback */
  onDenyExecution?: (requestId: string, reason?: string) => void;

  /** Compact mode for embedded use */
  compact?: boolean;

  /** Custom class name */
  className?: string;
}

// =============================================================================
// Safety Gate Props
// =============================================================================

export interface SafetyGateProps {
  /** Gate mode: 'pre' for approval, 'post' for acknowledgment */
  mode: 'pre' | 'post';

  /** Mutation (for post-execution acknowledgment) */
  mutation?: PendingMutation;

  /** Approval (for pre-execution gate) */
  approval?: PendingApproval;

  /** Callback when user approves (pre-execution) */
  onApprove?: (requestId: string, alwaysAllow: boolean) => void;

  /** Callback when user denies (pre-execution) */
  onDeny?: (requestId: string, reason?: string) => void;

  /** Callback when user acknowledges (post-execution) */
  onAcknowledge?: (id: string, mode: 'click' | 'keyboard' | 'timeout_accept') => void;
}
