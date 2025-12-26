/**
 * LossIndicator Examples
 *
 * Showcases all variants and usage patterns.
 */

import { useState } from 'react';
import { LossIndicator } from './LossIndicator';
import { LossGradient } from './LossGradient';
import { LossHeatmap } from './LossHeatmap';
import { WithLoss } from './WithLoss';

export function LossIndicatorExample() {
  const [loss, setLoss] = useState(0.42);

  return (
    <div
      style={{
        padding: 'var(--space-xl, 1.75rem)',
        background: 'var(--surface-0, #0a0a0c)',
        color: 'var(--text-primary, #e5e7eb)',
        minHeight: '100vh',
      }}
    >
      <h1 style={{ marginBottom: 'var(--space-xl, 1.75rem)' }}>Loss Primitives Examples</h1>

      {/* Section 1: LossIndicator */}
      <section style={{ marginBottom: 'var(--space-2xl, 2.5rem)' }}>
        <h2 style={{ marginBottom: 'var(--space-lg, 1.25rem)' }}>LossIndicator</h2>

        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-lg, 1.25rem)',
          }}
        >
          {/* Basic */}
          <div>
            <h3 style={{ fontSize: '0.875rem', marginBottom: 'var(--space-sm, 0.4rem)' }}>
              Basic (dot only)
            </h3>
            <LossIndicator loss={0.15} showLabel={false} />
          </div>

          {/* With label */}
          <div>
            <h3 style={{ fontSize: '0.875rem', marginBottom: 'var(--space-sm, 0.4rem)' }}>
              With label
            </h3>
            <LossIndicator loss={0.35} showLabel />
          </div>

          {/* With gradient */}
          <div>
            <h3 style={{ fontSize: '0.875rem', marginBottom: 'var(--space-sm, 0.4rem)' }}>
              With gradient bar
            </h3>
            <LossIndicator loss={0.65} showLabel showGradient />
          </div>

          {/* Interactive */}
          <div>
            <h3 style={{ fontSize: '0.875rem', marginBottom: 'var(--space-sm, 0.4rem)' }}>
              Interactive with navigation
            </h3>
            <LossIndicator
              loss={loss}
              showLabel
              showGradient
              interactive
              onNavigate={(direction) => {
                const delta = direction === 'lower' ? -0.1 : 0.1;
                setLoss(Math.max(0, Math.min(1, loss + delta)));
              }}
            />
          </div>

          {/* Size variants */}
          <div>
            <h3 style={{ fontSize: '0.875rem', marginBottom: 'var(--space-sm, 0.4rem)' }}>
              Size variants
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md, 0.85rem)' }}>
              <LossIndicator loss={0.25} size="sm" showLabel />
              <LossIndicator loss={0.25} size="md" showLabel />
              <LossIndicator loss={0.25} size="lg" showLabel />
            </div>
          </div>

          {/* Loss spectrum */}
          <div>
            <h3 style={{ fontSize: '0.875rem', marginBottom: 'var(--space-sm, 0.4rem)' }}>
              Loss spectrum (0.00 → 1.00)
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm, 0.4rem)' }}>
              <LossIndicator loss={0.0} showLabel />
              <LossIndicator loss={0.2} showLabel />
              <LossIndicator loss={0.4} showLabel />
              <LossIndicator loss={0.6} showLabel />
              <LossIndicator loss={0.8} showLabel />
              <LossIndicator loss={1.0} showLabel />
            </div>
          </div>
        </div>
      </section>

      {/* Section 2: LossGradient */}
      <section style={{ marginBottom: 'var(--space-2xl, 2.5rem)' }}>
        <h2 style={{ marginBottom: 'var(--space-lg, 1.25rem)' }}>LossGradient</h2>

        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-lg, 1.25rem)',
          }}
        >
          {/* Basic */}
          <div>
            <h3 style={{ fontSize: '0.875rem', marginBottom: 'var(--space-sm, 0.4rem)' }}>
              Basic with current position
            </h3>
            <LossGradient
              currentLoss={loss}
              onNavigate={(targetLoss) => setLoss(targetLoss)}
            />
          </div>

          {/* Without ticks */}
          <div>
            <h3 style={{ fontSize: '0.875rem', marginBottom: 'var(--space-sm, 0.4rem)' }}>
              Without tick marks
            </h3>
            <LossGradient
              currentLoss={loss}
              showTicks={false}
              onNavigate={(targetLoss) => setLoss(targetLoss)}
            />
          </div>

          {/* Custom dimensions */}
          <div>
            <h3 style={{ fontSize: '0.875rem', marginBottom: 'var(--space-sm, 0.4rem)' }}>
              Custom dimensions
            </h3>
            <LossGradient
              currentLoss={loss}
              width="300px"
              height="24px"
              onNavigate={(targetLoss) => setLoss(targetLoss)}
            />
          </div>
        </div>
      </section>

      {/* Section 3: LossHeatmap */}
      <section style={{ marginBottom: 'var(--space-2xl, 2.5rem)' }}>
        <h2 style={{ marginBottom: 'var(--space-lg, 1.25rem)' }}>LossHeatmap</h2>

        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-lg, 1.25rem)',
          }}
        >
          {/* Grid layout */}
          <div>
            <h3 style={{ fontSize: '0.875rem', marginBottom: 'var(--space-sm, 0.4rem)' }}>
              Grid layout (4 columns)
            </h3>
            <LossHeatmap
              items={[
                { id: '1', label: 'Axiom', loss: 0.05 },
                { id: '2', label: 'Value', loss: 0.15 },
                { id: '3', label: 'Capability', loss: 0.35 },
                { id: '4', label: 'Domain', loss: 0.55 },
                { id: '5', label: 'Service', loss: 0.65 },
                { id: '6', label: 'Construction', loss: 0.75 },
                { id: '7', label: 'Implementation', loss: 0.85 },
                { id: '8', label: 'Deprecated', loss: 0.95 },
              ]}
              columns={4}
            />
          </div>

          {/* List layout */}
          <div>
            <h3 style={{ fontSize: '0.875rem', marginBottom: 'var(--space-sm, 0.4rem)' }}>
              List layout
            </h3>
            <LossHeatmap
              items={[
                { id: '1', label: 'Axiom Layer', loss: 0.05 },
                { id: '2', label: 'Value Layer', loss: 0.25 },
                { id: '3', label: 'Domain Layer', loss: 0.65 },
              ]}
              layout="list"
            />
          </div>
        </div>
      </section>

      {/* Section 4: WithLoss */}
      <section style={{ marginBottom: 'var(--space-2xl, 2.5rem)' }}>
        <h2 style={{ marginBottom: 'var(--space-lg, 1.25rem)' }}>WithLoss</h2>

        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--space-lg, 1.25rem)',
          }}
        >
          {/* Top-right (default) */}
          <div>
            <h3 style={{ fontSize: '0.875rem', marginBottom: 'var(--space-sm, 0.4rem)' }}>
              Top-right position (default)
            </h3>
            <WithLoss loss={0.42}>
              <div
                style={{
                  padding: 'var(--space-lg, 1.25rem)',
                  background: 'var(--surface-1, #141418)',
                  border: '1px solid var(--border-subtle, #28282f)',
                  borderRadius: 'var(--radius-bare, 2px)',
                }}
              >
                <h4 style={{ marginBottom: 'var(--space-sm, 0.4rem)' }}>Sample K-Block</h4>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary, #8a8a94)' }}>
                  This is a sample component wrapped with loss indicator.
                </p>
              </div>
            </WithLoss>
          </div>

          {/* Top-left with label */}
          <div>
            <h3 style={{ fontSize: '0.875rem', marginBottom: 'var(--space-sm, 0.4rem)' }}>
              Top-left with label
            </h3>
            <WithLoss loss={0.65} position="top-left" showLabel>
              <div
                style={{
                  padding: 'var(--space-lg, 1.25rem)',
                  background: 'var(--surface-1, #141418)',
                  border: '1px solid var(--border-subtle, #28282f)',
                  borderRadius: 'var(--radius-bare, 2px)',
                }}
              >
                <h4 style={{ marginBottom: 'var(--space-sm, 0.4rem)' }}>Another K-Block</h4>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary, #8a8a94)' }}>
                  This one has a label showing the loss value.
                </p>
              </div>
            </WithLoss>
          </div>

          {/* Bottom-right with gradient */}
          <div>
            <h3 style={{ fontSize: '0.875rem', marginBottom: 'var(--space-sm, 0.4rem)' }}>
              Bottom-right with gradient
            </h3>
            <WithLoss loss={0.85} position="bottom-right" showGradient showLabel>
              <div
                style={{
                  padding: 'var(--space-lg, 1.25rem)',
                  background: 'var(--surface-1, #141418)',
                  border: '1px solid var(--border-subtle, #28282f)',
                  borderRadius: 'var(--radius-bare, 2px)',
                }}
              >
                <h4 style={{ marginBottom: 'var(--space-sm, 0.4rem)' }}>High Loss K-Block</h4>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary, #8a8a94)' }}>
                  This block has high loss and needs attention.
                </p>
              </div>
            </WithLoss>
          </div>
        </div>
      </section>
    </div>
  );
}

export default LossIndicatorExample;
