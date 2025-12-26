/**
 * Chat Component Stories
 *
 * STARK BIOME Design System: 90% steel, 10% earned glow
 *
 * "Chat is not a feature. Chat is an affordance that collapses discrete into continuous."
 *
 * These stories showcase the complete chat system:
 * - ChatPanel: Main container with context, messages, input, branching
 * - MessageList: Conversation turns with streaming support
 * - AssistantMessage: Response bubbles with confidence and tool transparency
 * - UserMessage: User input with @mentions
 * - InputArea: Message input with fork/rewind controls
 * - ActionPanel: Tool invocation transparency
 * - BranchTree: D3-powered session visualization
 * - SessionCrystal: Crystallized session summary
 * - MentionPicker: Fuzzy autocomplete for @mentions
 * - MentionCard: Injected context display
 * - ConstitutionalBadge: Principle score indicator
 * - ConfidenceIndicator: Bayesian confidence display
 *
 * Philosophy: "The trail IS the proof. The proof IS the trail."
 *
 * @see spec/protocols/chat-web.md
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';
import { UserMessage } from './UserMessage';
import { AssistantMessage } from './AssistantMessage';
import { MessageList } from './MessageList';
import { InputArea } from './InputArea';
import { ActionPanel } from './ActionPanel';
import { BranchTree } from './BranchTree';
import { SessionCrystal } from './SessionCrystal';
import { MentionPicker, type MentionSuggestion } from './MentionPicker';
import { MentionCard, type Mention } from './MentionCard';
import { ConstitutionalBadge } from './ConstitutionalBadge';
import { ConfidenceIndicator } from './ConfidenceIndicator';
import { ContextIndicator } from './ContextIndicator';
import type { ChatSession, Message, Turn, ToolUse, EvidenceDelta, ChatEvidence, SessionCrystal as SessionCrystalData } from './store';
import type { Branch, BranchTreeNode } from './useBranching';
import type { PrincipleScore } from '../../types/chat';

// Import CSS
import './UserMessage.css';
import './AssistantMessage.css';
import './MessageList.css';
import './InputArea.css';
import './BranchTree.css';
import './MentionPicker.css';
import './MentionCard.css';
import './ConstitutionalBadge.css';
import './ConfidenceIndicator.css';
import './ContextIndicator.css';

// =============================================================================
// Mock Data - Messages
// =============================================================================

const now = new Date();
const fiveMinutesAgo = new Date(now.getTime() - 5 * 60 * 1000).toISOString();
const tenMinutesAgo = new Date(now.getTime() - 10 * 60 * 1000).toISOString();
const twentyMinutesAgo = new Date(now.getTime() - 20 * 60 * 1000).toISOString();

/** Simple user message */
const mockUserMessage: Message = {
  role: 'user',
  content: 'Can you help me understand the branching system in the chat protocol?',
  mentions: [],
  linearity_tag: 'preserved',
};

/** User message with @mentions */
const mockUserMessageWithMentions: Message = {
  role: 'user',
  content: 'Look at the implementation and explain the merge strategies',
  mentions: [
    { type: 'file', query: 'useBranching.ts' },
    { type: 'spec', query: 'chat-web.md' },
  ],
  linearity_tag: 'required',
};

/** Simple assistant response */
const mockAssistantMessage: Message = {
  role: 'assistant',
  content: `The chat branching system implements a git-like DAG (Directed Acyclic Graph) for conversation history. Here are the key concepts:

**Fork**: Create a new branch at the current turn. Maximum 3 active branches (cognitive limit).

**Merge Strategies**:
- \`sequential\`: Append branch turns after current
- \`interleave\`: Merge by timestamp
- \`manual\`: User selects specific turns

**Rewind**: Move back N turns, discarding later turns. Unlike git reset, this is a K-Block operation.

The visual tree uses D3.js for layout with square nodes (brutalist, not rounded) and angular paths.`,
  mentions: [],
  linearity_tag: 'preserved',
};

/** Assistant response with streaming cursor */
const mockStreamingAssistantMessage: Message = {
  role: 'assistant',
  content: 'The branch tree visualization uses D3.js hierarchy layout with proper hierarchical spacing. Curved Bezier paths connect branch nodes, and the current branch shows an animated glow effect. You can click to switch branches or right-click for merge',
  mentions: [],
  linearity_tag: 'preserved',
};

// =============================================================================
// Mock Data - Tool Usage
// =============================================================================

const mockToolsSuccess: ToolUse[] = [
  {
    name: 'Read',
    input: { file_path: '/src/components/chat/BranchTree.tsx' },
    output: '// BranchTree Component...',
    success: true,
    duration_ms: 45,
  },
  {
    name: 'Grep',
    input: { pattern: 'MergeStrategy', path: '/src' },
    output: '5 matches found',
    success: true,
    duration_ms: 120,
  },
];

const mockToolsMixed: ToolUse[] = [
  {
    name: 'Read',
    input: { file_path: '/src/components/chat/store.ts' },
    output: '// Chat Store...',
    success: true,
    duration_ms: 38,
  },
  {
    name: 'Write',
    input: { file_path: '/tmp/test.txt', content: 'test' },
    output: 'Permission denied',
    success: false,
    duration_ms: 15,
  },
  {
    name: 'Bash',
    input: { command: 'npm run typecheck' },
    output: 'No errors found',
    success: true,
    duration_ms: 2340,
  },
];

const mockToolsFailed: ToolUse[] = [
  {
    name: 'WebFetch',
    input: { url: 'https://example.com/api' },
    output: 'Network timeout',
    success: false,
    duration_ms: 30000,
  },
];

// =============================================================================
// Mock Data - Evidence
// =============================================================================

const mockHighEvidenceDelta: EvidenceDelta = {
  tools_executed: 3,
  tools_succeeded: 3,
  confidence_change: 0.15,
};

const mockMediumEvidenceDelta: EvidenceDelta = {
  tools_executed: 2,
  tools_succeeded: 1,
  confidence_change: 0.02,
};

const mockLowEvidenceDelta: EvidenceDelta = {
  tools_executed: 1,
  tools_succeeded: 0,
  confidence_change: -0.08,
};

const mockChatEvidence: ChatEvidence = {
  prior_alpha: 12,
  prior_beta: 3,
  confidence: 0.85,
  should_stop: false,
  tools_succeeded: 25,
  tools_failed: 3,
  ashc_equivalence: 0.92,
};

// Low confidence evidence (used in ConfidenceIndicator stories)
const mockLowChatEvidence: ChatEvidence = {
  prior_alpha: 2,
  prior_beta: 5,
  confidence: 0.35,
  should_stop: false,
  tools_succeeded: 2,
  tools_failed: 5,
  ashc_equivalence: 0.42,
};

// =============================================================================
// Mock Data - Turns
// =============================================================================

const mockTurn1: Turn = {
  turn_number: 1,
  user_message: mockUserMessage,
  assistant_response: mockAssistantMessage,
  tools_used: mockToolsSuccess,
  evidence_delta: mockHighEvidenceDelta,
  confidence: 0.82,
  started_at: twentyMinutesAgo,
  completed_at: tenMinutesAgo,
};

const mockTurn2: Turn = {
  turn_number: 2,
  user_message: mockUserMessageWithMentions,
  assistant_response: {
    role: 'assistant',
    content: `Looking at the implementation in \`useBranching.ts\`, I can see the merge strategies are implemented as follows:

1. **Sequential** (default): Simple concatenation of turns
2. **Interleave**: Sorts by timestamp, useful for parallel exploration
3. **Manual**: Opens a merge dialog for turn selection

The spec in \`chat-web.md\` defines MAX_BRANCHES = 3 as a cognitive limit to prevent branch explosion.`,
    mentions: [],
    linearity_tag: 'preserved',
  },
  tools_used: mockToolsMixed,
  evidence_delta: mockMediumEvidenceDelta,
  confidence: 0.75,
  started_at: tenMinutesAgo,
  completed_at: fiveMinutesAgo,
};

// =============================================================================
// Mock Data - Session
// =============================================================================

const mockSession: ChatSession = {
  id: 'session-001',
  project_id: 'kgents',
  branch_name: 'main',
  parent_id: null,
  fork_point: null,
  turns: [mockTurn1, mockTurn2],
  context_size: 45000,
  evidence: mockChatEvidence,
  created_at: twentyMinutesAgo,
  last_active: fiveMinutesAgo,
};

const mockEmptySession: ChatSession = {
  id: 'session-002',
  project_id: null,
  branch_name: 'main',
  parent_id: null,
  fork_point: null,
  turns: [],
  context_size: 0,
  evidence: {
    prior_alpha: 1,
    prior_beta: 1,
    confidence: 0.5,
    should_stop: false,
    tools_succeeded: 0,
    tools_failed: 0,
  },
  created_at: now.toISOString(),
  last_active: now.toISOString(),
};

const mockHighContextSession: ChatSession = {
  ...mockSession,
  id: 'session-003',
  context_size: 175000, // 87.5% of 200k
};

const mockCriticalContextSession: ChatSession = {
  ...mockSession,
  id: 'session-004',
  context_size: 195000, // 97.5% of 200k
};

// =============================================================================
// Mock Data - Branches
// =============================================================================

const mockBranches: Branch[] = [
  {
    id: 'branch-main',
    parent_id: null,
    fork_point: 0,
    branch_name: 'main',
    turn_count: 5,
    created_at: twentyMinutesAgo,
    last_active: fiveMinutesAgo,
    is_merged: false,
    merged_into: null,
    is_active: true,
  },
  {
    id: 'branch-explore',
    parent_id: 'branch-main',
    fork_point: 2,
    branch_name: 'explore-alternative',
    turn_count: 3,
    created_at: tenMinutesAgo,
    last_active: fiveMinutesAgo,
    is_merged: false,
    merged_into: null,
    is_active: false,
  },
  {
    id: 'branch-refactor',
    parent_id: 'branch-main',
    fork_point: 3,
    branch_name: 'refactor-approach',
    turn_count: 2,
    created_at: fiveMinutesAgo,
    last_active: now.toISOString(),
    is_merged: false,
    merged_into: null,
    is_active: false,
  },
];

const mockBranchTree: BranchTreeNode = {
  branch: mockBranches[0],
  children: [
    { branch: mockBranches[1], children: [] },
    { branch: mockBranches[2], children: [] },
  ],
};

// =============================================================================
// Mock Data - Session Crystal
// =============================================================================

const mockSessionCrystal: SessionCrystalData = {
  session_id: 'session-001',
  title: 'Chat Branching Implementation Review',
  summary: 'Explored the chat branching system including fork, merge, and rewind operations. Identified the D3.js tree visualization and understood the MAX_BRANCHES cognitive limit of 3.',
  key_decisions: [
    'Use angular paths instead of Bezier curves for brutalist aesthetic',
    'Implement all three merge strategies: sequential, interleave, manual',
    'Keep MAX_BRANCHES at 3 based on cognitive load research',
  ],
  artifacts: [
    'src/components/chat/BranchTree.tsx',
    'src/components/chat/useBranching.ts',
    'spec/protocols/chat-web.md',
  ],
  final_evidence: {
    confidence: 0.88,
    tools_succeeded: 12,
    tools_failed: 1,
  },
  created_at: twentyMinutesAgo,
  turn_count: 5,
};

// =============================================================================
// Mock Data - Mentions
// =============================================================================

const mockMention: Mention = {
  id: 'mention-1',
  type: 'file',
  value: 'useBranching.ts',
  label: '@file:useBranching.ts',
  content: `export function useBranching(
  sessionId: string,
  onBranchChange?: (branchId: string) => void
): UseBranchingResult {
  const [branches, setBranches] = useState<Branch[]>([]);
  // ... hook implementation
}`,
};

const mockMentionWithError: Mention = {
  id: 'mention-2',
  type: 'web',
  value: 'https://api.example.com/docs',
  label: '@web:https://api.example.com/docs',
  error: 'Failed to fetch: Network timeout after 30s',
};

const mockMentionLoading: Mention = {
  id: 'mention-3',
  type: 'symbol',
  value: 'ChatSession',
  label: '@symbol:ChatSession',
  content: undefined, // Still loading
};

// =============================================================================
// Mock Data - Constitutional Scores
// =============================================================================

const mockHighScores: PrincipleScore = {
  tasteful: 0.92,
  curated: 0.88,
  ethical: 0.95,
  joy_inducing: 0.85,
  composable: 0.90,
  heterarchical: 0.82,
  generative: 0.87,
};

const mockMediumScores: PrincipleScore = {
  tasteful: 0.68,
  curated: 0.72,
  ethical: 0.65,
  joy_inducing: 0.58,
  composable: 0.75,
  heterarchical: 0.62,
  generative: 0.70,
};

const mockLowScores: PrincipleScore = {
  tasteful: 0.35,
  curated: 0.42,
  ethical: 0.48,
  joy_inducing: 0.28,
  composable: 0.38,
  heterarchical: 0.45,
  generative: 0.32,
};

// =============================================================================
// Meta Configuration
// =============================================================================

const meta: Meta = {
  title: 'Components/Chat',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: `
## Chat System Components

The chat system implements the **ChatKBlock** pattern - a transactional conversation model with fork/merge/rewind capabilities inspired by version control.

### STARK BIOME Design Philosophy

- **90% Steel**: Dark backgrounds (#141418), minimal decoration, brutalist typography
- **10% Earned Glow**: Color only for active states, confidence tiers, and principle badges

### Key Components

| Component | Purpose |
|-----------|---------|
| \`ChatPanel\` | Main container orchestrating all chat UI |
| \`MessageList\` | Scrollable conversation turns |
| \`UserMessage\` | User input with @mentions |
| \`AssistantMessage\` | Response with confidence + tools |
| \`InputArea\` | Message input with fork/rewind |
| \`ActionPanel\` | Tool transparency |
| \`BranchTree\` | D3 session visualization |
| \`SessionCrystal\` | Crystallized summary |
| \`MentionPicker\` | Fuzzy @mention autocomplete |
| \`MentionCard\` | Injected context display |
| \`ConstitutionalBadge\` | Principle score indicator |
| \`ConfidenceIndicator\` | Bayesian confidence |
| \`ContextIndicator\` | Token usage + cost |

### Evidence & Stopping

The chat system uses Bayesian evidence accumulation (inspired by ASHC):
- **High confidence (>0.80)**: Green indicators
- **Medium (0.50-0.80)**: Yellow/orange indicators
- **Low (<0.50)**: Red indicators

"The proof IS the decision. The mark IS the witness."
        `,
      },
    },
    layout: 'padded',
    backgrounds: {
      default: 'dark',
      values: [
        { name: 'dark', value: '#141418' },
        { name: 'steel', value: '#1A1A1F' },
      ],
    },
  },
};

export default meta;

// =============================================================================
// UserMessage Stories
// =============================================================================

export const UserMessageDefault: StoryObj = {
  name: 'UserMessage / Default',
  render: () => (
    <div style={{ maxWidth: '600px', padding: '16px' }}>
      <UserMessage message={mockUserMessage} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Simple user message without mentions. Right-aligned bubble with clean typography.',
      },
    },
  },
};

export const UserMessageWithMentions: StoryObj = {
  name: 'UserMessage / With @Mentions',
  render: () => (
    <div style={{ maxWidth: '600px', padding: '16px' }}>
      <UserMessage message={mockUserMessageWithMentions} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'User message with @file and @spec mentions. Mentions appear as pills above the message content.',
      },
    },
  },
};

export const UserMessagePinned: StoryObj = {
  name: 'UserMessage / Pinned (Required)',
  render: () => (
    <div style={{ maxWidth: '600px', padding: '16px' }}>
      <UserMessage message={mockUserMessageWithMentions} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Message with linearity_tag="required" shows a pin indicator. These messages are never dropped during compression.',
      },
    },
  },
};

// =============================================================================
// AssistantMessage Stories
// =============================================================================

export const AssistantMessageDefault: StoryObj = {
  name: 'AssistantMessage / Default',
  render: () => (
    <div style={{ maxWidth: '600px', padding: '16px' }}>
      <AssistantMessage
        message={mockAssistantMessage}
        tools={[]}
        confidence={0.85}
        evidenceDelta={mockHighEvidenceDelta}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Assistant response with high confidence. Shows green confidence indicator.',
      },
    },
  },
};

export const AssistantMessageWithTools: StoryObj = {
  name: 'AssistantMessage / With Tools',
  render: () => (
    <div style={{ maxWidth: '600px', padding: '16px' }}>
      <AssistantMessage
        message={mockAssistantMessage}
        tools={mockToolsSuccess}
        confidence={0.82}
        evidenceDelta={mockHighEvidenceDelta}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Response with collapsible tool transparency. Click toggle to expand action details.',
      },
    },
  },
};

export const AssistantMessageMixedTools: StoryObj = {
  name: 'AssistantMessage / Mixed Tool Results',
  render: () => (
    <div style={{ maxWidth: '600px', padding: '16px' }}>
      <AssistantMessage
        message={mockAssistantMessage}
        tools={mockToolsMixed}
        confidence={0.65}
        evidenceDelta={mockMediumEvidenceDelta}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Response with both successful and failed tool calls. Medium confidence indicator.',
      },
    },
  },
};

export const AssistantMessageStreaming: StoryObj = {
  name: 'AssistantMessage / Streaming',
  render: () => (
    <div style={{ maxWidth: '600px', padding: '16px' }}>
      <AssistantMessage
        message={mockStreamingAssistantMessage}
        tools={[]}
        confidence={0}
        evidenceDelta={{ tools_executed: 0, tools_succeeded: 0, confidence_change: 0 }}
        isStreaming
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Streaming response with blinking cursor. Confidence indicator hidden during streaming.',
      },
    },
  },
};

export const AssistantMessageLowConfidence: StoryObj = {
  name: 'AssistantMessage / Low Confidence',
  render: () => (
    <div style={{ maxWidth: '600px', padding: '16px' }}>
      <AssistantMessage
        message={{
          role: 'assistant',
          content: 'I attempted to fetch the API documentation but the request timed out. The network may be experiencing issues.',
          mentions: [],
          linearity_tag: 'preserved',
        }}
        tools={mockToolsFailed}
        confidence={0.35}
        evidenceDelta={mockLowEvidenceDelta}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Response with low confidence after tool failure. Red indicator warns of uncertainty.',
      },
    },
  },
};

// =============================================================================
// MessageList Stories
// =============================================================================

export const MessageListDefault: StoryObj = {
  name: 'MessageList / Default Conversation',
  render: () => (
    <div style={{ maxWidth: '700px', height: '500px', overflow: 'auto', padding: '16px' }}>
      <MessageList session={mockSession} isStreaming={false} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Full conversation with multiple turns. Each turn shows user message followed by assistant response.',
      },
    },
  },
};

export const MessageListEmpty: StoryObj = {
  name: 'MessageList / Empty State',
  render: () => (
    <div style={{ maxWidth: '700px', height: '300px', padding: '16px' }}>
      <MessageList session={mockEmptySession} isStreaming={false} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Empty conversation shows helpful prompt to start chatting.',
      },
    },
  },
};

export const MessageListStreaming: StoryObj = {
  name: 'MessageList / Streaming Active',
  render: () => (
    <div style={{ maxWidth: '700px', height: '500px', overflow: 'auto', padding: '16px' }}>
      <MessageList session={mockSession} isStreaming={true} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Conversation with streaming indicator at the bottom showing assistant is generating.',
      },
    },
  },
};

// =============================================================================
// InputArea Stories
// =============================================================================

export const InputAreaDefault: StoryObj = {
  name: 'InputArea / Default',
  render: () => {
    const handleSend = async (message: string) => {
      console.info('Sending:', message);
    };
    const handleRewind = async (turns: number) => {
      console.info('Rewinding:', turns);
    };

    return (
      <div style={{ maxWidth: '700px', padding: '16px' }}>
        <InputArea onSend={handleSend} onRewind={handleRewind} />
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Default input area with rewind and fork controls. Enter to send, Shift+Enter for newline.',
      },
    },
  },
};

export const InputAreaCompact: StoryObj = {
  name: 'InputArea / Compact',
  render: () => {
    const handleSend = async (message: string) => {
      console.info('Sending:', message);
    };
    const handleRewind = async (turns: number) => {
      console.info('Rewinding:', turns);
    };

    return (
      <div style={{ maxWidth: '500px', padding: '16px' }}>
        <InputArea onSend={handleSend} onRewind={handleRewind} compact />
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Compact mode hides fork/rewind controls. Used for embedded chat.',
      },
    },
  },
};

export const InputAreaDisabled: StoryObj = {
  name: 'InputArea / Disabled (Streaming)',
  render: () => {
    const handleSend = async (message: string) => {
      console.info('Sending:', message);
    };
    const handleRewind = async (turns: number) => {
      console.info('Rewinding:', turns);
    };

    return (
      <div style={{ maxWidth: '700px', padding: '16px' }}>
        <InputArea onSend={handleSend} onRewind={handleRewind} disabled />
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Disabled state while assistant is streaming. Prevents duplicate sends.',
      },
    },
  },
};

// =============================================================================
// ActionPanel Stories
// =============================================================================

export const ActionPanelSuccess: StoryObj = {
  name: 'ActionPanel / All Success',
  render: () => (
    <div style={{ maxWidth: '500px', padding: '16px' }}>
      <ActionPanel tools={mockToolsSuccess} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Tool panel showing all successful executions. Click individual tools to expand input/output.',
      },
    },
  },
};

export const ActionPanelMixed: StoryObj = {
  name: 'ActionPanel / Mixed Results',
  render: () => (
    <div style={{ maxWidth: '500px', padding: '16px' }}>
      <ActionPanel tools={mockToolsMixed} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Mixed results with success and failure. Summary shows count of each.',
      },
    },
  },
};

export const ActionPanelFailed: StoryObj = {
  name: 'ActionPanel / All Failed',
  render: () => (
    <div style={{ maxWidth: '500px', padding: '16px' }}>
      <ActionPanel tools={mockToolsFailed} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'All tools failed. Red indicators show error states.',
      },
    },
  },
};

// =============================================================================
// BranchTree Stories
// =============================================================================

export const BranchTreeDefault: StoryObj = {
  name: 'BranchTree / Default',
  render: () => (
    <div style={{ maxWidth: '400px', padding: '16px' }}>
      <BranchTree
        tree={mockBranchTree}
        branches={mockBranches}
        currentBranch="branch-main"
        canFork={false} // At max
        onSwitchBranch={(id) => console.info('Switch to:', id)}
        onMergeBranch={(id, strategy) => console.info('Merge:', id, strategy)}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Branch tree with 3 branches (max). Main branch is active. Click nodes to switch, right-click for merge menu.',
      },
    },
  },
};

export const BranchTreeEmpty: StoryObj = {
  name: 'BranchTree / Empty',
  render: () => (
    <div style={{ maxWidth: '400px', padding: '16px' }}>
      <BranchTree
        tree={null}
        branches={[]}
        currentBranch=""
        canFork={true}
        onSwitchBranch={(id) => console.info('Switch to:', id)}
        onMergeBranch={(id, strategy) => console.info('Merge:', id, strategy)}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Empty tree shows placeholder state.',
      },
    },
  },
};

export const BranchTreeCompact: StoryObj = {
  name: 'BranchTree / Compact',
  render: () => (
    <div style={{ maxWidth: '300px', padding: '16px' }}>
      <BranchTree
        tree={mockBranchTree}
        branches={mockBranches}
        currentBranch="branch-explore"
        canFork={false}
        onSwitchBranch={(id) => console.info('Switch to:', id)}
        onMergeBranch={(id, strategy) => console.info('Merge:', id, strategy)}
        compact
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Compact mode for mobile. Smaller nodes, hidden labels.',
      },
    },
  },
};

export const BranchTreeWithMerged: StoryObj = {
  name: 'BranchTree / With Merged Branch',
  render: () => {
    const branchesWithMerged: Branch[] = [
      ...mockBranches,
      {
        id: 'branch-archived',
        parent_id: 'branch-main',
        fork_point: 1,
        branch_name: 'archived-experiment',
        turn_count: 4,
        created_at: twentyMinutesAgo,
        last_active: tenMinutesAgo,
        is_merged: true,
        merged_into: 'branch-main',
        is_active: false,
      },
    ];

    const treeWithMerged: BranchTreeNode = {
      branch: branchesWithMerged[0],
      children: [
        { branch: branchesWithMerged[1], children: [] },
        { branch: branchesWithMerged[2], children: [] },
        { branch: branchesWithMerged[3], children: [] },
      ],
    };

    return (
      <div style={{ maxWidth: '500px', padding: '16px' }}>
        <BranchTree
          tree={treeWithMerged}
          branches={branchesWithMerged}
          currentBranch="branch-main"
          canFork={true} // Can fork because one is merged
          onSwitchBranch={(id) => console.info('Switch to:', id)}
          onMergeBranch={(id, strategy) => console.info('Merge:', id, strategy)}
        />
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Tree with a merged branch. Merged branches appear grayed out and cannot be switched to.',
      },
    },
  },
};

// =============================================================================
// SessionCrystal Stories
// =============================================================================

export const SessionCrystalPanel: StoryObj = {
  name: 'SessionCrystal / Panel Mode',
  render: () => {
    const [isOpen, setIsOpen] = useState(true);

    return (
      <div style={{ position: 'relative', height: '600px' }}>
        <button onClick={() => setIsOpen(!isOpen)} style={{ marginBottom: '16px' }}>
          Toggle Crystal Panel
        </button>
        <SessionCrystal
          crystal={mockSessionCrystal}
          isOpen={isOpen}
          onClose={() => setIsOpen(false)}
          mode="panel"
        />
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Side panel showing crystallized session summary. Shows key decisions, artifacts, and final evidence.',
      },
    },
  },
};

export const SessionCrystalModal: StoryObj = {
  name: 'SessionCrystal / Modal Mode',
  render: () => {
    const [isOpen, setIsOpen] = useState(true);

    return (
      <div>
        <button onClick={() => setIsOpen(true)}>Open Crystal Modal</button>
        <SessionCrystal
          crystal={mockSessionCrystal}
          isOpen={isOpen}
          onClose={() => setIsOpen(false)}
          mode="modal"
        />
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Modal overlay for viewing crystallized session. Centered with backdrop blur.',
      },
    },
  },
};

// =============================================================================
// MentionPicker Stories
// =============================================================================

export const MentionPickerDefault: StoryObj = {
  name: 'MentionPicker / Default (Type Suggestions)',
  render: () => (
    <div style={{ position: 'relative', height: '400px', padding: '16px' }}>
      <MentionPicker
        isOpen={true}
        query=""
        onSelect={(s) => console.info('Selected:', s)}
        onClose={() => console.info('Closed')}
        position={{ top: 50, left: 16 }}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Empty query shows all mention types. Use arrow keys or j/k to navigate.',
      },
    },
  },
};

export const MentionPickerWithFiles: StoryObj = {
  name: 'MentionPicker / With File Results',
  render: () => (
    <div style={{ position: 'relative', height: '400px', padding: '16px' }}>
      <MentionPicker
        isOpen={true}
        query="file:Branch"
        onSelect={(s) => console.info('Selected:', s)}
        onClose={() => console.info('Closed')}
        position={{ top: 50, left: 16 }}
        availableFiles={[
          'src/components/chat/BranchTree.tsx',
          'src/components/chat/useBranching.ts',
          'src/components/chat/BranchControls.tsx',
        ]}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'File search with fuzzy matching. Matching characters are highlighted.',
      },
    },
  },
};

export const MentionPickerWithRecent: StoryObj = {
  name: 'MentionPicker / With Recent',
  render: () => {
    const recentMentions: MentionSuggestion[] = [
      { type: 'file', value: 'store.ts', label: '@file:store.ts', recent: true },
      { type: 'spec', value: 'chat-web.md', label: '@spec:chat-web.md', recent: true },
    ];

    return (
      <div style={{ position: 'relative', height: '400px', padding: '16px' }}>
        <MentionPicker
          isOpen={true}
          query="s"
          onSelect={(s) => console.info('Selected:', s)}
          onClose={() => console.info('Closed')}
          position={{ top: 50, left: 16 }}
          recentMentions={recentMentions}
        />
      </div>
    );
  },
  parameters: {
    docs: {
      description: {
        story: 'Recent mentions appear at top with clock icon.',
      },
    },
  },
};

// =============================================================================
// MentionCard Stories
// =============================================================================

export const MentionCardDefault: StoryObj = {
  name: 'MentionCard / Default (Collapsed)',
  render: () => (
    <div style={{ maxWidth: '400px', padding: '16px' }}>
      <MentionCard
        mention={mockMention}
        onDismiss={(id) => console.info('Dismissed:', id)}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Collapsed mention card showing type and value. Click to expand full content.',
      },
    },
  },
};

export const MentionCardExpanded: StoryObj = {
  name: 'MentionCard / Expanded',
  render: () => (
    <div style={{ maxWidth: '500px', padding: '16px' }}>
      <MentionCard
        mention={mockMention}
        onDismiss={(id) => console.info('Dismissed:', id)}
        defaultExpanded
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Expanded card showing full content preview with syntax highlighting.',
      },
    },
  },
};

export const MentionCardError: StoryObj = {
  name: 'MentionCard / Error State',
  render: () => (
    <div style={{ maxWidth: '400px', padding: '16px' }}>
      <MentionCard
        mention={mockMentionWithError}
        onDismiss={(id) => console.info('Dismissed:', id)}
        defaultExpanded
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Mention that failed to resolve. Shows error message in red.',
      },
    },
  },
};

export const MentionCardLoading: StoryObj = {
  name: 'MentionCard / Loading',
  render: () => (
    <div style={{ maxWidth: '400px', padding: '16px' }}>
      <MentionCard
        mention={mockMentionLoading}
        onDismiss={(id) => console.info('Dismissed:', id)}
        defaultExpanded
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Mention still resolving. Shows loading indicator.',
      },
    },
  },
};

// =============================================================================
// ConstitutionalBadge Stories
// =============================================================================

export const ConstitutionalBadgeHigh: StoryObj = {
  name: 'ConstitutionalBadge / High Score',
  render: () => (
    <div style={{ display: 'flex', gap: '16px', padding: '16px' }}>
      <ConstitutionalBadge scores={mockHighScores} size="sm" onClick={() => console.info('Clicked')} />
      <ConstitutionalBadge scores={mockHighScores} size="md" onClick={() => console.info('Clicked')} />
      <ConstitutionalBadge scores={mockHighScores} size="lg" onClick={() => console.info('Clicked')} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'High constitutional alignment (>80). Green indicator with HIGH label.',
      },
    },
  },
};

export const ConstitutionalBadgeMedium: StoryObj = {
  name: 'ConstitutionalBadge / Medium Score',
  render: () => (
    <div style={{ display: 'flex', gap: '16px', padding: '16px' }}>
      <ConstitutionalBadge scores={mockMediumScores} size="sm" onClick={() => console.info('Clicked')} />
      <ConstitutionalBadge scores={mockMediumScores} size="md" onClick={() => console.info('Clicked')} />
      <ConstitutionalBadge scores={mockMediumScores} size="lg" onClick={() => console.info('Clicked')} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Medium alignment (50-80). Yellow/orange indicator with MED label.',
      },
    },
  },
};

export const ConstitutionalBadgeLow: StoryObj = {
  name: 'ConstitutionalBadge / Low Score',
  render: () => (
    <div style={{ display: 'flex', gap: '16px', padding: '16px' }}>
      <ConstitutionalBadge scores={mockLowScores} size="sm" onClick={() => console.info('Clicked')} />
      <ConstitutionalBadge scores={mockLowScores} size="md" onClick={() => console.info('Clicked')} />
      <ConstitutionalBadge scores={mockLowScores} size="lg" onClick={() => console.info('Clicked')} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Low alignment (<50). Red indicator with LOW label. Requires attention.',
      },
    },
  },
};

// =============================================================================
// ConfidenceIndicator Stories
// =============================================================================

export const ConfidenceIndicatorHigh: StoryObj = {
  name: 'ConfidenceIndicator / High',
  render: () => (
    <div style={{ display: 'flex', gap: '24px', padding: '16px' }}>
      <ConfidenceIndicator confidence={0.92} evidenceDelta={mockHighEvidenceDelta} size="sm" />
      <ConfidenceIndicator confidence={0.88} evidenceDelta={mockHighEvidenceDelta} size="md" />
      <ConfidenceIndicator confidence={0.85} evidenceDelta={mockHighEvidenceDelta} size="lg" />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'High confidence (>0.80). Green filled circle indicator.',
      },
    },
  },
};

export const ConfidenceIndicatorMedium: StoryObj = {
  name: 'ConfidenceIndicator / Medium',
  render: () => (
    <div style={{ display: 'flex', gap: '24px', padding: '16px' }}>
      <ConfidenceIndicator confidence={0.65} evidenceDelta={mockMediumEvidenceDelta} size="sm" />
      <ConfidenceIndicator confidence={0.58} evidenceDelta={mockMediumEvidenceDelta} size="md" />
      <ConfidenceIndicator confidence={0.72} evidenceDelta={mockMediumEvidenceDelta} size="lg" />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Medium confidence (0.50-0.80). Half-filled circle indicator.',
      },
    },
  },
};

export const ConfidenceIndicatorLow: StoryObj = {
  name: 'ConfidenceIndicator / Low',
  render: () => (
    <div style={{ display: 'flex', gap: '24px', padding: '16px' }}>
      <ConfidenceIndicator confidence={0.35} evidenceDelta={mockLowEvidenceDelta} size="sm" />
      <ConfidenceIndicator confidence={0.28} evidenceDelta={mockLowEvidenceDelta} size="md" />
      <ConfidenceIndicator confidence={0.42} evidenceDelta={mockLowEvidenceDelta} size="lg" />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Low confidence (<0.50). Empty circle indicator. Signals uncertainty.',
      },
    },
  },
};

export const ConfidenceIndicatorWithDetails: StoryObj = {
  name: 'ConfidenceIndicator / With Details',
  render: () => (
    <div style={{ maxWidth: '400px', padding: '16px' }}>
      <ConfidenceIndicator
        confidence={0.85}
        evidence={mockChatEvidence}
        evidenceDelta={mockHighEvidenceDelta}
        showDetails
        size="lg"
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Expanded view showing Bayesian prior, success rate, and ASHC equivalence.',
      },
    },
  },
};

export const ConfidenceIndicatorLowWithDetails: StoryObj = {
  name: 'ConfidenceIndicator / Low With Details',
  render: () => (
    <div style={{ maxWidth: '400px', padding: '16px' }}>
      <ConfidenceIndicator
        confidence={0.35}
        evidence={mockLowChatEvidence}
        evidenceDelta={mockLowEvidenceDelta}
        showDetails
        size="lg"
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Low confidence with full evidence breakdown. Shows weak Bayesian prior and tool failures.',
      },
    },
  },
};

// =============================================================================
// ContextIndicator Stories
// =============================================================================

export const ContextIndicatorNormal: StoryObj = {
  name: 'ContextIndicator / Normal Usage',
  render: () => (
    <div style={{ maxWidth: '600px', padding: '16px' }}>
      <ContextIndicator session={mockSession} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Normal context usage (~22%). Green progress bar.',
      },
    },
  },
};

export const ContextIndicatorCompressing: StoryObj = {
  name: 'ContextIndicator / Compression Active',
  render: () => (
    <div style={{ maxWidth: '600px', padding: '16px' }}>
      <ContextIndicator session={mockHighContextSession} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Context at 87.5%, compression is active. Yellow/orange indicator.',
      },
    },
  },
};

export const ContextIndicatorCritical: StoryObj = {
  name: 'ContextIndicator / Critical',
  render: () => (
    <div style={{ maxWidth: '600px', padding: '16px' }}>
      <ContextIndicator session={mockCriticalContextSession} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Context at 97.5%, critical warning. Red indicator, aggressive compression needed.',
      },
    },
  },
};

// =============================================================================
// Full Conversation Flow Story
// =============================================================================

export const FullConversationFlow: StoryObj = {
  name: 'Full Chat Flow',
  render: () => (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
        maxWidth: '800px',
        height: '700px',
        background: '#141418',
        borderRadius: '8px',
        border: '1px solid #28282F',
        padding: '16px',
      }}
    >
      {/* Context Indicator */}
      <ContextIndicator session={mockSession} />

      {/* Message List */}
      <div style={{ flex: 1, overflow: 'auto' }}>
        <MessageList session={mockSession} isStreaming={false} />
      </div>

      {/* Input Area */}
      <InputArea
        onSend={async (msg) => console.info('Send:', msg)}
        onRewind={async (n) => console.info('Rewind:', n)}
        onFork={async (name) => console.info('Fork:', name)}
        currentTurn={2}
        existingBranches={['main', 'explore-alternative']}
      />
    </div>
  ),
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        story: `
# Full Chat Flow

Complete chat interface combining:
- **ContextIndicator**: Token usage and cost
- **MessageList**: Conversation history
- **InputArea**: Message input with controls

This demonstrates the ChatKBlock pattern in action:
- Transactional conversation model
- Fork/merge/rewind capabilities
- Evidence accumulation
- Tool transparency

"Chat is not a feature. Chat is an affordance that collapses discrete into continuous."
        `,
      },
    },
  },
};

// =============================================================================
// Responsive Variants Story
// =============================================================================

export const ResponsiveVariants: StoryObj = {
  render: () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px', padding: '16px' }}>
      {/* Desktop */}
      <div>
        <h3 style={{ color: '#e0e0e0', marginBottom: '8px' }}>Desktop (Full)</h3>
        <div style={{ display: 'flex', gap: '16px' }}>
          <div style={{ flex: 2, maxWidth: '600px' }}>
            <MessageList session={mockSession} isStreaming={false} />
          </div>
          <div style={{ flex: 1, maxWidth: '300px' }}>
            <BranchTree
              tree={mockBranchTree}
              branches={mockBranches}
              currentBranch="branch-main"
              canFork={false}
              onSwitchBranch={(id) => console.info('Switch:', id)}
              onMergeBranch={(id, s) => console.info('Merge:', id, s)}
            />
          </div>
        </div>
      </div>

      {/* Tablet */}
      <div>
        <h3 style={{ color: '#e0e0e0', marginBottom: '8px' }}>Tablet (Condensed)</h3>
        <div style={{ maxWidth: '500px' }}>
          <BranchTree
            tree={mockBranchTree}
            branches={mockBranches}
            currentBranch="branch-main"
            canFork={false}
            onSwitchBranch={(id) => console.info('Switch:', id)}
            onMergeBranch={(id, s) => console.info('Merge:', id, s)}
            compact
          />
        </div>
      </div>

      {/* Mobile */}
      <div>
        <h3 style={{ color: '#e0e0e0', marginBottom: '8px' }}>Mobile (Minimal)</h3>
        <div style={{ maxWidth: '320px' }}>
          <InputArea
            onSend={async (msg) => console.info('Send:', msg)}
            onRewind={async (n) => console.info('Rewind:', n)}
            compact
          />
        </div>
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: `
# Responsive Variants

Chat components adapt to viewport size:

| Breakpoint | Branch Tree | Input Controls |
|------------|-------------|----------------|
| Desktop (>768px) | Full tree with labels | All controls visible |
| Tablet (481-768px) | Compact tree | Condensed controls |
| Mobile (<=480px) | Hidden or minimal | Basic input only |

Follows elastic-ui-patterns for responsive layout.
        `,
      },
    },
  },
};
