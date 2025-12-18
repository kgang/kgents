/**
 * CitizenBrowser - List, Search, and Filter Town Citizens
 *
 * P0 User Journey: Browse all citizens, filter by archetype/status,
 * view details, and start conversations.
 *
 * Design Language:
 * - Organic/crystalline aesthetic
 * - Violet theme (Coalition Crown Jewel)
 * - Virtualized list for performance
 *
 * @see docs/skills/elastic-ui-patterns.md
 * @see docs/skills/crown-jewel-patterns.md
 */

import { useState, useMemo } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Users,
  Search,
  Filter,
  User,
  MessageCircle,
  Activity,
  ChevronRight,
  X,
  Clock,
} from 'lucide-react';
import {
  useCitizens,
  useCitizen,
  useConversationHistory,
  useStartConversation,
} from '../../hooks';
import { useShell } from '../../shell/ShellProvider';
// JEWEL_COLORS import available if needed for custom styling
// import { JEWEL_COLORS } from '../../constants/jewels';

// =============================================================================
// Constants
// =============================================================================

// VIOLET colors from JEWEL_COLORS.coalition (used for theming)
// const VIOLET = JEWEL_COLORS.coalition;

const ARCHETYPES = [
  { value: '', label: 'All Archetypes' },
  { value: 'default', label: 'Default' },
  { value: 'leader', label: 'Leader' },
  { value: 'thinker', label: 'Thinker' },
  { value: 'builder', label: 'Builder' },
  { value: 'connector', label: 'Connector' },
];

// =============================================================================
// Sub-components
// =============================================================================

interface CitizenRowProps {
  id: string;
  name: string;
  archetype: string;
  isActive: boolean;
  interactionCount: number;
  isSelected: boolean;
  onClick: () => void;
}

function CitizenRow({ id: _id, name, archetype, isActive, interactionCount, isSelected, onClick }: CitizenRowProps) {
  return (
    <motion.button
      layout
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClick}
      className={`
        w-full p-3 flex items-center justify-between
        border-b border-violet-500/10 last:border-b-0
        transition-colors
        ${isSelected
          ? 'bg-violet-500/20 border-l-2 border-l-violet-400'
          : 'hover:bg-violet-950/50 border-l-2 border-l-transparent'
        }
      `}
    >
      <div className="flex items-center gap-3">
        <div className={`w-2.5 h-2.5 rounded-full ${isActive ? 'bg-green-400' : 'bg-gray-500'}`} />
        <div className="text-left">
          <p className={`font-medium ${isSelected ? 'text-white' : 'text-gray-200'}`}>{name}</p>
          <p className="text-xs text-gray-400 capitalize">{archetype}</p>
        </div>
      </div>
      <div className="flex items-center gap-4 text-sm text-gray-400">
        <span className="flex items-center gap-1">
          <MessageCircle className="w-3.5 h-3.5" />
          {interactionCount}
        </span>
        <ChevronRight className="w-4 h-4 text-violet-400" />
      </div>
    </motion.button>
  );
}

interface CitizenDetailPanelProps {
  citizenId: string;
  onClose: () => void;
  onStartConversation: () => void;
}

function CitizenDetailPanel({ citizenId, onClose, onStartConversation }: CitizenDetailPanelProps) {
  const citizen = useCitizen(citizenId);
  const history = useConversationHistory(citizenId);

  if (citizen.isLoading) {
    return (
      <div className="p-6 animate-pulse space-y-4">
        <div className="h-8 w-48 bg-violet-950/50 rounded" />
        <div className="h-4 w-32 bg-violet-950/50 rounded" />
        <div className="h-24 bg-violet-950/50 rounded" />
      </div>
    );
  }

  const data = citizen.data?.citizen;
  const conversations = history.data?.conversations ?? [];

  if (!data) {
    return (
      <div className="p-6 text-center text-gray-500">
        <p>Citizen not found</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-violet-500/30 flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-violet-500/20 flex items-center justify-center">
            <User className="w-6 h-6 text-violet-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">{data.name}</h2>
            <p className="text-sm text-gray-400 capitalize">{data.archetype}</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 hover:bg-violet-950/50 rounded-lg transition-colors"
        >
          <X className="w-4 h-4 text-gray-400" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Status */}
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${data.is_active ? 'bg-green-400' : 'bg-gray-500'}`} />
          <span className="text-sm text-gray-400">{data.is_active ? 'Active' : 'Inactive'}</span>
        </div>

        {/* Description */}
        {data.description && (
          <div>
            <h3 className="text-xs font-medium text-gray-500 uppercase mb-1">Description</h3>
            <p className="text-sm text-gray-300">{data.description}</p>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-violet-950/30 rounded-lg p-3">
            <div className="flex items-center gap-2 text-violet-400 mb-1">
              <MessageCircle className="w-4 h-4" />
              <span className="text-xs font-medium">Interactions</span>
            </div>
            <p className="text-xl font-bold text-white">{data.interaction_count}</p>
          </div>
          <div className="bg-violet-950/30 rounded-lg p-3">
            <div className="flex items-center gap-2 text-violet-400 mb-1">
              <Activity className="w-4 h-4" />
              <span className="text-xs font-medium">Conversations</span>
            </div>
            <p className="text-xl font-bold text-white">{conversations.length}</p>
          </div>
        </div>

        {/* Traits */}
        {data.traits && Object.keys(data.traits).length > 0 && (
          <div>
            <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">Traits</h3>
            <div className="flex flex-wrap gap-2">
              {Object.entries(data.traits).map(([key, value]) => (
                <span
                  key={key}
                  className="px-2 py-1 bg-violet-950/50 rounded text-xs text-gray-300"
                >
                  {key}: {String(value)}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Recent Conversations */}
        {conversations.length > 0 && (
          <div>
            <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">Recent Conversations</h3>
            <div className="space-y-2">
              {conversations.slice(0, 3).map((conv) => (
                <div
                  key={conv.id}
                  className="p-2 bg-violet-950/30 rounded-lg text-sm"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-gray-300">{conv.topic || 'General'}</span>
                    <span className="text-xs text-gray-500">{conv.turn_count} turns</span>
                  </div>
                  {conv.summary && (
                    <p className="text-xs text-gray-400 line-clamp-2">{conv.summary}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Metadata */}
        <div className="text-xs text-gray-500 flex items-center gap-1">
          <Clock className="w-3 h-3" />
          <span>Created {new Date(data.created_at).toLocaleDateString()}</span>
        </div>
      </div>

      {/* Actions */}
      <div className="p-4 border-t border-violet-500/30">
        <button
          onClick={onStartConversation}
          className="w-full py-2.5 bg-violet-500 hover:bg-violet-400 rounded-lg text-white font-medium transition-colors flex items-center justify-center gap-2"
        >
          <MessageCircle className="w-4 h-4" />
          Start Conversation
        </button>
      </div>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function CitizenBrowser() {
  const navigate = useNavigate();
  const { citizenId } = useParams<{ citizenId?: string }>();
  const { density } = useShell();
  const isCompact = density === 'compact';

  // Local state
  const [searchQuery, setSearchQuery] = useState('');
  const [archetypeFilter, setArchetypeFilter] = useState('');
  const [showActiveOnly, setShowActiveOnly] = useState(false);

  // Fetch citizens
  const citizens = useCitizens();
  const startConversation = useStartConversation();

  // Filter citizens
  const filteredCitizens = useMemo(() => {
    const list = citizens.data?.citizens ?? [];
    return list.filter((citizen) => {
      // Search filter
      if (searchQuery && !citizen.name.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false;
      }
      // Archetype filter
      if (archetypeFilter && citizen.archetype !== archetypeFilter) {
        return false;
      }
      // Active filter
      if (showActiveOnly && !citizen.is_active) {
        return false;
      }
      return true;
    });
  }, [citizens.data?.citizens, searchQuery, archetypeFilter, showActiveOnly]);

  const handleSelectCitizen = (id: string) => {
    navigate(`/town/citizens/${id}`);
  };

  const handleCloseCitizen = () => {
    navigate('/town/citizens');
  };

  const handleStartConversation = async () => {
    if (!citizenId) return;
    try {
      await startConversation.mutateAsync({ citizen_id: citizenId });
      // Navigate to conversation view (future)
    } catch (error) {
      console.error('Failed to start conversation:', error);
    }
  };

  // Loading state
  if (citizens.isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-violet-400 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-gray-400">Loading citizens...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (citizens.error) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center text-red-400">
          <p>Failed to load citizens</p>
          <p className="text-sm text-red-300/70">{(citizens.error as Error).message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex">
      {/* List Panel */}
      <div className={`${citizenId && !isCompact ? 'w-1/2 border-r border-violet-500/30' : 'w-full'} flex flex-col`}>
        {/* Header */}
        <div className="p-4 border-b border-violet-500/30">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Users className="w-5 h-5 text-violet-400" />
              <h1 className="text-lg font-semibold text-white">Citizens</h1>
              <span className="text-sm text-gray-500">({filteredCitizens.length})</span>
            </div>
          </div>

          {/* Search */}
          <div className="relative mb-3">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              placeholder="Search citizens..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-violet-950/50 border border-violet-500/30 rounded-lg text-white placeholder:text-gray-500 focus:outline-none focus:border-violet-400"
            />
          </div>

          {/* Filters */}
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 text-gray-400">
              <Filter className="w-4 h-4" />
            </div>
            <select
              value={archetypeFilter}
              onChange={(e) => setArchetypeFilter(e.target.value)}
              className="bg-violet-950/50 border border-violet-500/30 rounded px-2 py-1 text-sm text-gray-300 focus:outline-none focus:border-violet-400"
            >
              {ARCHETYPES.map((a) => (
                <option key={a.value} value={a.value}>
                  {a.label}
                </option>
              ))}
            </select>
            <label className="flex items-center gap-1.5 text-sm text-gray-400 cursor-pointer">
              <input
                type="checkbox"
                checked={showActiveOnly}
                onChange={(e) => setShowActiveOnly(e.target.checked)}
                className="w-4 h-4 rounded border-violet-500/30 bg-violet-950/50 text-violet-400 focus:ring-violet-400"
              />
              Active only
            </label>
          </div>
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto">
          <AnimatePresence>
            {filteredCitizens.length > 0 ? (
              filteredCitizens.map((citizen) => (
                <CitizenRow
                  key={citizen.id}
                  id={citizen.id}
                  name={citizen.name}
                  archetype={citizen.archetype}
                  isActive={citizen.is_active}
                  interactionCount={citizen.interaction_count}
                  isSelected={citizen.id === citizenId}
                  onClick={() => handleSelectCitizen(citizen.id)}
                />
              ))
            ) : (
              <div className="p-8 text-center text-gray-500">
                <Users className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>No citizens match your filters</p>
              </div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Detail Panel (Desktop) */}
      {citizenId && !isCompact && (
        <div className="w-1/2 bg-violet-950/20">
          <CitizenDetailPanel
            citizenId={citizenId}
            onClose={handleCloseCitizen}
            onStartConversation={handleStartConversation}
          />
        </div>
      )}

      {/* Detail Panel (Mobile - Bottom Sheet) */}
      {citizenId && isCompact && (
        <motion.div
          initial={{ y: '100%' }}
          animate={{ y: 0 }}
          exit={{ y: '100%' }}
          className="fixed inset-x-0 bottom-0 top-20 bg-violet-950 rounded-t-2xl shadow-xl z-50"
        >
          <CitizenDetailPanel
            citizenId={citizenId}
            onClose={handleCloseCitizen}
            onStartConversation={handleStartConversation}
          />
        </motion.div>
      )}
    </div>
  );
}

export default CitizenBrowser;
