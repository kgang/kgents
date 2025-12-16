/**
 * ProgressWidget: Progress bar and step indicator.
 *
 * Two variants:
 * - bar: Traditional progress bar with percentage
 * - steps: Step indicator for multi-step processes
 */

import React from 'react';

export type ProgressVariant = 'bar' | 'steps';

export interface ProgressStep {
  label: string;
  completed: boolean;
  current?: boolean;
}

export interface ProgressWidgetProps {
  /** Progress value 0-100 (for bar variant) */
  value?: number;
  /** Variant type */
  variant?: ProgressVariant;
  /** Label to display */
  label?: string;
  /** Steps for step variant */
  steps?: ProgressStep[];
  /** Indeterminate state */
  indeterminate?: boolean;
}

function ProgressBar({
  value,
  label,
  indeterminate,
}: {
  value: number;
  label?: string;
  indeterminate?: boolean;
}) {
  const clampedValue = Math.max(0, Math.min(100, value));

  return (
    <div className="kgents-progress-bar" style={{ width: '100%' }}>
      {label && (
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginBottom: '4px',
            fontSize: '14px',
          }}
        >
          <span>{label}</span>
          {!indeterminate && <span>{clampedValue}%</span>}
        </div>
      )}
      <div
        style={{
          height: '8px',
          backgroundColor: '#e5e7eb',
          borderRadius: '4px',
          overflow: 'hidden',
        }}
        role="progressbar"
        aria-valuenow={indeterminate ? undefined : clampedValue}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label || 'Progress'}
      >
        <div
          style={{
            height: '100%',
            backgroundColor: '#3b82f6',
            borderRadius: '4px',
            transition: 'width 0.3s ease',
            width: indeterminate ? '30%' : `${clampedValue}%`,
            animation: indeterminate ? 'kgents-progress-slide 1.5s infinite' : undefined,
          }}
        />
      </div>
      {indeterminate && (
        <style>{`
          @keyframes kgents-progress-slide {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(400%); }
          }
        `}</style>
      )}
    </div>
  );
}

function ProgressSteps({ steps }: { steps: ProgressStep[] }) {
  return (
    <div className="kgents-progress-steps" style={{ display: 'flex', alignItems: 'center' }}>
      {steps.map((step, i) => (
        <React.Fragment key={i}>
          {/* Step indicator */}
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '14px',
                fontWeight: 600,
                backgroundColor: step.completed
                  ? '#10b981'
                  : step.current
                    ? '#3b82f6'
                    : '#e5e7eb',
                color: step.completed || step.current ? 'white' : '#6b7280',
                border: step.current ? '2px solid #60a5fa' : 'none',
              }}
              aria-current={step.current ? 'step' : undefined}
            >
              {step.completed ? '✓' : i + 1}
            </div>
            <span
              style={{
                fontSize: '12px',
                color: step.current ? '#1f2937' : '#6b7280',
                fontWeight: step.current ? 600 : 400,
                textAlign: 'center',
                maxWidth: '80px',
              }}
            >
              {step.label}
            </span>
          </div>

          {/* Connector line */}
          {i < steps.length - 1 && (
            <div
              style={{
                flex: 1,
                height: '2px',
                backgroundColor: step.completed ? '#10b981' : '#e5e7eb',
                margin: '0 8px',
                marginBottom: '20px',
              }}
            />
          )}
        </React.Fragment>
      ))}
    </div>
  );
}

export function ProgressWidget({
  value = 0,
  variant = 'bar',
  label,
  steps,
  indeterminate = false,
}: ProgressWidgetProps) {
  if (variant === 'steps' && steps) {
    return <ProgressSteps steps={steps} />;
  }

  return <ProgressBar value={value} label={label} indeterminate={indeterminate} />;
}

export default ProgressWidget;
