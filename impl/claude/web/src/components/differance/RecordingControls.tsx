/**
 * RecordingControls — Session Recording for Differance DevEx
 *
 * One-click session recording to capture cognitive flow.
 * "Zero-Config Recording": Traces record automatically, session recording is opt-in enhancement.
 *
 * Design Principles (from differance-devex-enlightenment.md):
 * - "Generative, Not Archival": Record to understand, not to archive
 * - "The Mirror Test": Does this feel like seeing your own thinking?
 * - Living Earth aesthetic, Breathe animations on recording indicator
 *
 * ASCII Reference:
 * ```
 * ┌─────────────────────────────────────────────────┐
 * │  🔴 Recording    [Stop] [Pause] [Mark Decision] │
 * │  Session: "Refactoring auth flow"               │
 * │  Traces: 12  |  Ghosts: 4  |  Duration: 8m 32s  │
 * └─────────────────────────────────────────────────┘
 * ```
 *
 * @see spec/protocols/differance.md
 * @see plans/differance-devex-enlightenment.md - Phase 7D
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Circle,
  Square,
  Pause,
  Play,
  Flag,
  Clock,
  GitBranch,
  Edit3,
  Check,
  X,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { EARTH, GREEN, GLOW } from '@/constants/livingEarth';
import { Breathe } from '@/components/joy';

// =============================================================================
// Types
// =============================================================================

export interface RecordingSession {
  id: string;
  name: string;
  startTime: Date;
  endTime?: Date;
  status: 'recording' | 'paused' | 'stopped';
  traceCount: number;
  ghostCount: number;
  decisionMarkers: DecisionMarker[];
  correlationId: string;
}

export interface DecisionMarker {
  id: string;
  timestamp: Date;
  label: string;
  traceId?: string;
}

export interface RecordingControlsProps {
  /** Currently active session (if any) */
  session: RecordingSession | null;
  /** Callback to start a new session */
  onStartSession: (name: string) => void;
  /** Callback to stop the session */
  onStopSession: () => void;
  /** Callback to pause/resume the session */
  onTogglePause: () => void;
  /** Callback to add a decision marker */
  onMarkDecision: (label: string) => void;
  /** Callback when session name is updated */
  onUpdateSessionName?: (name: string) => void;
  /** Auto-generated session name suggestion */
  suggestedName?: string;
  /** Compact mode for smaller spaces */
  compact?: boolean;
  /** Custom class name */
  className?: string;
}

// =============================================================================
// Helper Functions
// =============================================================================

function formatDuration(startTime: Date, endTime?: Date): string {
  const end = endTime || new Date();
  const diffMs = end.getTime() - startTime.getTime();
  const seconds = Math.floor(diffMs / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);

  if (hours > 0) {
    return `${hours}h ${minutes % 60}m ${seconds % 60}s`;
  }
  if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`;
  }
  return `${seconds}s`;
}

function generateSessionId(): string {
  return `session_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
}

// =============================================================================
// Recording Indicator (pulsing dot)
// =============================================================================

interface RecordingIndicatorProps {
  status: 'recording' | 'paused' | 'stopped' | 'idle';
}

function RecordingIndicator({ status }: RecordingIndicatorProps) {
  const isRecording = status === 'recording';
  const isPaused = status === 'paused';

  return (
    <div className="relative w-4 h-4 flex items-center justify-center">
      {isRecording ? (
        <Breathe intensity={0.5} speed="slow">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: GLOW.copper }} />
        </Breathe>
      ) : isPaused ? (
        <div
          className="w-3 h-3 rounded-full"
          style={{ backgroundColor: GLOW.amber, opacity: 0.7 }}
        />
      ) : (
        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: EARTH.clay }} />
      )}
      {/* Outer ring for recording */}
      {isRecording && (
        <motion.div
          className="absolute inset-0 rounded-full"
          style={{ border: `1px solid ${GLOW.copper}` }}
          animate={{ scale: [1, 1.5, 1], opacity: [1, 0, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
      )}
    </div>
  );
}

// =============================================================================
// Decision Marker Input
// =============================================================================

interface DecisionMarkerInputProps {
  onMark: (label: string) => void;
  compact?: boolean;
}

function DecisionMarkerInput({ onMark, compact }: DecisionMarkerInputProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [label, setLabel] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = useCallback(() => {
    if (label.trim()) {
      onMark(label.trim());
      setLabel('');
      setIsOpen(false);
    }
  }, [label, onMark]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-colors hover:brightness-110`}
        style={{ backgroundColor: `${GLOW.amber}20`, color: GLOW.amber }}
        title="Mark important decision point"
      >
        <Flag className={compact ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
        {!compact && <span>Mark</span>}
      </button>
    );
  }

  return (
    <div className="flex items-center gap-1.5">
      <input
        ref={inputRef}
        type="text"
        value={label}
        onChange={(e) => setLabel(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') handleSubmit();
          if (e.key === 'Escape') setIsOpen(false);
        }}
        placeholder="Decision label..."
        className="w-32 px-2 py-1 rounded text-xs outline-none"
        style={{
          backgroundColor: `${EARTH.bark}60`,
          color: GLOW.lantern,
          border: `1px solid ${GLOW.amber}50`,
        }}
      />
      <button
        onClick={handleSubmit}
        className="p-1 rounded transition-colors hover:brightness-110"
        style={{ backgroundColor: `${GREEN.sage}30`, color: GREEN.sprout }}
      >
        <Check className="w-3 h-3" />
      </button>
      <button
        onClick={() => setIsOpen(false)}
        className="p-1 rounded transition-colors hover:brightness-110"
        style={{ backgroundColor: `${EARTH.bark}60`, color: EARTH.sand }}
      >
        <X className="w-3 h-3" />
      </button>
    </div>
  );
}

// =============================================================================
// Session Name Editor
// =============================================================================

interface SessionNameEditorProps {
  name: string;
  onUpdate: (name: string) => void;
  compact?: boolean;
}

function SessionNameEditor({ name, onUpdate, compact }: SessionNameEditorProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [value, setValue] = useState(name);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setValue(name);
  }, [name]);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const handleSubmit = useCallback(() => {
    if (value.trim() && value !== name) {
      onUpdate(value.trim());
    }
    setIsEditing(false);
  }, [value, name, onUpdate]);

  if (!isEditing) {
    return (
      <button
        onClick={() => setIsEditing(true)}
        className="flex items-center gap-1.5 group"
        title="Edit session name"
      >
        <span
          className={`truncate max-w-[200px] ${compact ? 'text-xs' : 'text-sm'}`}
          style={{ color: GLOW.lantern }}
        >
          {name}
        </span>
        <Edit3
          className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity"
          style={{ color: EARTH.sand }}
        />
      </button>
    );
  }

  return (
    <div className="flex items-center gap-1.5">
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') handleSubmit();
          if (e.key === 'Escape') {
            setValue(name);
            setIsEditing(false);
          }
        }}
        onBlur={handleSubmit}
        className={`w-48 px-2 py-0.5 rounded outline-none ${compact ? 'text-xs' : 'text-sm'}`}
        style={{
          backgroundColor: `${EARTH.bark}60`,
          color: GLOW.lantern,
          border: `1px solid ${GREEN.sage}50`,
        }}
      />
    </div>
  );
}

// =============================================================================
// Start Session Form
// =============================================================================

interface StartSessionFormProps {
  suggestedName?: string;
  onStart: (name: string) => void;
  compact?: boolean;
}

function StartSessionForm({ suggestedName, onStart, compact }: StartSessionFormProps) {
  const [name, setName] = useState(suggestedName || '');
  const [isExpanded, setIsExpanded] = useState(false);

  const handleStart = useCallback(() => {
    const sessionName = name.trim() || `Session ${new Date().toLocaleTimeString()}`;
    onStart(sessionName);
    setName('');
    setIsExpanded(false);
  }, [name, onStart]);

  if (!isExpanded) {
    return (
      <button
        onClick={() => setIsExpanded(true)}
        className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors hover:brightness-110 ${
          compact ? 'text-xs' : 'text-sm'
        }`}
        style={{ backgroundColor: `${GLOW.copper}20`, color: GLOW.copper }}
      >
        <Circle className={compact ? 'w-3 h-3' : 'w-4 h-4'} />
        <span>Start Recording</span>
      </button>
    );
  }

  return (
    <div
      className="flex flex-col gap-2 p-3 rounded-lg"
      style={{ backgroundColor: `${EARTH.bark}60`, border: `1px solid ${EARTH.wood}` }}
    >
      <div className="flex items-center gap-2">
        <RecordingIndicator status="idle" />
        <span className="text-xs" style={{ color: EARTH.sand }}>
          Name your session (optional)
        </span>
      </div>
      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleStart()}
        placeholder={suggestedName || 'e.g., Refactoring auth flow'}
        className={`w-full px-3 py-2 rounded-lg outline-none ${compact ? 'text-xs' : 'text-sm'}`}
        style={{
          backgroundColor: `${EARTH.bark}40`,
          color: GLOW.lantern,
          border: `1px solid ${EARTH.wood}`,
        }}
        autoFocus
      />
      <div className="flex gap-2">
        <button
          onClick={handleStart}
          className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg font-medium transition-colors hover:brightness-110 ${
            compact ? 'text-xs' : 'text-sm'
          }`}
          style={{ backgroundColor: GLOW.copper, color: GLOW.lantern }}
        >
          <Circle className="w-3 h-3 fill-current" />
          Start
        </button>
        <button
          onClick={() => setIsExpanded(false)}
          className={`px-3 py-2 rounded-lg transition-colors ${compact ? 'text-xs' : 'text-sm'}`}
          style={{ backgroundColor: `${EARTH.bark}40`, color: EARTH.sand }}
        >
          Cancel
        </button>
      </div>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function RecordingControls({
  session,
  onStartSession,
  onStopSession,
  onTogglePause,
  onMarkDecision,
  onUpdateSessionName,
  suggestedName,
  compact = false,
  className = '',
}: RecordingControlsProps) {
  const [showMarkers, setShowMarkers] = useState(false);
  const [duration, setDuration] = useState('0s');

  // Update duration every second while recording
  useEffect(() => {
    if (!session || session.status === 'stopped') {
      setDuration('0s');
      return;
    }

    const interval = setInterval(() => {
      setDuration(formatDuration(session.startTime));
    }, 1000);

    return () => clearInterval(interval);
  }, [session]);

  // No active session - show start form
  if (!session) {
    return (
      <div className={className}>
        <StartSessionForm
          suggestedName={suggestedName}
          onStart={onStartSession}
          compact={compact}
        />
      </div>
    );
  }

  const isRecording = session.status === 'recording';
  const isPaused = session.status === 'paused';
  const isStopped = session.status === 'stopped';

  return (
    <div
      className={`rounded-xl overflow-hidden ${className}`}
      style={{
        backgroundColor: EARTH.soil,
        border: `1px solid ${isRecording ? `${GLOW.copper}50` : EARTH.wood}`,
      }}
    >
      {/* Header row */}
      <div
        className={`flex items-center justify-between gap-3 ${compact ? 'px-3 py-2' : 'px-4 py-3'}`}
        style={{ backgroundColor: `${EARTH.bark}80` }}
      >
        {/* Status and name */}
        <div className="flex items-center gap-2.5 min-w-0">
          <RecordingIndicator status={session.status} />
          <span
            className={`font-medium ${compact ? 'text-xs' : 'text-sm'}`}
            style={{ color: isRecording ? GLOW.copper : EARTH.sand }}
          >
            {isRecording ? 'Recording' : isPaused ? 'Paused' : 'Stopped'}
          </span>
          {!isStopped && onUpdateSessionName && (
            <SessionNameEditor
              name={session.name}
              onUpdate={onUpdateSessionName}
              compact={compact}
            />
          )}
        </div>

        {/* Controls */}
        <div className="flex items-center gap-2">
          {!isStopped && (
            <>
              {/* Pause/Resume */}
              <button
                onClick={onTogglePause}
                className={`p-1.5 rounded-lg transition-colors hover:brightness-110`}
                style={{ backgroundColor: `${EARTH.bark}60` }}
                title={isPaused ? 'Resume recording' : 'Pause recording'}
              >
                {isPaused ? (
                  <Play className="w-3.5 h-3.5" style={{ color: GREEN.sprout }} />
                ) : (
                  <Pause className="w-3.5 h-3.5" style={{ color: GLOW.amber }} />
                )}
              </button>

              {/* Decision marker */}
              <DecisionMarkerInput onMark={onMarkDecision} compact={compact} />

              {/* Stop */}
              <button
                onClick={onStopSession}
                className={`p-1.5 rounded-lg transition-colors hover:brightness-110`}
                style={{ backgroundColor: `${GLOW.copper}20` }}
                title="Stop recording"
              >
                <Square className="w-3.5 h-3.5" style={{ color: GLOW.copper }} />
              </button>
            </>
          )}
        </div>
      </div>

      {/* Stats row */}
      <div
        className={`flex items-center justify-between gap-4 ${compact ? 'px-3 py-2' : 'px-4 py-2.5'}`}
        style={{ borderTop: `1px solid ${EARTH.wood}40` }}
      >
        {/* Session name (when stopped) */}
        {isStopped && (
          <span
            className={`truncate ${compact ? 'text-xs' : 'text-sm'}`}
            style={{ color: GLOW.lantern }}
          >
            {session.name}
          </span>
        )}

        {/* Stats */}
        <div className="flex items-center gap-4 flex-shrink-0">
          {/* Duration */}
          <div className="flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5" style={{ color: EARTH.clay }} />
            <span
              className={`${compact ? 'text-[10px]' : 'text-xs'} font-mono`}
              style={{ color: EARTH.sand }}
            >
              {duration}
            </span>
          </div>

          {/* Trace count */}
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: GREEN.mint }} />
            <span
              className={`${compact ? 'text-[10px]' : 'text-xs'}`}
              style={{ color: EARTH.sand }}
            >
              {session.traceCount} traces
            </span>
          </div>

          {/* Ghost count */}
          <div className="flex items-center gap-1.5">
            <GitBranch className="w-3.5 h-3.5" style={{ color: EARTH.clay }} />
            <span
              className={`${compact ? 'text-[10px]' : 'text-xs'}`}
              style={{ color: EARTH.sand }}
            >
              {session.ghostCount} ghosts
            </span>
          </div>
        </div>

        {/* Markers toggle */}
        {session.decisionMarkers.length > 0 && (
          <button
            onClick={() => setShowMarkers(!showMarkers)}
            className="flex items-center gap-1 text-xs hover:underline"
            style={{ color: GLOW.amber }}
          >
            <Flag className="w-3 h-3" />
            <span>{session.decisionMarkers.length}</span>
            {showMarkers ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>
        )}
      </div>

      {/* Decision markers panel */}
      <AnimatePresence>
        {showMarkers && session.decisionMarkers.length > 0 && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
            style={{ borderTop: `1px solid ${EARTH.wood}40` }}
          >
            <div className={`${compact ? 'p-2' : 'p-3'} space-y-1.5`}>
              {session.decisionMarkers.map((marker) => (
                <div
                  key={marker.id}
                  className="flex items-center gap-2 px-2 py-1.5 rounded-lg"
                  style={{ backgroundColor: `${GLOW.amber}10` }}
                >
                  <Flag className="w-3 h-3" style={{ color: GLOW.amber }} />
                  <span className="text-xs flex-1" style={{ color: GLOW.honey }}>
                    {marker.label}
                  </span>
                  <span className="text-[10px]" style={{ color: EARTH.clay }}>
                    {formatDuration(session.startTime, marker.timestamp)}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// =============================================================================
// Hook: useSessionRecording
// =============================================================================

export interface UseSessionRecordingOptions {
  /** Auto-stop after idle time (ms) */
  autoStopIdleMs?: number;
  /** Callback when session changes */
  onSessionChange?: (session: RecordingSession | null) => void;
}

export interface UseSessionRecordingReturn {
  session: RecordingSession | null;
  startSession: (name: string) => void;
  stopSession: () => void;
  togglePause: () => void;
  markDecision: (label: string) => void;
  updateSessionName: (name: string) => void;
  incrementTraceCount: () => void;
  incrementGhostCount: () => void;
}

export function useSessionRecording(
  options?: UseSessionRecordingOptions
): UseSessionRecordingReturn {
  const [session, setSession] = useState<RecordingSession | null>(null);
  const lastActivityRef = useRef<number>(Date.now());

  // Notify on session change
  useEffect(() => {
    options?.onSessionChange?.(session);
  }, [session, options]);

  // Auto-stop on idle
  useEffect(() => {
    if (!session || session.status !== 'recording' || !options?.autoStopIdleMs) {
      return;
    }

    const interval = setInterval(() => {
      const idleTime = Date.now() - lastActivityRef.current;
      if (idleTime > options.autoStopIdleMs!) {
        setSession((s) => (s ? { ...s, status: 'stopped', endTime: new Date() } : null));
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [session, options?.autoStopIdleMs]);

  const startSession = useCallback((name: string) => {
    const newSession: RecordingSession = {
      id: generateSessionId(),
      name,
      startTime: new Date(),
      status: 'recording',
      traceCount: 0,
      ghostCount: 0,
      decisionMarkers: [],
      correlationId: `corr_${Date.now().toString(36)}`,
    };
    setSession(newSession);
    lastActivityRef.current = Date.now();
  }, []);

  const stopSession = useCallback(() => {
    setSession((s) => (s ? { ...s, status: 'stopped', endTime: new Date() } : null));
  }, []);

  const togglePause = useCallback(() => {
    setSession((s) =>
      s
        ? {
            ...s,
            status: s.status === 'recording' ? 'paused' : 'recording',
          }
        : null
    );
    lastActivityRef.current = Date.now();
  }, []);

  const markDecision = useCallback((label: string) => {
    setSession((s) =>
      s
        ? {
            ...s,
            decisionMarkers: [
              ...s.decisionMarkers,
              {
                id: `marker_${Date.now().toString(36)}`,
                timestamp: new Date(),
                label,
              },
            ],
          }
        : null
    );
    lastActivityRef.current = Date.now();
  }, []);

  const updateSessionName = useCallback((name: string) => {
    setSession((s) => (s ? { ...s, name } : null));
  }, []);

  const incrementTraceCount = useCallback(() => {
    setSession((s) => (s ? { ...s, traceCount: s.traceCount + 1 } : null));
    lastActivityRef.current = Date.now();
  }, []);

  const incrementGhostCount = useCallback(() => {
    setSession((s) => (s ? { ...s, ghostCount: s.ghostCount + 1 } : null));
    lastActivityRef.current = Date.now();
  }, []);

  return {
    session,
    startSession,
    stopSession,
    togglePause,
    markDecision,
    updateSessionName,
    incrementTraceCount,
    incrementGhostCount,
  };
}

export default RecordingControls;
