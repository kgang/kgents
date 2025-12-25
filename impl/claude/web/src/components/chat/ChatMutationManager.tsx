/**
 * ChatMutationManager — Orchestrates mutation acknowledgment and trust escalation
 *
 * Integration layer between:
 * 1. MutationAcknowledger - Shows mutations requiring acknowledgment
 * 2. TrustEscalationPrompt - Suggests auto-approving after N approvals
 * 3. Chat Store - Manages state for both
 *
 * Flow:
 * 1. User acknowledges mutation → record approval
 * 2. Check if trust escalation should be suggested
 * 3. If yes, show TrustEscalationPrompt
 * 4. User makes choice → update trust level
 *
 * @see services/chat/trust_manager.py
 */

import { useChatStore } from './store';
import { MutationAcknowledger } from './MutationAcknowledger';
import { TrustEscalationPrompt } from './TrustEscalationPrompt';

// =============================================================================
// Main Component
// =============================================================================

export function ChatMutationManager() {
  const pendingMutations = useChatStore((state) => state.pendingMutations);
  const pendingEscalations = useChatStore((state) => state.pendingEscalations);
  const acknowledgeMutation = useChatStore((state) => state.acknowledgeMutation);
  const checkTrustEscalation = useChatStore((state) => state.checkTrustEscalation);
  const handleTrustChoice = useChatStore((state) => state.handleTrustChoice);
  const dismissEscalation = useChatStore((state) => state.dismissEscalation);

  // Handle mutation acknowledgment
  const handleAcknowledge = async (
    id: string,
    mode: 'click' | 'keyboard' | 'timeout_accept'
  ) => {
    // Find the mutation to get tool name
    const mutation = pendingMutations.find((m) => m.id === id);
    if (!mutation) return;

    // Acknowledge mutation (removes from pending)
    acknowledgeMutation(id, mode);

    // Check if we should suggest trust escalation
    await checkTrustEscalation(mutation.tool_name);
  };

  return (
    <>
      {/* Render pending mutations */}
      {pendingMutations.map((mutation) => (
        <MutationAcknowledger
          key={mutation.id}
          mutation={mutation}
          onAcknowledge={handleAcknowledge}
        />
      ))}

      {/* Render trust escalation prompts */}
      {pendingEscalations.map((escalation) => (
        <TrustEscalationPrompt
          key={escalation.id}
          toolName={escalation.tool_name}
          approvalCount={escalation.approval_count}
          onChoice={(choice) => handleTrustChoice(escalation.id, choice)}
          onDismiss={() => dismissEscalation(escalation.id)}
        />
      ))}
    </>
  );
}

export default ChatMutationManager;
