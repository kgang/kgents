/**
 * SynthesisPanel - The Fusion Result Display
 *
 * The center panel showing the synthesis result after sublation (Aufhebung).
 * "Not compromise (which loses information), but Aufhebung (which transcends both)."
 *
 * Design: STARK BIOME with earned glow for the synthesis moment.
 */

import { memo } from 'react';
import {
  getFusionResultLabel,
  getFusionResultIcon,
  getFusionResultClass,
  formatTrustDelta,
  type FusionResult,
} from '@/api/dialectic';
import type { SynthesisPanelProps } from './types';

/**
 * Get the CSS class for trust delta display.
 */
function getTrustDeltaClass(delta: number): string {
  if (delta > 0) return 'trust-delta--positive';
  if (delta < 0) return 'trust-delta--negative';
  return 'trust-delta--neutral';
}

/**
 * Loading skeleton for the synthesis panel.
 */
function SynthesisSkeleton() {
  return (
    <div className="fusion-synthesis__skeleton">
      <div className="fusion-synthesis__skeleton-pulse" />
      <div className="fusion-synthesis__skeleton-text">Synthesizing positions...</div>
      <div className="fusion-synthesis__skeleton-subtitle">The cocone is forming</div>
    </div>
  );
}

/**
 * Empty state when no synthesis yet.
 */
function SynthesisEmpty() {
  return (
    <div className="fusion-synthesis__empty">
      <div className="fusion-synthesis__empty-icon">+</div>
      <div className="fusion-synthesis__empty-text">Enter both positions to synthesize</div>
      <div className="fusion-synthesis__empty-subtitle">The fusion awaits</div>
    </div>
  );
}

/**
 * Result badge component.
 */
function ResultBadge({ result }: { result: FusionResult }) {
  return (
    <div className={`fusion-result-badge ${getFusionResultClass(result)}`}>
      <span className="fusion-result-badge__icon">{getFusionResultIcon(result)}</span>
      <span className="fusion-result-badge__label">{getFusionResultLabel(result)}</span>
    </div>
  );
}

/**
 * SynthesisPanel Component
 *
 * Shows the result of dialectical fusion:
 * - What was preserved from Kent
 * - What was preserved from Claude
 * - What transcends both
 * - The trust delta
 *
 * @example
 * <SynthesisPanel
 *   synthesis={synthesis}
 *   result={result}
 *   reasoning={reasoning}
 *   trustDelta={trustDelta}
 * />
 */
export const SynthesisPanel = memo(function SynthesisPanel({
  synthesis,
  result,
  reasoning,
  trustDelta,
  loading = false,
  className = '',
}: SynthesisPanelProps) {
  // Loading state
  if (loading) {
    return (
      <div className={`fusion-panel fusion-panel--synthesis ${className}`}>
        <div className="fusion-panel__header fusion-panel__header--synthesis">
          <span className="fusion-panel__badge fusion-panel__badge--synthesis">+</span>
          <h3 className="fusion-panel__title">Synthesis</h3>
          <span className="fusion-panel__subtitle">Aufhebung</span>
        </div>
        <div className="fusion-panel__content">
          <SynthesisSkeleton />
        </div>
      </div>
    );
  }

  // Empty state
  if (!synthesis && !result) {
    return (
      <div className={`fusion-panel fusion-panel--synthesis ${className}`}>
        <div className="fusion-panel__header fusion-panel__header--synthesis">
          <span className="fusion-panel__badge fusion-panel__badge--synthesis">+</span>
          <h3 className="fusion-panel__title">Synthesis</h3>
          <span className="fusion-panel__subtitle">Aufhebung</span>
        </div>
        <div className="fusion-panel__content">
          <SynthesisEmpty />
        </div>
      </div>
    );
  }

  return (
    <div className={`fusion-panel fusion-panel--synthesis fusion-panel--complete ${className}`}>
      {/* Panel Header */}
      <div className="fusion-panel__header fusion-panel__header--synthesis">
        <span className="fusion-panel__badge fusion-panel__badge--synthesis">+</span>
        <h3 className="fusion-panel__title">Synthesis</h3>
        {result && <ResultBadge result={result} />}
      </div>

      {/* Panel Content */}
      <div className="fusion-panel__content">
        {/* Trust Delta */}
        {trustDelta !== null && (
          <div className={`fusion-trust-delta ${getTrustDeltaClass(trustDelta)}`}>
            <span className="fusion-trust-delta__label">Trust Delta</span>
            <span className="fusion-trust-delta__value">{formatTrustDelta(trustDelta)}</span>
          </div>
        )}

        {/* Synthesis Content */}
        {synthesis && (
          <>
            {/* The Synthesis */}
            <div className="fusion-synthesis-block fusion-synthesis-block--main">
              <div className="fusion-synthesis-block__label">The Synthesis</div>
              <div className="fusion-synthesis-block__content">{synthesis.content}</div>
            </div>

            {/* Reasoning */}
            {synthesis.reasoning && (
              <div className="fusion-synthesis-block fusion-synthesis-block--reasoning">
                <div className="fusion-synthesis-block__label">Reasoning</div>
                <div className="fusion-synthesis-block__content">{synthesis.reasoning}</div>
              </div>
            )}

            {/* Preservation Section */}
            <div className="fusion-preservation">
              {/* Preserved from Kent */}
              <div className="fusion-preservation__item fusion-preservation__item--kent">
                <div className="fusion-preservation__badge">K</div>
                <div className="fusion-preservation__content">
                  <div className="fusion-preservation__label">Preserved from Kent</div>
                  <div className="fusion-preservation__text">
                    {synthesis.preservedFromKent || '(Nothing explicit)'}
                  </div>
                </div>
              </div>

              {/* Preserved from Claude */}
              <div className="fusion-preservation__item fusion-preservation__item--claude">
                <div className="fusion-preservation__badge">C</div>
                <div className="fusion-preservation__content">
                  <div className="fusion-preservation__label">Preserved from Claude</div>
                  <div className="fusion-preservation__text">
                    {synthesis.preservedFromClaude || '(Nothing explicit)'}
                  </div>
                </div>
              </div>
            </div>

            {/* What Transcends */}
            {synthesis.transcends && (
              <div className="fusion-synthesis-block fusion-synthesis-block--transcends">
                <div className="fusion-synthesis-block__label">What Transcends Both</div>
                <div className="fusion-synthesis-block__content">{synthesis.transcends}</div>
              </div>
            )}
          </>
        )}

        {/* Fallback: Just show reasoning if no full synthesis */}
        {!synthesis && reasoning && (
          <div className="fusion-synthesis-block fusion-synthesis-block--reasoning">
            <div className="fusion-synthesis-block__label">Decision Reasoning</div>
            <div className="fusion-synthesis-block__content">{reasoning}</div>
          </div>
        )}
      </div>

      {/* Panel Footer */}
      <div className="fusion-panel__footer fusion-panel__footer--synthesis">
        <span className="fusion-panel__hint">Individual ego dissolved into shared purpose.</span>
      </div>
    </div>
  );
});

export default SynthesisPanel;
