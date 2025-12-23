/**
 * TerrariumCreature — A Living Specimen
 *
 * Wrapper component for creatures in the Terrarium grid.
 * Shows the creature name, its current entropy response, and the animation itself.
 *
 * Each creature demonstrates a different animation primitive responding to entropy.
 */

import type { ReactNode, CSSProperties } from 'react';
import { GRAYS } from '@/constants/colors';

export interface TerrariumCreatureProps {
  /** Creature name (displayed as label) */
  name: string;
  /** Current entropy level (for display, creature animation handles internally) */
  entropy: number;
  /** The animated component itself */
  children: ReactNode;
  /** Short description of how this creature responds to entropy */
  description?: string;
  /** Additional CSS classes */
  className?: string;
  /** Additional inline styles */
  style?: CSSProperties;
}

/**
 * Get entropy response description based on level.
 */
function getEntropyResponse(entropy: number): string {
  if (entropy < 0.3) return 'dormant';
  if (entropy < 0.5) return 'stirring';
  if (entropy < 0.7) return 'active';
  if (entropy < 0.85) return 'excited';
  return 'frantic';
}

export function TerrariumCreature({
  name,
  entropy,
  children,
  description,
  className = '',
  style,
}: TerrariumCreatureProps) {
  const response = getEntropyResponse(entropy);

  return (
    <div
      className={`terrarium-creature ${className}`}
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '0.75rem',
        padding: '1.5rem',
        background: GRAYS[800],
        borderRadius: '0.75rem',
        border: `1px solid ${GRAYS[700]}`,
        transition: 'border-color 0.3s ease',
        ...style,
      }}
    >
      {/* Creature name */}
      <span
        style={{
          fontFamily: 'monospace',
          fontSize: '0.75rem',
          fontWeight: 600,
          color: GRAYS[200],
          textTransform: 'uppercase',
          letterSpacing: '0.1em',
        }}
      >
        {name}
      </span>

      {/* The creature itself (animated content) */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: '6rem',
          height: '6rem',
        }}
      >
        {children}
      </div>

      {/* Entropy response indicator */}
      <span
        style={{
          fontFamily: 'monospace',
          fontSize: '0.625rem',
          color: GRAYS[500],
          textTransform: 'lowercase',
        }}
      >
        {response}
      </span>

      {/* Optional description */}
      {description && (
        <p
          style={{
            fontFamily: 'monospace',
            fontSize: '0.625rem',
            color: GRAYS[500],
            textAlign: 'center',
            margin: 0,
            maxWidth: '10rem',
          }}
        >
          {description}
        </p>
      )}
    </div>
  );
}

export default TerrariumCreature;
