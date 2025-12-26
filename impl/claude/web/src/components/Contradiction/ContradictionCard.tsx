/**
 * ContradictionCard: Display detected contradictions between K-Blocks.
 *
 * Shows two statements side-by-side with strength indicator and resolution options.
 * Follows the Zero Seed principle: "This is INFORMATION, not JUDGMENT."
 *
 * Design Philosophy:
 * - Warm, non-judgmental tone
 * - Clear visual hierarchy
 * - Backend-driven presentation (no logic in frontend)
 * - STARK BIOME aesthetic with strength-based coloring
 *
 * @see plans/zero-seed-genesis-grand-strategy.md (Phase 4)
 */

import { type ReactNode } from 'react';
import { ElasticCard } from '@/components/elastic/ElasticCard';

export interface ContradictionCardData {
  id: string;
  title: string;
  statement_a: string;
  statement_a_label: string;
  statement_b: string;
  statement_b_label: string;
  strength: number;
  strength_label: string;
  strength_percentage: number;
  classification: {
    type: string;
    color: string;
    description: string;
  };
  guidance: {
    title: string;
    text: string;
    suggested_action: string;
  };
  actions: Array<{
    value: string;
    label: string;
    icon: string;
    variant: string;
  }>;
}

export interface ContradictionCardProps {
  data: ContradictionCardData;
  onAction?: (action: string) => void;
  className?: string;
}

/**
 * Map classification color to STARK BIOME color
 */
function getClassificationColor(color: string): string {
  const colorMap: Record<string, string> = {
    gray: 'rgb(var(--steel-zinc))',      // APPARENT - neutral
    green: 'rgb(var(--glow-spore))',     // PRODUCTIVE - opportunity
    yellow: 'rgb(var(--glow-medium))',   // TENSION - warning
    red: 'rgb(var(--steel-rust))',       // FUNDAMENTAL - critical
  };
  return colorMap[color] || colorMap.gray;
}

export function ContradictionCard({
  data,
  onAction,
  className = '',
}: ContradictionCardProps): ReactNode {
  const strengthColor = getClassificationColor(data.classification.color);

  return (
    <ElasticCard
      className={`contradiction-card ${className}`}
      priority={2}
      minContent="summary"
    >
      <div className="flex flex-col gap-4 p-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-lg font-medium text-glow-light">
              {data.title}
            </h3>
            <p className="text-sm text-steel-zinc mt-1">
              {data.classification.description}
            </p>
          </div>
        </div>

        {/* Strength Indicator */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-steel-zinc">Contradiction Strength</span>
            <span
              className="font-medium"
              style={{ color: strengthColor }}
            >
              {data.strength_label}
            </span>
          </div>
          <div className="w-full h-2 bg-steel-carbon rounded-full overflow-hidden">
            <div
              className="h-full transition-all duration-500"
              style={{
                width: `${data.strength_percentage}%`,
                backgroundColor: strengthColor,
              }}
            />
          </div>
        </div>

        {/* Statements Side-by-Side */}
        <div className="grid grid-cols-2 gap-4">
          {/* Statement A */}
          <div className="flex flex-col gap-2 p-3 bg-steel-carbon/30 rounded border border-steel-gunmetal">
            <div className="text-xs text-steel-zinc uppercase tracking-wide">
              {data.statement_a_label}
            </div>
            <div className="text-sm text-glow-light">
              {data.statement_a}
            </div>
          </div>

          {/* Statement B */}
          <div className="flex flex-col gap-2 p-3 bg-steel-carbon/30 rounded border border-steel-gunmetal">
            <div className="text-xs text-steel-zinc uppercase tracking-wide">
              {data.statement_b_label}
            </div>
            <div className="text-sm text-glow-light">
              {data.statement_b}
            </div>
          </div>
        </div>

        {/* Guidance */}
        <div className="flex flex-col gap-2 p-3 bg-glow-spore/5 rounded border border-glow-spore/20">
          <div className="text-sm font-medium text-glow-medium">
            {data.guidance.title}
          </div>
          <div className="text-sm text-steel-zinc">
            {data.guidance.text}
          </div>
          {data.guidance.suggested_action && (
            <div className="text-sm text-glow-light mt-2">
              {data.guidance.suggested_action}
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-2 justify-end">
          {data.actions.map((action) => (
            <button
              key={action.value}
              onClick={() => onAction?.(action.value)}
              className={`
                px-4 py-2 rounded text-sm font-medium transition-colors
                ${
                  action.variant === 'primary'
                    ? 'bg-glow-spore text-steel-carbon hover:bg-glow-medium'
                    : 'bg-steel-carbon text-glow-light border border-steel-gunmetal hover:border-glow-spore'
                }
              `}
            >
              {action.label}
            </button>
          ))}
        </div>
      </div>
    </ElasticCard>
  );
}

export default ContradictionCard;
