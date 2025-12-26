/**
 * ResolutionDialog: Modal for choosing contradiction resolution strategy.
 *
 * Presents the five resolution strategies with contextual guidance:
 * 1. SYNTHESIZE - Create a new K-Block that resolves both
 * 2. SCOPE - Clarify these apply in different contexts
 * 3. CHOOSE - Decide which you actually believe
 * 4. TOLERATE - Keep both as productive tension
 * 5. IGNORE - Think about it later
 *
 * Design Philosophy:
 * - User always chooses (never forced)
 * - Suggested option highlighted but not enforced
 * - Clear explanation of each strategy
 * - When Synthesize chosen, open editor for new K-Block
 *
 * @see plans/zero-seed-genesis-grand-strategy.md (Phase 4)
 */

import { type ReactNode, useState } from 'react';

export interface ResolutionDialogData {
  contradiction_id: string;
  title: string;
  subtitle: string;
  statement_a: string;
  statement_a_label: string;
  statement_b: string;
  statement_b_label: string;
  strength: number;
  strength_label: string;
  classification_color: string;
  options: Array<{
    value: string;
    label: string;
    description: string;
    icon: string;
    suggested: boolean;
  }>;
  suggested_option: string;
  suggestion_reasoning: string;
}

export interface ResolutionDialogProps {
  data: ResolutionDialogData;
  isOpen: boolean;
  onClose: () => void;
  onResolve: (strategy: string, metadata?: Record<string, unknown>) => void;
  className?: string;
}

/**
 * Map classification color to STARK BIOME color
 */
function getClassificationColor(color: string): string {
  const colorMap: Record<string, string> = {
    gray: 'rgb(var(--steel-zinc))',
    green: 'rgb(var(--glow-spore))',
    yellow: 'rgb(var(--glow-medium))',
    red: 'rgb(var(--steel-rust))',
  };
  return colorMap[color] || colorMap.gray;
}

/**
 * Map strategy icon name to actual icon (placeholder - integrate with icon system)
 */
function getStrategyIcon(icon: string): string {
  const iconMap: Record<string, string> = {
    merge: '⚡',
    scope: '🔍',
    'check-circle': '✓',
    balance: '⚖',
    clock: '⏰',
  };
  return iconMap[icon] || '•';
}

export function ResolutionDialog({
  data,
  isOpen,
  onClose,
  onResolve,
  className = '',
}: ResolutionDialogProps): ReactNode {
  const [selectedStrategy, setSelectedStrategy] = useState<string | null>(
    data.suggested_option
  );

  if (!isOpen) return null;

  const strengthColor = getClassificationColor(data.classification_color);

  const handleResolve = () => {
    if (!selectedStrategy) return;
    onResolve(selectedStrategy);
  };

  return (
    <div className={`fixed inset-0 z-50 flex items-center justify-center ${className}`}>
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-steel-carbon/80 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Dialog */}
      <div className="relative w-full max-w-3xl max-h-[90vh] overflow-y-auto bg-steel-carbon border border-steel-gunmetal rounded-lg shadow-2xl">
        {/* Header */}
        <div className="sticky top-0 bg-steel-carbon border-b border-steel-gunmetal p-6">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-2xl font-medium text-glow-light">
                {data.title}
              </h2>
              <p className="text-sm text-steel-zinc mt-2">
                {data.subtitle}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-steel-zinc hover:text-glow-light transition-colors"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 flex flex-col gap-6">
          {/* Strength Indicator */}
          <div className="flex items-center gap-3">
            <span className="text-sm text-steel-zinc">Strength:</span>
            <span
              className="text-sm font-medium"
              style={{ color: strengthColor }}
            >
              {data.strength_label}
            </span>
          </div>

          {/* Statements */}
          <div className="grid grid-cols-2 gap-4">
            {/* Statement A */}
            <div className="flex flex-col gap-2 p-4 bg-steel-carbon/30 rounded border border-steel-gunmetal">
              <div className="text-xs text-steel-zinc uppercase tracking-wide">
                {data.statement_a_label}
              </div>
              <div className="text-sm text-glow-light leading-relaxed">
                {data.statement_a}
              </div>
            </div>

            {/* Statement B */}
            <div className="flex flex-col gap-2 p-4 bg-steel-carbon/30 rounded border border-steel-gunmetal">
              <div className="text-xs text-steel-zinc uppercase tracking-wide">
                {data.statement_b_label}
              </div>
              <div className="text-sm text-glow-light leading-relaxed">
                {data.statement_b}
              </div>
            </div>
          </div>

          {/* Suggestion Reasoning */}
          <div className="p-4 bg-glow-spore/5 rounded border border-glow-spore/20">
            <div className="text-sm text-steel-zinc leading-relaxed whitespace-pre-line">
              {data.suggestion_reasoning}
            </div>
          </div>

          {/* Resolution Options */}
          <div className="flex flex-col gap-3">
            <div className="text-sm font-medium text-glow-light mb-2">
              Choose how to resolve:
            </div>
            {data.options.map((option) => {
              const isSelected = selectedStrategy === option.value;
              const isSuggested = option.suggested;

              return (
                <button
                  key={option.value}
                  onClick={() => setSelectedStrategy(option.value)}
                  className={`
                    flex items-start gap-4 p-4 rounded transition-all
                    ${
                      isSelected
                        ? 'bg-glow-spore/10 border-2 border-glow-spore'
                        : 'bg-steel-carbon/30 border border-steel-gunmetal hover:border-glow-spore/50'
                    }
                  `}
                >
                  {/* Icon */}
                  <div
                    className={`
                      text-2xl flex-shrink-0
                      ${isSelected ? 'text-glow-spore' : 'text-steel-zinc'}
                    `}
                  >
                    {getStrategyIcon(option.icon)}
                  </div>

                  {/* Content */}
                  <div className="flex-1 text-left">
                    <div className="flex items-center gap-2">
                      <span
                        className={`
                          font-medium
                          ${isSelected ? 'text-glow-light' : 'text-steel-zinc'}
                        `}
                      >
                        {option.label}
                      </span>
                      {isSuggested && (
                        <span className="text-xs px-2 py-1 bg-glow-spore/20 text-glow-spore rounded">
                          Suggested
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-steel-zinc mt-1">
                      {option.description}
                    </div>
                  </div>

                  {/* Selection Indicator */}
                  <div
                    className={`
                      flex-shrink-0 w-5 h-5 rounded-full border-2 flex items-center justify-center
                      ${
                        isSelected
                          ? 'border-glow-spore bg-glow-spore'
                          : 'border-steel-gunmetal'
                      }
                    `}
                  >
                    {isSelected && (
                      <div className="w-2 h-2 bg-steel-carbon rounded-full" />
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-steel-carbon border-t border-steel-gunmetal p-6 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-6 py-2 rounded text-sm font-medium bg-steel-carbon text-glow-light border border-steel-gunmetal hover:border-glow-spore transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleResolve}
            disabled={!selectedStrategy}
            className={`
              px-6 py-2 rounded text-sm font-medium transition-colors
              ${
                selectedStrategy
                  ? 'bg-glow-spore text-steel-carbon hover:bg-glow-medium'
                  : 'bg-steel-gunmetal text-steel-zinc cursor-not-allowed'
              }
            `}
          >
            Apply Resolution
          </button>
        </div>
      </div>
    </div>
  );
}

export default ResolutionDialog;
