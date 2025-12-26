/**
 * CoherenceTimeline Example
 *
 * Demo component showing CoherenceTimeline usage with sample data.
 */

import { CoherenceTimeline, CoherencePoint } from './CoherenceTimeline';

// =============================================================================
// Sample Data
// =============================================================================

const generateSampleData = (): CoherencePoint[] => {
  const now = new Date();
  const points: CoherencePoint[] = [];

  // Generate 30 days of data
  for (let i = 0; i < 30; i++) {
    const date = new Date(now);
    date.setDate(date.getDate() - (29 - i));

    // Simulate coherence growth with some noise
    const baseScore = 0.5 + (i / 30) * 0.3; // Gradual improvement
    const noise = (Math.random() - 0.5) * 0.1; // Random fluctuation
    const score = Math.max(0, Math.min(1, baseScore + noise));

    // Layer distribution: more layers as coherence improves
    const layerCount = Math.floor(score * 5);
    const distribution: Record<number, number> = {};
    for (let layer = 0; layer <= layerCount; layer++) {
      distribution[layer] = Math.floor(Math.random() * 10) + 5;
    }

    points.push({
      timestamp: date,
      score,
      commitId: `${Math.random().toString(36).substring(2, 9)}`, // Random hash
      layerDistribution: distribution,
    });
  }

  return points;
};

// =============================================================================
// Example Component
// =============================================================================

export function CoherenceTimelineExample() {
  const points = generateSampleData();

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1 style={{ color: 'var(--text-primary)', marginBottom: '20px' }}>
        Coherence Timeline Example
      </h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '40px' }}>
        This demo shows 30 days of coherence evolution with breakthrough detection.
      </p>

      <CoherenceTimeline points={points} width={1000} height={500} />

      <div style={{ marginTop: '40px', color: 'var(--text-secondary)' }}>
        <h2 style={{ color: 'var(--text-primary)', marginBottom: '10px' }}>
          Features
        </h2>
        <ul style={{ lineHeight: '1.8' }}>
          <li>Hover over points to see details</li>
          <li>Breakthrough points are marked with 🏆 (2x average delta)</li>
          <li>Switch to Distribution tab to see layer breakdown</li>
          <li>Export to Markdown or SVG using the buttons</li>
        </ul>
      </div>
    </div>
  );
}

export default CoherenceTimelineExample;
