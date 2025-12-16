/**
 * Chat/Inhabit: Direct agent interaction components.
 *
 * Enables INHABIT mode where users can:
 * - Suggest actions (citizen may refuse)
 * - Force actions (uses force tokens, increases consent debt)
 * - Apologize (reduces consent debt)
 * - View inner voice (citizen's internal monologue)
 *
 * @see plans/web-refactor/user-flows.md
 * @see spec/protocols/inhabit.md
 */

export { ChatDrawer, type ChatDrawerProps } from './ChatDrawer';
export { ChatMessage, type ChatMessageProps, type MessageType } from './ChatMessage';
export { MultiAgentChat, type MultiAgentChatProps } from './MultiAgentChat';
export { ChatInput, type ChatInputProps } from './ChatInput';
