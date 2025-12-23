/**
 * The Terrarium — A Living Gallery
 *
 * "The Gallery is not a catalogue—it is a living demonstration of the categorical ground."
 *
 * One page. Components breathe. Entropy controls them. The polynomial is visible.
 *
 * Four creatures. One slider. That's bold restraint.
 *
 * @see spec/gallery/gallery-v2.md
 * @see plans/ethereal-churning-spark.md
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Breathe, Pop, Shimmer, PersonalityLoading } from '@/components/joy';
import {
  EntropySlider,
  PhaseIndicator,
  TeachingCallout,
  TerrariumCreature,
} from '@/components/terrarium';
import { useTerrarium } from '@/hooks/useTerrarium';

/**
 * The Terrarium.
 *
 * Four creatures respond to global entropy:
 * - Breather: Breathe component, speed + intensity scale with entropy
 * - Popper: Pop component, triggers more frequently at high entropy
 * - Shimmerer: Shimmer component, duration shortens as entropy rises
 * - Loader: PersonalityLoading, message rotation speeds up
 */
export default function TerrariumPage() {
  const { entropy, setEntropy, phase, setPhase } = useTerrarium();

  // Pop triggers periodically based on entropy
  // Higher entropy = more frequent pops
  const [popTrigger, setPopTrigger] = useState(false);
  useEffect(() => {
    // Pop interval: 5s at low entropy, 1s at high entropy
    const interval = Math.max(1000, 5000 - entropy * 4000);
    const timer = setInterval(() => {
      setPopTrigger(true);
      setTimeout(() => setPopTrigger(false), 200);
    }, interval);
    return () => clearInterval(timer);
  }, [entropy]);

  return (
    <div
      className="terrarium-page"
      style={{
        minHeight: '100vh',
        background: 'var(--surface-canvas)',
        padding: '2rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '2rem',
      }}
    >
      {/* Header */}
      <header
        style={{
          maxWidth: '48rem',
          margin: '0 auto',
          width: '100%',
          textAlign: 'center',
        }}
      >
        <h1
          style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '1.5rem',
            fontWeight: 600,
            color: 'var(--text-primary)',
            margin: 0,
            letterSpacing: '-0.02em',
          }}
        >
          The Terrarium
        </h1>
        <p
          style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '0.875rem',
            color: 'var(--text-secondary)',
            marginTop: '0.5rem',
          }}
        >
          A living gallery. Drag entropy. Watch them breathe.
        </p>
      </header>

      {/* Main content */}
      <main
        style={{
          maxWidth: '48rem',
          margin: '0 auto',
          width: '100%',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.5rem',
        }}
      >
        {/* Entropy Slider — The Heart */}
        <EntropySlider value={entropy} onChange={setEntropy} />

        {/* Creature Grid — Four creatures, no more */}
        <div
          className="creature-grid"
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(10rem, 1fr))',
            gap: '1rem',
          }}
        >
          {/* Creature 1: Breather */}
          <TerrariumCreature
            name="Breather"
            entropy={entropy}
            description="Speed and intensity scale with entropy"
          >
            <Breathe entropy={entropy} intensity={0.5}>
              <div
                style={{
                  width: '4rem',
                  height: '4rem',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, var(--sage-500), var(--sage-600))',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                }}
              />
            </Breathe>
          </TerrariumCreature>

          {/* Creature 2: Popper */}
          <TerrariumCreature
            name="Popper"
            entropy={entropy}
            description="Pops more frequently as entropy rises"
          >
            <Pop trigger={popTrigger} scale={1 + entropy * 0.3}>
              <div
                style={{
                  width: '4rem',
                  height: '4rem',
                  borderRadius: '0.5rem',
                  background: 'linear-gradient(135deg, var(--copper-500), var(--copper-600))',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                }}
              />
            </Pop>
          </TerrariumCreature>

          {/* Creature 3: Shimmerer */}
          <TerrariumCreature
            name="Shimmerer"
            entropy={entropy}
            description="Duration shortens, becomes frantic"
          >
            <Shimmer duration={Math.max(0.5, 2 - entropy * 1.5)}>
              <div
                style={{
                  width: '4rem',
                  height: '4rem',
                  borderRadius: '0.25rem',
                  background: 'var(--surface-3)',
                }}
              />
            </Shimmer>
          </TerrariumCreature>

          {/* Creature 4: Loader */}
          <TerrariumCreature
            name="Loader"
            entropy={entropy}
            description="Message rotation speeds up"
          >
            <PersonalityLoading
              jewel="brain"
              size="md"
              rotateInterval={Math.max(1000, 4000 - entropy * 3000)}
            />
          </TerrariumCreature>
        </div>

        {/* Phase Indicator — The Polynomial Made Visible */}
        <PhaseIndicator phase={phase} onPhaseClick={setPhase} />

        {/* Teaching Callout — Context Without Lecture */}
        <TeachingCallout entropy={entropy} />

        {/* Navigation to sub-galleries */}
        <nav
          style={{
            display: 'flex',
            gap: '1rem',
            justifyContent: 'center',
            paddingTop: '1rem',
            borderTop: '1px solid var(--surface-3)',
          }}
        >
          <Link
            to="/_/gallery/layout"
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.75rem',
              color: 'var(--text-tertiary)',
              textDecoration: 'none',
            }}
          >
            Layout Gallery
          </Link>
          <Link
            to="/_/gallery/interactive-text"
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.75rem',
              color: 'var(--text-tertiary)',
              textDecoration: 'none',
            }}
          >
            Animation Gallery
          </Link>
        </nav>
      </main>

      {/* Footer quote */}
      <footer
        style={{
          maxWidth: '48rem',
          margin: '0 auto',
          width: '100%',
          textAlign: 'center',
          paddingTop: '2rem',
        }}
      >
        <p
          style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '0.75rem',
            fontStyle: 'italic',
            color: 'var(--text-tertiary)',
          }}
        >
          "The persona is a garden, not a museum."
        </p>
      </footer>
    </div>
  );
}
