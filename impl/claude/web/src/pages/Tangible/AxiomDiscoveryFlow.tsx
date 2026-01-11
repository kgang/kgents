/**
 * AxiomDiscoveryFlow - 5-turn dialogue for discovering user axioms
 *
 * A structured flow that helps users articulate their endeavor axioms:
 * A1: What does success look like?
 * A2: What do you want to feel?
 * A3: What's non-negotiable?
 * A4: How will you know it's working?
 * A5: Confirmation
 */

import { memo, useState, useCallback, useRef, useEffect, useMemo } from 'react';
import {
  Compass,
  Heart,
  Shield,
  Target,
  Check,
  X,
  ChevronRight,
  ChevronLeft,
  Sparkles,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

import type {
  AxiomDiscoveryFlowProps,
  AxiomDiscoveryStep,
  EndeavorAxioms,
} from './actualize-types';
import { AXIOM_STEPS } from './actualize-types';

// =============================================================================
// Step Icons
// =============================================================================

const STEP_ICONS: Record<AxiomDiscoveryStep, LucideIcon> = {
  A1: Compass,
  A2: Heart,
  A3: Shield,
  A4: Target,
  A5: Check,
};

const STEP_COLORS: Record<AxiomDiscoveryStep, string> = {
  A1: '#3b82f6', // blue
  A2: '#ec4899', // pink
  A3: '#22c55e', // green
  A4: '#f59e0b', // amber
  A5: '#8b5cf6', // purple
};

// =============================================================================
// Step Indicator
// =============================================================================

interface StepIndicatorProps {
  currentStep: AxiomDiscoveryStep;
  completedSteps: AxiomDiscoveryStep[];
}

const StepIndicator = memo(function StepIndicator({
  currentStep,
  completedSteps,
}: StepIndicatorProps) {
  const steps: AxiomDiscoveryStep[] = ['A1', 'A2', 'A3', 'A4', 'A5'];

  return (
    <div className="axiom-discovery__steps">
      {steps.map((step, index) => {
        const Icon = STEP_ICONS[step];
        const isActive = step === currentStep;
        const isComplete = completedSteps.includes(step);
        const color = STEP_COLORS[step];

        return (
          <div key={step} className="axiom-discovery__step-item">
            <div
              className={`axiom-discovery__step-icon ${isActive ? 'axiom-discovery__step-icon--active' : ''} ${isComplete ? 'axiom-discovery__step-icon--complete' : ''}`}
              style={{ borderColor: color, color: isActive || isComplete ? color : undefined }}
            >
              <Icon size={14} />
            </div>
            {index < steps.length - 1 && (
              <div
                className={`axiom-discovery__step-line ${isComplete ? 'axiom-discovery__step-line--complete' : ''}`}
                style={{ backgroundColor: isComplete ? color : undefined }}
              />
            )}
          </div>
        );
      })}
    </div>
  );
});

// =============================================================================
// Axiom Input
// =============================================================================

interface AxiomInputProps {
  step: AxiomDiscoveryStep;
  value: string;
  onChange: (value: string) => void;
  onNext: () => void;
  onBack: () => void;
  isFirst: boolean;
  isLast: boolean;
}

const AxiomInput = memo(function AxiomInput({
  step,
  value,
  onChange,
  onNext,
  onBack,
  isFirst,
  isLast,
}: AxiomInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const stepConfig = AXIOM_STEPS[step];
  const Icon = STEP_ICONS[step];
  const color = STEP_COLORS[step];

  // Focus textarea on mount
  useEffect(() => {
    textareaRef.current?.focus();
  }, [step]);

  // Handle Enter key (Shift+Enter for newline)
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (value.trim()) {
          onNext();
        }
      }
    },
    [value, onNext]
  );

  return (
    <div className="axiom-discovery__input">
      <div className="axiom-discovery__question">
        <Icon size={20} style={{ color }} />
        <span>{stepConfig.question}</span>
      </div>

      <textarea
        ref={textareaRef}
        className="axiom-discovery__textarea"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={stepConfig.placeholder}
        rows={4}
      />

      <div className="axiom-discovery__actions">
        {!isFirst && (
          <button className="axiom-discovery__btn axiom-discovery__btn--secondary" onClick={onBack}>
            <ChevronLeft size={14} />
            Back
          </button>
        )}
        <button
          className="axiom-discovery__btn axiom-discovery__btn--primary"
          onClick={onNext}
          disabled={!value.trim()}
          style={{ backgroundColor: value.trim() ? color : undefined }}
        >
          {isLast ? (
            <>
              <Check size={14} />
              Confirm
            </>
          ) : (
            <>
              Next
              <ChevronRight size={14} />
            </>
          )}
        </button>
      </div>
    </div>
  );
});

// =============================================================================
// Confirmation View
// =============================================================================

interface ConfirmationViewProps {
  responses: Partial<EndeavorAxioms>;
  onConfirm: () => void;
  onBack: () => void;
}

const ConfirmationView = memo(function ConfirmationView({
  responses,
  onConfirm,
  onBack,
}: ConfirmationViewProps) {
  const axiomEntries = [
    { step: 'A1' as const, label: 'Success looks like', value: responses.A1_success },
    { step: 'A2' as const, label: 'You want to feel', value: responses.A2_feeling },
    { step: 'A3' as const, label: 'Non-negotiable', value: responses.A3_nonnegotiable },
    { step: 'A4' as const, label: 'Validation signal', value: responses.A4_validation },
  ];

  return (
    <div className="axiom-discovery__confirmation">
      <div className="axiom-discovery__confirm-header">
        <Sparkles size={20} />
        <span>Your Axioms</span>
      </div>

      <div className="axiom-discovery__confirm-endeavor">
        <span className="axiom-discovery__confirm-label">Endeavor</span>
        <span className="axiom-discovery__confirm-value">{responses.endeavor}</span>
      </div>

      <div className="axiom-discovery__confirm-list">
        {axiomEntries.map(({ step, label, value }) => {
          const Icon = STEP_ICONS[step];
          const color = STEP_COLORS[step];
          return (
            <div key={step} className="axiom-discovery__confirm-item">
              <div className="axiom-discovery__confirm-item-header">
                <Icon size={14} style={{ color }} />
                <span className="axiom-discovery__confirm-label">{label}</span>
              </div>
              <div className="axiom-discovery__confirm-value">{value}</div>
            </div>
          );
        })}
      </div>

      <div className="axiom-discovery__actions">
        <button className="axiom-discovery__btn axiom-discovery__btn--secondary" onClick={onBack}>
          <ChevronLeft size={14} />
          Edit
        </button>
        <button
          className="axiom-discovery__btn axiom-discovery__btn--primary"
          onClick={onConfirm}
          style={{ backgroundColor: STEP_COLORS.A5 }}
        >
          <Check size={14} />
          Begin Journey
        </button>
      </div>
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const AxiomDiscoveryFlow = memo(function AxiomDiscoveryFlow({
  endeavor,
  onComplete,
  onCancel,
}: AxiomDiscoveryFlowProps) {
  const [step, setStep] = useState<AxiomDiscoveryStep>('A1');
  const [responses, setResponses] = useState<Partial<EndeavorAxioms>>({
    endeavor,
  });

  const steps: AxiomDiscoveryStep[] = useMemo(() => ['A1', 'A2', 'A3', 'A4', 'A5'], []);
  const stepIndex = steps.indexOf(step);

  const completedSteps = steps.filter((s) => {
    const idx = steps.indexOf(s);
    return idx < stepIndex;
  });

  const getCurrentValue = (): string => {
    switch (step) {
      case 'A1':
        return responses.A1_success || '';
      case 'A2':
        return responses.A2_feeling || '';
      case 'A3':
        return responses.A3_nonnegotiable || '';
      case 'A4':
        return responses.A4_validation || '';
      default:
        return '';
    }
  };

  const setCurrentValue = (value: string) => {
    switch (step) {
      case 'A1':
        setResponses((r) => ({ ...r, A1_success: value }));
        break;
      case 'A2':
        setResponses((r) => ({ ...r, A2_feeling: value }));
        break;
      case 'A3':
        setResponses((r) => ({ ...r, A3_nonnegotiable: value }));
        break;
      case 'A4':
        setResponses((r) => ({ ...r, A4_validation: value }));
        break;
    }
  };

  const handleNext = useCallback(() => {
    if (stepIndex < steps.length - 1) {
      setStep(steps[stepIndex + 1]);
    }
  }, [stepIndex, steps]);

  const handleBack = useCallback(() => {
    if (stepIndex > 0) {
      setStep(steps[stepIndex - 1]);
    }
  }, [stepIndex, steps]);

  const handleConfirm = useCallback(() => {
    const axioms: EndeavorAxioms = {
      endeavor: responses.endeavor || '',
      A1_success: responses.A1_success || '',
      A2_feeling: responses.A2_feeling || '',
      A3_nonnegotiable: responses.A3_nonnegotiable || '',
      A4_validation: responses.A4_validation || '',
      confirmedAt: new Date(),
    };
    onComplete(axioms);
  }, [responses, onComplete]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onCancel();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onCancel]);

  return (
    <div className="axiom-discovery">
      <div className="axiom-discovery__header">
        <div className="axiom-discovery__title">
          <Sparkles size={16} />
          <span>Discover Your Axioms</span>
        </div>
        <button className="axiom-discovery__close" onClick={onCancel} aria-label="Cancel">
          <X size={16} />
        </button>
      </div>

      <div className="axiom-discovery__endeavor">
        <span className="axiom-discovery__endeavor-label">Your Endeavor</span>
        <span className="axiom-discovery__endeavor-value">&quot;{endeavor}&quot;</span>
      </div>

      <StepIndicator currentStep={step} completedSteps={completedSteps} />

      <div className="axiom-discovery__content">
        {step === 'A5' ? (
          <ConfirmationView responses={responses} onConfirm={handleConfirm} onBack={handleBack} />
        ) : (
          <AxiomInput
            step={step}
            value={getCurrentValue()}
            onChange={setCurrentValue}
            onNext={handleNext}
            onBack={handleBack}
            isFirst={stepIndex === 0}
            isLast={stepIndex === steps.length - 2}
          />
        )}
      </div>
    </div>
  );
});

export default AxiomDiscoveryFlow;
