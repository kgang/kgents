/**
 * GalleryPage: Projection Component Gallery web interface.
 *
 * Displays all pilots with their projections across CLI, HTML, and JSON targets.
 * Supports category filtering and real-time override controls.
 */

import { useState, useEffect, useMemo, useCallback } from 'react';
import { galleryApi } from '@/api/client';
import type {
  GalleryCategory,
  GalleryOverrides,
  GalleryResponse,
  PilotResponse,
} from '@/api/types';
import { PilotCard, CategoryFilter, OverrideControls } from '@/components/gallery';
import { EmpathyError, PersonalityLoading } from '@/components/joy';

type FilterCategory = GalleryCategory | 'ALL';

export default function GalleryPage() {
  // State
  const [galleryData, setGalleryData] = useState<GalleryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeCategory, setActiveCategory] = useState<FilterCategory>('ALL');
  const [overrides, setOverrides] = useState<GalleryOverrides>({});
  const [selectedPilot, setSelectedPilot] = useState<PilotResponse | null>(null);

  // Fetch gallery data
  const fetchGallery = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await galleryApi.getAll(
        overrides,
        activeCategory !== 'ALL' ? activeCategory : undefined
      );
      setGalleryData(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load gallery');
    } finally {
      setLoading(false);
    }
  }, [overrides, activeCategory]);

  // Initial fetch
  useEffect(() => {
    fetchGallery();
  }, [fetchGallery]);

  // Compute category counts
  const categoryCounts = useMemo((): Partial<Record<GalleryCategory, number>> => {
    if (!galleryData) return {};
    const counts: Partial<Record<GalleryCategory, number>> = {};
    galleryData.pilots.forEach((pilot) => {
      counts[pilot.category] = (counts[pilot.category] || 0) + 1;
    });
    return counts;
  }, [galleryData]);

  // Filter pilots by category
  const filteredPilots = useMemo(() => {
    if (!galleryData) return [];
    if (activeCategory === 'ALL') return galleryData.pilots;
    return galleryData.pilots.filter((p) => p.category === activeCategory);
  }, [galleryData, activeCategory]);

  // Handle override changes with debounce
  const handleOverrideChange = useCallback((newOverrides: GalleryOverrides) => {
    setOverrides(newOverrides);
  }, []);

  // Loading state - Foundation 5: PersonalityLoading (generic)
  if (loading && !galleryData) {
    return (
      <div className="h-[calc(100vh-64px)] flex items-center justify-center bg-town-bg">
        <PersonalityLoading jewel="gestalt" size="lg" action="connect" />
      </div>
    );
  }

  // Error state - Foundation 5: EmpathyError
  if (error && !galleryData) {
    return (
      <div className="h-[calc(100vh-64px)] flex items-center justify-center bg-town-bg">
        <EmpathyError
          type="network"
          title="Gallery Unavailable"
          subtitle={error}
          action="Retry"
          onAction={fetchGallery}
          size="lg"
        />
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col bg-town-bg">
      {/* Header */}
      <div className="bg-town-surface/50 border-b border-town-accent/30 px-4 py-3">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-semibold">Projection Gallery</h1>
            <span className="text-sm text-gray-400">
              {filteredPilots.length} components
            </span>
            {loading && (
              <span className="text-xs text-town-highlight animate-pulse">
                Updating...
              </span>
            )}
          </div>
          <OverrideControls overrides={overrides} onChange={handleOverrideChange} />
        </div>

        {/* Category filter */}
        <CategoryFilter
          categories={(galleryData?.categories || []) as GalleryCategory[]}
          activeCategory={activeCategory}
          onChange={setActiveCategory}
          counts={categoryCounts}
        />
      </div>

      {/* Gallery grid */}
      <div className="flex-1 overflow-auto p-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-4">
          {filteredPilots.map((pilot) => (
            <PilotCard
              key={pilot.name}
              pilot={pilot}
              onClick={() => setSelectedPilot(pilot)}
            />
          ))}
        </div>

        {filteredPilots.length === 0 && (
          <div className="flex items-center justify-center h-64 text-gray-500">
            No pilots in this category
          </div>
        )}
      </div>

      {/* Detail modal */}
      {selectedPilot && (
        <PilotDetailModal
          pilot={selectedPilot}
          onClose={() => setSelectedPilot(null)}
        />
      )}
    </div>
  );
}

// =============================================================================
// Pilot Detail Modal
// =============================================================================

interface PilotDetailModalProps {
  pilot: PilotResponse;
  onClose: () => void;
}

function PilotDetailModal({ pilot, onClose }: PilotDetailModalProps) {
  return (
    <div
      className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-town-surface border border-town-accent/30 rounded-lg max-w-3xl w-full max-h-[80vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal header */}
        <div className="px-4 py-3 border-b border-town-accent/30 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">{pilot.name}</h2>
            <p className="text-sm text-gray-400">{pilot.description}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-xl"
          >
            &times;
          </button>
        </div>

        {/* Modal content */}
        <div className="p-4 overflow-auto max-h-[calc(80vh-120px)]">
          {/* Tags */}
          <div className="flex gap-2 mb-4">
            <span className="text-xs px-2 py-1 rounded bg-town-highlight/30 text-town-highlight">
              {pilot.category}
            </span>
            {pilot.tags.map((tag) => (
              <span
                key={tag}
                className="text-xs px-2 py-1 rounded bg-town-accent/20 text-gray-400"
              >
                {tag}
              </span>
            ))}
          </div>

          {/* Projections in full */}
          <div className="space-y-4">
            {/* CLI */}
            <div>
              <h3 className="text-sm font-medium text-gray-300 mb-2">CLI Projection</h3>
              <pre className="font-mono text-sm bg-gray-900/80 rounded p-3 text-green-400 whitespace-pre-wrap overflow-x-auto">
                {pilot.projections.cli}
              </pre>
            </div>

            {/* HTML */}
            <div>
              <h3 className="text-sm font-medium text-gray-300 mb-2">HTML Projection</h3>
              <div
                className="bg-gray-800/50 rounded p-3 kgents-projection"
                dangerouslySetInnerHTML={{ __html: pilot.projections.html }}
              />
            </div>

            {/* JSON */}
            <div>
              <h3 className="text-sm font-medium text-gray-300 mb-2">JSON Projection</h3>
              <pre className="font-mono text-xs bg-gray-900/80 rounded p-3 text-blue-300 whitespace-pre-wrap overflow-x-auto">
                {JSON.stringify(pilot.projections.json, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
