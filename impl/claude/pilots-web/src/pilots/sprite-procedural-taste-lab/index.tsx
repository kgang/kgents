/**
 * Sprite Procedural Taste Lab
 *
 * "Every character has a story. The pixels are just how you hear it."
 *
 * This pilot is an animation studio for creating characters with soul.
 * Users describe a character's backstory, and the system proposes
 * visual designs—body shape, colors, animations—that reflect the narrative.
 *
 * Laws Implemented:
 * - L1: Visual-First Law - Sprites always visible, never just described
 * - L2: Backstory-Trace Law - Every visual traces to backstory
 * - L3: Animation-Personality Law - Idle animations reflect emotional state
 * - L4: Proposal-Rationale Law - System explains WHY each choice
 * - L5: Iteration-Memory Law - Previous iterations preserved
 * - L6: Quality-Gate Law - Flag generic/incoherent designs
 *
 * Flavor Laws (foxes, kittens, seals):
 * - L-FLAV-1: All characters include fox, kitten, or seal elements
 * - L-FLAV-2: Backstories incorporate animal traits
 * - L-FLAV-3: Animations reflect species movement patterns
 * - L-FLAV-4: Colors from natural animal palettes
 *
 * QAs Addressed:
 * - QA-1: Collaborating with an artist, not filling out a form
 * - QA-2: Surprising-but-fitting details
 * - QA-3: Dramatic difference between first and final iteration
 * - QA-4: Idle animation makes you want to know more
 * - QA-5: System rationale makes you say "oh, that's clever"
 *
 * @see pilots/sprite-procedural-taste-lab/PROTO_SPEC.md
 */

import { useState, useCallback, useMemo } from 'react';
import type {
  Sprite,
  StyleTrace,
  StyleCrystal,
  Mutation,
} from '@kgents/shared-primitives';
import {
  emitCrystalMark,
  DEMO_SPRITES,
  DEMO_TRACE,
} from './api';
import {
  SpriteCanvas,
  CharacterProposer,
  TasteGravityField,
  BranchExplorer,
  StyleCrystalView,
  SpriteGallery,
} from './components';

// =============================================================================
// Types
// =============================================================================

type ViewMode = 'gallery' | 'explorer' | 'crystal';

// =============================================================================
// Main Component
// =============================================================================

export function SpriteTasteLab() {
  // Core state
  const [sprites, setSprites] = useState<Sprite[]>(DEMO_SPRITES);
  const [trace, setTrace] = useState<StyleTrace>(DEMO_TRACE);
  const [selectedSprite, setSelectedSprite] = useState<Sprite | null>(
    DEMO_SPRITES[0] || null
  );

  // UI state
  const [viewMode, setViewMode] = useState<ViewMode>('gallery');
  const [showProposer, setShowProposer] = useState(false);
  const [activeBranchId, setActiveBranchId] = useState<string>(
    trace.branches[0]?.id || ''
  );
  const [showCrystal, setShowCrystal] = useState(false);
  const [latestCrystal, setLatestCrystal] = useState<StyleCrystal | null>(null);

  // Handle new character accepted
  const handleCharacterAccepted = useCallback(
    (sprite: Sprite, rationale: string) => {
      // Add to sprites list
      setSprites((prev) => [...prev, sprite]);

      // Update trace with creation mutation
      setTrace((prev) => {
        const canonicalBranch = prev.branches.find(
          (b) => b.status === 'canonical'
        );
        if (!canonicalBranch) return prev;

        const newMutation: Mutation = {
          id: `mut-${Date.now()}`,
          timestamp: new Date().toISOString(),
          change_description: `Created character: ${sprite.name}`,
          aesthetic_weights: sprite.weights,
          rationale: {
            reason: rationale.slice(0, 100),
            affected_dimensions: sprite.weights.map((w) => w.dimension),
          },
          galois_loss: 0.1, // New characters have low loss
          status: 'accepted',
        };

        return {
          ...prev,
          branches: prev.branches.map((b) =>
            b.id === canonicalBranch.id
              ? { ...b, mutations: [...b.mutations, newMutation] }
              : b
          ),
          updated_at: new Date().toISOString(),
        };
      });

      // Select the new sprite
      setSelectedSprite(sprite);

      // Close proposer
      setShowProposer(false);
    },
    []
  );

  // Handle mutation selection from branch explorer
  const handleMutationSelected = useCallback((mutation: Mutation) => {
    // Could show mutation details in a panel
    console.log('Selected mutation:', mutation.id);
  }, []);

  // Handle crystallization
  const handleCrystallize = useCallback(async () => {
    // Create crystal from current trace
    const crystal: StyleCrystal = {
      id: `crystal-${Date.now()}`,
      created_at: new Date().toISOString(),
      journey_summary: `Evolved through ${trace.branches[0]?.mutations.length || 0} accepted mutations. Key changes: ${trace.branches[0]?.mutations
        .slice(-3)
        .map((m) => m.change_description)
        .join(', ')}`,
      stability_justification: `The style has settled into a stable pattern with ${Math.round(trace.attractor.stability * 100)}% coherence. Recent mutations reinforce rather than diverge.`,
      final_weights: trace.attractor.canonical_weights,
      mutations_explored: trace.branches.reduce(
        (sum, b) => sum + b.mutations.length,
        0
      ),
      mutations_accepted: trace.branches.reduce(
        (sum, b) => sum + b.mutations.filter((m) => m.status === 'accepted').length,
        0
      ),
      branches_explored: trace.branches.length,
      wild_branches: trace.branches.filter((b) => b.is_wild).length,
      final_loss:
        1 - trace.attractor.stability > 0 ? 1 - trace.attractor.stability : 0.05,
      key_decisions: trace.branches[0]?.mutations
        .slice(-3)
        .map((m) => m.rationale?.reason || m.change_description) || [],
    };

    // Emit witness mark (real API)
    try {
      await emitCrystalMark(crystal);
    } catch (error) {
      console.error('Failed to emit crystal mark:', error);
      // Continue anyway
    }

    // Update trace with crystal
    setTrace((prev) => ({
      ...prev,
      crystals: [...prev.crystals, crystal],
    }));

    // Show crystal
    setLatestCrystal(crystal);
    setShowCrystal(true);
  }, [trace]);

  // Handle sprite export
  const handleExportSprite = useCallback((sprite: Sprite) => {
    // Create canvas and draw sprite
    const canvas = document.createElement('canvas');
    canvas.width = sprite.width * 8; // Scale up for export
    canvas.height = sprite.height * 8;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.imageSmoothingEnabled = false;

    for (let y = 0; y < sprite.height; y++) {
      for (let x = 0; x < sprite.width; x++) {
        const pixelIndex = y * sprite.width + x;
        const colorIndex = sprite.pixels[pixelIndex];

        if (colorIndex >= 0 && colorIndex < sprite.palette.length) {
          ctx.fillStyle = sprite.palette[colorIndex];
          ctx.fillRect(x * 8, y * 8, 8, 8);
        }
      }
    }

    // Download as PNG
    const link = document.createElement('a');
    link.download = `${sprite.name.replace(/\s+/g, '-').toLowerCase()}.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
  }, []);

  // Compute stats for header
  const stats = useMemo(() => {
    const foxCount = sprites.filter((s) => s.id.includes('fox')).length;
    const kittenCount = sprites.filter((s) => s.id.includes('kitten')).length;
    const sealCount = sprites.filter((s) => s.id.includes('seal')).length;
    const totalMutations = trace.branches.reduce(
      (sum, b) => sum + b.mutations.length,
      0
    );
    return { foxCount, kittenCount, sealCount, totalMutations };
  }, [sprites, trace]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-900/80 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-3xl">🎨</span>
              <div>
                <h1 className="text-xl font-bold text-amber-300">
                  Sprite Taste Lab
                </h1>
                <p className="text-slate-400 text-sm">
                  Every character has a story. The pixels are how you hear it.
                </p>
              </div>
            </div>

            {/* Stats */}
            <div className="hidden md:flex items-center gap-4 text-sm">
              <span className="flex items-center gap-1">
                <span>🦊</span>
                <span className="text-slate-400">{stats.foxCount}</span>
              </span>
              <span className="flex items-center gap-1">
                <span>🐱</span>
                <span className="text-slate-400">{stats.kittenCount}</span>
              </span>
              <span className="flex items-center gap-1">
                <span>🦭</span>
                <span className="text-slate-400">{stats.sealCount}</span>
              </span>
              <span className="text-slate-600">|</span>
              <span className="text-slate-400">
                {stats.totalMutations} mutations
              </span>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowProposer(true)}
                className="bg-amber-500 hover:bg-amber-400 text-slate-900 px-4 py-2 rounded-lg font-medium transition-colors"
              >
                ✨ New Character
              </button>
            </div>
          </div>

          {/* View tabs */}
          <div className="flex gap-1 mt-4 -mb-px">
            {(['gallery', 'explorer', 'crystal'] as ViewMode[]).map((mode) => (
              <button
                key={mode}
                onClick={() => setViewMode(mode)}
                className={`px-4 py-2 text-sm rounded-t-lg transition-colors ${
                  viewMode === mode
                    ? 'bg-slate-800 text-amber-300 border-b-2 border-amber-400'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {mode === 'gallery' && '🎨 Gallery'}
                {mode === 'explorer' && '🌳 Branches'}
                {mode === 'crystal' && '💎 Crystals'}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Left column: Main view */}
          <div className="lg:col-span-2 space-y-6">
            {viewMode === 'gallery' && (
              <SpriteGallery
                sprites={sprites}
                selectedSpriteId={selectedSprite?.id}
                onSelectSprite={setSelectedSprite}
                onExportSprite={handleExportSprite}
              />
            )}

            {viewMode === 'explorer' && (
              <BranchExplorer
                branches={trace.branches}
                activeBranchId={activeBranchId}
                onSelectBranch={setActiveBranchId}
                onSelectMutation={handleMutationSelected}
              />
            )}

            {viewMode === 'crystal' && (
              <div className="space-y-4">
                {trace.crystals.length === 0 ? (
                  <div className="bg-slate-800 rounded-xl p-8 text-center">
                    <div className="text-4xl mb-4">💎</div>
                    <p className="text-slate-400 mb-4">
                      No crystals yet. When you've explored enough, crystallize
                      your style journey.
                    </p>
                    <button
                      onClick={handleCrystallize}
                      className="bg-amber-500 hover:bg-amber-400 text-slate-900 px-6 py-2 rounded-lg font-medium transition-colors"
                    >
                      ✨ Crystallize Style
                    </button>
                  </div>
                ) : (
                  trace.crystals.map((crystal) => (
                    <StyleCrystalView key={crystal.id} crystal={crystal} />
                  ))
                )}
              </div>
            )}

            {/* Selected sprite detail */}
            {selectedSprite && viewMode === 'gallery' && (
              <div className="bg-slate-800 rounded-xl p-6">
                <div className="flex items-start gap-6">
                  {/* Large sprite view */}
                  <div className="flex-shrink-0">
                    <SpriteCanvas
                      sprite={selectedSprite}
                      scale={12}
                      animating={true}
                      showGrid={false}
                    />
                  </div>

                  {/* Details */}
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-amber-300 mb-2">
                      {selectedSprite.name}
                    </h3>

                    {/* Dimensions */}
                    <p className="text-slate-400 text-sm mb-4">
                      {selectedSprite.width}×{selectedSprite.height} pixels ·{' '}
                      {selectedSprite.palette.length} colors
                    </p>

                    {/* Palette preview */}
                    <div className="flex gap-1 mb-4">
                      {selectedSprite.palette.map((color, i) => (
                        <div
                          key={i}
                          className="w-6 h-6 rounded border border-slate-600"
                          style={{ backgroundColor: color }}
                          title={color}
                        />
                      ))}
                    </div>

                    {/* Aesthetic weights */}
                    <div className="space-y-2">
                      {selectedSprite.weights.map((weight) => (
                        <div
                          key={weight.dimension}
                          className="flex items-center gap-3"
                        >
                          <span className="text-slate-300 text-sm capitalize w-24">
                            {weight.dimension}
                          </span>
                          <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-amber-400"
                              style={{ width: `${weight.value * 100}%` }}
                            />
                          </div>
                          <span className="text-slate-400 text-xs w-12 text-right">
                            {Math.round(weight.value * 100)}%
                          </span>
                        </div>
                      ))}
                    </div>

                    {/* Export button */}
                    <button
                      onClick={() => handleExportSprite(selectedSprite)}
                      className="mt-4 bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg text-sm transition-colors"
                    >
                      📥 Export PNG
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right column: Taste field */}
          <div className="space-y-6">
            <TasteGravityField
              attractor={trace.attractor}
              currentWeights={selectedSprite?.weights}
              wildThreshold={trace.attractor.wild_threshold}
            />

            {/* Crystallize button */}
            <button
              onClick={handleCrystallize}
              className="w-full bg-gradient-to-r from-purple-600 to-amber-500 hover:from-purple-500 hover:to-amber-400 text-white px-6 py-3 rounded-lg font-medium transition-all"
            >
              💎 Crystallize Style Journey
            </button>

            {/* Quick stats */}
            <div className="bg-slate-800 rounded-xl p-4 space-y-3">
              <h4 className="text-sm font-medium text-slate-400">
                Session Stats
              </h4>
              <div className="grid grid-cols-2 gap-3 text-center">
                <div className="bg-slate-700 rounded-lg p-2">
                  <div className="text-xl font-bold text-amber-300">
                    {sprites.length}
                  </div>
                  <div className="text-xs text-slate-400">Characters</div>
                </div>
                <div className="bg-slate-700 rounded-lg p-2">
                  <div className="text-xl font-bold text-green-400">
                    {trace.branches.filter((b) => b.status === 'canonical')
                      .length}
                  </div>
                  <div className="text-xs text-slate-400">Canon</div>
                </div>
                <div className="bg-slate-700 rounded-lg p-2">
                  <div className="text-xl font-bold text-purple-400">
                    {trace.branches.filter((b) => b.is_wild).length}
                  </div>
                  <div className="text-xs text-slate-400">Wild</div>
                </div>
                <div className="bg-slate-700 rounded-lg p-2">
                  <div className="text-xl font-bold text-blue-400">
                    {trace.crystals.length}
                  </div>
                  <div className="text-xs text-slate-400">Crystals</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Character Proposer Modal */}
      {showProposer && (
        <CharacterProposer
          onAccept={handleCharacterAccepted}
          onClose={() => setShowProposer(false)}
        />
      )}

      {/* Crystal modal */}
      {showCrystal && latestCrystal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="max-w-2xl w-full">
            <StyleCrystalView
              crystal={latestCrystal}
              onClose={() => setShowCrystal(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default SpriteTasteLab;
