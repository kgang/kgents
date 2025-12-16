/**
 * AgentCreationWizard: Modal wizard for creating new citizens.
 *
 * Flow: Archetype → Name → (Optional: Eigenvectors) → Create
 * Target: ≤3 clicks for simple mode.
 */

import { useState, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { ArchetypePalette } from './ArchetypePalette';
import { EigenvectorSliders } from './EigenvectorSliders';
import { AgentPreview } from './AgentPreview';
import { AdvancedEditor } from './AdvancedEditor';
import type { Archetype, Eigenvectors } from '@/api/types';

/** Stub for citizen creation until backend endpoint is implemented */
async function createCitizenStub(_townId: string, config: {
  name: string;
  archetype: Archetype;
  eigenvectors: Eigenvectors;
  region?: string;
}): Promise<{ citizen_id: string }> {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 500));
  // Generate a mock citizen ID
  const citizenId = `citizen-${Date.now()}-${config.name.toLowerCase().replace(/\s+/g, '-')}`;
  console.log('[AgentCreationWizard] Created citizen (stub):', { citizenId, config });
  return { citizen_id: citizenId };
}

export type CreationMode = 'simple' | 'custom' | 'advanced';
type WizardStep = 'archetype' | 'customize' | 'preview';

export interface AgentCreationWizardProps {
  townId: string;
  isOpen: boolean;
  onClose: () => void;
  onCreated?: (citizenId: string) => void;
}

interface AgentConfig {
  name: string;
  archetype: Archetype | null;
  eigenvectors: Partial<Eigenvectors>;
  region?: string;
}

const DEFAULT_EIGENVECTORS: Eigenvectors = {
  warmth: 0.5,
  curiosity: 0.5,
  trust: 0.5,
  creativity: 0.5,
  patience: 0.5,
  resilience: 0.5,
  ambition: 0.5,
};

const ARCHETYPE_EIGENVECTOR_BIASES: Record<Archetype, Partial<Eigenvectors>> = {
  Builder: { creativity: 0.7, patience: 0.6, resilience: 0.7 },
  Trader: { trust: 0.6, ambition: 0.7, warmth: 0.6 },
  Healer: { warmth: 0.8, patience: 0.7, trust: 0.7 },
  Scholar: { curiosity: 0.8, patience: 0.7, creativity: 0.6 },
  Watcher: { curiosity: 0.7, patience: 0.8, resilience: 0.6 },
};

export function AgentCreationWizard({
  townId,
  isOpen,
  onClose,
  onCreated,
}: AgentCreationWizardProps) {
  const [mode, setMode] = useState<CreationMode>('simple');
  const [step, setStep] = useState<WizardStep>('archetype');
  const [config, setConfig] = useState<AgentConfig>({
    name: '',
    archetype: null,
    eigenvectors: { ...DEFAULT_EIGENVECTORS },
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Generate random name based on archetype
  const generateName = useCallback((archetype: Archetype | null) => {
    const prefixes: Record<Archetype, string[]> = {
      Builder: ['Mason', 'Forge', 'Stone', 'Craft', 'Oak'],
      Trader: ['Mercer', 'Silver', 'Coin', 'Deal', 'Fair'],
      Healer: ['Sage', 'Willow', 'Calm', 'Grace', 'Haven'],
      Scholar: ['Quill', 'Tome', 'Lore', 'Ink', 'Page'],
      Watcher: ['Vigil', 'Owl', 'Dawn', 'Dusk', 'Shade'],
    };
    const suffixes = ['wind', 'brook', 'vale', 'crest', 'mere', 'dale', 'holm', 'wold'];

    const prefix = archetype
      ? prefixes[archetype][Math.floor(Math.random() * prefixes[archetype].length)]
      : ['Nova', 'Echo', 'Flux', 'Pulse', 'Drift'][Math.floor(Math.random() * 5)];
    const suffix = suffixes[Math.floor(Math.random() * suffixes.length)];

    return `${prefix}${suffix}`;
  }, []);

  // Handle archetype selection
  const handleArchetypeSelect = (archetype: Archetype) => {
    const biases = ARCHETYPE_EIGENVECTOR_BIASES[archetype];
    const newEigenvectors = { ...DEFAULT_EIGENVECTORS, ...biases };

    setConfig((prev) => ({
      ...prev,
      archetype,
      eigenvectors: newEigenvectors,
      name: prev.name || generateName(archetype),
    }));

    if (mode === 'simple') {
      setStep('preview');
    } else {
      setStep('customize');
    }
  };

  // Handle creation
  const handleCreate = async () => {
    if (!config.archetype || !config.name) {
      setError('Please select an archetype and provide a name');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await createCitizenStub(townId, {
        name: config.name,
        archetype: config.archetype,
        eigenvectors: config.eigenvectors as Eigenvectors,
        region: config.region,
      });

      onCreated?.(result.citizen_id);
      handleClose();
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      setError(axiosErr.response?.data?.detail || 'Failed to create citizen');
    } finally {
      setLoading(false);
    }
  };

  // Reset and close
  const handleClose = () => {
    setConfig({
      name: '',
      archetype: null,
      eigenvectors: { ...DEFAULT_EIGENVECTORS },
    });
    setStep('archetype');
    setError(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="relative bg-town-bg border border-town-accent/30 rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-town-accent/20">
          <div>
            <h2 className="text-xl font-bold">Create New Citizen</h2>
            <p className="text-sm text-gray-400">
              {step === 'archetype' && 'Choose an archetype to begin'}
              {step === 'customize' && 'Customize your citizen'}
              {step === 'preview' && 'Review and create'}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <ModeSelector value={mode} onChange={setMode} />
            <button
              onClick={handleClose}
              className="p-2 hover:bg-town-accent/20 rounded-lg transition-colors"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Progress */}
        <StepIndicator step={step} mode={mode} />

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {mode === 'advanced' ? (
            <AdvancedEditor
              config={config}
              onChange={setConfig}
              onValidate={(valid) => !valid && setError('Invalid configuration')}
            />
          ) : (
            <>
              {step === 'archetype' && (
                <ArchetypePalette
                  selected={config.archetype}
                  onSelect={handleArchetypeSelect}
                />
              )}

              {step === 'customize' && (
                <div className="space-y-6">
                  {/* Name input */}
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">
                      Name
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={config.name}
                        onChange={(e) =>
                          setConfig((prev) => ({ ...prev, name: e.target.value }))
                        }
                        placeholder="Enter citizen name"
                        className="flex-1 bg-town-surface/50 border border-town-accent/30 rounded-lg px-4 py-2 focus:outline-none focus:border-town-highlight"
                      />
                      <button
                        onClick={() =>
                          setConfig((prev) => ({
                            ...prev,
                            name: generateName(config.archetype),
                          }))
                        }
                        className="px-3 py-2 bg-town-accent/30 hover:bg-town-accent/50 rounded-lg transition-colors"
                        title="Generate random name"
                      >
                        🎲
                      </button>
                    </div>
                  </div>

                  {/* Eigenvector sliders */}
                  <EigenvectorSliders
                    values={config.eigenvectors as Eigenvectors}
                    onChange={(eigenvectors) =>
                      setConfig((prev) => ({ ...prev, eigenvectors }))
                    }
                    archetype={config.archetype}
                  />
                </div>
              )}

              {step === 'preview' && (
                <AgentPreview
                  config={config}
                  onEdit={() => setStep('customize')}
                />
              )}
            </>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="px-6 py-2 bg-red-500/10 border-t border-red-500/20">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between p-4 border-t border-town-accent/20">
          <button
            onClick={() => {
              if (step === 'customize') setStep('archetype');
              else if (step === 'preview') setStep(mode === 'simple' ? 'archetype' : 'customize');
            }}
            disabled={step === 'archetype'}
            className={cn(
              'px-4 py-2 rounded-lg transition-colors',
              step === 'archetype'
                ? 'text-gray-600 cursor-not-allowed'
                : 'text-gray-400 hover:text-white hover:bg-town-accent/20'
            )}
          >
            ← Back
          </button>

          <div className="flex gap-2">
            {step !== 'preview' && mode !== 'advanced' && (
              <button
                onClick={() => setStep('preview')}
                disabled={!config.archetype}
                className={cn(
                  'px-4 py-2 rounded-lg transition-colors',
                  config.archetype
                    ? 'bg-town-accent/50 hover:bg-town-accent text-white'
                    : 'bg-town-surface text-gray-600 cursor-not-allowed'
                )}
              >
                Preview →
              </button>
            )}

            {(step === 'preview' || mode === 'advanced') && (
              <button
                onClick={handleCreate}
                disabled={loading || !config.archetype || !config.name}
                className={cn(
                  'px-6 py-2 rounded-lg font-medium transition-colors',
                  loading || !config.archetype || !config.name
                    ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                    : 'bg-town-highlight hover:bg-town-highlight/80 text-white'
                )}
              >
                {loading ? 'Creating...' : '✨ Create Citizen'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

function ModeSelector({
  value,
  onChange,
}: {
  value: CreationMode;
  onChange: (v: CreationMode) => void;
}) {
  const modes: { id: CreationMode; label: string }[] = [
    { id: 'simple', label: 'Simple' },
    { id: 'custom', label: 'Custom' },
    { id: 'advanced', label: 'Advanced' },
  ];

  return (
    <div className="flex bg-town-surface/30 rounded-lg p-1">
      {modes.map(({ id, label }) => (
        <button
          key={id}
          onClick={() => onChange(id)}
          className={cn(
            'px-3 py-1 text-xs font-medium rounded transition-colors',
            value === id ? 'bg-town-accent text-white' : 'text-gray-400 hover:text-white'
          )}
        >
          {label}
        </button>
      ))}
    </div>
  );
}

function StepIndicator({ step, mode }: { step: WizardStep; mode: CreationMode }) {
  if (mode === 'advanced') return null;

  const steps: { id: WizardStep; label: string }[] =
    mode === 'simple'
      ? [
          { id: 'archetype', label: 'Archetype' },
          { id: 'preview', label: 'Create' },
        ]
      : [
          { id: 'archetype', label: 'Archetype' },
          { id: 'customize', label: 'Customize' },
          { id: 'preview', label: 'Create' },
        ];

  const currentIndex = steps.findIndex((s) => s.id === step);

  return (
    <div className="px-6 py-3 border-b border-town-accent/10">
      <div className="flex items-center justify-center gap-2">
        {steps.map((s, i) => (
          <div key={s.id} className="flex items-center">
            <div
              className={cn(
                'w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium transition-colors',
                i <= currentIndex
                  ? 'bg-town-highlight text-white'
                  : 'bg-town-surface text-gray-500'
              )}
            >
              {i + 1}
            </div>
            <span
              className={cn(
                'ml-2 text-sm',
                i <= currentIndex ? 'text-white' : 'text-gray-500'
              )}
            >
              {s.label}
            </span>
            {i < steps.length - 1 && (
              <div
                className={cn(
                  'w-8 h-0.5 mx-3',
                  i < currentIndex ? 'bg-town-highlight' : 'bg-town-accent/30'
                )}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default AgentCreationWizard;
