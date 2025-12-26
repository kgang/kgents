import { Routes, Route, Navigate, NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useState, useEffect, useCallback, useMemo } from 'react';
import {
  MarkCaptureInput,
  TrailTimeline,
  CrystalCard,
  ValueCompassRadar,
  type CaptureRequest,
  type TrailMark,
  type TimeGap,
  type PrincipleWeights,
  type Crystal,
} from '@kgents/shared-primitives';
import { captureMarkApi, getTodayTrailApi, crystallizeDayApi, getCrystalsApi, type TrailResponse, type CrystalizeResponse } from '../../api/witness';
import { ShareModal } from './ShareModal';
import { GapDetail, type GapAnnotation } from './GapDetail';
import { GapSummaryCard } from './GapSummaryCard';
import { DayClosurePrompt } from './DayClosurePrompt';
import { useKeyboardShortcuts } from '../../hooks';
import { KeyboardHint } from '../../components';

export function DailyLabLayout() {
  const navigate = useNavigate();
  const location = useLocation();

  // State for day closure prompt
  const [trailData, setTrailData] = useState<TrailResponse | null>(null);
  const [hasCrystal, setHasCrystal] = useState(false);

  // Keyboard shortcuts for tab navigation
  useKeyboardShortcuts(
    useMemo(
      () => ({
        'mod+1': () => navigate('/daily-lab'),
        'mod+2': () => navigate('/daily-lab/trail'),
        'mod+3': () => navigate('/daily-lab/crystal'),
        'mod+enter': () => {
          // Focus the capture input if on capture page
          if (location.pathname === '/daily-lab' || location.pathname === '/daily-lab/') {
            const input = document.querySelector<HTMLTextAreaElement>('.mark-capture-input textarea');
            if (input) {
              input.focus();
              // Dispatch enter key to trigger submit if there's content
              if (input.value.trim()) {
                input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
              }
            }
          }
        },
      }),
      [navigate, location.pathname]
    )
  );

  // Fetch trail and crystal status on mount
  useEffect(() => {
    // Get today's trail for mark count
    getTodayTrailApi()
      .then(setTrailData)
      .catch(console.error);

    // Check if crystal exists for today
    getCrystalsApi()
      .then((crystals) => {
        if (crystals.length > 0) {
          // Check if the most recent crystal is from today
          const today = new Date().toDateString();
          const crystalDate = new Date(crystals[0].timestamp).toDateString();
          setHasCrystal(crystalDate === today);
        }
      })
      .catch(console.error);
  }, []);

  // Handle crystallization from closure prompt
  const handleClosureCrystallize = useCallback(async () => {
    const result = await crystallizeDayApi();
    if (result) {
      setHasCrystal(true);
    }
    return result;
  }, []);

  // Mark count for the prompt
  const markCount = useMemo(() => trailData?.marks.length ?? 0, [trailData]);

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-lantern mb-2">Trail to Crystal</h1>
        <p className="text-sand">Turn your day into proof of intention</p>
      </div>

      {/* Navigation tabs */}
      <nav className="flex justify-center gap-4 border-b border-sage/20 pb-4">
        <TabLink to="/daily-lab" label="Capture" shortcut="1" end />
        <TabLink to="/daily-lab/trail" label="Trail" shortcut="2" />
        <TabLink to="/daily-lab/crystal" label="Crystal" shortcut="3" />
      </nav>

      <Routes>
        <Route index element={<MarkCapturePage />} />
        <Route path="trail" element={<TrailPage />} />
        <Route path="crystal" element={<CrystalPage />} />
        <Route path="*" element={<Navigate to="." replace />} />
      </Routes>

      {/* Day Closure Prompt - appears after 6 PM if no crystal exists */}
      <DayClosurePrompt
        markCount={markCount}
        marks={trailData?.marks}
        hasCrystal={hasCrystal}
        onCrystallize={handleClosureCrystallize}
      />
    </div>
  );
}

interface TabLinkProps {
  to: string;
  label: string;
  shortcut?: string;
  end?: boolean;
}

function TabLink({ to, label, shortcut, end }: TabLinkProps) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        `px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${
          isActive
            ? 'bg-sage/20 text-sage'
            : 'text-sand hover:text-lantern'
        }`
      }
    >
      <span>{label}</span>
      {shortcut && <KeyboardHint shortcut={shortcut} size="sm" />}
    </NavLink>
  );
}

// ============================================================================
// Mark Capture Page
// ============================================================================

function MarkCapturePage() {
  const [recentMarks, setRecentMarks] = useState<TrailMark[]>([]);

  const handleCapture = useCallback(async (request: CaptureRequest) => {
    try {
      const response = await captureMarkApi(request);
      // Add to recent marks
      setRecentMarks((prev) => [{
        mark_id: response.mark_id,
        content: response.content,
        tags: response.tag ? [response.tag] : [],
        timestamp: response.timestamp,
      }, ...prev.slice(0, 4)]);
      return response;
    } catch (error) {
      console.error('Failed to capture:', error);
      throw error;
    }
  }, []);

  useEffect(() => {
    // Load recent marks on mount
    getTodayTrailApi()
      .then((trail) => setRecentMarks(trail.marks.slice(-5).reverse()))
      .catch(console.error);
  }, []);

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <MarkCaptureInput
        onCapture={handleCapture}
        autoFocus
        showTags
      />

      {recentMarks.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-sand">Recent marks</h3>
          <div className="space-y-2">
            {recentMarks.map((mark) => (
              <div
                key={mark.mark_id}
                className="p-3 rounded-lg border border-sage/20 text-sm"
              >
                <p className="text-lantern">{mark.content}</p>
                <div className="flex items-center gap-2 mt-2 text-xs text-clay">
                  {mark.tags.map((tag) => (
                    <span key={tag} className="px-2 py-0.5 rounded-full bg-sage/20 text-sage">
                      {tag}
                    </span>
                  ))}
                  <span>{new Date(mark.timestamp).toLocaleTimeString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Trail Page
// ============================================================================

function TrailPage() {
  const [trail, setTrail] = useState<TrailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedMark, setSelectedMark] = useState<TrailMark | null>(null);
  const [selectedGap, setSelectedGap] = useState<TimeGap | null>(null);
  const [isGapDetailOpen, setIsGapDetailOpen] = useState(false);

  useEffect(() => {
    getTodayTrailApi()
      .then(setTrail)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  // Sort marks by timestamp for context finding
  const sortedMarks = useMemo(() => {
    if (!trail) return [];
    return [...trail.marks].sort(
      (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );
  }, [trail]);

  // Find marks before and after a gap for context
  const getGapContext = useCallback(
    (gap: TimeGap) => {
      const gapStart = new Date(gap.start).getTime();
      const gapEnd = new Date(gap.end).getTime();

      let beforeMark: TrailMark | null = null;
      let afterMark: TrailMark | null = null;

      for (const mark of sortedMarks) {
        const markTime = new Date(mark.timestamp).getTime();
        if (markTime <= gapStart) {
          beforeMark = mark;
        }
        if (markTime >= gapEnd && !afterMark) {
          afterMark = mark;
          break;
        }
      }

      return { beforeMark, afterMark };
    },
    [sortedMarks]
  );

  // Handle gap click
  const handleGapClick = useCallback((gap: TimeGap) => {
    setSelectedGap(gap);
    setSelectedMark(null); // Clear mark selection
    setIsGapDetailOpen(true);
  }, []);

  // Handle gap annotation (placeholder for future persistence)
  const handleGapAnnotate = useCallback((gap: TimeGap, annotation: GapAnnotation) => {
    console.log('Gap annotated:', gap, annotation);
    // TODO: Persist annotation to backend when API is ready
    // For now, just close the panel
    setIsGapDetailOpen(false);
    setSelectedGap(null);
  }, []);

  // Handle gap detail close
  const handleGapDetailClose = useCallback(() => {
    setIsGapDetailOpen(false);
    // Keep selectedGap for a moment to allow animation
    setTimeout(() => setSelectedGap(null), 300);
  }, []);

  // Get context for selected gap
  const gapContext = useMemo(() => {
    if (!selectedGap) return { beforeMark: null, afterMark: null };
    return getGapContext(selectedGap);
  }, [selectedGap, getGapContext]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="text-sand">Loading trail...</div>
      </div>
    );
  }

  if (!trail || trail.marks.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-sand mb-2">No marks yet today.</p>
        <p className="text-clay text-sm">Start capturing to build your trail.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <TrailTimeline
        marks={trail.marks}
        gaps={trail.gaps ?? []}
        date={new Date()}
        selectedMarkId={selectedMark?.mark_id}
        onSelectMark={(mark) => {
          setSelectedMark(mark);
          setSelectedGap(null); // Clear gap selection when selecting mark
        }}
        onGapClick={handleGapClick}
        showTimestamps
      />

      {/* Selected Mark Detail */}
      {selectedMark && (
        <div className="p-4 rounded-xl border border-amber/30 bg-amber/5">
          <h3 className="font-medium text-lantern mb-2">Selected Mark</h3>
          <p className="text-sand">{selectedMark.content}</p>
          <div className="flex items-center gap-2 mt-2 text-xs text-clay">
            {selectedMark.tags.map((tag) => (
              <span key={tag} className="px-2 py-0.5 rounded-full bg-sage/20 text-sage">
                {tag}
              </span>
            ))}
            <span>{new Date(selectedMark.timestamp).toLocaleTimeString()}</span>
          </div>
        </div>
      )}

      {/* Gap Detail Slide-over */}
      {selectedGap && (
        <GapDetail
          gap={selectedGap}
          beforeMark={gapContext.beforeMark}
          afterMark={gapContext.afterMark}
          isOpen={isGapDetailOpen}
          onClose={handleGapDetailClose}
          onAnnotate={handleGapAnnotate}
        />
      )}
    </div>
  );
}

// ============================================================================
// Crystal Page
// ============================================================================

/**
 * Derive principle weights from crystal data.
 * If crystal has explicit principles, weight those higher.
 * Otherwise, infer sensible defaults based on topics and content.
 */
function derivePrincipleWeights(crystal: Crystal): PrincipleWeights {
  // Base weights - moderately balanced
  const weights: PrincipleWeights = {
    tasteful: 0.5,
    curated: 0.5,
    ethical: 0.5,
    joy_inducing: 0.5,
    composable: 0.5,
    heterarchical: 0.5,
    generative: 0.5,
  };

  // If crystal has explicit principles, boost those
  if (crystal.principles && crystal.principles.length > 0) {
    const principleMap: Record<string, keyof PrincipleWeights> = {
      'tasteful': 'tasteful',
      'curated': 'curated',
      'ethical': 'ethical',
      'joy': 'joy_inducing',
      'joy-inducing': 'joy_inducing',
      'joy_inducing': 'joy_inducing',
      'composable': 'composable',
      'heterarchical': 'heterarchical',
      'generative': 'generative',
    };

    for (const p of crystal.principles) {
      const key = principleMap[p.toLowerCase()];
      if (key) {
        weights[key] = Math.min(1, weights[key] + 0.35);
      }
    }
  }

  // Infer from topics if available
  if (crystal.topics && crystal.topics.length > 0) {
    const topicInferences: Record<string, Partial<PrincipleWeights>> = {
      'productivity': { composable: 0.2, generative: 0.15 },
      'creativity': { generative: 0.25, tasteful: 0.15, joy_inducing: 0.1 },
      'learning': { curated: 0.2, generative: 0.15 },
      'reflection': { ethical: 0.15, tasteful: 0.1 },
      'collaboration': { heterarchical: 0.2, composable: 0.1 },
      'flow': { joy_inducing: 0.25, composable: 0.15 },
      'design': { tasteful: 0.25, curated: 0.15 },
      'architecture': { composable: 0.2, generative: 0.15 },
      'wellbeing': { ethical: 0.2, joy_inducing: 0.2 },
    };

    for (const topic of crystal.topics) {
      const inferences = topicInferences[topic.toLowerCase()];
      if (inferences) {
        for (const [key, boost] of Object.entries(inferences)) {
          const k = key as keyof PrincipleWeights;
          weights[k] = Math.min(1, weights[k] + boost);
        }
      }
    }
  }

  // Use confidence to scale overall weights
  const confidenceScale = 0.5 + (crystal.confidence * 0.5); // 0.5-1.0 range
  for (const key of Object.keys(weights) as (keyof PrincipleWeights)[]) {
    weights[key] = weights[key] * confidenceScale;
  }

  return weights;
}

function CrystalPage() {
  const navigate = useNavigate();
  const [crystal, setCrystal] = useState<CrystalizeResponse | null>(null);
  const [trail, setTrail] = useState<TrailResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPrinciple, setSelectedPrinciple] = useState<keyof PrincipleWeights | null>(null);
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);

  const handleCrystallize = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await crystallizeDayApi();
      if (result) {
        setCrystal(result);
      } else {
        setError('Not enough marks to create a crystal. Keep capturing!');
      }
    } catch (err) {
      setError('Failed to create crystal. Try again later.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Load existing crystal and trail on mount
  useEffect(() => {
    getCrystalsApi()
      .then((crystals) => {
        if (crystals.length > 0) {
          // Use most recent crystal
          setCrystal({ crystal: crystals[0], honesty: { dropped_count: 0, dropped_tags: [], dropped_summaries: [], galois_loss: 0 } });
        }
      })
      .catch(console.error);

    // Also load trail for gap summary
    getTodayTrailApi()
      .then(setTrail)
      .catch(console.error);
  }, []);

  // Calculate tracked time from marks
  const trackedMinutes = useMemo(() => {
    if (!trail || trail.marks.length < 2) return 0;
    const sortedMarks = [...trail.marks].sort(
      (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );
    const first = new Date(sortedMarks[0].timestamp).getTime();
    const last = new Date(sortedMarks[sortedMarks.length - 1].timestamp).getTime();
    const totalMinutes = (last - first) / (1000 * 60);
    // Defensive: handle undefined gaps gracefully
    const gapMinutes = (trail.gaps ?? []).reduce((sum, g) => sum + g.duration_minutes, 0);
    return Math.max(0, Math.round(totalMinutes - gapMinutes));
  }, [trail]);

  // Navigate to trail page to view gaps
  const handleViewTrail = useCallback(() => {
    navigate('/daily-lab/trail');
  }, [navigate]);

  // Handle opening the share modal
  const handleOpenShare = useCallback(() => {
    setIsShareModalOpen(true);
  }, []);

  // Handle closing the share modal
  const handleCloseShare = useCallback(() => {
    setIsShareModalOpen(false);
  }, []);

  // Principle descriptions for the info panel
  const principleDescriptions: Record<keyof PrincipleWeights, string> = {
    tasteful: 'Each action serves a clear, justified purpose. Quality over quantity.',
    curated: 'Intentional selection over exhaustive cataloging. Depth over breadth.',
    ethical: 'Augments human capability, never replaces judgment. Sovereignty preserved.',
    joy_inducing: 'Delight in interaction. Flow states and moments of satisfaction.',
    composable: 'Actions combine naturally. Small pieces, loosely joined.',
    heterarchical: 'Fluid relationships, not fixed hierarchy. Adaptable to context.',
    generative: 'Creates more than it consumes. Compression that enables expansion.',
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      {crystal ? (
        <>
          <CrystalCard
            crystal={crystal.crystal}
            honesty={crystal.honesty}
            onShare={handleOpenShare}
          />

          {/* Share Modal */}
          <ShareModal
            crystal={crystal.crystal}
            honesty={crystal.honesty}
            isOpen={isShareModalOpen}
            onClose={handleCloseShare}
          />

          {/* Gap Summary Card (QA-2: Gaps are honored) */}
          {trail && (trail.gaps ?? []).length > 0 && (
            <GapSummaryCard
              gaps={trail.gaps ?? []}
              trackedMinutes={trackedMinutes}
              onViewTrail={handleViewTrail}
            />
          )}

          {/* Constitutional Alignment Section */}
          <div className="rounded-xl border border-sage/20 p-6 space-y-4">
            <h3 className="text-lg font-medium text-lantern">Constitutional Alignment</h3>
            <p className="text-sm text-sand">
              How this crystal reflects the 7 kgents principles
            </p>

            <div className="flex flex-col items-center">
              <ValueCompassRadar
                weights={derivePrincipleWeights(crystal.crystal)}
                domain="productivity"
                size="md"
                showLabels
                showLegend
                interactive
                onPrincipleClick={(principle) => {
                  setSelectedPrinciple(
                    selectedPrinciple === principle ? null : principle
                  );
                }}
              />
            </div>

            {/* Selected Principle Info Panel */}
            {selectedPrinciple && (
              <div className="mt-4 p-4 rounded-lg bg-sage/10 border border-sage/20">
                <h4 className="text-sm font-medium text-sage capitalize">
                  {selectedPrinciple.replace('_', '-')}
                </h4>
                <p className="text-sm text-sand mt-1">
                  {principleDescriptions[selectedPrinciple]}
                </p>
              </div>
            )}
          </div>
        </>
      ) : (
        <div className="text-center py-12 rounded-xl border border-sage/20">
          <p className="text-sand mb-4">
            {error || "Ready to crystallize your day's marks into a memory artifact?"}
          </p>
          <button
            onClick={handleCrystallize}
            disabled={loading}
            className="px-6 py-3 rounded-xl bg-amber text-bark font-medium hover:bg-amber/90 transition-colors disabled:opacity-50"
          >
            {loading ? 'Crystallizing...' : 'Create Crystal'}
          </button>
        </div>
      )}
    </div>
  );
}
