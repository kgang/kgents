/**
 * Brain Page - Holographic Memory Interface
 *
 * 2D Renaissance (2025-12-18): Three.js visualization mothballed.
 * This page now shows a placeholder until Brain2D is built.
 *
 * Next: Phase 4 of 2D Renaissance builds Brain2D.
 *
 * @see spec/protocols/2d-renaissance.md - Phase 4: Brain2D
 */

import { PathProjection } from '../shell/PathProjection';
import { Brain, GitBranch, Sparkles, BookOpen } from 'lucide-react';
import type { BrainTopologyResponse } from '../api/types';

export default function BrainPage() {
  return (
    <PathProjection<BrainTopologyResponse>
      path="self.memory"
      aspect="topology"
      jewel="brain"
      loadingAction="analyze"
      body={{ similarity_threshold: 0.3 }}
      className="h-screen"
    >
      {(topology) => <Brain2DPlaceholder topology={topology} />}
    </PathProjection>
  );
}

/**
 * Placeholder for Brain2D visualization.
 * Shows real crystal data from AGENTESE in a tree layout.
 *
 * "Memories are not data points—they are living crystallizations of thought."
 */
function Brain2DPlaceholder({ topology }: { topology: BrainTopologyResponse }) {
  const { nodes = [], edges = [] } = topology;

  // Group nodes by category (first segment of label)
  const categories = nodes.reduce(
    (acc, node) => {
      const category = node.label?.split('.')[0] || 'uncategorized';
      if (!acc[category]) acc[category] = [];
      acc[category].push(node);
      return acc;
    },
    {} as Record<string, typeof nodes>
  );

  // Stats
  const totalLinks = edges.length;
  const avgSimilarity =
    edges.length > 0 ? edges.reduce((sum, e) => sum + (e.similarity || 0), 0) / edges.length : 0;

  return (
    <div className="h-full bg-[#1a1a1a] text-white p-6 overflow-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <Brain className="w-8 h-8 text-[#D4A574]" />
        <div>
          <h1 className="text-2xl font-semibold">Brain</h1>
          <p className="text-sm text-gray-400">
            {nodes.length} crystals · {totalLinks} connections · {(avgSimilarity * 100).toFixed(0)}%
            avg similarity
          </p>
        </div>
      </div>

      {/* Coming Soon Banner */}
      <div className="mb-6 p-4 bg-[#D4A574]/20 border border-[#D4A574]/40 rounded-lg">
        <p className="text-[#E8C4A0] text-sm">
          <span className="font-semibold">2D Renaissance:</span> Full Brain2D visualization with
          tree-based cartography coming in Phase 4. This placeholder shows real crystal data.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="mb-6 flex gap-3">
        <button className="flex items-center gap-2 px-4 py-2 bg-[#4A6B4A] hover:bg-[#5A7B5A] rounded-lg text-sm transition-colors">
          <Sparkles className="w-4 h-4" />
          Capture Memory
        </button>
        <button className="flex items-center gap-2 px-4 py-2 bg-[#2a2a2a] hover:bg-[#3a3a3a] rounded-lg text-sm transition-colors">
          <BookOpen className="w-4 h-4" />
          Ghost Surface
        </button>
      </div>

      {/* Crystal Cartography */}
      <h2 className="text-lg font-medium mb-3 flex items-center gap-2">
        <GitBranch className="w-5 h-5 text-gray-400" />
        Crystal Cartography
      </h2>
      <div className="space-y-4">
        {Object.entries(categories)
          .sort((a, b) => b[1].length - a[1].length)
          .map(([category, categoryNodes]) => (
            <div key={category} className="bg-[#2a2a2a] p-4 rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <span className="font-medium text-[#D4A574]">◆ {category}</span>
                <span className="text-sm text-gray-400">{categoryNodes.length} crystals</span>
              </div>
              <div className="space-y-2 pl-4 border-l-2 border-[#3a3a3a]">
                {categoryNodes.slice(0, 5).map((node) => (
                  <div key={node.id} className="flex items-start gap-2 text-sm">
                    <span className="text-gray-500">◇</span>
                    <div>
                      <span className="text-gray-200">{node.label || node.id}</span>
                      {node.content_preview && (
                        <p className="text-gray-500 text-xs mt-0.5 line-clamp-1">
                          {node.content_preview}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
                {categoryNodes.length > 5 && (
                  <span className="text-xs text-gray-500 pl-4">
                    +{categoryNodes.length - 5} more
                  </span>
                )}
              </div>
            </div>
          ))}
      </div>

      {nodes.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <Brain className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>No crystals yet. Start capturing memories!</p>
        </div>
      )}
    </div>
  );
}
