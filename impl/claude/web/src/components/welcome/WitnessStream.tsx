/**
 * WitnessStream — Mini live-updating stream for Welcome page
 *
 * "The proof IS the decision. The mark IS the witness."
 *
 * A whimsical, animated component showing recent witness marks
 * flowing across the screen like a gentle stream.
 */

import { useEffect, useState, useCallback, memo } from 'react';
import './WitnessStream.css';

// =============================================================================
// Types
// =============================================================================

interface WitnessMark {
  id: string;
  text: string;
  timestamp: Date;
  principle?: string;
}

// =============================================================================
// Mock Data (will connect to real API later)
// =============================================================================

const SAMPLE_MARKS: string[] = [
  'Tasteful node created',
  'Composable edge formed',
  'Joy-inducing interaction',
  'Ethical boundary respected',
  'Curated selection made',
  'Generative pattern emerged',
  'Heterarchical decision',
];

const PRINCIPLES = ['tasteful', 'composable', 'joy-inducing', 'ethical', 'curated', 'generative', 'heterarchical'];

// =============================================================================
// Component
// =============================================================================

function WitnessStreamComponent() {
  const [marks, setMarks] = useState<WitnessMark[]>([]);
  const [isPaused, setIsPaused] = useState(false);

  // Generate a new mark periodically
  const generateMark = useCallback(() => {
    const text = SAMPLE_MARKS[Math.floor(Math.random() * SAMPLE_MARKS.length)];
    const principle = PRINCIPLES[Math.floor(Math.random() * PRINCIPLES.length)];

    const newMark: WitnessMark = {
      id: `mark-${Date.now()}-${Math.random()}`,
      text,
      timestamp: new Date(),
      principle,
    };

    setMarks((prev) => {
      const updated = [newMark, ...prev];
      // Keep only last 5
      return updated.slice(0, 5);
    });
  }, []);

  // Start the stream
  useEffect(() => {
    if (isPaused) return;

    // Generate first mark immediately
    generateMark();

    // Then generate periodically
    const interval = setInterval(generateMark, 3000);

    return () => clearInterval(interval);
  }, [isPaused, generateMark]);

  return (
    <div
      className="witness-stream"
      onClick={() => setIsPaused(!isPaused)}
      title={isPaused ? "Click to resume" : "Click to pause"}
    >
      <div className="witness-stream__header">
        <span className="witness-stream__title">Witness Stream</span>
        <span className="witness-stream__pulse" />
      </div>

      <div className="witness-stream__container">
        {marks.map((mark, index) => (
          <div
            key={mark.id}
            className="witness-stream__mark"
            style={{
              animationDelay: `${index * 0.1}s`,
              opacity: 1 - (index * 0.15),
            }}
          >
            <span className="witness-stream__mark-glyph">◇</span>
            <span className="witness-stream__mark-text">{mark.text}</span>
            {mark.principle && (
              <span className="witness-stream__mark-principle" data-principle={mark.principle}>
                {mark.principle}
              </span>
            )}
          </div>
        ))}

        {marks.length === 0 && !isPaused && (
          <div className="witness-stream__empty">
            Listening for marks...
          </div>
        )}
      </div>

      <div className="witness-stream__footer">
        "The proof IS the decision. The mark IS the witness."
      </div>
    </div>
  );
}

// Memoize to prevent re-renders from parent
export const WitnessStream = memo(WitnessStreamComponent);
