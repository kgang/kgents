/**
 * PathSearch - Quick path navigation with `/` key
 *
 * A focused, minimal search interface for navigating to AGENTESE paths.
 * Press `/` to open, type to filter, arrow keys to navigate, Enter to go.
 *
 * Joy-inducing: Instant filtering, fuzzy matching, smooth animations.
 *
 * @see spec/protocols/os-shell.md
 */

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, Globe, User, BookOpen, Sparkles, Clock, type LucideIcon } from 'lucide-react';
import { useMotionPreferences } from '@/components/joy/useMotionPreferences';
import { apiClient } from '@/api/client';
import type { AgenteseContext } from '@/utils/parseAgentesePath';

// =============================================================================
// Types
// =============================================================================

export interface PathSearchProps {
  /** Whether the search is open */
  isOpen: boolean;
  /** Callback to close the search */
  onClose: () => void;
}

interface PathItem {
  path: string;
  context: AgenteseContext;
  segments: string[];
}

// =============================================================================
// Constants
// =============================================================================

/** Context icons and colors */
const CONTEXT_ICONS: Record<AgenteseContext, LucideIcon> = {
  world: Globe,
  self: User,
  concept: BookOpen,
  void: Sparkles,
  time: Clock,
};

const CONTEXT_COLORS: Record<AgenteseContext, string> = {
  world: 'text-green-400',
  self: 'text-cyan-400',
  concept: 'text-violet-400',
  void: 'text-pink-400',
  time: 'text-amber-400',
};

// =============================================================================
// Fuzzy matching
// =============================================================================

/**
 * Score a match - higher is better
 * Prefers: exact prefix > word boundary > fuzzy
 */
function matchScore(query: string, target: string): number {
  if (!query) return 0;
  const q = query.toLowerCase();
  const t = target.toLowerCase();

  // Exact prefix match - highest score
  if (t.startsWith(q)) return 1000 - q.length;

  // Segment prefix match (e.g., "ci" matches "world.town.citizen")
  const segments = t.split('.');
  for (let i = 0; i < segments.length; i++) {
    if (segments[i].startsWith(q)) {
      return 500 - i * 10; // Earlier segments score higher
    }
  }

  // Check if query matches start of any segment
  for (let i = 0; i < segments.length; i++) {
    if (segments.slice(i).join('.').startsWith(q)) {
      return 300 - i * 10;
    }
  }

  // Fuzzy match score based on compactness
  let qi = 0;
  let lastMatch = -1;
  let gapPenalty = 0;
  for (let ti = 0; ti < t.length && qi < q.length; ti++) {
    if (t[ti] === q[qi]) {
      if (lastMatch >= 0) gapPenalty += ti - lastMatch - 1;
      lastMatch = ti;
      qi++;
    }
  }
  if (qi === q.length) {
    return 100 - gapPenalty;
  }

  return -1; // No match
}

// =============================================================================
// Component
// =============================================================================

export function PathSearch({ isOpen, onClose }: PathSearchProps) {
  const navigate = useNavigate();
  const { shouldAnimate } = useMotionPreferences();
  const inputRef = useRef<HTMLInputElement>(null);

  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [paths, setPaths] = useState<PathItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch paths on mount
  useEffect(() => {
    async function fetchPaths() {
      try {
        const response = await apiClient.get<{
          paths: string[];
        }>('/agentese/discover');

        const items: PathItem[] = response.data.paths.map((p) => ({
          path: p,
          context: p.split('.')[0] as AgenteseContext,
          segments: p.split('.'),
        }));

        setPaths(items);
      } catch (e) {
        console.error('[PathSearch] Failed to fetch paths:', e);
      } finally {
        setLoading(false);
      }
    }

    if (isOpen && paths.length === 0) {
      fetchPaths();
    }
  }, [isOpen, paths.length]);

  // Filter and sort paths based on query
  const filteredPaths = useMemo(() => {
    if (!query.trim()) return paths.slice(0, 15); // Show first 15 when no query

    // Filter with fuzzy matching
    const withScores = paths
      .map((p) => ({ ...p, score: matchScore(query, p.path) }))
      .filter((p) => p.score >= 0);

    // Sort by score (highest first)
    withScores.sort((a, b) => b.score - a.score);

    return withScores.slice(0, 15);
  }, [paths, query]);

  // Reset state when opened
  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  // Keep selected index in bounds
  useEffect(() => {
    if (selectedIndex >= filteredPaths.length) {
      setSelectedIndex(Math.max(0, filteredPaths.length - 1));
    }
  }, [filteredPaths.length, selectedIndex]);

  // Navigate to path
  const navigateToPath = useCallback(
    (path: string) => {
      navigate(`/${path}`);
      onClose();
    },
    [navigate, onClose]
  );

  // Keyboard navigation
  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent) => {
      switch (event.key) {
        case 'ArrowDown':
          event.preventDefault();
          setSelectedIndex((prev) => (prev < filteredPaths.length - 1 ? prev + 1 : 0));
          break;
        case 'ArrowUp':
          event.preventDefault();
          setSelectedIndex((prev) => (prev > 0 ? prev - 1 : filteredPaths.length - 1));
          break;
        case 'Enter':
          event.preventDefault();
          if (filteredPaths[selectedIndex]) {
            navigateToPath(filteredPaths[selectedIndex].path);
          } else if (query.trim()) {
            // Try to navigate to typed path directly
            navigateToPath(query.trim().replace(/^\//, ''));
          }
          break;
        case 'Tab':
          event.preventDefault();
          if (filteredPaths[selectedIndex]) {
            // Auto-complete to selected path
            setQuery(filteredPaths[selectedIndex].path);
          }
          break;
        case 'Escape':
          event.preventDefault();
          onClose();
          break;
      }
    },
    [filteredPaths, selectedIndex, query, navigateToPath, onClose]
  );

  // Format path with query highlighting
  const formatPath = (path: string, q: string) => {
    if (!q) return path;

    const lowerPath = path.toLowerCase();
    const lowerQ = q.toLowerCase();

    // Find match positions for highlighting
    const parts: Array<{ text: string; highlight: boolean }> = [];
    let lastEnd = 0;
    let qi = 0;

    for (let i = 0; i < path.length && qi < lowerQ.length; i++) {
      if (lowerPath[i] === lowerQ[qi]) {
        if (i > lastEnd) {
          parts.push({ text: path.slice(lastEnd, i), highlight: false });
        }
        parts.push({ text: path[i], highlight: true });
        lastEnd = i + 1;
        qi++;
      }
    }

    if (lastEnd < path.length) {
      parts.push({ text: path.slice(lastEnd), highlight: false });
    }

    return parts;
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: shouldAnimate ? 0.15 : 0 }}
            className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* Search panel */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -20 }}
            transition={{
              duration: shouldAnimate ? 0.2 : 0,
              ease: [0.4, 0, 0.2, 1],
            }}
            className="fixed z-50 top-[15%] left-1/2 -translate-x-1/2 w-full max-w-lg"
          >
            <div className="bg-steel-carbon/95 backdrop-blur-md rounded-xl border border-steel-gunmetal/50 shadow-2xl overflow-hidden">
              {/* Search input */}
              <div className="flex items-center gap-3 px-4 py-3 border-b border-steel-gunmetal/50">
                <span className="text-cyan-400 font-mono text-sm">/</span>
                <input
                  ref={inputRef}
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type path... (e.g., world.town.citizen)"
                  className="flex-1 bg-transparent text-white placeholder-steel-zinc outline-none text-sm font-mono"
                  autoComplete="off"
                  autoCapitalize="off"
                  spellCheck={false}
                />
                <kbd className="px-1.5 py-0.5 text-[10px] font-mono bg-steel-slate/50 border border-steel-gunmetal/50 rounded text-steel-zinc">
                  Esc
                </kbd>
              </div>

              {/* Results */}
              <div className="max-h-[50vh] overflow-auto py-2">
                {loading ? (
                  <div className="px-4 py-8 text-center text-steel-zinc text-sm">
                    Loading paths...
                  </div>
                ) : filteredPaths.length === 0 ? (
                  <div className="px-4 py-8 text-center text-steel-zinc text-sm">
                    {query ? (
                      <>
                        <p>No paths match "{query}"</p>
                        <p className="mt-2 text-xs">Press Enter to navigate to /{query}</p>
                      </>
                    ) : (
                      'No paths discovered'
                    )}
                  </div>
                ) : (
                  filteredPaths.map((item, index) => {
                    const Icon = CONTEXT_ICONS[item.context];
                    const colorClass = CONTEXT_COLORS[item.context];
                    const isSelected = index === selectedIndex;
                    const pathParts = formatPath(item.path, query);

                    return (
                      <button
                        key={item.path}
                        onClick={() => navigateToPath(item.path)}
                        onMouseEnter={() => setSelectedIndex(index)}
                        className={`
                          w-full flex items-center gap-3 px-4 py-2.5 text-left
                          transition-colors
                          ${isSelected ? 'bg-steel-slate/50' : 'hover:bg-steel-slate/30'}
                        `}
                      >
                        <Icon className={`w-4 h-4 flex-shrink-0 ${colorClass}`} />
                        <div className="flex-1 min-w-0 font-mono text-sm">
                          {typeof pathParts === 'string' ? (
                            <span className="text-white">{pathParts}</span>
                          ) : (
                            pathParts.map((part, i) => (
                              <span
                                key={i}
                                className={
                                  part.highlight ? 'text-cyan-400 font-semibold' : 'text-steel-zinc'
                                }
                              >
                                {part.text}
                              </span>
                            ))
                          )}
                        </div>
                        {isSelected && (
                          <ArrowRight className="w-4 h-4 text-steel-zinc flex-shrink-0" />
                        )}
                      </button>
                    );
                  })
                )}
              </div>

              {/* Footer hints */}
              <div className="px-4 py-2 border-t border-steel-gunmetal/50 bg-steel-carbon/50 flex items-center justify-between text-xs text-steel-zinc">
                <div className="flex items-center gap-3">
                  <span className="flex items-center gap-1">
                    <kbd className="px-1 py-0.5 text-[10px] font-mono bg-steel-slate/50 border border-steel-gunmetal/50 rounded">
                      ↑
                    </kbd>
                    <kbd className="px-1 py-0.5 text-[10px] font-mono bg-steel-slate/50 border border-steel-gunmetal/50 rounded">
                      ↓
                    </kbd>
                    navigate
                  </span>
                  <span className="flex items-center gap-1">
                    <kbd className="px-1 py-0.5 text-[10px] font-mono bg-steel-slate/50 border border-steel-gunmetal/50 rounded">
                      Tab
                    </kbd>
                    complete
                  </span>
                  <span className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 text-[10px] font-mono bg-steel-slate/50 border border-steel-gunmetal/50 rounded">
                      Enter
                    </kbd>
                    go
                  </span>
                </div>
                <span>{filteredPaths.length} paths</span>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

export default PathSearch;
