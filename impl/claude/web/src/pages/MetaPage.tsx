/**
 * MetaPage — Journey 5: Watching Yourself Grow
 *
 * Displays coherence timeline showing epistemic evolution over time.
 *
 * Features:
 * - Line graph of coherence score over time
 * - Breakthrough badges (🏆) at significant jumps
 * - Layer distribution pie chart
 * - "Tell my story" narrative export
 *
 * Philosophy:
 *   "The journey IS the garden. Growth is witnessable."
 *
 * See: plans/zero-seed-creative-strategy.md (Journey 5)
 */

import { useEffect, useState } from 'react';
import { CoherenceTimeline } from '../primitives/Meta/CoherenceTimeline';
import type { CoherencePoint } from '../primitives/Meta/CoherenceTimeline';

interface TimelineData {
  points: Array<{
    timestamp: string;
    score: number;
    commit_id?: string;
    layer_distribution: Record<number, number>;
    total_nodes: number;
    total_edges: number;
    breakthrough: boolean;
  }>;
  breakthroughs: Array<{
    timestamp: string;
    old_score: number;
    new_score: number;
    delta: number;
    commit_id?: string;
    description: string;
  }>;
  current_score: number;
  average_score: number;
  layer_distribution: Record<number, number>;
  total_nodes: number;
  total_edges: number;
  start_date?: string;
  end_date?: string;
}

interface StoryData {
  story: string;
  timeline: TimelineData;
}

export function MetaPage() {
  const [timeline, setTimeline] = useState<CoherencePoint[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [story, setStory] = useState<string | null>(null);
  const [generatingStory, setGeneratingStory] = useState(false);

  // Fetch timeline data
  useEffect(() => {
    const fetchTimeline = async () => {
      try {
        const response = await fetch('/api/meta/timeline');
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data: TimelineData = await response.json();

        // Convert to CoherencePoint format
        const points: CoherencePoint[] = data.points.map((p) => ({
          timestamp: new Date(p.timestamp),
          score: p.score,
          commitId: p.commit_id,
          breakthrough: p.breakthrough,
          layerDistribution: p.layer_distribution,
        }));

        setTimeline(points);
        setLoading(false);
      } catch (err) {
        console.error('Failed to fetch timeline:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
        setLoading(false);
      }
    };

    fetchTimeline();
  }, []);

  // Generate story
  const handleTellStory = async () => {
    setGeneratingStory(true);
    try {
      const response = await fetch('/api/meta/story', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data: StoryData = await response.json();
      setStory(data.story);
    } catch (err) {
      console.error('Failed to generate story:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setGeneratingStory(false);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-surface-canvas flex items-center justify-center">
        <div className="text-center">
          <div className="animate-pulse text-text-secondary mb-4">Loading timeline...</div>
          <div className="text-sm text-text-tertiary">Calculating coherence...</div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-surface-canvas flex items-center justify-center">
        <div className="text-center">
          <div className="text-xl text-red-400 mb-4">Timeline Error</div>
          <div className="text-sm text-text-secondary max-w-md">{error}</div>
          <button
            onClick={() => window.location.reload()}
            className="mt-6 px-4 py-2 bg-surface-overlay hover:bg-surface-3 rounded transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Empty state
  if (!timeline || timeline.length === 0) {
    return (
      <div className="min-h-screen bg-surface-canvas flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-2xl text-text-primary mb-4">Your Journey Awaits</div>
          <div className="text-text-secondary mb-6">
            No coherence data yet. Create your first K-Block to begin tracking your epistemic
            evolution.
          </div>
          <a
            href="/world.document"
            className="inline-block px-6 py-3 bg-color-life-sage hover:bg-color-life-moss text-surface-0 rounded-lg transition-colors"
          >
            Start Creating
          </a>
        </div>
      </div>
    );
  }

  // Main content
  return (
    <div className="min-h-screen bg-surface-canvas">
      {/* Header */}
      <div className="border-b border-surface-3 bg-surface-0">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <h1 className="text-3xl font-bold text-text-primary mb-2">
            Journey 5: Watching Yourself Grow
          </h1>
          <p className="text-text-secondary">
            Your epistemic evolution over time. Coherence score, breakthroughs, and layer
            distribution.
          </p>
        </div>
      </div>

      {/* Timeline */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <CoherenceTimeline points={timeline} width={1200} height={500} />
      </div>

      {/* Story Section */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="bg-surface-0 border border-surface-3 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-text-primary">Your Story</h2>
            <button
              onClick={handleTellStory}
              disabled={generatingStory}
              className="px-4 py-2 bg-color-life-sage hover:bg-color-life-moss text-surface-0 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {generatingStory ? 'Generating...' : 'Tell My Story'}
            </button>
          </div>

          {story ? (
            <div className="prose prose-invert max-w-none">
              <div className="whitespace-pre-wrap text-text-secondary leading-relaxed">
                {story}
              </div>
            </div>
          ) : (
            <div className="text-text-tertiary text-center py-8">
              Click "Tell My Story" to generate a narrative summary of your coherence journey.
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="text-center text-text-tertiary text-sm">
          <p>"The proof IS the decision. The mark IS the witness. The journey IS the garden."</p>
        </div>
      </div>
    </div>
  );
}
