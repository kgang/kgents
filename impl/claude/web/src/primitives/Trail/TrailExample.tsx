/**
 * TrailExample - Visual demonstration of Trail primitive
 *
 * Shows Trail in various configurations:
 * - Basic breadcrumb
 * - With compression ratio
 * - With principle scores
 * - Long path (collapsed)
 * - Compact mode
 */

import { useState } from 'react';
import { Trail } from './Trail';
import type { ConstitutionScores } from '../../types/theory';

export function TrailExample() {
  const [activeExample, setActiveExample] = useState<number>(0);

  // Example 1: Basic breadcrumb
  const basicPath = ['axioms', 'values', 'goals', 'specs', 'actions'];

  // Example 2: With compression ratio
  const compressionPath = ['root', 'theory', 'implementation', 'validation'];
  const compressionRatio = 0.42; // 42% compressed

  // Example 3: With principle scores
  const principlePath = ['tasteful', 'curated', 'ethical'];
  const principleScores: ConstitutionScores[] = [
    {
      tasteful: 0.95,
      curated: 0.85,
      ethical: 0.9,
      joyInducing: 0.88,
      composable: 0.75,
      heterarchical: 0.8,
      generative: 0.92,
    },
    {
      tasteful: 0.9,
      curated: 0.9,
      ethical: 0.88,
      joyInducing: 0.85,
      composable: 0.82,
      heterarchical: 0.78,
      generative: 0.9,
    },
    {
      tasteful: 0.92,
      curated: 0.88,
      ethical: 0.95,
      joyInducing: 0.9,
      composable: 0.8,
      heterarchical: 0.85,
      generative: 0.88,
    },
  ];

  // Example 4: Long path (auto-collapsed)
  const longPath = [
    'root',
    'foundation',
    'architecture',
    'design',
    'implementation',
    'testing',
    'validation',
    'deployment',
    'monitoring',
    'current',
  ];

  const examples = [
    { name: 'Basic', path: basicPath, compression: undefined, showPrinciples: false },
    { name: 'With Compression', path: compressionPath, compression: compressionRatio, showPrinciples: false },
    { name: 'With Principles', path: principlePath, compression: undefined, showPrinciples: true },
    { name: 'Long Path', path: longPath, compression: 0.65, showPrinciples: false },
  ];

  return (
    <div style={{ padding: '40px', background: '#0a0a0c', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Header */}
        <header style={{ marginBottom: '40px' }}>
          <h1
            style={{
              fontSize: '28px',
              fontWeight: 600,
              color: '#e5e7eb',
              marginBottom: '8px',
            }}
          >
            Trail Primitive Examples
          </h1>
          <p style={{ fontSize: '14px', color: '#8a8a94' }}>
            Semantic breadcrumb with PolicyTrace compression and principle indicators
          </p>
        </header>

        {/* Example Selector */}
        <div
          style={{
            display: 'flex',
            gap: '12px',
            marginBottom: '32px',
            flexWrap: 'wrap',
          }}
        >
          {examples.map((example, idx) => (
            <button
              key={idx}
              onClick={() => setActiveExample(idx)}
              style={{
                padding: '8px 16px',
                background: activeExample === idx ? '#1c1c22' : 'transparent',
                border: `1px solid ${activeExample === idx ? '#c4a77d' : '#28282f'}`,
                borderRadius: '6px',
                color: activeExample === idx ? '#e5e7eb' : '#8a8a94',
                fontSize: '13px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
            >
              {example.name}
            </button>
          ))}
        </div>

        {/* Active Example */}
        <div
          style={{
            background: '#141418',
            border: '1px solid #28282f',
            borderRadius: '8px',
            overflow: 'hidden',
            marginBottom: '40px',
          }}
        >
          <div
            style={{
              padding: '12px 20px',
              borderBottom: '1px solid #28282f',
              background: '#1c1c22',
            }}
          >
            <h3 style={{ fontSize: '14px', color: '#c4a77d', fontWeight: 500 }}>
              {examples[activeExample].name}
            </h3>
          </div>
          <div style={{ padding: '20px' }}>
            <Trail
              path={examples[activeExample].path}
              compressionRatio={examples[activeExample].compression}
              showPrinciples={examples[activeExample].showPrinciples}
              principleScores={
                examples[activeExample].showPrinciples ? principleScores : undefined
              }
              currentIndex={examples[activeExample].path.length - 1}
              onStepClick={(idx, stepId) => {
                console.log(`Navigate to step ${idx}: ${stepId}`);
              }}
            />
          </div>
        </div>

        {/* Compact Mode Demo */}
        <div
          style={{
            background: '#141418',
            border: '1px solid #28282f',
            borderRadius: '8px',
            overflow: 'hidden',
            marginBottom: '40px',
          }}
        >
          <div
            style={{
              padding: '12px 20px',
              borderBottom: '1px solid #28282f',
              background: '#1c1c22',
            }}
          >
            <h3 style={{ fontSize: '14px', color: '#c4a77d', fontWeight: 500 }}>
              Compact Mode
            </h3>
          </div>
          <div style={{ padding: '20px' }}>
            <Trail
              path={basicPath}
              compressionRatio={0.5}
              compact
              currentIndex={basicPath.length - 1}
              onStepClick={(idx, stepId) => {
                console.log(`Navigate to step ${idx}: ${stepId}`);
              }}
            />
          </div>
        </div>

        {/* Props Reference */}
        <div
          style={{
            background: '#141418',
            border: '1px solid #28282f',
            borderRadius: '8px',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              padding: '12px 20px',
              borderBottom: '1px solid #28282f',
              background: '#1c1c22',
            }}
          >
            <h3 style={{ fontSize: '14px', color: '#c4a77d', fontWeight: 500 }}>
              Props Reference
            </h3>
          </div>
          <div style={{ padding: '20px' }}>
            <table style={{ width: '100%', fontSize: '13px', color: '#8a8a94' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #28282f', textAlign: 'left' }}>
                  <th style={{ padding: '8px', color: '#c4a77d' }}>Prop</th>
                  <th style={{ padding: '8px', color: '#c4a77d' }}>Type</th>
                  <th style={{ padding: '8px', color: '#c4a77d' }}>Description</th>
                </tr>
              </thead>
              <tbody>
                <tr style={{ borderBottom: '1px solid #28282f' }}>
                  <td style={{ padding: '8px', color: '#e5e7eb' }}>path</td>
                  <td style={{ padding: '8px' }}>string[]</td>
                  <td style={{ padding: '8px' }}>Navigation path as array of step IDs</td>
                </tr>
                <tr style={{ borderBottom: '1px solid #28282f' }}>
                  <td style={{ padding: '8px', color: '#e5e7eb' }}>compressionRatio</td>
                  <td style={{ padding: '8px' }}>number?</td>
                  <td style={{ padding: '8px' }}>PolicyTrace compression (0-1)</td>
                </tr>
                <tr style={{ borderBottom: '1px solid #28282f' }}>
                  <td style={{ padding: '8px', color: '#e5e7eb' }}>showPrinciples</td>
                  <td style={{ padding: '8px' }}>boolean?</td>
                  <td style={{ padding: '8px' }}>Show principle dots</td>
                </tr>
                <tr style={{ borderBottom: '1px solid #28282f' }}>
                  <td style={{ padding: '8px', color: '#e5e7eb' }}>currentIndex</td>
                  <td style={{ padding: '8px' }}>number?</td>
                  <td style={{ padding: '8px' }}>Highlight step index</td>
                </tr>
                <tr style={{ borderBottom: '1px solid #28282f' }}>
                  <td style={{ padding: '8px', color: '#e5e7eb' }}>onStepClick</td>
                  <td style={{ padding: '8px' }}>function?</td>
                  <td style={{ padding: '8px' }}>Navigate callback</td>
                </tr>
                <tr style={{ borderBottom: '1px solid #28282f' }}>
                  <td style={{ padding: '8px', color: '#e5e7eb' }}>compact</td>
                  <td style={{ padding: '8px' }}>boolean?</td>
                  <td style={{ padding: '8px' }}>Minimal mode</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TrailExample;
