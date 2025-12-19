/**
 * Terminal - OS Shell AGENTESE Terminal Layer
 *
 * The terminal provides direct AGENTESE gateway interaction with persistence.
 * It lives at the bottom of the shell and adapts to density.
 *
 * Features:
 * - Full AGENTESE CLI in browser
 * - Tab completion from registry
 * - History (persisted to localStorage)
 * - Collections (save/load request sets)
 * - Density-adaptive layout
 *
 * Density adaptation:
 * - spacious: Docked at bottom, resizable height
 * - comfortable: Collapsed to input line, expand on focus
 * - compact: Floating action button (bottom-left), full-screen modal on tap
 *            Bottom-left positioning avoids collision with context-specific
 *            mobile buttons (FloatingActions) that appear on the right side.
 *
 * @see spec/protocols/os-shell.md Part VI: Terminal Service
 */

import {
  useState,
  useEffect,
  useRef,
  useCallback,
  useMemo,
  type KeyboardEvent,
} from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Terminal as TerminalIcon,
  ChevronUp,
  ChevronDown,
  X,
  Maximize2,
  Minimize2,
  Send,
  Trash2,
} from 'lucide-react';
import { useShell } from './ShellProvider';
import { getTerminalService } from './TerminalService';
import { useMotionPreferences } from '../components/joy/useMotionPreferences';
import type { TerminalLine, CompletionSuggestion } from './types';

// =============================================================================
// Types
// =============================================================================

export interface TerminalProps {
  /** Additional CSS classes */
  className?: string;
  /** Default expanded state on desktop */
  defaultExpanded?: boolean;
  /** Default height in pixels (spacious density) */
  defaultHeight?: number;
}

// =============================================================================
// Constants
// =============================================================================

/** Terminal heights for different states */
const HEIGHTS = {
  collapsed: 48,
  comfortable: 48,
  default: 200,
  max: 400,
} as const;

/** Prompt prefix */
const PROMPT = 'kg>';

/** Storage key for persisted terminal output */
const STORAGE_KEY_OUTPUT = 'kgents:terminal:output';

/** Maximum lines to persist */
const MAX_PERSISTED_LINES = 50;

// =============================================================================
// Line Renderers
// =============================================================================

/**
 * Render a terminal output line with appropriate styling.
 */
function TerminalOutputLine({ line }: { line: TerminalLine }) {
  const colorClass = {
    input: 'text-cyan-400',
    output: 'text-gray-300',
    error: 'text-red-400',
    info: 'text-amber-400',
    system: 'text-gray-500',
  }[line.type];

  // Handle JSON data display
  if (line.type === 'output' && line.data && typeof line.data === 'object') {
    return (
      <div className="font-mono text-xs">
        <pre className={`${colorClass} whitespace-pre-wrap overflow-x-auto`}>
          {JSON.stringify(line.data, null, 2)}
        </pre>
      </div>
    );
  }

  return (
    <div className={`font-mono text-xs ${colorClass}`}>
      {line.content}
    </div>
  );
}

/**
 * Completion dropdown for tab completion.
 */
function CompletionDropdown({
  suggestions,
  selectedIndex,
  onSelect,
}: {
  suggestions: CompletionSuggestion[];
  selectedIndex: number;
  onSelect: (suggestion: CompletionSuggestion) => void;
}) {
  if (suggestions.length === 0) return null;

  return (
    <div className="absolute bottom-full left-0 right-0 bg-gray-800 border border-gray-700 rounded-t-lg shadow-lg max-h-48 overflow-auto">
      {suggestions.map((suggestion, index) => (
        <button
          key={suggestion.text}
          onClick={() => onSelect(suggestion)}
          className={`w-full px-3 py-1.5 text-left text-xs font-mono flex items-center gap-2 hover:bg-gray-700 transition-colors ${
            index === selectedIndex ? 'bg-gray-700' : ''
          }`}
        >
          <span
            className={`px-1 rounded text-[10px] ${
              {
                path: 'bg-cyan-900 text-cyan-300',
                aspect: 'bg-green-900 text-green-300',
                command: 'bg-amber-900 text-amber-300',
                alias: 'bg-violet-900 text-violet-300',
              }[suggestion.type]
            }`}
          >
            {suggestion.type}
          </span>
          <span className="text-white">{suggestion.text}</span>
          {suggestion.description && (
            <span className="text-gray-500 ml-auto truncate max-w-48">
              {suggestion.description}
            </span>
          )}
        </button>
      ))}
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * Terminal component for the OS Shell.
 *
 * @example
 * ```tsx
 * // In Shell layout
 * <Terminal />
 *
 * // With options
 * <Terminal
 *   defaultExpanded={true}
 *   defaultHeight={250}
 * />
 * ```
 */
export function Terminal({
  className = '',
  defaultExpanded = false,
  defaultHeight = HEIGHTS.default,
}: TerminalProps) {
  const {
    density,
    terminalExpanded,
    setTerminalExpanded,
    observer,
  } = useShell();
  const { shouldAnimate } = useMotionPreferences();

  // Terminal service
  const service = useMemo(() => getTerminalService(), []);

  // Set observer on service when it changes
  useEffect(() => {
    service.setObserver(observer);
  }, [service, observer]);

  // State
  const [input, setInput] = useState('');
  // Initialize lines from localStorage for session persistence
  const [lines, setLines] = useState<TerminalLine[]>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY_OUTPUT);
      if (stored) {
        const parsed = JSON.parse(stored);
        // Restore dates from ISO strings
        return parsed.map((line: TerminalLine) => ({
          ...line,
          timestamp: new Date(line.timestamp),
        }));
      }
    } catch {
      // Ignore parse errors
    }
    return [];
  });
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [suggestions, setSuggestions] = useState<CompletionSuggestion[]>([]);
  const [selectedSuggestion, setSelectedSuggestion] = useState(0);
  const [isExecuting, setIsExecuting] = useState(false);
  const [height, setHeight] = useState(defaultHeight);

  // Refs
  const inputRef = useRef<HTMLInputElement>(null);
  const outputRef = useRef<HTMLDivElement>(null);
  const resizeRef = useRef<HTMLDivElement>(null);

  // Initialize expansion state
  useEffect(() => {
    if (defaultExpanded && !terminalExpanded) {
      setTerminalExpanded(true);
    }
  }, [defaultExpanded, terminalExpanded, setTerminalExpanded]);

  // Listen for shell focus/command events
  useEffect(() => {
    const handleFocus = () => {
      inputRef.current?.focus();
    };

    const handleCommand = (event: Event) => {
      const customEvent = event as CustomEvent<{ command: string }>;
      const command = customEvent.detail?.command;
      if (command) {
        setInput(command);
        inputRef.current?.focus();
      }
    };

    document.addEventListener('shell:focus-terminal', handleFocus);
    document.addEventListener('shell:terminal-command', handleCommand);

    return () => {
      document.removeEventListener('shell:focus-terminal', handleFocus);
      document.removeEventListener('shell:terminal-command', handleCommand);
    };
  }, []);

  // Auto-scroll output
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [lines]);

  // Persist lines to localStorage
  useEffect(() => {
    try {
      // Only persist the most recent lines
      const toStore = lines.slice(-MAX_PERSISTED_LINES);
      localStorage.setItem(STORAGE_KEY_OUTPUT, JSON.stringify(toStore));
    } catch {
      // Ignore storage errors
    }
  }, [lines]);

  // ===========================================================================
  // Handlers
  // ===========================================================================

  const handleExpand = useCallback(() => {
    setTerminalExpanded(true);
    setTimeout(() => inputRef.current?.focus(), 100);
  }, [setTerminalExpanded]);

  const handleCollapse = useCallback(() => {
    setTerminalExpanded(false);
  }, [setTerminalExpanded]);

  const handleClear = useCallback(() => {
    setLines([]);
    // Also clear persisted output
    try {
      localStorage.removeItem(STORAGE_KEY_OUTPUT);
    } catch {
      // Ignore storage errors
    }
  }, []);

  const handleExecute = useCallback(async () => {
    if (!input.trim() || isExecuting) return;

    setIsExecuting(true);
    setSuggestions([]);
    setSelectedSuggestion(0);
    setHistoryIndex(-1);

    try {
      const result = await service.execute(input);

      // Handle special clear command
      if (result.some((l) => l.content === '__CLEAR__')) {
        setLines([]);
      } else {
        setLines((prev) => [...prev, ...result]);
      }
    } finally {
      setInput('');
      setIsExecuting(false);
    }
  }, [input, isExecuting, service]);

  const handleInputChange = useCallback(
    async (value: string) => {
      setInput(value);
      setHistoryIndex(-1);

      // Get completions if typing
      if (value.length > 0) {
        const completions = await service.complete(value);
        setSuggestions(completions);
        setSelectedSuggestion(0);
      } else {
        setSuggestions([]);
      }
    },
    [service]
  );

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLInputElement>) => {
      switch (e.key) {
        case 'Enter':
          if (suggestions.length > 0 && selectedSuggestion >= 0) {
            // Accept suggestion
            setInput(suggestions[selectedSuggestion].text);
            setSuggestions([]);
          } else {
            // Execute command
            handleExecute();
          }
          e.preventDefault();
          break;

        case 'Tab':
          e.preventDefault();
          if (suggestions.length > 0) {
            // Accept first suggestion
            setInput(suggestions[selectedSuggestion].text);
            setSuggestions([]);
          }
          break;

        case 'ArrowUp':
          e.preventDefault();
          if (suggestions.length > 0) {
            setSelectedSuggestion((prev) =>
              prev > 0 ? prev - 1 : suggestions.length - 1
            );
          } else {
            // Navigate history
            const history = service.history;
            if (historyIndex < history.length - 1) {
              const newIndex = historyIndex + 1;
              setHistoryIndex(newIndex);
              setInput(history[newIndex].input);
            }
          }
          break;

        case 'ArrowDown':
          e.preventDefault();
          if (suggestions.length > 0) {
            setSelectedSuggestion((prev) =>
              prev < suggestions.length - 1 ? prev + 1 : 0
            );
          } else {
            // Navigate history
            if (historyIndex > 0) {
              const newIndex = historyIndex - 1;
              setHistoryIndex(newIndex);
              setInput(service.history[newIndex].input);
            } else if (historyIndex === 0) {
              setHistoryIndex(-1);
              setInput('');
            }
          }
          break;

        case 'Escape':
          setSuggestions([]);
          setSelectedSuggestion(0);
          break;

        case 'c':
          if (e.ctrlKey) {
            setInput('');
            setSuggestions([]);
          }
          break;

        case 'l':
          if (e.ctrlKey) {
            e.preventDefault();
            handleClear();
          }
          break;
      }
    },
    [
      handleExecute,
      handleClear,
      suggestions,
      selectedSuggestion,
      service,
      historyIndex,
    ]
  );

  const handleSuggestionSelect = useCallback(
    (suggestion: CompletionSuggestion) => {
      setInput(suggestion.text);
      setSuggestions([]);
      inputRef.current?.focus();
    },
    []
  );

  // ===========================================================================
  // Resize handling (spacious density only)
  // ===========================================================================

  useEffect(() => {
    if (density !== 'spacious' || !resizeRef.current) return;

    let startY = 0;
    let startHeight = 0;

    const handleMouseDown = (e: MouseEvent) => {
      startY = e.clientY;
      startHeight = height;
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    };

    const handleMouseMove = (e: MouseEvent) => {
      const deltaY = startY - e.clientY;
      const newHeight = Math.min(
        HEIGHTS.max,
        Math.max(HEIGHTS.collapsed, startHeight + deltaY)
      );
      setHeight(newHeight);
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    const resizeHandle = resizeRef.current;
    resizeHandle.addEventListener('mousedown', handleMouseDown);

    return () => {
      resizeHandle.removeEventListener('mousedown', handleMouseDown);
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [density, height]);

  // ===========================================================================
  // Render - Compact (mobile)
  // ===========================================================================

  if (density === 'compact') {
    return (
      <>
        {/* Floating Action Button - Bottom-left to avoid collision with context-specific mobile buttons on right */}
        <button
          onClick={handleExpand}
          className={`fixed bottom-4 left-4 w-14 h-14 bg-gray-800 hover:bg-gray-700 rounded-full shadow-lg flex items-center justify-center z-40 transition-colors ${className}`}
          aria-label="Open terminal"
        >
          <TerminalIcon className="w-6 h-6 text-cyan-400" />
        </button>

        {/* Full-screen modal */}
        <AnimatePresence>
          {terminalExpanded && (
            <motion.div
              initial={{ opacity: 0, y: '100%' }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: '100%' }}
              transition={{ duration: shouldAnimate ? 0.3 : 0 }}
              className="fixed inset-0 bg-gray-900 z-50 flex flex-col"
            >
              {/* Header */}
              <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700">
                <div className="flex items-center gap-2">
                  <TerminalIcon className="w-5 h-5 text-cyan-400" />
                  <span className="text-white font-medium">AGENTESE Terminal</span>
                </div>
                <button
                  onClick={handleCollapse}
                  className="p-2 hover:bg-gray-700 rounded transition-colors"
                  aria-label="Close terminal"
                >
                  <X className="w-5 h-5 text-gray-400" />
                </button>
              </div>

              {/* Output */}
              <div
                ref={outputRef}
                className="flex-1 overflow-auto p-4 space-y-1"
              >
                {lines.map((line) => (
                  <TerminalOutputLine key={line.id} line={line} />
                ))}
              </div>

              {/* Input */}
              <div className="relative border-t border-gray-700 p-4">
                <CompletionDropdown
                  suggestions={suggestions}
                  selectedIndex={selectedSuggestion}
                  onSelect={handleSuggestionSelect}
                />
                <div className="flex items-center gap-2">
                  <span className="text-cyan-400 font-mono text-sm">{PROMPT}</span>
                  <input
                    ref={inputRef}
                    type="text"
                    value={input}
                    onChange={(e) => handleInputChange(e.target.value)}
                    onKeyDown={handleKeyDown}
                    className="flex-1 bg-transparent text-white font-mono text-sm outline-none"
                    placeholder="Enter command..."
                    autoFocus
                    autoComplete="off"
                    autoCapitalize="off"
                    spellCheck={false}
                  />
                  <button
                    onClick={handleExecute}
                    disabled={isExecuting || !input.trim()}
                    className="p-2 bg-cyan-600 hover:bg-cyan-500 disabled:bg-gray-700 disabled:text-gray-500 rounded transition-colors"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </>
    );
  }

  // ===========================================================================
  // Render - Comfortable (tablet) - Fixed at bottom
  // ===========================================================================

  if (density === 'comfortable') {
    return (
      <div className={`fixed bottom-0 left-0 right-0 z-40 bg-gray-800/[0.825] backdrop-blur-md border-t border-gray-700/50 ${className}`}>
        <AnimatePresence mode="wait" initial={false}>
          {terminalExpanded ? (
            <motion.div
              key="expanded"
              initial={{ height: HEIGHTS.comfortable }}
              animate={{ height: HEIGHTS.default }}
              exit={{ height: HEIGHTS.comfortable }}
              transition={{ duration: shouldAnimate ? 0.2 : 0 }}
              className="flex flex-col"
            >
              {/* Header */}
              <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700/50">
                <div className="flex items-center gap-2">
                  <TerminalIcon className="w-4 h-4 text-cyan-400" />
                  <span className="text-white text-sm font-medium">Terminal</span>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={handleClear}
                    className="p-1 hover:bg-gray-700 rounded transition-colors"
                    title="Clear"
                  >
                    <Trash2 className="w-4 h-4 text-gray-400" />
                  </button>
                  <button
                    onClick={handleCollapse}
                    className="p-1 hover:bg-gray-700 rounded transition-colors"
                    title="Collapse"
                  >
                    <ChevronDown className="w-4 h-4 text-gray-400" />
                  </button>
                </div>
              </div>

              {/* Output */}
              <div
                ref={outputRef}
                className="flex-1 overflow-auto px-4 py-2 space-y-0.5"
              >
                {lines.map((line) => (
                  <TerminalOutputLine key={line.id} line={line} />
                ))}
              </div>

              {/* Input */}
              <div className="relative px-4 py-2 border-t border-gray-700/50">
                <CompletionDropdown
                  suggestions={suggestions}
                  selectedIndex={selectedSuggestion}
                  onSelect={handleSuggestionSelect}
                />
                <div className="flex items-center gap-2">
                  <span className="text-cyan-400 font-mono text-xs">{PROMPT}</span>
                  <input
                    ref={inputRef}
                    type="text"
                    value={input}
                    onChange={(e) => handleInputChange(e.target.value)}
                    onKeyDown={handleKeyDown}
                    className="flex-1 bg-transparent text-white font-mono text-xs outline-none"
                    placeholder="Enter command..."
                    autoComplete="off"
                    autoCapitalize="off"
                    spellCheck={false}
                  />
                </div>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="collapsed"
              initial={{ height: HEIGHTS.default }}
              animate={{ height: HEIGHTS.comfortable }}
              exit={{ height: HEIGHTS.default }}
              transition={{ duration: shouldAnimate ? 0.2 : 0 }}
            >
              {/* Collapsed input line */}
              <div className="flex items-center gap-2 px-4 h-12">
                <button
                  onClick={handleExpand}
                  className="p-1.5 hover:bg-gray-700 rounded transition-colors"
                  title="Expand terminal"
                >
                  <TerminalIcon className="w-4 h-4 text-cyan-400" />
                </button>
                <span className="text-cyan-400 font-mono text-xs">{PROMPT}</span>
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => handleInputChange(e.target.value)}
                  onKeyDown={handleKeyDown}
                  onFocus={handleExpand}
                  className="flex-1 bg-transparent text-white font-mono text-xs outline-none"
                  placeholder="Enter command..."
                  autoComplete="off"
                  autoCapitalize="off"
                  spellCheck={false}
                />
                <button
                  onClick={handleExpand}
                  className="p-1.5 hover:bg-gray-700 rounded transition-colors"
                  title="Expand"
                >
                  <ChevronUp className="w-4 h-4 text-gray-400" />
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    );
  }

  // ===========================================================================
  // Render - Spacious (desktop) - Fixed at bottom
  // ===========================================================================

  const isExpanded = terminalExpanded;
  const currentHeight = isExpanded ? height : HEIGHTS.collapsed;

  return (
    <div
      className={`fixed bottom-0 left-0 right-0 z-40 bg-gray-800/[0.825] backdrop-blur-md border-t border-gray-700/50 flex flex-col ${className}`}
      style={{ height: currentHeight }}
    >
      {/* Resize handle */}
      {isExpanded && (
        <div
          ref={resizeRef}
          className="absolute top-0 left-0 right-0 h-1 cursor-ns-resize hover:bg-cyan-500/50 transition-colors"
        />
      )}

      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700/50 shrink-0">
        <div className="flex items-center gap-2">
          <TerminalIcon className="w-4 h-4 text-cyan-400" />
          <span className="text-white text-sm font-medium">AGENTESE Terminal</span>
        </div>
        <div className="flex items-center gap-1">
          {isExpanded && (
            <>
              <button
                onClick={handleClear}
                className="p-1.5 hover:bg-gray-700 rounded transition-colors"
                title="Clear (Ctrl+L)"
              >
                <Trash2 className="w-4 h-4 text-gray-400" />
              </button>
              <button
                onClick={() => setHeight((h) => (h === HEIGHTS.max ? HEIGHTS.default : HEIGHTS.max))}
                className="p-1.5 hover:bg-gray-700 rounded transition-colors"
                title={height === HEIGHTS.max ? 'Restore' : 'Maximize'}
              >
                {height === HEIGHTS.max ? (
                  <Minimize2 className="w-4 h-4 text-gray-400" />
                ) : (
                  <Maximize2 className="w-4 h-4 text-gray-400" />
                )}
              </button>
            </>
          )}
          <button
            onClick={isExpanded ? handleCollapse : handleExpand}
            className="p-1.5 hover:bg-gray-700 rounded transition-colors"
            title={isExpanded ? 'Collapse' : 'Expand'}
          >
            {isExpanded ? (
              <ChevronDown className="w-4 h-4 text-gray-400" />
            ) : (
              <ChevronUp className="w-4 h-4 text-gray-400" />
            )}
          </button>
        </div>
      </div>

      {/* Output (only when expanded) */}
      {isExpanded && (
        <div
          ref={outputRef}
          className="flex-1 overflow-auto px-4 py-2 space-y-0.5 min-h-0"
        >
          {lines.length === 0 ? (
            <div className="text-xs font-mono space-y-0.5">
              <div className="text-cyan-400">Welcome to the AGENTESE Terminal</div>
              <div className="text-gray-500">&nbsp;</div>
              <div className="text-gray-400">Try these commands:</div>
              <div className="text-gray-300">  <span className="text-cyan-300">discover</span>         List all paths</div>
              <div className="text-gray-300">  <span className="text-cyan-300">self.soul.manifest</span> View K-gent state</div>
              <div className="text-gray-300">  <span className="text-cyan-300">world.codebase</span>     Codebase health</div>
              <div className="text-gray-300">  <span className="text-cyan-300">help</span>              Full command reference</div>
              <div className="text-gray-500">&nbsp;</div>
              <div className="text-gray-500">Tab for completion · ↑↓ for history</div>
            </div>
          ) : (
            lines.map((line) => (
              <TerminalOutputLine key={line.id} line={line} />
            ))
          )}
        </div>
      )}

      {/* Input */}
      <div
        className={`relative px-4 py-2 shrink-0 ${
          isExpanded ? 'border-t border-gray-700/50' : ''
        }`}
      >
        <CompletionDropdown
          suggestions={suggestions}
          selectedIndex={selectedSuggestion}
          onSelect={handleSuggestionSelect}
        />
        <div className="flex items-center gap-2">
          <span className="text-cyan-400 font-mono text-xs">{PROMPT}</span>
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => handleInputChange(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => !isExpanded && handleExpand()}
            className="flex-1 bg-transparent text-white font-mono text-xs outline-none"
            placeholder="Enter command..."
            autoComplete="off"
            autoCapitalize="off"
            spellCheck={false}
          />
          {input.trim() && (
            <button
              onClick={handleExecute}
              disabled={isExecuting}
              className="px-2 py-1 text-xs bg-cyan-600 hover:bg-cyan-500 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded transition-colors"
            >
              Run
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default Terminal;
