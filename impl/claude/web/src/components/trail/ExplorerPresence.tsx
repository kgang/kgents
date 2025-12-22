/**
 * ExplorerPresence - Explorer/creator information display.
 *
 * Shows who created/is exploring the trail with avatar and status.
 *
 * @see spec/protocols/trail-protocol.md Section 8
 */

// =============================================================================
// Types
// =============================================================================

interface ExplorerPresenceProps {
  /** Creator archetype (e.g., "developer", "architect") */
  creator?: string;
  /** List of current explorers (future: multi-user) */
  explorers?: Array<{
    id: string;
    archetype: string;
    status: 'viewing' | 'navigating';
  }>;
  /** Optional className */
  className?: string;
}

// =============================================================================
// Component
// =============================================================================

/**
 * ExplorerPresence component.
 *
 * Displays trail creator and current explorers.
 */
export function ExplorerPresence({
  creator,
  explorers = [],
  className = '',
}: ExplorerPresenceProps) {
  // If no creator, show default
  const displayCreator = creator || 'unknown';
  const isAgent = displayCreator.toLowerCase().includes('agent');

  return (
    <div
      className={`bg-gray-800 rounded-lg border border-gray-700 p-4 ${className}`}
    >
      <h3 className="text-sm font-medium text-gray-300 mb-3">Explorers</h3>

      {/* Creator */}
      <div className="flex items-center gap-3">
        <div
          className={`
            w-8 h-8 rounded-full flex items-center justify-center text-lg
            ${isAgent ? 'bg-purple-900/50 text-purple-400' : 'bg-blue-900/50 text-blue-400'}
          `}
        >
          {isAgent ? ' ' : ' '}
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium text-gray-200 capitalize">
            {isAgent ? 'Agent' : 'Kent'}
          </div>
          <div className="text-xs text-gray-500">
            {displayCreator} (creator)
          </div>
        </div>
      </div>

      {/* Active explorers (future multi-user support) */}
      {explorers.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-700 space-y-2">
          {explorers.map((explorer) => (
            <div key={explorer.id} className="flex items-center gap-3">
              <div
                className={`
                  w-6 h-6 rounded-full flex items-center justify-center text-sm
                  ${explorer.archetype.includes('agent')
                    ? 'bg-purple-900/30 text-purple-500'
                    : 'bg-blue-900/30 text-blue-500'}
                `}
              >
                {explorer.archetype.includes('agent') ? ' ' : ' '}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-xs text-gray-300 capitalize truncate">
                  {explorer.id}
                </div>
              </div>
              <StatusBadge status={explorer.status} />
            </div>
          ))}
        </div>
      )}

      {/* Empty explorers hint */}
      {explorers.length === 0 && (
        <div className="mt-3 pt-3 border-t border-gray-700">
          <div className="text-xs text-gray-500 italic">
            No other explorers active
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

interface StatusBadgeProps {
  status: 'viewing' | 'navigating';
}

function StatusBadge({ status }: StatusBadgeProps) {
  const isNavigating = status === 'navigating';

  return (
    <span
      className={`
        inline-flex items-center px-2 py-0.5 rounded text-xs
        ${isNavigating
          ? 'bg-green-900/30 text-green-400'
          : 'bg-gray-700 text-gray-400'}
      `}
    >
      {isNavigating && (
        <span className="w-1.5 h-1.5 rounded-full bg-green-400 mr-1.5 animate-pulse" />
      )}
      {status}
    </span>
  );
}

export default ExplorerPresence;
