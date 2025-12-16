/**
 * Brain Page - Holographic Memory Interface
 *
 * Provides UI for:
 * - Capturing content to memory
 * - Surfacing ghost memories
 * - Viewing memory topology
 * - Checking brain status
 *
 * Session 6: Crown Jewel Brain Web UI
 */

import { useState, useEffect } from 'react';
import { brainApi } from '../api/client';
import type { BrainStatusResponse, BrainMapResponse, GhostMemory } from '../api/types';

export default function Brain() {
  // State
  const [status, setStatus] = useState<BrainStatusResponse | null>(null);
  const [map, setMap] = useState<BrainMapResponse | null>(null);
  const [captureContent, setCaptureContent] = useState('');
  const [ghostContext, setGhostContext] = useState('');
  const [ghostResults, setGhostResults] = useState<GhostMemory[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Load status and map on mount
  useEffect(() => {
    loadStatus();
    loadMap();
  }, []);

  const loadStatus = async () => {
    try {
      const response = await brainApi.getStatus();
      setStatus(response.data);
    } catch (error) {
      console.error('Failed to load brain status:', error);
    }
  };

  const loadMap = async () => {
    try {
      const response = await brainApi.getMap();
      setMap(response.data);
    } catch (error) {
      console.error('Failed to load brain map:', error);
    }
  };

  const handleCapture = async () => {
    if (!captureContent.trim()) return;

    setLoading(true);
    setMessage(null);

    try {
      const response = await brainApi.capture({ content: captureContent });
      setMessage({
        type: 'success',
        text: `Captured: ${response.data.concept_id}`,
      });
      setCaptureContent('');
      // Refresh map to show new content
      loadMap();
    } catch (error) {
      setMessage({
        type: 'error',
        text: 'Failed to capture content',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleGhostSurface = async () => {
    if (!ghostContext.trim()) return;

    setLoading(true);
    setMessage(null);

    try {
      const response = await brainApi.ghost({
        context: ghostContext,
        limit: 10,
      });
      setGhostResults(response.data.surfaced);
      if (response.data.count === 0) {
        setMessage({
          type: 'success',
          text: 'No memories surfaced for this context',
        });
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: 'Failed to surface memories',
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (s: string) => {
    switch (s) {
      case 'healthy':
        return 'text-green-400';
      case 'degraded':
        return 'text-yellow-400';
      default:
        return 'text-red-400';
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Holographic Brain</h1>
          <p className="text-gray-400">
            Semantic memory with ghost surfacing and holographic compression
          </p>
        </div>

        {/* Status Panel */}
        <div className="bg-gray-800 rounded-lg p-4 mb-6">
          <h2 className="text-lg font-semibold mb-3">Brain Status</h2>
          {status ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-400">Status:</span>
                <span className={`ml-2 ${getStatusColor(status.status)}`}>{status.status}</span>
              </div>
              <div>
                <span className="text-gray-400">Embedder:</span>
                <span className="ml-2">{status.embedder_type}</span>
              </div>
              <div>
                <span className="text-gray-400">Dimension:</span>
                <span className="ml-2">{status.embedder_dimension}</span>
              </div>
              <div>
                <span className="text-gray-400">Concepts:</span>
                <span className="ml-2">{status.concept_count}</span>
              </div>
            </div>
          ) : (
            <p className="text-gray-500">Loading status...</p>
          )}
        </div>

        {/* Topology Panel */}
        <div className="bg-gray-800 rounded-lg p-4 mb-6">
          <h2 className="text-lg font-semibold mb-3">Memory Topology</h2>
          {map ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-400">Concepts:</span>
                <span className="ml-2">{map.concept_count}</span>
              </div>
              <div>
                <span className="text-gray-400">Hot Patterns:</span>
                <span className="ml-2 text-orange-400">{map.hot_patterns}</span>
              </div>
              <div>
                <span className="text-gray-400">Landmarks:</span>
                <span className="ml-2">{map.landmarks}</span>
              </div>
              <div>
                <span className="text-gray-400">Dimension:</span>
                <span className="ml-2">{map.dimension}</span>
              </div>
            </div>
          ) : (
            <p className="text-gray-500">Loading topology...</p>
          )}
        </div>

        {/* Capture Panel */}
        <div className="bg-gray-800 rounded-lg p-4 mb-6">
          <h2 className="text-lg font-semibold mb-3">Capture Content</h2>
          <div className="flex gap-3">
            <textarea
              value={captureContent}
              onChange={(e) => setCaptureContent(e.target.value)}
              placeholder="Enter content to capture to memory..."
              className="flex-1 bg-gray-700 rounded px-3 py-2 text-white placeholder-gray-500 resize-none"
              rows={3}
            />
            <button
              onClick={handleCapture}
              disabled={loading || !captureContent.trim()}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded font-medium transition-colors"
            >
              {loading ? 'Capturing...' : 'Capture'}
            </button>
          </div>
        </div>

        {/* Ghost Surface Panel */}
        <div className="bg-gray-800 rounded-lg p-4 mb-6">
          <h2 className="text-lg font-semibold mb-3">Ghost Surfacing</h2>
          <div className="flex gap-3 mb-4">
            <input
              type="text"
              value={ghostContext}
              onChange={(e) => setGhostContext(e.target.value)}
              placeholder="Enter context to surface related memories..."
              className="flex-1 bg-gray-700 rounded px-3 py-2 text-white placeholder-gray-500"
              onKeyDown={(e) => e.key === 'Enter' && handleGhostSurface()}
            />
            <button
              onClick={handleGhostSurface}
              disabled={loading || !ghostContext.trim()}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 rounded font-medium transition-colors"
            >
              {loading ? 'Surfacing...' : 'Surface'}
            </button>
          </div>

          {/* Ghost Results */}
          {ghostResults.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-sm text-gray-400 mb-2">
                Surfaced Memories ({ghostResults.length})
              </h3>
              {ghostResults.map((memory) => (
                <div
                  key={memory.concept_id}
                  className="bg-gray-700 rounded p-3 border-l-2 border-purple-500"
                >
                  <div className="flex justify-between items-start mb-1">
                    <span className="text-xs text-gray-400 font-mono">{memory.concept_id}</span>
                    <span className="text-xs px-2 py-0.5 bg-purple-900 rounded">
                      {(memory.relevance * 100).toFixed(0)}% relevant
                    </span>
                  </div>
                  <p className="text-sm">
                    {memory.content || <span className="text-gray-500 italic">No content</span>}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Message Toast */}
        {message && (
          <div
            className={`fixed bottom-4 right-4 px-4 py-2 rounded shadow-lg ${
              message.type === 'success' ? 'bg-green-600' : 'bg-red-600'
            }`}
          >
            {message.text}
          </div>
        )}
      </div>
    </div>
  );
}
