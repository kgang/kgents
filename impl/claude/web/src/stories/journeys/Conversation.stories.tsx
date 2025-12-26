/**
 * Conversation.stories.tsx - Unified Chat Primitive Storybook
 *
 * Comprehensive stories for the Conversation system:
 * - Conversation (main container)
 * - MessageList (turn display)
 * - InputArea (message input with @mentions)
 * - SafetyGate (pre/post execution gates)
 * - BranchTree (session branching visualization)
 * - ForkModal (branch creation dialog)
 *
 * STARK BIOME: "The frame is humble, the content is the jewel."
 *
 * Philosophy:
 * - "Chat is not a feature. Chat is an affordance that collapses discrete into continuous."
 * - Pre-execution gates: timeout = DENY (safe default)
 * - Post-execution acknowledgment: timeout = ACCEPT (user informed)
 * - MAX_BRANCHES = 3 (cognitive limit)
 *
 * @see spec/protocols/chat-web.md
 * @see src/primitives/Conversation/
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState, useCallback } from 'react';
import { Conversation } from '../../primitives/Conversation/Conversation';
import { InputArea } from '../../primitives/Conversation/InputArea';
import { SafetyGate } from '../../primitives/Conversation/SafetyGate';
import { BranchTree } from '../../primitives/Conversation/BranchTree';
import { ForkModal } from '../../primitives/Conversation/ForkModal';
import type {
  Turn,
  Message,
  PendingMutation,
  PendingApproval,
  SafetyMode,
} from '../../primitives/Conversation/types';
import type { Branch, BranchTreeNode } from '../../primitives/Conversation/useBranching';

// =============================================================================
// Mock Data Factories
// =============================================================================

/** Create a realistic message */
function createMessage(
  role: 'user' | 'assistant',
  content: string,
  linearity: 'required' | 'preserved' | 'droppable' = 'preserved'
): Message {
  return {
    role,
    content,
    mentions: [],
    linearity_tag: linearity,
  };
}

/** Create a conversation turn with realistic data */
function createTurn(
  turnNumber: number,
  userContent: string,
  assistantContent: string,
  confidence: number = 0.85
): Turn {
  const baseTime = Date.now() - (10 - turnNumber) * 60000;
  return {
    turn_number: turnNumber,
    user_message: createMessage('user', userContent, 'required'),
    assistant_response: createMessage('assistant', assistantContent),
    tools_used: [],
    evidence_delta: {
      tools_executed: 0,
      tools_succeeded: 0,
      confidence_change: 0,
    },
    confidence,
    started_at: new Date(baseTime).toISOString(),
    completed_at: new Date(baseTime + 5000).toISOString(),
  };
}

/** Create realistic conversation turns */
function createConversationTurns(): Turn[] {
  return [
    createTurn(
      1,
      'I want to refactor the authentication module to use OAuth 2.0 instead of our custom JWT implementation.',
      `I can help with that refactor. Let me analyze the current authentication module.

Based on my analysis, here's what I recommend:

1. **Replace custom JWT with OAuth 2.0 flows** - This will improve security and reduce maintenance burden
2. **Add PKCE support** - For mobile and SPA clients
3. **Implement token refresh** - Handle seamless session renewal

Would you like me to start with the OAuth provider configuration, or should we first audit the existing JWT implementation to understand what claims we need to preserve?`,
      0.92
    ),
    createTurn(
      2,
      '@file src/auth/jwt.ts Show me the current implementation first.',
      `Here's the current JWT implementation:

\`\`\`typescript
// src/auth/jwt.ts
export function createToken(user: User): string {
  return jwt.sign({
    sub: user.id,
    email: user.email,
    roles: user.roles,
    permissions: user.permissions,
  }, SECRET, { expiresIn: '1h' });
}
\`\`\`

Key observations:
- Custom claims: roles and permissions are embedded
- Short expiry (1h) - good practice
- No refresh token mechanism

For OAuth 2.0 migration, we'll need to:
1. Move roles/permissions to the access token or a separate endpoint
2. Implement refresh token rotation
3. Add PKCE for public clients

Shall I create a migration plan?`,
      0.88
    ),
    createTurn(
      3,
      'Yes, create a migration plan. Also, we need to support both during the transition period.',
      `Here's the phased migration plan:

## Phase 1: Parallel Authentication (Week 1-2)
- Add OAuth 2.0 endpoints alongside existing JWT
- Implement provider abstraction layer
- Both systems validate tokens independently

## Phase 2: Feature Parity (Week 3-4)
- Migrate permissions to OAuth scopes
- Add refresh token support
- Update all clients to use new endpoints

## Phase 3: Deprecation (Week 5-6)
- Add deprecation warnings to old endpoints
- Monitor for legacy token usage
- Final cutover date announcement

## Phase 4: Cleanup (Week 7)
- Remove old JWT code
- Archive migration documentation
- Update security audit logs

I can start implementing Phase 1 now. Should I create the OAuth provider abstraction first?`,
      0.95
    ),
  ];
}

/** Create pending mutation for acknowledgment */
function createPendingMutation(
  id: string,
  toolName: string,
  description: string,
  isDestructive: boolean = false
): PendingMutation {
  return {
    id,
    tool_name: toolName,
    description,
    target: '/src/auth/oauth.ts',
    is_destructive: isDestructive,
    timestamp: new Date().toISOString(),
  };
}

/** Create pending approval for pre-execution gate */
function createPendingApproval(
  requestId: string,
  toolName: string,
  inputPreview: string,
  isDestructive: boolean = true
): PendingApproval {
  return {
    request_id: requestId,
    tool_name: toolName,
    input_preview: inputPreview,
    is_destructive: isDestructive,
    timeout_seconds: 10,
    timestamp: new Date().toISOString(),
  };
}

/** Create branch data */
function createBranch(
  id: string,
  name: string,
  turnCount: number,
  parentId: string | null = null,
  isActive: boolean = false,
  isMerged: boolean = false
): Branch {
  const baseTime = Date.now() - 3600000; // 1 hour ago
  return {
    id,
    parent_id: parentId,
    fork_point: parentId ? 2 : 0,
    branch_name: name,
    turn_count: turnCount,
    created_at: new Date(baseTime).toISOString(),
    last_active: new Date().toISOString(),
    is_merged: isMerged,
    merged_into: isMerged ? 'main' : null,
    is_active: isActive,
  };
}

/** Create branch tree for visualization */
function createBranchTree(): { branches: Branch[]; tree: BranchTreeNode } {
  const mainBranch = createBranch('branch-main', 'main', 5, null, true);
  const exploreBranch = createBranch('branch-explore', 'explore-oauth', 3, 'branch-main');
  const experimentBranch = createBranch('branch-experiment', 'try-passkeys', 2, 'branch-main');

  const branches = [mainBranch, exploreBranch, experimentBranch];

  const tree: BranchTreeNode = {
    branch: mainBranch,
    children: [
      { branch: exploreBranch, children: [] },
      { branch: experimentBranch, children: [] },
    ],
  };

  return { branches, tree };
}

// =============================================================================
// STARK BIOME Style Tokens
// =============================================================================

const S = {
  s0: { background: 'var(--surface-0, #0a0a0c)' },
  s1: { background: 'var(--surface-1, #141418)' },
  s2: { background: 'var(--surface-2, #1c1c22)' },
  s3: { background: 'var(--surface-3, #28282f)' },
};

const card: React.CSSProperties = {
  borderRadius: 'var(--radius-bare, 2px)',
  border: '1px solid var(--border-subtle, #28282f)',
  padding: '1rem',
};

const label: React.CSSProperties = {
  margin: '0 0 0.75rem',
  color: 'var(--text-secondary)',
  fontSize: '0.75rem',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
};

// =============================================================================
// Story Components
// =============================================================================

/** Full Conversation with all features */
function ConversationFull() {
  const [turns, setTurns] = useState<Turn[]>(createConversationTurns());
  const [isStreaming, setIsStreaming] = useState(false);
  const [safetyMode] = useState<SafetyMode>('trust');

  const handleMessage = useCallback(
    (content: string) => {
      // Simulate sending a message
      setIsStreaming(true);
      const newTurn = createTurn(
        turns.length + 1,
        content,
        'Processing your request...',
        0.5
      );
      setTurns([...turns, newTurn]);

      // Simulate response after delay
      setTimeout(() => {
        setTurns((prev) =>
          prev.map((t, i) =>
            i === prev.length - 1
              ? {
                  ...t,
                  assistant_response: createMessage(
                    'assistant',
                    `I've processed your request: "${content}"\n\nHere's my response with full context and analysis.`
                  ),
                  confidence: 0.88,
                }
              : t
          )
        );
        setIsStreaming(false);
      }, 2000);
    },
    [turns]
  );

  return (
    <div style={{ height: '600px', ...S.s0 }}>
      <Conversation
        turns={turns}
        onMessage={handleMessage}
        onBranch={(turnId) => console.log('Branch from turn:', turnId)}
        onRewind={(turnId) => console.log('Rewind to turn:', turnId)}
        safetyMode={safetyMode}
        isStreaming={isStreaming}
      />
    </div>
  );
}

/** Empty conversation state */
function ConversationEmpty() {
  const handleMessage = useCallback((content: string) => {
    console.log('Message sent:', content);
  }, []);

  return (
    <div style={{ height: '400px', ...S.s0 }}>
      <Conversation
        turns={[]}
        onMessage={handleMessage}
        safetyMode="trust"
      />
    </div>
  );
}

/** Conversation with streaming indicator */
function ConversationStreaming() {
  return (
    <div style={{ height: '400px', ...S.s0 }}>
      <Conversation
        turns={createConversationTurns().slice(0, 2)}
        onMessage={() => {}}
        safetyMode="trust"
        isStreaming={true}
      />
    </div>
  );
}

/** Conversation with error state */
function ConversationError() {
  return (
    <div style={{ height: '400px', ...S.s0 }}>
      <Conversation
        turns={[]}
        onMessage={() => {}}
        safetyMode="trust"
        error="Connection lost. Unable to reach the agent service. Please check your network and try again."
      />
    </div>
  );
}

/** Compact mode for embedded use */
function ConversationCompact() {
  return (
    <div style={{ height: '300px', width: '400px', ...S.s0 }}>
      <Conversation
        turns={createConversationTurns().slice(0, 1)}
        onMessage={() => {}}
        safetyMode="trust"
        compact={true}
      />
    </div>
  );
}

/** Pre-execution safety gate (approval required) */
function SafetyGatePreExecution() {
  const [approved, setApproved] = useState<string | null>(null);
  const [denied, setDenied] = useState<string | null>(null);

  const approval = createPendingApproval(
    'req-001',
    'file_delete',
    'rm -rf /tmp/build/* (Delete all build artifacts)',
    true
  );

  if (approved) {
    return (
      <div style={{ ...S.s1, ...card, color: 'var(--health-healthy, #22c55e)' }}>
        Approved: {approved}
      </div>
    );
  }

  if (denied) {
    return (
      <div style={{ ...S.s1, ...card, color: 'var(--health-warning, #f97316)' }}>
        Denied: {denied}
      </div>
    );
  }

  return (
    <div style={{ ...S.s1, padding: '1rem', minWidth: '500px' }}>
      <SafetyGate
        mode="pre"
        approval={approval}
        onApprove={(requestId, alwaysAllow) => {
          setApproved(`${requestId} (always: ${alwaysAllow})`);
        }}
        onDeny={(requestId, reason) => {
          setDenied(`${requestId}: ${reason}`);
        }}
      />
    </div>
  );
}

/** Post-execution mutation acknowledgment */
function SafetyGatePostExecution() {
  const [acknowledged, setAcknowledged] = useState<string | null>(null);

  const mutation = createPendingMutation(
    'mut-001',
    'file_write',
    'Created OAuth provider configuration',
    false
  );

  if (acknowledged) {
    return (
      <div style={{ ...S.s1, ...card, color: 'var(--text-secondary)' }}>
        Acknowledged: {acknowledged}
      </div>
    );
  }

  return (
    <div style={{ ...S.s1, padding: '1rem', minWidth: '500px' }}>
      <SafetyGate
        mode="post"
        mutation={mutation}
        onAcknowledge={(id, mode) => {
          setAcknowledged(`${id} via ${mode}`);
        }}
      />
    </div>
  );
}

/** Destructive mutation acknowledgment */
function SafetyGateDestructive() {
  const [acknowledged, setAcknowledged] = useState(false);

  const mutation = createPendingMutation(
    'mut-002',
    'git_reset',
    'Reset branch to previous commit (3 commits discarded)',
    true
  );

  if (acknowledged) {
    return (
      <div style={{ ...S.s1, ...card, color: 'var(--health-warning)' }}>
        Destructive action acknowledged
      </div>
    );
  }

  return (
    <div style={{ ...S.s1, padding: '1rem', minWidth: '500px' }}>
      <SafetyGate
        mode="post"
        mutation={mutation}
        onAcknowledge={() => setAcknowledged(true)}
      />
    </div>
  );
}

/** Input area with controls */
function InputAreaDemo() {
  const [lastMessage, setLastMessage] = useState<string | null>(null);

  return (
    <div style={{ ...S.s1, padding: '1rem', minWidth: '500px' }}>
      <h4 style={label}>Input Area</h4>
      <InputArea
        onSend={async (msg) => {
          setLastMessage(msg);
        }}
        onRewind={async (turns) => {
          console.log('Rewind:', turns, 'turns');
        }}
        onFork={async (name, point) => {
          console.log('Fork:', name, 'at turn', point);
        }}
        currentTurn={5}
        existingBranches={['main', 'explore-oauth']}
      />
      {lastMessage && (
        <div style={{ marginTop: '1rem', ...S.s2, ...card }}>
          <strong>Last message:</strong> {lastMessage}
        </div>
      )}
    </div>
  );
}

/** Input area in compact mode */
function InputAreaCompact() {
  return (
    <div style={{ ...S.s1, padding: '1rem', width: '350px' }}>
      <h4 style={label}>Compact Input</h4>
      <InputArea
        onSend={async () => {}}
        onRewind={async () => {}}
        compact={true}
        currentTurn={3}
      />
    </div>
  );
}

/** Input area with mention hint */
function InputAreaWithMentions() {
  return (
    <div style={{ ...S.s1, padding: '1rem', minWidth: '500px' }}>
      <h4 style={label}>Type @ to see mention picker hint</h4>
      <InputArea
        onSend={async () => {}}
        onRewind={async () => {}}
        currentTurn={2}
      />
      <p style={{ marginTop: '1rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
        Supported mentions: @file, @symbol, @spec, @witness, @web
      </p>
    </div>
  );
}

/** Branch tree visualization */
function BranchTreeDemo() {
  const { branches, tree } = createBranchTree();
  const [currentBranch, setCurrentBranch] = useState('branch-main');

  return (
    <div style={{ ...S.s1, padding: '1rem', minWidth: '400px' }}>
      <BranchTree
        tree={tree}
        branches={branches}
        currentBranch={currentBranch}
        canFork={branches.filter((b) => !b.is_merged).length < 3}
        onSwitchBranch={setCurrentBranch}
        onMergeBranch={(branchId, strategy) => {
          console.log('Merge:', branchId, 'with strategy:', strategy);
        }}
      />
    </div>
  );
}

/** Branch tree at maximum capacity */
function BranchTreeMaxed() {
  const mainBranch = createBranch('branch-main', 'main', 5, null, true);
  const branch1 = createBranch('branch-1', 'feature-auth', 3, 'branch-main');
  const branch2 = createBranch('branch-2', 'explore-ui', 2, 'branch-main');

  const branches = [mainBranch, branch1, branch2];
  const tree: BranchTreeNode = {
    branch: mainBranch,
    children: [
      { branch: branch1, children: [] },
      { branch: branch2, children: [] },
    ],
  };

  return (
    <div style={{ ...S.s1, padding: '1rem', minWidth: '400px' }}>
      <h4 style={label}>Maximum 3 branches reached</h4>
      <BranchTree
        tree={tree}
        branches={branches}
        currentBranch="branch-main"
        canFork={false}
        onSwitchBranch={() => {}}
        onMergeBranch={() => {}}
      />
    </div>
  );
}

/** Empty branch tree */
function BranchTreeEmpty() {
  return (
    <div style={{ ...S.s1, padding: '1rem', minWidth: '300px' }}>
      <BranchTree
        tree={null}
        branches={[]}
        currentBranch=""
        canFork={true}
        onSwitchBranch={() => {}}
        onMergeBranch={() => {}}
      />
    </div>
  );
}

/** Fork modal dialog */
function ForkModalDemo() {
  const [isOpen, setIsOpen] = useState(true);
  const [created, setCreated] = useState<string | null>(null);

  return (
    <div style={{ ...S.s1, padding: '1rem', minWidth: '400px', minHeight: '200px' }}>
      {created ? (
        <div style={{ ...S.s2, ...card }}>
          <strong>Created branch:</strong> {created}
          <button
            style={{ marginLeft: '1rem', padding: '0.25rem 0.5rem' }}
            onClick={() => {
              setCreated(null);
              setIsOpen(true);
            }}
          >
            Open Again
          </button>
        </div>
      ) : (
        <button
          style={{ padding: '0.5rem 1rem', ...S.s2, border: '1px solid var(--border-subtle)' }}
          onClick={() => setIsOpen(true)}
        >
          Open Fork Modal
        </button>
      )}
      <ForkModal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        onConfirm={(name, point) => {
          setCreated(`${name} (from turn ${point || 'current'})`);
          setIsOpen(false);
        }}
        currentTurn={5}
        existingBranches={['main', 'explore-oauth']}
        canFork={true}
      />
    </div>
  );
}

/** Fork modal at branch limit */
function ForkModalAtLimit() {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div style={{ ...S.s1, padding: '1rem', minWidth: '400px', minHeight: '200px' }}>
      <ForkModal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        onConfirm={() => {}}
        currentTurn={5}
        existingBranches={['main', 'explore', 'experiment']}
        canFork={false}
      />
    </div>
  );
}

/** Combined safety modes demonstration */
function SafetyModeComparison() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', ...S.s0, padding: '1rem' }}>
      <div>
        <h4 style={label}>Gate Mode (Pre-Execution Approval)</h4>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
          Blocks execution until user approves. Timeout = DENY (safe default).
        </p>
        <div style={{ ...S.s1, ...card }}>
          <SafetyGate
            mode="pre"
            approval={createPendingApproval('req-gate', 'shell_execute', 'npm run build')}
            onApprove={() => {}}
            onDeny={() => {}}
          />
        </div>
      </div>

      <div>
        <h4 style={label}>Acknowledge Mode (Post-Execution Notification)</h4>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
          Informs user of completed action. Timeout = ACCEPT (user informed).
        </p>
        <div style={{ ...S.s1, ...card }}>
          <SafetyGate
            mode="post"
            mutation={createPendingMutation('mut-ack', 'file_create', 'Created new configuration file')}
            onAcknowledge={() => {}}
          />
        </div>
      </div>

      <div>
        <h4 style={label}>Trust Mode</h4>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
          Tools run freely with minimal UI. No gates shown.
        </p>
      </div>
    </div>
  );
}

// =============================================================================
// Storybook Configuration
// =============================================================================

const meta: Meta = {
  title: 'Journeys/Conversation',
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: `
# Conversation Primitive

The unified chat system for kgents. Consolidates chat, safety gates, and branching into a coherent primitive.

> "Chat is not a feature. Chat is an affordance that collapses discrete into continuous."

## Component Tree

\`\`\`
Conversation
  BranchTree (optional)
  MessageList
    Turn[]
      UserMessage
      AssistantMessage
  SafetyGate mode="post" (acknowledgment)
  SafetyGate mode="pre" (approval)
  InputArea
    ForkModal
\`\`\`

## Safety Modes

| Mode | Behavior | Timeout | Use Case |
|------|----------|---------|----------|
| \`gate\` | Pre-execution approval | DENY | Destructive operations |
| \`acknowledge\` | Post-execution notification | ACCEPT | Mutation awareness |
| \`trust\` | No gates | N/A | Trusted tools |

## Branching

MAX_BRANCHES = 3 (cognitive limit from spec)

- **Fork**: Create new branch at any turn
- **Switch**: Navigate between branches
- **Merge**: Combine branches (sequential, interleave, manual)
- **Rewind**: Go back N turns on current branch

## STARK BIOME Styling

- \`--surface-0\` through \`--surface-3\` for depth
- \`--accent-primary\` (#8b5cf6) for assistant messages
- \`--accent-secondary\` (#6366f1) for user messages
- Sharp corners (\`--radius-bare\`) for industrial aesthetic
        `,
      },
    },
  },
  tags: ['autodocs'],
};

export default meta;

// =============================================================================
// Stories: Conversation (Main Component)
// =============================================================================

export const Full: StoryObj = {
  name: 'Conversation/Full Interactive',
  render: () => <ConversationFull />,
  parameters: {
    docs: {
      description: {
        story: 'Full conversation with message history, streaming support, and interactive input. Type a message and send to see the response simulation.',
      },
    },
  },
};

export const Empty: StoryObj = {
  name: 'Conversation/Empty State',
  render: () => <ConversationEmpty />,
  parameters: {
    docs: {
      description: {
        story: 'Empty conversation showing the onboarding state with helpful instructions.',
      },
    },
  },
};

export const Streaming: StoryObj = {
  name: 'Conversation/Streaming',
  render: () => <ConversationStreaming />,
  parameters: {
    docs: {
      description: {
        story: 'Conversation with active streaming indicator (animated dots).',
      },
    },
  },
};

export const Error: StoryObj = {
  name: 'Conversation/Error State',
  render: () => <ConversationError />,
  parameters: {
    docs: {
      description: {
        story: 'Conversation error state with descriptive error message.',
      },
    },
  },
};

export const Compact: StoryObj = {
  name: 'Conversation/Compact Mode',
  render: () => <ConversationCompact />,
  parameters: {
    docs: {
      description: {
        story: 'Compact conversation for embedded use cases (reduced padding, no branch tree).',
      },
    },
  },
};

// =============================================================================
// Stories: Safety Gates
// =============================================================================

export const GatePre: StoryObj = {
  name: 'SafetyGate/Pre-Execution',
  render: () => <SafetyGatePreExecution />,
  parameters: {
    docs: {
      description: {
        story: 'Pre-execution approval gate. Blocks tool execution until user approves. Timeout = DENY (safe default). Shows Allow Once, Always Allow, and Deny buttons.',
      },
    },
  },
};

export const GatePost: StoryObj = {
  name: 'SafetyGate/Post-Execution',
  render: () => <SafetyGatePostExecution />,
  parameters: {
    docs: {
      description: {
        story: 'Post-execution acknowledgment. Informs user of completed mutation. Timeout = ACCEPT (user has been informed).',
      },
    },
  },
};

export const GateDestructive: StoryObj = {
  name: 'SafetyGate/Destructive Action',
  render: () => <SafetyGateDestructive />,
  parameters: {
    docs: {
      description: {
        story: 'Destructive action acknowledgment with warning styling (orange accent).',
      },
    },
  },
};

export const SafetyModes: StoryObj = {
  name: 'SafetyGate/Mode Comparison',
  render: () => <SafetyModeComparison />,
  parameters: {
    docs: {
      description: {
        story: 'Side-by-side comparison of gate, acknowledge, and trust safety modes.',
      },
    },
  },
};

// =============================================================================
// Stories: Input Area
// =============================================================================

export const Input: StoryObj = {
  name: 'InputArea/Full Controls',
  render: () => <InputAreaDemo />,
  parameters: {
    docs: {
      description: {
        story: 'Input area with full controls: Rewind button, Fork button, and send functionality. Shows the last sent message.',
      },
    },
  },
};

export const InputCompact: StoryObj = {
  name: 'InputArea/Compact',
  render: () => <InputAreaCompact />,
  parameters: {
    docs: {
      description: {
        story: 'Compact input area without control buttons (for embedded/mobile use).',
      },
    },
  },
};

export const InputMentions: StoryObj = {
  name: 'InputArea/Mentions',
  render: () => <InputAreaWithMentions />,
  parameters: {
    docs: {
      description: {
        story: 'Input area showing the @mention hint when typing @. Supports @file, @symbol, @spec, @witness, @web.',
      },
    },
  },
};

// =============================================================================
// Stories: Branch Tree
// =============================================================================

export const BranchTreeStory: StoryObj = {
  name: 'BranchTree/Interactive',
  render: () => <BranchTreeDemo />,
  parameters: {
    docs: {
      description: {
        story: 'Interactive branch tree with D3.js visualization. Click nodes to switch branches. Right-click for context menu (merge, archive, delete).',
      },
    },
  },
};

export const BranchTreeMax: StoryObj = {
  name: 'BranchTree/At Limit',
  render: () => <BranchTreeMaxed />,
  parameters: {
    docs: {
      description: {
        story: 'Branch tree at maximum capacity (3 branches). Shows warning that no new forks can be created.',
      },
    },
  },
};

export const BranchTreeEmptyStory: StoryObj = {
  name: 'BranchTree/Empty',
  render: () => <BranchTreeEmpty />,
  parameters: {
    docs: {
      description: {
        story: 'Empty branch tree state before any branches exist.',
      },
    },
  },
};

// =============================================================================
// Stories: Fork Modal
// =============================================================================

export const ForkModalStory: StoryObj = {
  name: 'ForkModal/Create Branch',
  render: () => <ForkModalDemo />,
  parameters: {
    docs: {
      description: {
        story: 'Fork modal for creating new conversation branches. Validates branch names (no spaces, unique), allows selecting fork point.',
      },
    },
  },
};

export const ForkModalLimit: StoryObj = {
  name: 'ForkModal/At Limit',
  render: () => <ForkModalAtLimit />,
  parameters: {
    docs: {
      description: {
        story: 'Fork modal when at 3-branch limit. Shows warning and disables creation.',
      },
    },
  },
};
