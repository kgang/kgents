/**
 * Membrane — The single morphing co-thinking surface
 *
 * This is the entire app. No routes, no navigation.
 * One surface that morphs based on context.
 *
 * Three surfaces, one membrane:
 * - Focus: What you're working on
 * - Witness: Real-time stream of decisions
 * - Dialogue: Where you and K-gent think together
 *
 * "Stop documenting agents. Become the agent."
 */

import { useEffect } from 'react';

import { ElasticContainer } from '../components/elastic/ElasticContainer';
import { ElasticSplit } from '../components/elastic/ElasticSplit';
import { useWindowLayout } from '../hooks/useLayoutContext';

import { DialoguePane } from './DialoguePane';
import { FocusPane } from './FocusPane';
import { useMembrane } from './useMembrane';
import { WitnessStream } from './WitnessStream';

import './Membrane.css';

// =============================================================================
// Component
// =============================================================================

export function Membrane() {
  const membrane = useMembrane();
  const { density } = useWindowLayout();

  // Expose membrane for testing (dev only)
  useEffect(() => {
    if (import.meta.env.DEV) {
      (window as unknown as { __membrane: typeof membrane }).__membrane = membrane;
    }
  }, [membrane]);

  // Auto-adjust mode based on viewport density
  const { setMode } = membrane;
  useEffect(() => {
    if (density === 'compact') {
      setMode('compact');
    } else if (density === 'spacious') {
      setMode('spacious');
    } else {
      setMode('comfortable');
    }
  }, [density, setMode]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Mod+1/2/3 for mode switching
      if (e.metaKey || e.ctrlKey) {
        if (e.key === '1') {
          e.preventDefault();
          membrane.setMode('compact');
        } else if (e.key === '2') {
          e.preventDefault();
          membrane.setMode('comfortable');
        } else if (e.key === '3') {
          e.preventDefault();
          membrane.setMode('spacious');
        }
      }

      // Escape to go home
      if (e.key === 'Escape') {
        membrane.goHome();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [membrane]);

  return (
    <div className={`membrane membrane--${membrane.mode}`}>
      <ElasticContainer layout="stack" className="membrane__container">
        {/* Comfortable and Spacious: Full three-pane layout */}
        {membrane.mode !== 'compact' && (
          <ElasticSplit
            direction="horizontal"
            defaultRatio={0.7}
            resizable={membrane.mode === 'spacious'}
            className="membrane__main-split"
            primary={
              /* Left: Focus + Dialogue stacked */
              <ElasticSplit
                direction="vertical"
                defaultRatio={0.6}
                resizable={membrane.mode === 'spacious'}
                className="membrane__focus-dialogue"
                primary={<FocusPane focus={membrane.focus} onFocusChange={membrane.setFocus} />}
                secondary={
                  <DialoguePane
                    dialogueHistory={membrane.dialogueHistory}
                    onAppendDialogue={membrane.appendDialogue}
                    onFocusChange={membrane.setFocus}
                    onCrystallize={membrane.crystallize}
                    kblockIsolation={membrane.kblockIsolation}
                    kblockIsDirty={membrane.kblockIsDirty}
                  />
                }
              />
            }
            secondary={<WitnessStream />}
          />
        )}

        {/* Compact: Focus only with collapsed dialogue */}
        {membrane.mode === 'compact' && (
          <div className="membrane__compact">
            <FocusPane focus={membrane.focus} onFocusChange={membrane.setFocus} />
            <div className="membrane__compact-dialogue">
              <DialoguePane
                dialogueHistory={membrane.dialogueHistory}
                onAppendDialogue={membrane.appendDialogue}
                onFocusChange={membrane.setFocus}
                onCrystallize={membrane.crystallize}
                kblockIsolation={membrane.kblockIsolation}
                kblockIsDirty={membrane.kblockIsDirty}
              />
            </div>
          </div>
        )}
      </ElasticContainer>

      {/* Mode indicator */}
      <div className="membrane__mode-indicator">
        <span className="membrane__mode-label">{membrane.mode}</span>
        <div className="membrane__mode-hints">
          <kbd>⌘1</kbd> compact
          <kbd>⌘2</kbd> comfortable
          <kbd>⌘3</kbd> spacious
        </div>
      </div>
    </div>
  );
}
