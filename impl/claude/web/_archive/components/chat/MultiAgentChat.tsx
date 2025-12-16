/**
 * MultiAgentChat: Group conversation with multiple citizens.
 *
 * Enables:
 * - Adding/removing participants
 * - Moderator injection (system messages)
 * - Observing inter-citizen dialogue
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { type MessageType } from './ChatMessage';

export interface MultiAgentChatProps {
  townId: string;
  initialParticipants?: string[];
  onClose?: () => void;
  className?: string;
}

interface Participant {
  id: string;
  name: string;
  archetype: string;
  color: string;
}

interface GroupMessage {
  id: string;
  type: MessageType | 'participant';
  speaker?: Participant;
  content: string;
  timestamp: Date;
  innerVoice?: string;
}

const PARTICIPANT_COLORS = [
  'text-blue-400',
  'text-green-400',
  'text-purple-400',
  'text-amber-400',
  'text-pink-400',
  'text-cyan-400',
];

export function MultiAgentChat({
  townId: _townId,
  initialParticipants = [],
  onClose,
  className,
}: MultiAgentChatProps) {
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [messages, setMessages] = useState<GroupMessage[]>([]);
  const [moderatorInput, setModeratorInput] = useState('');
  const [isSimulating, setIsSimulating] = useState(false);
  const [showInnerVoice, setShowInnerVoice] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize participants
  useEffect(() => {
    // Mock: In production, fetch citizen details
    const mockParticipants: Participant[] = initialParticipants.map((id, i) => ({
      id,
      name: `Citizen ${i + 1}`,
      archetype: ['Builder', 'Scholar', 'Trader', 'Healer', 'Watcher'][i % 5],
      color: PARTICIPANT_COLORS[i % PARTICIPANT_COLORS.length],
    }));

    setParticipants(mockParticipants);

    // Welcome message
    if (mockParticipants.length > 0) {
      setMessages([
        {
          id: 'welcome',
          type: 'system',
          content: `Group chat started with ${mockParticipants.length} participants.`,
          timestamp: new Date(),
        },
      ]);
    }
  }, [initialParticipants]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Simulate conversation
  const simulateDialogue = useCallback(async () => {
    if (participants.length < 2) return;

    setIsSimulating(true);

    // Pick two random participants
    const shuffled = [...participants].sort(() => Math.random() - 0.5);
    const speaker = shuffled[0];
    const responder = shuffled[1];

    // Generate mock dialogue
    const topics = [
      'the weather in town',
      'recent events',
      'their work',
      'a new idea',
      'an observation about the town',
    ];
    const topic = topics[Math.floor(Math.random() * topics.length)];

    // Speaker message
    const speakerMsg: GroupMessage = {
      id: `msg-${Date.now()}`,
      type: 'participant',
      speaker,
      content: generateDialogue(speaker.archetype, topic, true),
      timestamp: new Date(),
      innerVoice: showInnerVoice ? generateThought(speaker.archetype) : undefined,
    };
    setMessages((prev) => [...prev, speakerMsg]);

    // Wait for response
    await new Promise((r) => setTimeout(r, 1500));

    // Responder message
    const responderMsg: GroupMessage = {
      id: `msg-${Date.now()}-resp`,
      type: 'participant',
      speaker: responder,
      content: generateDialogue(responder.archetype, topic, false),
      timestamp: new Date(),
      innerVoice: showInnerVoice ? generateThought(responder.archetype) : undefined,
    };
    setMessages((prev) => [...prev, responderMsg]);

    setIsSimulating(false);
  }, [participants, showInnerVoice]);

  // Moderator injection
  const handleModeratorInject = () => {
    if (!moderatorInput.trim()) return;

    const msg: GroupMessage = {
      id: `mod-${Date.now()}`,
      type: 'system',
      content: `[Moderator] ${moderatorInput}`,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, msg]);
    setModeratorInput('');
  };

  // Add participant
  const handleAddParticipant = (name: string) => {
    const newParticipant: Participant = {
      id: `p-${Date.now()}`,
      name,
      archetype: 'Watcher',
      color: PARTICIPANT_COLORS[participants.length % PARTICIPANT_COLORS.length],
    };
    setParticipants((prev) => [...prev, newParticipant]);

    setMessages((prev) => [
      ...prev,
      {
        id: `join-${Date.now()}`,
        type: 'system',
        content: `${name} has joined the conversation.`,
        timestamp: new Date(),
      },
    ]);
  };

  // Remove participant
  const handleRemoveParticipant = (id: string) => {
    const participant = participants.find((p) => p.id === id);
    if (!participant) return;

    setParticipants((prev) => prev.filter((p) => p.id !== id));

    setMessages((prev) => [
      ...prev,
      {
        id: `leave-${Date.now()}`,
        type: 'system',
        content: `${participant.name} has left the conversation.`,
        timestamp: new Date(),
      },
    ]);
  };

  return (
    <div className={cn('flex flex-col h-full bg-town-bg', className)}>
      {/* Header */}
      <div className="p-4 border-b border-town-accent/30">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-bold text-lg">Group Dialogue</h2>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowInnerVoice(!showInnerVoice)}
              className={cn(
                'p-2 rounded transition-colors text-sm',
                showInnerVoice
                  ? 'bg-purple-500/20 text-purple-400'
                  : 'text-gray-500 hover:text-gray-300'
              )}
              title="Toggle inner voice"
            >
              💭
            </button>
            {onClose && (
              <button
                onClick={onClose}
                className="p-2 hover:bg-town-accent/20 rounded transition-colors"
              >
                ✕
              </button>
            )}
          </div>
        </div>

        {/* Participants */}
        <ParticipantList
          participants={participants}
          onRemove={handleRemoveParticipant}
          onAdd={handleAddParticipant}
        />
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <GroupChatMessage
            key={msg.id}
            message={msg}
            showInnerVoice={showInnerVoice}
          />
        ))}
        {isSimulating && (
          <div className="text-center text-gray-500 text-sm animate-pulse">
            Citizens are conversing...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Controls */}
      <div className="p-4 border-t border-town-accent/30 space-y-3">
        {/* Simulate button */}
        <button
          onClick={simulateDialogue}
          disabled={isSimulating || participants.length < 2}
          className={cn(
            'w-full py-2 rounded-lg font-medium transition-colors',
            isSimulating || participants.length < 2
              ? 'bg-town-surface text-gray-600 cursor-not-allowed'
              : 'bg-town-highlight hover:bg-town-highlight/80 text-white'
          )}
        >
          {isSimulating ? 'Simulating...' : '🎭 Simulate Dialogue'}
        </button>

        {/* Moderator input */}
        <div className="flex gap-2">
          <input
            type="text"
            value={moderatorInput}
            onChange={(e) => setModeratorInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleModeratorInject()}
            placeholder="Moderator message..."
            className="flex-1 bg-town-surface/50 border border-town-accent/30 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-town-highlight"
          />
          <button
            onClick={handleModeratorInject}
            disabled={!moderatorInput.trim()}
            className={cn(
              'px-4 py-2 rounded-lg transition-colors',
              moderatorInput.trim()
                ? 'bg-town-accent hover:bg-town-accent/80 text-white'
                : 'bg-town-surface text-gray-600 cursor-not-allowed'
            )}
          >
            Inject
          </button>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

interface ParticipantListProps {
  participants: Participant[];
  onRemove: (id: string) => void;
  onAdd: (name: string) => void;
}

function ParticipantList({ participants, onRemove, onAdd }: ParticipantListProps) {
  const [showAdd, setShowAdd] = useState(false);
  const [newName, setNewName] = useState('');

  const handleAdd = () => {
    if (newName.trim()) {
      onAdd(newName.trim());
      setNewName('');
      setShowAdd(false);
    }
  };

  return (
    <div className="flex flex-wrap gap-2">
      {participants.map((p) => (
        <div
          key={p.id}
          className="flex items-center gap-1 bg-town-surface/50 rounded-full px-3 py-1"
        >
          <span className={cn('text-sm', p.color)}>{p.name}</span>
          <button
            onClick={() => onRemove(p.id)}
            className="text-gray-500 hover:text-red-400 text-xs"
          >
            ✕
          </button>
        </div>
      ))}

      {showAdd ? (
        <div className="flex items-center gap-1">
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
            placeholder="Name"
            className="bg-town-surface/50 border border-town-accent/30 rounded-full px-3 py-1 text-sm w-24 focus:outline-none"
            autoFocus
          />
          <button
            onClick={handleAdd}
            className="text-green-400 hover:text-green-300 text-sm"
          >
            ✓
          </button>
          <button
            onClick={() => setShowAdd(false)}
            className="text-gray-500 hover:text-gray-300 text-sm"
          >
            ✕
          </button>
        </div>
      ) : (
        <button
          onClick={() => setShowAdd(true)}
          className="text-gray-500 hover:text-white text-sm px-3 py-1 border border-dashed border-gray-600 rounded-full"
        >
          + Add
        </button>
      )}
    </div>
  );
}

interface GroupChatMessageProps {
  message: GroupMessage;
  showInnerVoice: boolean;
}

function GroupChatMessage({ message, showInnerVoice }: GroupChatMessageProps) {
  if (message.type === 'system') {
    return (
      <div className="flex justify-center">
        <div className="bg-town-surface/30 px-4 py-2 rounded-full text-xs text-gray-400 text-center">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-1">
      {/* Speaker name */}
      {message.speaker && (
        <div className={cn('text-xs font-medium', message.speaker.color)}>
          {message.speaker.name}
          <span className="text-gray-600 ml-2">{message.speaker.archetype}</span>
        </div>
      )}

      {/* Message */}
      <div className="bg-town-surface/30 rounded-lg px-4 py-2">
        <p className="text-sm text-gray-200">{message.content}</p>
      </div>

      {/* Inner voice */}
      {showInnerVoice && message.innerVoice && (
        <div className="flex items-start gap-2 ml-2">
          <span className="text-purple-400 text-sm">💭</span>
          <p className="text-xs italic text-purple-300/70">
            {message.innerVoice}
          </p>
        </div>
      )}

      {/* Timestamp */}
      <div className="text-xs text-gray-600 ml-1">
        {message.timestamp.toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit',
        })}
      </div>
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function generateDialogue(archetype: string, topic: string, isInitiator: boolean): string {
  const openers: Record<string, string[]> = {
    Builder: [
      `I've been thinking about ${topic}...`,
      `You know, when it comes to ${topic}, I believe we should build something lasting.`,
    ],
    Scholar: [
      `Fascinating - ${topic} reminds me of something I read recently.`,
      `Let me share my thoughts on ${topic}...`,
    ],
    Trader: [
      `Here's a perspective on ${topic} you might not have considered.`,
      `Speaking of ${topic}, I heard an interesting story...`,
    ],
    Healer: [
      `How are you feeling about ${topic}?`,
      `${topic} is important for our well-being, I think.`,
    ],
    Watcher: [
      `I've observed something interesting about ${topic}.`,
      `From my vantage point, ${topic} looks quite different.`,
    ],
  };

  const responses: Record<string, string[]> = {
    Builder: [
      'That gives me an idea for something we could create together.',
      "I see practical applications in what you're saying.",
    ],
    Scholar: [
      'That aligns with what I understand about the matter.',
      'Interesting perspective. Let me add to that...',
    ],
    Trader: [
      'I can see value in that approach.',
      'That reminds me of a similar situation...',
    ],
    Healer: [
      'I appreciate you sharing that.',
      'How does that make you feel?',
    ],
    Watcher: [
      "I've noticed that pattern too.",
      'There may be more to observe here.',
    ],
  };

  const options = isInitiator
    ? openers[archetype] || openers.Watcher
    : responses[archetype] || responses.Watcher;

  return options[Math.floor(Math.random() * options.length)];
}

function generateThought(archetype: string): string {
  const thoughts: Record<string, string[]> = {
    Builder: ['I wonder if I could build on this...', 'This sparks my creativity...'],
    Scholar: ['Hmm, this requires more analysis...', 'Let me cross-reference this...'],
    Trader: ['There might be an opportunity here...', 'Interesting dynamics at play...'],
    Healer: ['I sense their emotions...', 'They seem to need support...'],
    Watcher: ['I must observe more carefully...', 'There are patterns emerging...'],
  };

  const options = thoughts[archetype] || thoughts.Watcher;
  return options[Math.floor(Math.random() * options.length)];
}

export default MultiAgentChat;
