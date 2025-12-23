/**
 * TeachingCallout — Context Without Lecture
 *
 * A dynamic message that responds to entropy changes.
 * The callout itself breathes—meta-teaching.
 *
 * Teaching happens through interaction, not documentation.
 */

import type { CSSProperties } from 'react';
import { Breathe } from '@/components/joy';
import { describeEntropy } from '@/hooks/useTerrarium';
import { LIVING_EARTH, GRAYS } from '@/constants/colors';

export interface TeachingCalloutProps {
  /** Current entropy level (0-1) */
  entropy: number;
  /** Additional CSS classes */
  className?: string;
  /** Additional inline styles */
  style?: CSSProperties;
}

export function TeachingCallout({ entropy, className = '', style }: TeachingCalloutProps) {
  const message = describeEntropy(entropy);

  return (
    <div
      className={`teaching-callout ${className}`}
      style={{
        padding: '1rem 1.5rem',
        background: GRAYS[800],
        borderRadius: '0.5rem',
        borderLeft: `3px solid ${LIVING_EARTH.copper}`,
        ...style,
      }}
      role="status"
      aria-live="polite"
    >
      {/* The callout itself breathes at low intensity—meta-teaching */}
      <Breathe intensity={0.2} entropy={entropy}>
        <p
          style={{
            fontFamily: 'monospace',
            fontSize: '0.875rem',
            fontStyle: 'italic',
            color: GRAYS[400],
            margin: 0,
            lineHeight: 1.5,
          }}
        >
          {message}
        </p>
      </Breathe>
    </div>
  );
}

export default TeachingCallout;
