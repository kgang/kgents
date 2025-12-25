/**
 * ValueCompass Example
 *
 * Demonstrates the ValueCompass primitive with:
 * - Static scores
 * - Trajectory animation
 * - Attractor visualization
 */

import { useState, useEffect } from 'react';
import { ValueCompass } from './ValueCompass';
import type { ConstitutionScores, PersonalityAttractor } from '@/types/theory';

// Example: Kent's personality attractor (high tasteful, joy-inducing, generative)
const KENT_ATTRACTOR: PersonalityAttractor = {
  coordinates: {
    tasteful: 0.95,
    curated: 0.85,
    ethical: 0.80,
    joyInducing: 0.90,
    composable: 0.75,
    heterarchical: 0.70,
    generative: 0.92,
  },
  basin: [
    // Attractor basin - variations within personality range
    {
      tasteful: 0.90,
      curated: 0.80,
      ethical: 0.75,
      joyInducing: 0.85,
      composable: 0.70,
      heterarchical: 0.65,
      generative: 0.88,
    },
    {
      tasteful: 0.92,
      curated: 0.88,
      ethical: 0.82,
      joyInducing: 0.92,
      composable: 0.78,
      heterarchical: 0.72,
      generative: 0.90,
    },
  ],
  stability: 0.85,
};

// Initial decision scores (before learning Kent's style)
const INITIAL_SCORES: ConstitutionScores = {
  tasteful: 0.5,
  curated: 0.5,
  ethical: 0.7,
  joyInducing: 0.4,
  composable: 0.6,
  heterarchical: 0.5,
  generative: 0.5,
};

export function ValueCompassExample() {
  const [scores, setScores] = useState<ConstitutionScores>(INITIAL_SCORES);
  const [trajectory, setTrajectory] = useState<ConstitutionScores[]>([]);
  const [showAttractor, setShowAttractor] = useState(false);

  // Simulate learning trajectory - converge toward attractor
  useEffect(() => {
    const interval = setInterval(() => {
      setScores(prev => {
        const next = { ...prev };
        let hasChanged = false;

        // Gradually move each principle toward attractor
        for (const key of Object.keys(next) as (keyof ConstitutionScores)[]) {
          const target = KENT_ATTRACTOR.coordinates[key];
          const current = next[key];
          const diff = target - current;

          if (Math.abs(diff) > 0.01) {
            next[key] = current + diff * 0.1; // 10% step toward target
            hasChanged = true;
          }
        }

        // Add to trajectory
        if (hasChanged) {
          setTrajectory(t => [...t.slice(-5), prev]); // Keep last 6 positions
        }

        return next;
      });
    }, 500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: '2rem', maxWidth: '600px', margin: '0 auto' }}>
      <h2 style={{ color: 'var(--text-primary)', marginBottom: '1rem' }}>
        ValueCompass Example
      </h2>

      <div style={{ marginBottom: '1rem' }}>
        <label style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <input
            type="checkbox"
            checked={showAttractor}
            onChange={e => setShowAttractor(e.target.checked)}
          />
          Show Kent's Personality Attractor
        </label>
      </div>

      <ValueCompass
        scores={scores}
        trajectory={trajectory}
        attractor={showAttractor ? KENT_ATTRACTOR : undefined}
      />

      <div style={{ marginTop: '2rem', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
        <p>
          This demonstrates convergence toward a personality attractor.
          The filled area shows current scores, faint trails show trajectory,
          and the dashed outline (when enabled) shows Kent's target personality basin.
        </p>
      </div>

      {/* Compact version */}
      <div style={{ marginTop: '3rem' }}>
        <h3 style={{ color: 'var(--text-primary)', marginBottom: '1rem' }}>
          Compact Version
        </h3>
        <ValueCompass
          scores={scores}
          compact
        />
      </div>
    </div>
  );
}

export default ValueCompassExample;
