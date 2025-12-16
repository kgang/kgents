/**
 * Atelier: Main page for Tiny Atelier - the creative workshop demo.
 *
 * Features:
 * - Artisan selection and commissioning
 * - Gallery browsing
 * - Piece detail view with provenance
 * - Lineage visualization
 * - Multi-artisan collaboration
 *
 * Theme: Orisinal.com aesthetic - whimsical, minimal, melancholic but hopeful.
 */

import { useState, useEffect, useCallback } from 'react';
import { atelierApi } from '@/api/atelier';
import type { Artisan, PieceSummary, Piece, LineageResponse } from '@/api/atelier';
import { useAtelierStream } from '@/hooks/useAtelierStream';
import {
  ArtisanGrid,
  CommissionForm,
  StreamingProgress,
  GalleryGrid,
  PieceDetail,
  LineageTree,
  CollaborationBuilder,
  ErrorPanel,
  LoadingPanel,
} from '@/components/atelier';

type View = 'commission' | 'collaborate' | 'gallery' | 'piece' | 'lineage';

export default function Atelier() {
  // Navigation state
  const [view, setView] = useState<View>('gallery');
  const [selectedArtisan, setSelectedArtisan] = useState<string | null>(null);
  const [selectedPieceId, setSelectedPieceId] = useState<string | null>(null);

  // Data state
  const [artisans, setArtisans] = useState<Artisan[]>([]);
  const [pieces, setPieces] = useState<PieceSummary[]>([]);
  const [currentPiece, setCurrentPiece] = useState<Piece | null>(null);
  const [lineage, setLineage] = useState<LineageResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Streaming hook
  const stream = useAtelierStream();

  // Load initial data
  useEffect(() => {
    const load = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const [artisansRes, galleryRes] = await Promise.all([
          atelierApi.getArtisans(),
          atelierApi.getGallery({ limit: 50 }),
        ]);
        setArtisans(artisansRes.data.artisans);
        setPieces(galleryRes.data.pieces);
      } catch (err) {
        setError('Failed to load atelier data');
        console.error('[Atelier] Load error:', err);
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, []);

  // Load piece detail
  const loadPiece = useCallback(async (pieceId: string) => {
    setSelectedPieceId(pieceId);
    setView('piece');
    try {
      const res = await atelierApi.getPiece(pieceId);
      setCurrentPiece(res.data);
    } catch (err) {
      console.error('[Atelier] Failed to load piece:', err);
    }
  }, []);

  // Load lineage
  const loadLineage = useCallback(async (pieceId: string) => {
    setSelectedPieceId(pieceId);
    setView('lineage');
    try {
      const res = await atelierApi.getLineage(pieceId);
      setLineage(res.data);
    } catch (err) {
      console.error('[Atelier] Failed to load lineage:', err);
    }
  }, []);

  // Delete piece
  const deletePiece = useCallback(async () => {
    if (!selectedPieceId) return;
    try {
      await atelierApi.deletePiece(selectedPieceId);
      setPieces((prev) => prev.filter((p) => p.id !== selectedPieceId));
      setCurrentPiece(null);
      setSelectedPieceId(null);
      setView('gallery');
    } catch (err) {
      console.error('[Atelier] Failed to delete piece:', err);
    }
  }, [selectedPieceId]);

  // Commission handler
  const handleCommission = async (request: string) => {
    if (!selectedArtisan) return;
    const piece = await stream.commission(selectedArtisan, request);
    if (piece) {
      // Refresh gallery
      const galleryRes = await atelierApi.getGallery({ limit: 50 });
      setPieces(galleryRes.data.pieces);
    }
  };

  // Collaboration handler
  const handleCollaborate = async (artisanNames: string[], request: string, mode: string) => {
    const piece = await stream.collaborate(artisanNames, request, mode);
    if (piece) {
      const galleryRes = await atelierApi.getGallery({ limit: 50 });
      setPieces(galleryRes.data.pieces);
    }
    return piece;
  };

  // Select artisan for commission
  const selectArtisan = (names: string[]) => {
    if (names.length > 0) {
      setSelectedArtisan(names[0]);
      setView('commission');
      stream.reset();
    }
  };

  // Navigation tabs
  const tabs: Array<{ key: View; label: string }> = [
    { key: 'gallery', label: 'Gallery' },
    { key: 'commission', label: 'Commission' },
    { key: 'collaborate', label: 'Collaborate' },
  ];

  return (
    <div className="min-h-screen bg-stone-50">
      {/* Header */}
      <header className="bg-white border-b border-stone-100">
        <div className="max-w-6xl mx-auto px-6 py-8">
          <h1 className="text-2xl font-serif text-stone-800">Tiny Atelier</h1>
          <p className="mt-1 text-sm text-stone-400">A workshop of creative artisans</p>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-stone-100 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex items-center gap-1">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                onClick={() => {
                  setView(tab.key);
                  if (tab.key !== 'commission') {
                    setSelectedArtisan(null);
                  }
                }}
                className={`
                  px-4 py-3 text-sm font-medium transition-colors
                  border-b-2 -mb-px
                  ${
                    view === tab.key ||
                    (view === 'piece' && tab.key === 'gallery') ||
                    (view === 'lineage' && tab.key === 'gallery')
                      ? 'border-amber-400 text-amber-700'
                      : 'border-transparent text-stone-500 hover:text-stone-700'
                  }
                `}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        {/* Global Error State */}
        {error && (
          <ErrorPanel
            title="Unable to load workshop"
            message={error}
            onRetry={() => {
              setError(null);
              setIsLoading(true);
              Promise.all([atelierApi.getArtisans(), atelierApi.getGallery({ limit: 50 })])
                .then(([artisansRes, galleryRes]) => {
                  setArtisans(artisansRes.data.artisans);
                  setPieces(galleryRes.data.pieces);
                })
                .catch((err) => {
                  setError('Failed to load atelier data');
                  console.error('[Atelier] Retry error:', err);
                })
                .finally(() => setIsLoading(false));
            }}
          />
        )}

        {/* Global Loading State */}
        {isLoading && !error && <LoadingPanel message="Preparing the workshop..." />}

        {/* Gallery View */}
        {!isLoading && !error && view === 'gallery' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium text-stone-700">Gallery</h2>
              <span className="text-sm text-stone-400">
                {pieces.length} {pieces.length === 1 ? 'piece' : 'pieces'}
              </span>
            </div>
            <GalleryGrid pieces={pieces} isLoading={isLoading} onPieceClick={loadPiece} />
          </div>
        )}

        {/* Commission View */}
        {!isLoading && !error && view === 'commission' && (
          <div className="space-y-8">
            {/* Artisan Selection */}
            {!selectedArtisan && (
              <div className="space-y-4">
                <h2 className="text-lg font-medium text-stone-700">Choose an Artisan</h2>
                <ArtisanGrid onSelect={selectArtisan} />
              </div>
            )}

            {/* Commission Form */}
            {selectedArtisan && (
              <div className="max-w-xl mx-auto space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-medium text-stone-700">
                      Commission {selectedArtisan}
                    </h2>
                    <p className="text-sm text-stone-400">
                      {artisans.find((a) => a.name === selectedArtisan)?.specialty}
                    </p>
                  </div>
                  <button
                    onClick={() => setSelectedArtisan(null)}
                    className="text-sm text-stone-400 hover:text-stone-600"
                  >
                    Choose another
                  </button>
                </div>

                {/* Form or Progress */}
                {!stream.isStreaming && stream.status === 'idle' && (
                  <CommissionForm onSubmit={(data) => handleCommission(data.request)} />
                )}

                {/* Streaming Progress */}
                {(stream.isStreaming || stream.status !== 'idle') && (
                  <div className="space-y-6">
                    <StreamingProgress
                      status={stream.status}
                      progress={stream.progress}
                      currentFragment={stream.currentFragment}
                      error={stream.error}
                      events={stream.events}
                      showEvents={true}
                    />

                    {/* Completed Piece Preview */}
                    {stream.piece && (
                      <div className="p-6 rounded-lg bg-white border border-stone-200 shadow-sm">
                        <p className="text-stone-700 whitespace-pre-wrap">
                          {typeof stream.piece.content === 'string'
                            ? stream.piece.content
                            : JSON.stringify(stream.piece.content, null, 2)}
                        </p>
                        <div className="mt-4 flex items-center justify-between">
                          <button
                            onClick={() => loadPiece(stream.piece!.id)}
                            className="text-sm text-amber-600 hover:text-amber-700"
                          >
                            View in gallery
                          </button>
                          <button
                            onClick={() => stream.reset()}
                            className="text-sm text-stone-400 hover:text-stone-600"
                          >
                            Commission another
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Collaborate View */}
        {!isLoading && !error && view === 'collaborate' && (
          <div className="max-w-xl mx-auto space-y-6">
            <h2 className="text-lg font-medium text-stone-700">Collaboration</h2>

            {!stream.isStreaming && stream.status === 'idle' && (
              <CollaborationBuilder
                artisans={artisans}
                onCollaborate={handleCollaborate}
                isLoading={stream.isStreaming}
              />
            )}

            {/* Streaming Progress */}
            {(stream.isStreaming || stream.status !== 'idle') && (
              <div className="space-y-6">
                <StreamingProgress
                  status={stream.status}
                  progress={stream.progress}
                  currentFragment={stream.currentFragment}
                  error={stream.error}
                  events={stream.events}
                  showEvents={true}
                />

                {stream.piece && (
                  <div className="p-6 rounded-lg bg-white border border-stone-200 shadow-sm">
                    <p className="text-stone-700 whitespace-pre-wrap">
                      {typeof stream.piece.content === 'string'
                        ? stream.piece.content
                        : JSON.stringify(stream.piece.content, null, 2)}
                    </p>
                    <div className="mt-4 flex items-center justify-between">
                      <button
                        onClick={() => loadPiece(stream.piece!.id)}
                        className="text-sm text-amber-600 hover:text-amber-700"
                      >
                        View in gallery
                      </button>
                      <button
                        onClick={() => stream.reset()}
                        className="text-sm text-stone-400 hover:text-stone-600"
                      >
                        Start new collaboration
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Piece Detail View */}
        {!isLoading && !error && view === 'piece' && currentPiece && (
          <div className="max-w-2xl mx-auto">
            <button
              onClick={() => setView('gallery')}
              className="mb-6 text-sm text-stone-400 hover:text-stone-600 flex items-center gap-1"
            >
              <span>&larr;</span> Back to gallery
            </button>
            <div className="bg-white rounded-lg border border-stone-200 p-6">
              <PieceDetail piece={currentPiece} onDelete={deletePiece} onInspiration={loadPiece} />
              <div className="mt-4 pt-4 border-t border-stone-100">
                <button
                  onClick={() => loadLineage(currentPiece.id)}
                  className="text-sm text-amber-600 hover:text-amber-700"
                >
                  View lineage
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Lineage View */}
        {!isLoading && !error && view === 'lineage' && lineage && (
          <div className="max-w-2xl mx-auto">
            <button
              onClick={() => {
                if (selectedPieceId && currentPiece?.id === selectedPieceId) {
                  setView('piece');
                } else {
                  setView('gallery');
                }
              }}
              className="mb-6 text-sm text-stone-400 hover:text-stone-600 flex items-center gap-1"
            >
              <span>&larr;</span> Back
            </button>
            <div className="bg-white rounded-lg border border-stone-200 p-6">
              <h2 className="text-lg font-medium text-stone-700 mb-4">Inspiration Lineage</h2>
              <LineageTree lineage={lineage} onNodeClick={loadPiece} />
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-stone-100 bg-white mt-16">
        <div className="max-w-6xl mx-auto px-6 py-8 text-center">
          <p className="text-xs text-stone-300">Tiny Atelier &middot; A kgents demo</p>
        </div>
      </footer>
    </div>
  );
}
