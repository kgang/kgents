/**
 * CommissionWizard: Step-by-step guided commission creation flow.
 *
 * The main deliverable of Phase 4.5 - a wizard that guides Kent through
 * creating a new commission with full control over the metaphysical fullstack.
 *
 * Steps:
 * 1. Intent - What do you want to build?
 * 2. Workshop - Where will it be built?
 * 3. Artisans - Who will build it?
 * 4. Confirm - Review before starting
 * 5. Progress - Watch it build (with auto-advance)
 * 6. Complete - Celebrate!
 *
 * "The commission is the intent. The artisans are the hands. The artifact is the agent."
 *
 * @see ~/.claude/plans/atomic-launching-pearl.md
 * @see docs/skills/crown-jewel-patterns.md - Pattern 4: Teaching Mode
 */

import { useState, useCallback, useEffect } from 'react';
import {
  X,
  ChevronRight,
  ChevronLeft,
  Loader2,
  Check,
  Play,
  Pause,
  Sparkles,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  useCreateCommission,
  useStartCommission,
  useAdvanceCommission,
  usePauseCommission,
  useResumeCommission,
  useCommission,
  type Commission,
  type CommissionStatus,
} from '@/hooks/useForgeQuery';
import { WorkshopSelector, PERSONAL_WORKSHOP_ID } from './WorkshopSelector';
import { WorkshopCreateForm } from './WorkshopCreateForm';

// =============================================================================
// Types
// =============================================================================

type WizardStep = 'intent' | 'workshop' | 'artisans' | 'confirm' | 'progress' | 'complete';

export interface CommissionWizardProps {
  /** Whether the wizard is open */
  isOpen: boolean;
  /** Callback to close the wizard */
  onClose: () => void;
  /** Callback when commission completes */
  onComplete?: (commission: Commission) => void;
  /** Default workshop to pre-select */
  defaultWorkshop?: string;
}

interface ArtisanDef {
  id: string;
  name: string;
  layer: string;
  icon: string;
  description: string;
  disabled?: boolean;
}

// =============================================================================
// Constants
// =============================================================================

const ARTISANS: ArtisanDef[] = [
  { id: 'kgent', name: 'K-gent', layer: 'Soul', icon: '~', description: 'Governance & taste' },
  { id: 'architect', name: 'Architect', layer: 'Design', icon: '~', description: 'Categorical design' },
  { id: 'smith', name: 'Smith', layer: 'Code', icon: '~', description: 'Service implementation' },
  { id: 'herald', name: 'Herald', layer: 'Protocol', icon: '~', description: 'AGENTESE node' },
  { id: 'projector', name: 'Projector', layer: 'Surface', icon: '~', description: 'React components' },
  { id: 'sentinel', name: 'Sentinel', layer: 'Security', icon: '~', description: 'Security review', disabled: true },
  { id: 'witness', name: 'Witness', layer: 'Testing', icon: '~', description: 'Test generation', disabled: true },
];

const STEP_ORDER: WizardStep[] = ['intent', 'workshop', 'artisans', 'confirm', 'progress', 'complete'];

const STEP_LABELS: Record<WizardStep, string> = {
  intent: 'Intent',
  workshop: 'Workshop',
  artisans: 'Artisans',
  confirm: 'Confirm',
  progress: 'Building',
  complete: 'Complete',
};

const ACTIVE_STATUSES: CommissionStatus[] = [
  'designing', 'implementing', 'exposing', 'projecting', 'securing', 'verifying', 'reviewing'
];

// =============================================================================
// CommissionWizard Component
// =============================================================================

export function CommissionWizard({
  isOpen,
  onClose,
  onComplete,
  defaultWorkshop,
}: CommissionWizardProps) {
  // Step state
  const [step, setStep] = useState<WizardStep>('intent');

  // Form state
  const [intent, setIntent] = useState('');
  const [name, setName] = useState('');
  const [workshopId, setWorkshopId] = useState<string | null>(defaultWorkshop || PERSONAL_WORKSHOP_ID);
  const [selectedArtisans, setSelectedArtisans] = useState<string[]>(
    ARTISANS.filter(a => !a.disabled).map(a => a.id)
  );
  const [showCreateWorkshop, setShowCreateWorkshop] = useState(false);

  // Commission state
  const [commissionId, setCommissionId] = useState<string | null>(null);
  const [autoAdvance, setAutoAdvance] = useState(true);
  const [isPaused, setIsPaused] = useState(false);

  // Mutations
  const createCommission = useCreateCommission();
  const startCommission = useStartCommission();
  const advanceCommission = useAdvanceCommission();
  const pauseCommission = usePauseCommission();
  const resumeCommission = useResumeCommission();

  // Live commission data (polling)
  const { data: liveCommission, refetch: refetchCommission } = useCommission(
    commissionId || '',
    { enabled: !!commissionId && step === 'progress' }
  );

  // Auto-advance polling effect
  useEffect(() => {
    if (!commissionId || step !== 'progress' || !autoAdvance || isPaused) return;

    const interval = setInterval(() => {
      refetchCommission();
    }, 2000);

    return () => clearInterval(interval);
  }, [commissionId, step, autoAdvance, isPaused, refetchCommission]);

  // Auto-advance logic
  useEffect(() => {
    if (!liveCommission || !autoAdvance || isPaused) return;

    const status = liveCommission.status;

    // If complete, move to complete step
    if (status === 'complete') {
      setStep('complete');
      onComplete?.(liveCommission as Commission);
      return;
    }

    // If failed or rejected, stay on progress (show error)
    if (status === 'failed' || status === 'rejected') {
      return;
    }

    // If in an active status, try to advance
    if (ACTIVE_STATUSES.includes(status)) {
      // Check if current artisan is done (has output)
      const canAdvance = true; // Backend handles the actual check
      if (canAdvance) {
        advanceCommission.mutateAsync({ commission_id: commissionId! }).catch(() => {});
      }
    }
  }, [liveCommission, autoAdvance, isPaused, commissionId, advanceCommission, onComplete]);

  // Reset state when closed
  useEffect(() => {
    if (!isOpen) {
      setStep('intent');
      setIntent('');
      setName('');
      setWorkshopId(defaultWorkshop || PERSONAL_WORKSHOP_ID);
      setSelectedArtisans(ARTISANS.filter(a => !a.disabled).map(a => a.id));
      setCommissionId(null);
      setAutoAdvance(true);
      setIsPaused(false);
    }
  }, [isOpen, defaultWorkshop]);

  // Handlers
  const handleNext = useCallback(async () => {
    const currentIndex = STEP_ORDER.indexOf(step);

    // If on confirm, create and start commission
    if (step === 'confirm') {
      try {
        const result = await createCommission.mutateAsync({
          intent: intent.trim(),
          name: name.trim() || undefined,
        });

        if (result?.id) {
          setCommissionId(result.id);
          await startCommission.mutateAsync({ commission_id: result.id });
          setStep('progress');
        }
      } catch {
        // Error handled by mutation state
      }
      return;
    }

    if (currentIndex < STEP_ORDER.length - 1) {
      setStep(STEP_ORDER[currentIndex + 1]);
    }
  }, [step, intent, name, createCommission, startCommission]);

  const handleBack = useCallback(() => {
    const currentIndex = STEP_ORDER.indexOf(step);
    if (currentIndex > 0) {
      setStep(STEP_ORDER[currentIndex - 1]);
    }
  }, [step]);

  const handleTogglePause = useCallback(async () => {
    if (!commissionId) return;

    try {
      if (isPaused) {
        await resumeCommission.mutateAsync({ commission_id: commissionId });
        setIsPaused(false);
      } else {
        await pauseCommission.mutateAsync({ commission_id: commissionId });
        setIsPaused(true);
      }
    } catch {
      // Error handled by mutation state
    }
  }, [commissionId, isPaused, pauseCommission, resumeCommission]);

  const handleToggleArtisan = useCallback((artisanId: string) => {
    setSelectedArtisans(prev =>
      prev.includes(artisanId)
        ? prev.filter(id => id !== artisanId)
        : [...prev, artisanId]
    );
  }, []);

  // Validation
  const canProceed = useCallback(() => {
    switch (step) {
      case 'intent':
        return intent.trim().length > 0;
      case 'workshop':
        return true; // Workshop is optional
      case 'artisans':
        return selectedArtisans.length > 0;
      case 'confirm':
        return true;
      default:
        return false;
    }
  }, [step, intent, selectedArtisans]);

  if (!isOpen) return null;

  const stepIndex = STEP_ORDER.indexOf(step);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={() => step !== 'progress' && onClose()}
      />

      {/* Modal */}
      <div className={cn(
        'relative w-full max-w-2xl mx-4 bg-white rounded-xl shadow-2xl',
        'max-h-[90vh] overflow-hidden flex flex-col'
      )}>
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-stone-200">
          <div>
            <h2 className="font-semibold text-stone-800">New Commission</h2>
            <p className="text-sm text-stone-500">{STEP_LABELS[step]}</p>
          </div>
          {step !== 'progress' && (
            <button
              onClick={onClose}
              className="p-1 text-stone-400 hover:text-stone-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Progress Dots */}
        <div className="px-6 py-3 bg-stone-50 border-b border-stone-100">
          <div className="flex items-center justify-center gap-2">
            {STEP_ORDER.slice(0, -1).map((s, i) => (
              <div
                key={s}
                className={cn(
                  'w-2 h-2 rounded-full transition-colors',
                  i < stepIndex ? 'bg-amber-500' :
                  i === stepIndex ? 'bg-amber-500' :
                  'bg-stone-300'
                )}
              />
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Step 1: Intent */}
          {step === 'intent' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-stone-700 mb-1">
                  What do you want to build?
                </label>
                <textarea
                  value={intent}
                  onChange={(e) => setIntent(e.target.value)}
                  placeholder="Describe the agent you want to create..."
                  rows={4}
                  className={cn(
                    'w-full px-3 py-2 text-sm rounded-lg border',
                    'focus:outline-none focus:ring-2 focus:ring-amber-200 focus:border-amber-300',
                    'border-stone-200 resize-none'
                  )}
                  autoFocus
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-stone-700 mb-1">
                  Name <span className="text-stone-400">(optional)</span>
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="My Agent"
                  className={cn(
                    'w-full px-3 py-2 text-sm rounded-lg border',
                    'focus:outline-none focus:ring-2 focus:ring-amber-200 focus:border-amber-300',
                    'border-stone-200'
                  )}
                />
              </div>
            </div>
          )}

          {/* Step 2: Workshop */}
          {step === 'workshop' && (
            <div className="space-y-4">
              {showCreateWorkshop ? (
                <WorkshopCreateForm
                  onCreated={(workshop) => {
                    setWorkshopId(workshop.id);
                    setShowCreateWorkshop(false);
                  }}
                  onCancel={() => setShowCreateWorkshop(false)}
                />
              ) : (
                <>
                  <div>
                    <label className="block text-sm font-medium text-stone-700 mb-2">
                      Where will it be built?
                    </label>
                    <WorkshopSelector
                      selected={workshopId}
                      onSelect={setWorkshopId}
                      onCreateNew={() => setShowCreateWorkshop(true)}
                    />
                  </div>
                  <p className="text-xs text-stone-400">
                    Workshops organize your commissions. You can skip this to use your Personal Workshop.
                  </p>
                </>
              )}
            </div>
          )}

          {/* Step 3: Artisans */}
          {step === 'artisans' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-stone-700 mb-2">
                  Who will build it?
                </label>
                <p className="text-xs text-stone-400 mb-4">
                  Select the artisans to involve. All enabled by default for full metaphysical fullstack.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                {ARTISANS.map((artisan) => (
                  <button
                    key={artisan.id}
                    type="button"
                    onClick={() => !artisan.disabled && handleToggleArtisan(artisan.id)}
                    disabled={artisan.disabled}
                    className={cn(
                      'p-3 rounded-lg border text-left transition-all',
                      selectedArtisans.includes(artisan.id)
                        ? 'bg-amber-50 border-amber-300'
                        : 'bg-white border-stone-200 hover:border-stone-300',
                      artisan.disabled && 'opacity-50 cursor-not-allowed'
                    )}
                  >
                    <div className="flex items-start gap-2">
                      <span className="text-lg">{artisan.icon}</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-stone-800 text-sm">
                            {artisan.name}
                          </span>
                          {selectedArtisans.includes(artisan.id) && (
                            <Check className="w-3 h-3 text-amber-500" />
                          )}
                        </div>
                        <span className="text-xs text-stone-400">{artisan.layer}</span>
                        <p className="text-xs text-stone-500 mt-1">{artisan.description}</p>
                        {artisan.disabled && (
                          <span className="text-[10px] text-stone-400 italic">Coming soon</span>
                        )}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 4: Confirm */}
          {step === 'confirm' && (
            <div className="space-y-6">
              <div className="p-4 bg-stone-50 rounded-lg">
                <h4 className="text-sm font-medium text-stone-700 mb-2">Intent</h4>
                <p className="text-sm text-stone-600">{intent}</p>
                {name && (
                  <p className="text-xs text-stone-400 mt-1">Name: {name}</p>
                )}
              </div>

              <div className="p-4 bg-stone-50 rounded-lg">
                <h4 className="text-sm font-medium text-stone-700 mb-2">Workshop</h4>
                <p className="text-sm text-stone-600">
                  {workshopId === PERSONAL_WORKSHOP_ID ? 'Personal Workshop' : workshopId}
                </p>
              </div>

              <div className="p-4 bg-stone-50 rounded-lg">
                <h4 className="text-sm font-medium text-stone-700 mb-2">Artisans ({selectedArtisans.length})</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedArtisans.map((id) => {
                    const artisan = ARTISANS.find(a => a.id === id);
                    return (
                      <span
                        key={id}
                        className="px-2 py-1 text-xs bg-amber-100 text-amber-800 rounded"
                      >
                        {artisan?.icon} {artisan?.name}
                      </span>
                    );
                  })}
                </div>
              </div>

              <div className="flex items-center gap-2 text-xs text-stone-500">
                <input
                  type="checkbox"
                  id="auto-advance"
                  checked={autoAdvance}
                  onChange={(e) => setAutoAdvance(e.target.checked)}
                  className="rounded border-stone-300"
                />
                <label htmlFor="auto-advance">Auto-advance through stages</label>
              </div>
            </div>
          )}

          {/* Step 5: Progress */}
          {step === 'progress' && liveCommission && (
            <div className="space-y-6">
              {/* Status */}
              <div className="text-center">
                <Loader2 className="w-8 h-8 mx-auto text-amber-500 animate-spin mb-2" />
                <p className="text-sm font-medium text-stone-700">
                  {liveCommission.status.charAt(0).toUpperCase() + liveCommission.status.slice(1)}...
                </p>
                {isPaused && (
                  <span className="text-xs text-yellow-600">Paused</span>
                )}
              </div>

              {/* Artisan Progress */}
              <div className="space-y-2">
                {ARTISANS.filter(a => selectedArtisans.includes(a.id)).map((artisan) => {
                  const output = liveCommission.artisan_outputs?.[artisan.id];
                  const status = output?.status || 'pending';

                  return (
                    <div
                      key={artisan.id}
                      className={cn(
                        'flex items-center gap-3 p-3 rounded-lg transition-all',
                        status === 'working' ? 'bg-amber-50 border border-amber-200' :
                        status === 'complete' ? 'bg-green-50 border border-green-200' :
                        status === 'failed' ? 'bg-red-50 border border-red-200' :
                        'bg-stone-50 border border-stone-200'
                      )}
                    >
                      <span className="text-lg">{artisan.icon}</span>
                      <div className="flex-1">
                        <span className="text-sm font-medium text-stone-700">{artisan.name}</span>
                        {output?.annotation && (
                          <p className="text-xs text-stone-500 mt-0.5">{output.annotation}</p>
                        )}
                      </div>
                      <div>
                        {status === 'working' && <Loader2 className="w-4 h-4 text-amber-500 animate-spin" />}
                        {status === 'complete' && <Check className="w-4 h-4 text-green-500" />}
                        {status === 'failed' && <X className="w-4 h-4 text-red-500" />}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Controls */}
              <div className="flex items-center justify-center gap-2">
                <button
                  onClick={handleTogglePause}
                  className={cn(
                    'px-4 py-2 text-sm rounded-lg transition-colors',
                    'border border-stone-200 hover:bg-stone-50'
                  )}
                >
                  {isPaused ? (
                    <span className="flex items-center gap-2"><Play className="w-4 h-4" /> Resume</span>
                  ) : (
                    <span className="flex items-center gap-2"><Pause className="w-4 h-4" /> Pause</span>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* Step 6: Complete */}
          {step === 'complete' && liveCommission && (
            <div className="text-center space-y-6">
              <div>
                <Sparkles className="w-12 h-12 mx-auto text-amber-500 mb-4" />
                <h3 className="text-xl font-semibold text-stone-800">Commission Complete!</h3>
                <p className="text-sm text-stone-500 mt-1">
                  {liveCommission.name || 'Your agent'} has been forged.
                </p>
              </div>

              {liveCommission.artifact_summary && (
                <div className="p-4 bg-stone-50 rounded-lg text-left">
                  <h4 className="text-sm font-medium text-stone-700 mb-2">Summary</h4>
                  <p className="text-sm text-stone-600">{liveCommission.artifact_summary}</p>
                </div>
              )}

              {liveCommission.artifact_path && (
                <div className="p-4 bg-stone-50 rounded-lg text-left">
                  <h4 className="text-sm font-medium text-stone-700 mb-2">Artifact Path</h4>
                  <code className="text-xs text-amber-700 bg-amber-50 px-2 py-1 rounded">
                    {liveCommission.artifact_path}
                  </code>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-stone-50 border-t border-stone-200 flex items-center justify-between">
          {/* Back Button */}
          {step !== 'intent' && step !== 'progress' && step !== 'complete' ? (
            <button
              onClick={handleBack}
              className="flex items-center gap-1 px-4 py-2 text-sm text-stone-600 hover:text-stone-800 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
              Back
            </button>
          ) : (
            <div />
          )}

          {/* Next/Complete Button */}
          {step === 'complete' ? (
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  setStep('intent');
                  setIntent('');
                  setName('');
                  setCommissionId(null);
                }}
                className="px-4 py-2 text-sm text-stone-600 hover:text-stone-800 transition-colors"
              >
                Start Another
              </button>
              <button
                onClick={onClose}
                className={cn(
                  'px-4 py-2 text-sm font-medium rounded-lg transition-colors',
                  'bg-amber-500 text-white hover:bg-amber-600'
                )}
              >
                Done
              </button>
            </div>
          ) : step === 'progress' ? (
            <div />
          ) : (
            <button
              onClick={handleNext}
              disabled={!canProceed() || createCommission.isPending}
              className={cn(
                'flex items-center gap-1 px-4 py-2 text-sm font-medium rounded-lg transition-colors',
                'bg-amber-500 text-white hover:bg-amber-600',
                'disabled:opacity-50 disabled:cursor-not-allowed'
              )}
            >
              {createCommission.isPending ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> Starting...</>
              ) : step === 'confirm' ? (
                <>Commission!</>
              ) : (
                <>Next <ChevronRight className="w-4 h-4" /></>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default CommissionWizard;
