/**
 * GenesisLanding — The First Screen
 *
 * "The system already knows itself. Your job is to explore—and then extend."
 *
 * One button. One action. No friction.
 */

import { useEffect, useState } from 'react';

interface GenesisLandingProps {
  onEnter: () => void;
}

/**
 * Landing screen with breathing animation
 */
export function GenesisLanding({ onEnter }: GenesisLandingProps) {
  const [breathePhase, setBreathePhase] = useState(0);

  // Gentle breathing animation for the background
  useEffect(() => {
    const interval = setInterval(() => {
      setBreathePhase((prev) => (prev + 1) % 360);
    }, 50);
    return () => clearInterval(interval);
  }, []);

  const breatheScale = 1 + Math.sin((breathePhase * Math.PI) / 180) * 0.02;

  return (
    <div className="genesis-landing">
      {/* Background with subtle breathing */}
      <div
        className="genesis-landing__background"
        style={{ transform: `scale(${breatheScale})` }}
      />

      {/* Content */}
      <div className="genesis-landing__content">
        <h1 className="genesis-landing__title">kgents</h1>

        <p className="genesis-landing__subtitle">The system already knows itself.</p>
        <p className="genesis-landing__subtitle genesis-landing__subtitle--secondary">
          Your job is to explore—and then extend.
        </p>

        <button className="genesis-landing__enter" onClick={onEnter} autoFocus>
          Enter the Garden
          <span className="genesis-landing__enter-arrow">↓</span>
        </button>
      </div>

      {/* Decorative nodes in background */}
      <div className="genesis-landing__nodes">
        {[0, 1, 2, 3].map((i) => (
          <div
            key={i}
            className="genesis-landing__node"
            style={
              {
                '--node-delay': `${i * 0.5}s`,
                '--node-x': `${20 + i * 20}%`,
                '--node-y': `${30 + (i % 2) * 40}%`,
              } as React.CSSProperties
            }
          />
        ))}
      </div>
    </div>
  );
}
