import { useEffect, useRef, useState } from 'react';
import { useWorkshopStore } from '@/stores/workshopStore';
import { useUIStore } from '@/stores/uiStore';
import { workshopApi } from '@/api/client';
import { WorkshopMesa } from '@/components/workshop/WorkshopMesa';
import { BuilderPanel } from '@/components/workshop/BuilderPanel';
import { TaskProgress } from '@/components/workshop/TaskProgress';
import { ArtifactFeed } from '@/components/workshop/ArtifactFeed';
import { useWorkshopStream } from '@/hooks/useWorkshopStream';
import type { WorkshopPhase } from '@/api/types';

type LoadingState = 'loading' | 'loaded' | 'error';

export default function Workshop() {
  const {
    workshopId: _workshopId, // Reserved for workshop routing
    setWorkshopId,
    builders,
    setBuilders,
    currentPhase,
    activeTask,
    setActiveTask,
    events,
    artifacts,
    isRunning,
    setRunning,
    speed,
    setSpeed,
    metrics: _metrics, // Reserved for metrics display
    selectedBuilder,
    selectBuilder,
  } = useWorkshopStore();
  const { isEventFeedOpen, toggleEventFeed } = useUIStore();
  const mesaContainerRef = useRef<HTMLDivElement>(null);
  const [mesaSize, setMesaSize] = useState({ width: 800, height: 600 });
  const [loadingState, setLoadingState] = useState<LoadingState>('loading');
  const [error, setError] = useState<string | null>(null);
  const [taskInput, setTaskInput] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Connect SSE stream when running
  useWorkshopStream({ speed, autoConnect: true });

  // Load workshop data on mount
  useEffect(() => {
    const loadWorkshop = async () => {
      setLoadingState('loading');
      setError(null);
      try {
        console.log('[Workshop] Loading workshop...');
        const response = await workshopApi.get();
        console.log('[Workshop] Loaded:', response.data);
        setWorkshopId(response.data.id);
        setBuilders(response.data.builders);
        if (response.data.active_task) {
          setActiveTask(response.data.active_task);
        }
        setRunning(response.data.is_running);
        setLoadingState('loaded');
      } catch (err: unknown) {
        console.error('[Workshop] Failed to load:', err);
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        setError(axiosErr.response?.data?.detail || 'Failed to load workshop');
        setLoadingState('error');
      }
    };

    loadWorkshop();
  }, [setWorkshopId, setBuilders, setActiveTask, setRunning]);

  // Track mesa container size
  useEffect(() => {
    const container = mesaContainerRef.current;
    if (!container) return;

    const observer = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (entry) {
        setMesaSize({
          width: entry.contentRect.width,
          height: entry.contentRect.height,
        });
      }
    });

    observer.observe(container);
    return () => observer.disconnect();
  }, []);

  // Handle task submission
  const handleSubmitTask = async () => {
    if (!taskInput.trim() || isSubmitting) return;

    setIsSubmitting(true);
    try {
      const response = await workshopApi.assignTask(taskInput.trim());
      console.log('[Workshop] Task assigned:', response.data);
      setActiveTask(response.data.task);
      setRunning(true);
      setTaskInput('');
    } catch (err: unknown) {
      console.error('[Workshop] Failed to assign task:', err);
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      setError(axiosErr.response?.data?.detail || 'Failed to assign task');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle reset
  const handleReset = async () => {
    try {
      await workshopApi.reset();
      setActiveTask(null);
      setRunning(false);
      // Reload workshop
      const response = await workshopApi.get();
      setBuilders(response.data.builders);
    } catch (err) {
      console.error('[Workshop] Failed to reset:', err);
    }
  };

  // Loading state
  if (loadingState === 'loading') {
    return (
      <div className="h-[calc(100vh-64px)] flex items-center justify-center bg-town-bg">
        <div className="text-center">
          <div className="animate-pulse text-6xl mb-4">🔧</div>
          <p className="text-gray-400 text-lg">Loading workshop...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (loadingState === 'error') {
    return (
      <div className="h-[calc(100vh-64px)] flex items-center justify-center bg-town-bg">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold mb-2 text-red-400">Workshop Error</h2>
          <p className="text-gray-400 mb-6">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2 bg-town-highlight hover:bg-town-highlight/80 rounded-lg font-medium transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col">
      {/* Workshop Header */}
      <div className="bg-town-surface/50 border-b border-town-accent/30 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="font-semibold">🔧 Workshop</h1>
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <span className={`font-medium ${getPhaseColor(currentPhase)}`}>{currentPhase}</span>
            <span>•</span>
            <span>{builders.length} builders</span>
            {activeTask && (
              <>
                <span>•</span>
                <span className="text-white truncate max-w-[200px]">{activeTask.description}</span>
              </>
            )}
          </div>
        </div>
        <div className="flex items-center gap-4">
          {/* Speed Control */}
          <select
            value={speed}
            onChange={(e) => setSpeed(parseFloat(e.target.value))}
            className="bg-town-surface border border-town-accent/30 rounded px-2 py-1 text-sm"
          >
            <option value="0.5">0.5x</option>
            <option value="1">1x</option>
            <option value="2">2x</option>
            <option value="4">4x</option>
          </select>
          {/* Reset Button */}
          {(isRunning || activeTask) && (
            <button
              onClick={handleReset}
              className="px-3 py-1 bg-red-600/30 text-red-300 rounded text-sm hover:bg-red-600/50 transition-colors"
            >
              Reset
            </button>
          )}
        </div>
      </div>

      {/* Task Input (when idle) */}
      {!activeTask && !isRunning && (
        <div className="bg-town-surface/30 border-b border-town-accent/30 px-4 py-3">
          <div className="flex gap-3 max-w-2xl mx-auto">
            <input
              type="text"
              value={taskInput}
              onChange={(e) => setTaskInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSubmitTask()}
              placeholder="Describe a task for the workshop..."
              className="flex-1 bg-town-surface border border-town-accent/30 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-town-highlight"
            />
            <button
              onClick={handleSubmitTask}
              disabled={!taskInput.trim() || isSubmitting}
              className="px-6 py-2 bg-town-highlight hover:bg-town-highlight/80 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg font-medium transition-colors"
            >
              {isSubmitting ? 'Assigning...' : 'Assign Task'}
            </button>
          </div>
        </div>
      )}

      {/* Task Progress Bar */}
      {activeTask && <TaskProgress />}

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Mesa (Main Canvas) */}
        <div className="flex-1 relative" ref={mesaContainerRef}>
          <div className="absolute inset-0 bg-town-bg">
            <WorkshopMesa
              width={mesaSize.width}
              height={mesaSize.height}
              builders={builders}
              selectedBuilder={selectedBuilder}
              onSelectBuilder={selectBuilder}
              currentPhase={currentPhase}
            />
          </div>
        </div>

        {/* Right Sidebar */}
        <div className="w-80 border-l border-town-accent/30 flex flex-col bg-town-surface/30">
          {/* Builder Panel */}
          <div className="flex-1 overflow-y-auto">
            <BuilderPanel />
          </div>

          {/* Artifact Feed */}
          <div
            className={`border-t border-town-accent/30 transition-all ${
              isEventFeedOpen ? 'h-64' : 'h-10'
            }`}
          >
            <button
              onClick={toggleEventFeed}
              className="w-full px-4 py-2 flex items-center justify-between text-sm font-semibold hover:bg-town-surface/50"
            >
              <span>
                Artifacts ({artifacts.length}) / Events ({events.length})
              </span>
              <span>{isEventFeedOpen ? '▼' : '▲'}</span>
            </button>
            {isEventFeedOpen && <ArtifactFeed />}
          </div>
        </div>
      </div>
    </div>
  );
}

function getPhaseColor(phase: WorkshopPhase): string {
  switch (phase) {
    case 'EXPLORING':
      return 'text-green-400';
    case 'DESIGNING':
      return 'text-purple-400';
    case 'PROTOTYPING':
      return 'text-amber-400';
    case 'REFINING':
      return 'text-blue-400';
    case 'INTEGRATING':
      return 'text-pink-400';
    case 'COMPLETE':
      return 'text-emerald-400';
    default:
      return 'text-gray-400';
  }
}
