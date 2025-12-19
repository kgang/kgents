/**
 * ChatPage — Conversational Interface to K-gent
 *
 * The self.chat node provides conversational affordances for any AGENTESE node.
 * This page wraps the ChatNode with a clean, minimalist chat interface.
 *
 * "Daring, bold, creative, opinionated but not gaudy"
 *
 * AGENTESE Route: /self.chat
 *
 * @see spec/protocols/chat.md
 * @see services/chat/node.py
 */

import { useState, useCallback, useRef, useEffect, forwardRef, type KeyboardEvent } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Loader2, MessageSquare, Trash2, RotateCcw, ChevronDown } from 'lucide-react';
import { useAgenteseMutation } from '@/hooks/useAgentesePath';
import { useShell } from '@/shell/ShellProvider';
import { Breathe } from '@/components/joy';
import type {
  SelfChatSendResponse,
  SelfChatCreateResponse,
} from '@/api/types/_generated/self-chat';

// =============================================================================
// Types
// =============================================================================

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  tokens?: { in: number; out: number };
}

interface ChatState {
  sessionId: string | null;
  messages: ChatMessage[];
  nodePath: string;
  turnCount: number;
}

// =============================================================================
// Sub-Components
// =============================================================================

function ChatHeader({
  sessionId,
  turnCount,
  nodePath,
  onReset,
  onClear,
}: {
  sessionId: string | null;
  turnCount: number;
  nodePath: string;
  onReset: () => void;
  onClear: () => void;
}) {
  return (
    <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700/50 bg-gray-800/40">
      <div className="flex items-center gap-3">
        <Breathe intensity={0.2} speed="slow">
          <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20">
            <MessageSquare className="w-5 h-5 text-cyan-400" />
          </div>
        </Breathe>
        <div>
          <h1 className="font-semibold text-white">Chat</h1>
          <p className="text-xs text-gray-500">
            {nodePath} {sessionId ? `• ${turnCount} turns` : '• New session'}
          </p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <button
          onClick={onClear}
          title="Clear messages"
          className="p-2 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-gray-700/50 transition-colors"
        >
          <Trash2 className="w-4 h-4" />
        </button>
        <button
          onClick={onReset}
          title="Reset session"
          className="p-2 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-gray-700/50 transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

interface MessageBubbleProps {
  message: ChatMessage;
  isUser: boolean;
}

const MessageBubble = forwardRef<HTMLDivElement, MessageBubbleProps>(
  function MessageBubble({ message, isUser }, ref) {
    return (
      <motion.div
        ref={ref}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
      >
        <div
          className={`max-w-[80%] px-4 py-2.5 rounded-2xl ${
            isUser
              ? 'bg-cyan-600/80 text-white rounded-br-sm'
              : 'bg-gray-700/60 text-gray-100 rounded-bl-sm'
          }`}
        >
          <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
          <div
            className={`flex items-center gap-2 mt-1.5 text-xs ${
              isUser ? 'text-cyan-200/70' : 'text-gray-500'
            }`}
          >
            <span>
              {message.timestamp.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>
            {message.tokens && (
              <span>
                • {message.tokens.in + message.tokens.out} tokens
              </span>
            )}
          </div>
        </div>
      </motion.div>
    );
  }
);

const TypingIndicator = forwardRef<HTMLDivElement>(function TypingIndicator(_props, ref) {
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex items-center gap-1 px-4 py-2.5 bg-gray-700/60 rounded-2xl rounded-bl-sm w-fit"
    >
      {[0, 1, 2].map((i) => (
        <motion.span
          key={i}
          animate={{ opacity: [0.4, 1, 0.4] }}
          transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
          className="w-2 h-2 rounded-full bg-gray-400"
        />
      ))}
    </motion.div>
  );
});

function ScrollToBottomButton({ onClick, visible }: { onClick: () => void; visible: boolean }) {
  return (
    <AnimatePresence>
      {visible && (
        <motion.button
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
          onClick={onClick}
          className="absolute bottom-2 right-2 p-2 rounded-full bg-gray-700 border border-gray-600 text-gray-300 hover:bg-gray-600 shadow-lg"
        >
          <ChevronDown className="w-4 h-4" />
        </motion.button>
      )}
    </AnimatePresence>
  );
}

function WelcomeScreen({ onStart }: { onStart: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex-1 flex flex-col items-center justify-center text-center px-8"
    >
      <Breathe intensity={0.3} speed="slow">
        <div className="p-4 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 mb-6">
          <MessageSquare className="w-12 h-12 text-cyan-400" />
        </div>
      </Breathe>
      <h2 className="text-xl font-semibold text-white mb-2">Welcome to Chat</h2>
      <p className="text-gray-400 max-w-md mb-6">
        Converse with K-gent. Ask questions, explore ideas, or just say hello.
        Every conversation is a new garden to tend.
      </p>
      <button
        onClick={onStart}
        className="px-6 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-medium transition-colors"
      >
        Start Conversation
      </button>
    </motion.div>
  );
}

function InputArea({
  value,
  onChange,
  onSend,
  disabled,
  placeholder,
}: {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  disabled: boolean;
  placeholder?: string;
}) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [value]);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!disabled && value.trim()) {
        onSend();
      }
    }
  };

  return (
    <div className="px-4 py-3 border-t border-gray-700/50 bg-gray-800/40">
      <div className="flex items-end gap-2">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder || 'Type your message...'}
          disabled={disabled}
          rows={1}
          className="flex-1 resize-none bg-gray-700/50 border border-gray-600 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30 disabled:opacity-50 disabled:cursor-not-allowed"
        />
        <button
          onClick={onSend}
          disabled={disabled || !value.trim()}
          className="p-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-cyan-600 transition-colors"
        >
          {disabled ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Send className="w-5 h-5" />
          )}
        </button>
      </div>
      <p className="text-xs text-gray-600 mt-2 text-center">
        Press Enter to send, Shift+Enter for new line
      </p>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export default function ChatPage() {
  const { density } = useShell();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  // Chat state
  const [state, setState] = useState<ChatState>({
    sessionId: null,
    messages: [],
    nodePath: 'self.soul',
    turnCount: 0,
  });
  const [input, setInput] = useState('');
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [started, setStarted] = useState(false);

  // Create session mutation
  const { mutate: createSession, isLoading: isCreating } = useAgenteseMutation<
    { node_path: string; force_new?: boolean },
    SelfChatCreateResponse
  >('self.chat:create');

  // Send message mutation
  const { mutate: sendMessage, isLoading: isSending } = useAgenteseMutation<
    { message: string; session_id?: string; node_path?: string },
    SelfChatSendResponse
  >('self.chat:send');

  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  // Scroll handler for scroll-to-bottom button
  const handleScroll = useCallback(() => {
    if (messagesContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current;
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
      setShowScrollButton(!isNearBottom);
    }
  }, []);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    if (state.messages.length > 0) {
      scrollToBottom();
    }
  }, [state.messages, scrollToBottom]);

  // Start a new session
  const handleStart = useCallback(async () => {
    setStarted(true);
    const response = await createSession({
      node_path: state.nodePath,
      force_new: true,
    });

    if (response) {
      setState((prev) => ({
        ...prev,
        sessionId: response.session_id,
        turnCount: 0,
      }));
    }
  }, [createSession, state.nodePath]);

  // Send a message
  const handleSend = useCallback(async () => {
    const trimmedInput = input.trim();
    if (!trimmedInput || isSending) return;

    // Add user message immediately
    const userMessage: ChatMessage = {
      role: 'user',
      content: trimmedInput,
      timestamp: new Date(),
    };
    setState((prev) => ({
      ...prev,
      messages: [...prev.messages, userMessage],
    }));
    setInput('');

    // Send to backend
    const response = await sendMessage({
      message: trimmedInput,
      session_id: state.sessionId || undefined,
      node_path: state.sessionId ? undefined : state.nodePath,
    });

    if (response) {
      // Update session ID if this was first message
      if (!state.sessionId) {
        setState((prev) => ({
          ...prev,
          sessionId: response.session_id,
        }));
      }

      // Add assistant response
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        tokens: {
          in: response.tokens_in,
          out: response.tokens_out,
        },
      };
      setState((prev) => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        turnCount: response.turn_number,
      }));
    }
  }, [input, isSending, sendMessage, state.sessionId, state.nodePath]);

  // Reset session
  const handleReset = useCallback(async () => {
    const response = await createSession({
      node_path: state.nodePath,
      force_new: true,
    });

    if (response) {
      setState({
        sessionId: response.session_id,
        messages: [],
        nodePath: state.nodePath,
        turnCount: 0,
      });
    }
  }, [createSession, state.nodePath]);

  // Clear messages (keep session)
  const handleClear = useCallback(() => {
    setState((prev) => ({
      ...prev,
      messages: [],
    }));
  }, []);

  const isCompact = density === 'compact';

  // Show welcome screen if not started
  if (!started) {
    return (
      <div className="h-[calc(100vh-64px)] flex flex-col bg-gray-900">
        <WelcomeScreen onStart={handleStart} />
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col bg-gray-900">
      {/* Header */}
      <ChatHeader
        sessionId={state.sessionId}
        turnCount={state.turnCount}
        nodePath={state.nodePath}
        onReset={handleReset}
        onClear={handleClear}
      />

      {/* Messages Area */}
      <div
        ref={messagesContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto relative"
      >
        <div className={`max-w-3xl mx-auto ${isCompact ? 'p-3' : 'p-4'} space-y-4`}>
          <AnimatePresence mode="popLayout">
            {state.messages.map((message, index) => (
              <MessageBubble
                key={`${message.timestamp.getTime()}-${index}`}
                message={message}
                isUser={message.role === 'user'}
              />
            ))}
            {isSending && <TypingIndicator key="typing" />}
          </AnimatePresence>
          <div ref={messagesEndRef} />
        </div>

        <ScrollToBottomButton onClick={scrollToBottom} visible={showScrollButton} />
      </div>

      {/* Input Area */}
      <div className="max-w-3xl mx-auto w-full">
        <InputArea
          value={input}
          onChange={setInput}
          onSend={handleSend}
          disabled={isSending || isCreating}
          placeholder={
            isCreating
              ? 'Creating session...'
              : isSending
              ? 'Thinking...'
              : 'Type your message...'
          }
        />
      </div>
    </div>
  );
}
