/**
 * PathPicker - Modal for selecting files/concepts when building trails.
 *
 * Visual Trail Graph Session 2: Path Validation
 *
 * Features:
 * - Search files by path
 * - Recent selections
 * - AGENTESE node suggestions
 * - **Path validation with fuzzy suggestions**
 * - "Use as conceptual" for non-existing paths
 * - Suggested connections (based on current trail)
 *
 * @see brainstorming/visual-trail-graph-r&d.md Section 2.2
 * @see plans/visual-trail-graph-fullstack.md Section 3.2
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { apiClient } from '@/api/client';
import { validatePath, type PathValidation } from '@/api/trail';

// =============================================================================
// Types
// =============================================================================

interface PathPickerProps {
  /** Is the modal open? */
  isOpen: boolean;
  /** Callback to close modal */
  onClose: () => void;
  /** Callback when path is selected */
  onSelect: (path: string) => void;
  /** Optional: paths to exclude from suggestions */
  excludePaths?: string[];
  /** Optional className */
  className?: string;
}

interface RecentPath {
  path: string;
  lastUsed: number;
}

// =============================================================================
// Constants
// =============================================================================

/**
 * Common AGENTESE nodes for quick selection.
 */
const AGENTESE_NODES = [
  { path: 'self.trail', description: 'Trail management' },
  { path: 'self.context', description: 'Context perception' },
  { path: 'self.portal', description: 'Portal navigation' },
  { path: 'world.repo', description: 'Repository files' },
  { path: 'concept.principle', description: 'Core principles' },
];

/**
 * Example paths for demo purposes.
 */
const EXAMPLE_PATHS = [
  'spec/services/witness.md',
  'spec/protocols/trail-protocol.md',
  'spec/principles.md',
  'services/witness/bus.py',
  'services/witness/trail_bridge.py',
  'protocols/agentese/contexts/self_trail.py',
  'models/witness.py',
  'web/src/pages/Trail.tsx',
  'CLAUDE.md',
  'HYDRATE.md',
];

const STORAGE_KEY = 'kgents-recent-paths';

/**
 * Get icon for file type based on extension.
 */
function getFileIcon(path: string): string {
  const ext = path.split('.').pop()?.toLowerCase();
  switch (ext) {
    case 'py':
      return '🐍';
    case 'ts':
    case 'tsx':
      return '📘';
    case 'js':
    case 'jsx':
      return '📒';
    case 'md':
      return '📝';
    case 'json':
      return '📋';
    case 'yaml':
    case 'yml':
      return '⚙️';
    case 'sql':
      return '🗄️';
    case 'css':
    case 'scss':
      return '🎨';
    case 'html':
      return '🌐';
    default:
      return '📄';
  }
}

// =============================================================================
// Component
// =============================================================================

export function PathPicker({
  isOpen,
  onClose,
  onSelect,
  excludePaths = [],
  className = '',
}: PathPickerProps) {
  const [search, setSearch] = useState('');
  const [recentPaths, setRecentPaths] = useState<RecentPath[]>([]);
  const [searchResults, setSearchResults] = useState<string[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const searchTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Path validation state (Session 2)
  const [validation, setValidation] = useState<PathValidation | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const validationTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Load recent paths from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        setRecentPaths(JSON.parse(stored));
      }
    } catch {
      // Ignore localStorage errors
    }
  }, [isOpen]);

  // Debounced live file search via world.file.glob
  useEffect(() => {
    // Clear previous timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    // Only search if we have at least 2 characters
    if (search.length < 2) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }

    setIsSearching(true);

    // Debounce the search
    searchTimeoutRef.current = setTimeout(async () => {
      try {
        // Call world.file.glob with pattern matching the search term
        const response = await apiClient.post<{
          result: {
            summary: string;
            content: string;
            metadata: {
              paths?: string[];
              count?: number;
            };
          };
        }>('/agentese/world/file/glob', {
          pattern: `**/*${search}*`,
          limit: 20,
          response_format: 'json',
        });

        const paths = response.data?.result?.metadata?.paths || [];
        setSearchResults(paths);
      } catch (err) {
        console.error('[PathPicker] Search error:', err);
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [search]);

  // Path validation effect (Session 2)
  // Validates if the exact search path exists when user has typed a path-like string
  useEffect(() => {
    if (validationTimeoutRef.current) {
      clearTimeout(validationTimeoutRef.current);
    }

    // Reset if search is too short or looks like an AGENTESE path
    if (search.length < 3 || search.startsWith('self.') || search.startsWith('world.') || search.startsWith('concept.')) {
      setValidation(null);
      setIsValidating(false);
      return;
    }

    // Only validate if it looks like a file path (has / or .)
    if (!search.includes('/') && !search.includes('.')) {
      setValidation(null);
      setIsValidating(false);
      return;
    }

    setIsValidating(true);

    validationTimeoutRef.current = setTimeout(async () => {
      try {
        const result = await validatePath(search.trim());
        setValidation(result);
      } catch (err) {
        console.warn('[PathPicker] Validation failed:', err);
        setValidation(null);
      } finally {
        setIsValidating(false);
      }
    }, 400); // Slightly longer debounce for validation to avoid spamming

    return () => {
      if (validationTimeoutRef.current) {
        clearTimeout(validationTimeoutRef.current);
      }
    };
  }, [search]);

  // Save recent path
  const saveRecent = useCallback((path: string) => {
    setRecentPaths((prev) => {
      const filtered = prev.filter((p) => p.path !== path);
      const updated = [{ path, lastUsed: Date.now() }, ...filtered].slice(0, 10);

      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      } catch {
        // Ignore localStorage errors
      }

      return updated;
    });
  }, []);

  // Handle selection
  const handleSelect = useCallback(
    (path: string) => {
      saveRecent(path);
      onSelect(path);
    },
    [onSelect, saveRecent]
  );

  // Handle custom path submission
  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      if (search.trim()) {
        handleSelect(search.trim());
        setSearch('');
      }
    },
    [search, handleSelect]
  );

  // Filter paths by search
  const filteredExamples = EXAMPLE_PATHS.filter(
    (path) =>
      path.toLowerCase().includes(search.toLowerCase()) &&
      !excludePaths.includes(path)
  );

  const filteredRecent = recentPaths.filter(
    (p) =>
      p.path.toLowerCase().includes(search.toLowerCase()) &&
      !excludePaths.includes(p.path)
  );

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          onClick={(e) => e.stopPropagation()}
          className={`
            bg-gray-900 border border-gray-700 rounded-lg shadow-xl
            w-full max-w-lg max-h-[80vh] overflow-hidden flex flex-col
            ${className}
          `}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700">
            <h3 className="font-medium text-white">Select Path</h3>
            <button
              onClick={onClose}
              className="p-1.5 text-gray-400 hover:text-white"
            >
              ×
            </button>
          </div>

          {/* Search */}
          <form onSubmit={handleSubmit} className="p-4 border-b border-gray-700">
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">
                🔍
              </span>
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search files, concepts, AGENTESE..."
                autoFocus
                className={`
                  w-full pl-9 pr-10 py-2 bg-gray-800 border rounded
                  text-white placeholder-gray-500
                  focus:outline-none
                  ${validation?.exists ? 'border-green-500 focus:border-green-400' :
                    validation && !validation.exists ? 'border-amber-500 focus:border-amber-400' :
                    'border-gray-700 focus:border-blue-500'}
                `}
              />
              {/* Validation indicator */}
              <span className="absolute right-3 top-1/2 -translate-y-1/2">
                {isValidating ? (
                  <span className="animate-spin text-gray-400">⏳</span>
                ) : validation?.exists ? (
                  <span className="text-green-400" title="Path exists">✓</span>
                ) : validation && !validation.exists ? (
                  <span className="text-amber-400" title="Path not found">⚠</span>
                ) : null}
              </span>
            </div>
            <p className="mt-2 text-xs text-gray-500">
              Type a path and press Enter, or select from suggestions below
            </p>
          </form>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {/* Validation Suggestions (Session 2) */}
            {validation && !validation.exists && validation.suggestions.length > 0 && (
              <Section title="Did you mean?">
                {validation.suggestions.map((suggestion) => (
                  <PathOption
                    key={suggestion}
                    path={suggestion}
                    icon="💡"
                    subtitle="Similar path found"
                    onClick={() => handleSelect(suggestion)}
                  />
                ))}
                <button
                  onClick={() => handleSelect(search.trim())}
                  className="w-full flex items-start gap-3 p-2 rounded hover:bg-gray-800 text-left transition-colors border border-dashed border-gray-600 mt-2"
                >
                  <span className="text-gray-500 mt-0.5">📌</span>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-gray-300">Use as conceptual</div>
                    <div className="text-xs text-gray-500">
                      Add "{search}" even though it doesn't exist yet
                    </div>
                  </div>
                </button>
              </Section>
            )}

            {/* Path not found, no suggestions */}
            {validation && !validation.exists && validation.suggestions.length === 0 && searchResults.length === 0 && (
              <Section title="Path Not Found">
                <div className="text-sm text-gray-400 mb-3">
                  <span className="text-amber-400">⚠</span> "{search}" doesn't exist in the repository
                </div>
                <button
                  onClick={() => handleSelect(search.trim())}
                  className="w-full flex items-start gap-3 p-2 rounded hover:bg-gray-800 text-left transition-colors border border-dashed border-gray-600"
                >
                  <span className="text-gray-500 mt-0.5">📌</span>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-gray-300">Use as conceptual</div>
                    <div className="text-xs text-gray-500">
                      Add this path as a conceptual reference
                    </div>
                  </div>
                </button>
                {validation.can_create && (
                  <div className="mt-2 text-xs text-green-400">
                    ✓ This file type can be created later
                  </div>
                )}
              </Section>
            )}

            {/* Live Search Results (from backend) */}
            {search.length >= 2 && (
              <Section title={isSearching ? 'Searching...' : `Files (${searchResults.length})`}>
                {isSearching ? (
                  <div className="text-sm text-gray-500 py-2 flex items-center gap-2">
                    <span className="animate-spin">⏳</span>
                    Searching repository...
                  </div>
                ) : searchResults.length > 0 ? (
                  searchResults
                    .filter((path) => !excludePaths.includes(path))
                    .map((path) => (
                      <PathOption
                        key={path}
                        path={path}
                        icon={getFileIcon(path)}
                        onClick={() => handleSelect(path)}
                      />
                    ))
                ) : (
                  <div className="text-sm text-gray-500 py-2">
                    No files found. Press Enter to use "{search}"
                  </div>
                )}
              </Section>
            )}

            {/* Recent */}
            {filteredRecent.length > 0 && (
              <Section title="Recent">
                {filteredRecent.map((p) => (
                  <PathOption
                    key={p.path}
                    path={p.path}
                    onClick={() => handleSelect(p.path)}
                  />
                ))}
              </Section>
            )}

            {/* AGENTESE Nodes */}
            {!search && (
              <Section title="AGENTESE Nodes">
                {AGENTESE_NODES.filter(
                  (n) => !excludePaths.includes(n.path)
                ).map((node) => (
                  <PathOption
                    key={node.path}
                    path={node.path}
                    subtitle={node.description}
                    icon="◈"
                    onClick={() => handleSelect(node.path)}
                  />
                ))}
              </Section>
            )}

            {/* Examples (only when not searching) */}
            {!search && (
              <Section title="Examples">
                {filteredExamples.map((path) => (
                  <PathOption
                    key={path}
                    path={path}
                    onClick={() => handleSelect(path)}
                  />
                ))}
              </Section>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

interface SectionProps {
  title: string;
  children: React.ReactNode;
}

function Section({ title, children }: SectionProps) {
  return (
    <div>
      <h4 className="text-xs text-gray-500 uppercase tracking-wide mb-2">
        {title}
      </h4>
      <div className="space-y-1">{children}</div>
    </div>
  );
}

interface PathOptionProps {
  path: string;
  subtitle?: string;
  icon?: string;
  onClick: () => void;
}

function PathOption({ path, subtitle, icon, onClick }: PathOptionProps) {
  // Extract holon from path
  const parts = path.split('/');
  const holon = parts[parts.length - 1].split('.')[0];

  return (
    <button
      onClick={onClick}
      className="
        w-full flex items-start gap-3 p-2 rounded
        hover:bg-gray-800 text-left transition-colors
      "
    >
      <span className="text-gray-500 mt-0.5">{icon || '•'}</span>
      <div className="flex-1 min-w-0">
        <div className="font-medium text-white truncate">{holon}</div>
        <div className="text-xs text-gray-500 truncate">{path}</div>
        {subtitle && (
          <div className="text-xs text-gray-400 mt-0.5">{subtitle}</div>
        )}
      </div>
    </button>
  );
}

export default PathPicker;
