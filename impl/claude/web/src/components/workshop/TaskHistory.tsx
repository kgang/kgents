/**
 * TaskHistory: List of completed tasks with pagination (Chunk 9).
 *
 * Shows completed and interrupted tasks with quick stats,
 * builder sequence visualization, and replay button.
 */

import { useEffect, useState } from 'react';
import { useWorkshopStore } from '@/stores/workshopStore';
import { workshopApi } from '@/api/client';
import { BUILDER_COLORS, BUILDER_ICONS, type BuilderArchetype, type TaskHistoryItem } from '@/api/types';

interface TaskHistoryProps {
  pageSize?: number;
  onSelectTask?: (taskId: string) => void;
  onReplayTask?: (taskId: string) => void;
}

type StatusFilter = 'all' | 'completed' | 'interrupted';

export function TaskHistory({
  pageSize = 10,
  onSelectTask,
  onReplayTask,
}: TaskHistoryProps) {
  const {
    taskHistory,
    historyPage,
    historyTotal,
    historyTotalPages,
    setTaskHistory,
  } = useWorkshopStore();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  // Load history
  useEffect(() => {
    const loadHistory = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await workshopApi.getHistory(
          currentPage,
          pageSize,
          statusFilter === 'all' ? undefined : statusFilter
        );
        setTaskHistory(
          response.data.tasks,
          response.data.total,
          response.data.page,
          response.data.total_pages
        );
      } catch (err: unknown) {
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        setError(axiosErr.response?.data?.detail || 'Failed to load history');
      } finally {
        setLoading(false);
      }
    };

    loadHistory();
  }, [currentPage, pageSize, statusFilter, setTaskHistory]);

  // Filter by search query (client-side)
  const filteredTasks = searchQuery
    ? taskHistory.filter((task) =>
        task.description.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : taskHistory;

  if (loading && taskHistory.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-pulse text-4xl mb-2">📜</div>
          <p className="text-gray-400">Loading history...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-4xl mb-2">⚠️</div>
          <p className="text-red-400">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Task History</h2>
        <div className="flex items-center gap-2">
          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value as StatusFilter);
              setCurrentPage(1);
            }}
            className="bg-town-surface border border-town-accent/30 rounded px-2 py-1 text-sm"
          >
            <option value="all">All</option>
            <option value="completed">Completed</option>
            <option value="interrupted">Interrupted</option>
          </select>
          {/* Search */}
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search..."
            className="bg-town-surface border border-town-accent/30 rounded px-2 py-1 text-sm w-40"
          />
        </div>
      </div>

      {/* Task List */}
      {filteredTasks.length === 0 ? (
        <div className="text-center py-8 text-gray-400">
          {searchQuery ? 'No matching tasks' : 'No tasks yet'}
        </div>
      ) : (
        <div className="space-y-2">
          {filteredTasks.map((task) => (
            <TaskHistoryCard
              key={task.id}
              task={task}
              onSelect={() => onSelectTask?.(task.id)}
              onReplay={() => onReplayTask?.(task.id)}
            />
          ))}
        </div>
      )}

      {/* Pagination */}
      {historyTotalPages > 1 && (
        <div className="flex items-center justify-between pt-4 border-t border-town-accent/20">
          <div className="text-sm text-gray-400">
            Showing {(historyPage - 1) * pageSize + 1}-
            {Math.min(historyPage * pageSize, historyTotal)} of {historyTotal}
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="px-2 py-1 text-sm bg-town-surface rounded disabled:opacity-50"
            >
              ◀
            </button>
            {Array.from({ length: Math.min(5, historyTotalPages) }, (_, i) => {
              const page = i + 1;
              return (
                <button
                  key={page}
                  onClick={() => setCurrentPage(page)}
                  className={`px-2 py-1 text-sm rounded ${
                    currentPage === page
                      ? 'bg-town-highlight text-white'
                      : 'bg-town-surface text-gray-400'
                  }`}
                >
                  {page}
                </button>
              );
            })}
            <button
              onClick={() => setCurrentPage((p) => Math.min(historyTotalPages, p + 1))}
              disabled={currentPage === historyTotalPages}
              className="px-2 py-1 text-sm bg-town-surface rounded disabled:opacity-50"
            >
              ▶
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Sub-Components
// =============================================================================

interface TaskHistoryCardProps {
  task: TaskHistoryItem;
  onSelect?: () => void;
  onReplay?: () => void;
}

function TaskHistoryCard({ task, onSelect, onReplay }: TaskHistoryCardProps) {
  const statusIcon = task.status === 'completed' ? '✓' : '⚠';
  const statusColor = task.status === 'completed' ? 'text-green-400' : 'text-amber-400';
  const createdAt = new Date(task.created_at);
  const dateStr = createdAt.toLocaleDateString();
  const timeStr = createdAt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return (
    <div className="bg-town-surface/30 rounded-lg p-3 border border-town-accent/20 hover:border-town-accent/40 transition-colors">
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className={statusColor}>{statusIcon}</span>
          <span className="font-medium truncate max-w-[300px]">{task.description}</span>
        </div>
        <div className="text-xs text-gray-400 whitespace-nowrap">
          {dateStr}, {timeStr}
        </div>
      </div>

      {/* Builder Sequence */}
      <div className="flex items-center gap-1 mt-2">
        {task.builder_sequence.map((builder, idx) => {
          const archetype = builder as BuilderArchetype;
          const icon = BUILDER_ICONS[archetype] || '?';
          const color = BUILDER_COLORS[archetype] || '#666';
          const isLast = idx === task.builder_sequence.length - 1;

          return (
            <div key={idx} className="flex items-center">
              <div
                className="w-6 h-6 rounded-full flex items-center justify-center text-xs"
                style={{ backgroundColor: color + '30' }}
                title={builder}
              >
                {icon}
              </div>
              {!isLast && <span className="text-gray-500 mx-1">→</span>}
            </div>
          );
        })}
        {task.status === 'interrupted' && (
          <span className="text-amber-400 ml-1">[INTERRUPTED]</span>
        )}
      </div>

      {/* Stats */}
      <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
        <span>Artifacts: {task.artifacts_count}</span>
        <span>Tokens: {task.tokens_used.toLocaleString()}</span>
        <span>Handoffs: {task.handoffs}</span>
        <span>Duration: {task.duration_seconds.toFixed(1)}s</span>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 mt-3">
        <button
          onClick={onSelect}
          className="px-3 py-1 text-xs bg-town-surface hover:bg-town-accent/30 rounded transition-colors"
        >
          View Details
        </button>
        <button
          onClick={onReplay}
          className="px-3 py-1 text-xs bg-town-highlight/30 hover:bg-town-highlight/50 rounded transition-colors"
        >
          {task.status === 'interrupted' ? 'Resume' : 'Replay'}
        </button>
      </div>
    </div>
  );
}

export default TaskHistory;
