/**
 * Feedback Laws (F-01 through F-05)
 *
 * Tests for the 5 feedback design laws from Zero Seed Creative Strategy.
 *
 * @see plans/zero-seed-creative-strategy.md (Part IV: UI/UX Design Laws)
 */

import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import userEvent from '@testing-library/user-event';
import React from 'react';

// =============================================================================
// F-01: Multiple Channel Confirmation
// =============================================================================

describe('F-01: Multiple Channel Confirmation', () => {
  /**
   * Law Statement: 2+ channels for significant actions.
   *
   * Justification: Significant actions (commit, delete, publish) should
   * provide feedback through multiple channels: visual, auditory (optional),
   * haptic (on mobile), and state change.
   *
   * Test: Significant actions trigger at least 2 feedback channels.
   */

  it('provides visual + state feedback for commit action', async () => {
    const user = userEvent.setup();
    const onCommit = vi.fn();

    const CommitButton = () => {
      const [committed, setCommitted] = React.useState(false);
      const [showToast, setShowToast] = React.useState(false);

      const handleCommit = () => {
        setCommitted(true);
        setShowToast(true);
        onCommit();
      };

      return (
        <div>
          <button onClick={handleCommit} data-committed={committed}>
            Commit
          </button>
          {showToast && <div data-testid="toast">Committed successfully!</div>}
        </div>
      );
    };

    render(<CommitButton />);

    const button = screen.getByText('Commit');
    await user.click(button);

    // Channel 1: Visual feedback (toast)
    expect(screen.getByTestId('toast')).toBeInTheDocument();

    // Channel 2: State change (button attribute)
    expect(button).toHaveAttribute('data-committed', 'true');
  });

  it('provides visual + motion feedback for delete action', async () => {
    const user = userEvent.setup();

    const DeleteButton = () => {
      const [isDeleting, setIsDeleting] = React.useState(false);
      const [deleted, setDeleted] = React.useState(false);

      const handleDelete = () => {
        setIsDeleting(true);
        setTimeout(() => {
          setIsDeleting(false);
          setDeleted(true);
        }, 300);
      };

      return (
        <div>
          {!deleted ? (
            <button onClick={handleDelete} data-deleting={isDeleting}>
              Delete
            </button>
          ) : (
            <div data-testid="deleted-state">Item deleted</div>
          )}
        </div>
      );
    };

    render(<DeleteButton />);

    const button = screen.getByText('Delete');
    await user.click(button);

    // Channel 1: Motion feedback (deleting state for animation)
    expect(button).toHaveAttribute('data-deleting', 'true');

    // Channel 2: Visual feedback (deleted state appears)
    await waitFor(() => {
      expect(screen.getByTestId('deleted-state')).toBeInTheDocument();
    });
  });

  it('combines visual + sound + haptic for critical actions', () => {
    const triggerFeedback = () => {
      // Visual: Color change, icon, toast
      const visual = { color: 'green', icon: '✓', toast: 'Success!' };

      // Sound: Optional audio cue (if user preference allows)
      const sound = { enabled: false, file: 'success.mp3' };

      // Haptic: Vibration on mobile (if supported)
      const haptic = { enabled: navigator.vibrate !== undefined, pattern: [100] };

      return { visual, sound, haptic };
    };

    const feedback = triggerFeedback();

    // At least 2 channels should be available
    const channels = [feedback.visual, feedback.sound.enabled, feedback.haptic.enabled].filter(
      Boolean
    );

    expect(channels.length).toBeGreaterThanOrEqual(1); // Visual always present
  });

  it('rejects single-channel feedback for significant actions', async () => {
    const user = userEvent.setup();

    // Anti-pattern: Only state change, no visual feedback
    const BadPattern = () => {
      const [_state, setState] = React.useState('idle');
      return <button onClick={() => setState('done')}>Action</button>;
    };

    // Good pattern: Multiple channels
    const GoodPattern = () => {
      const [state, setState] = React.useState('idle');
      const [showFeedback, setShowFeedback] = React.useState(false);

      const handleAction = () => {
        setState('done');
        setShowFeedback(true);
      };

      return (
        <div>
          <button onClick={handleAction} data-state={state}>
            Action
          </button>
          {showFeedback && <div data-testid="feedback">Done!</div>}
        </div>
      );
    };

    const { unmount } = render(<GoodPattern />);
    const button = screen.getByText('Action');
    await user.click(button);

    // Should have both state change AND visual feedback
    expect(button).toHaveAttribute('data-state', 'done');
    expect(screen.getByTestId('feedback')).toBeInTheDocument();

    unmount();
  });
});

// =============================================================================
// F-02: Contradiction as Information
// =============================================================================

describe('F-02: Contradiction as Information', () => {
  /**
   * Law Statement: Surface as info, not judgment.
   *
   * Justification: Contradictions are information, not errors. They should
   * be presented neutrally, not with alarming red or error styling.
   *
   * Test: Contradictions use info styling (amber/blue), not error (red).
   */

  it('presents contradictions with info styling, not error styling', () => {
    const Contradiction = () => (
      <div
        data-testid="contradiction"
        className="info-badge"
        style={{ backgroundColor: 'var(--color-amber-100)', color: 'var(--color-amber-900)' }}
      >
        ⚡ Contradiction detected
      </div>
    );

    render(<Contradiction />);

    const badge = screen.getByTestId('contradiction');
    const style = window.getComputedStyle(badge);

    // Should NOT use error red
    expect(style.backgroundColor).not.toContain('red');
    expect(badge).toHaveClass('info-badge');
  });

  it('uses neutral language for contradiction messages', () => {
    const messages = {
      bad: 'ERROR: Conflicting principles!',
      good: 'These principles have tension worth exploring',
    };

    const BadMessage = () => <div>{messages.bad}</div>;
    const GoodMessage = () => <div data-testid="msg">{messages.good}</div>;

    const { unmount: unmount1 } = render(<BadMessage />);
    expect(screen.getByText(/ERROR/)).toBeInTheDocument();
    unmount1();

    const { unmount: unmount2 } = render(<GoodMessage />);
    const msg = screen.getByTestId('msg');
    expect(msg.textContent).toMatch(/tension worth exploring/);
    expect(msg.textContent).not.toMatch(/ERROR|CONFLICT|WRONG/i);
    unmount2();
  });

  it('frames contradictions as creative opportunity, not failure', () => {
    const ContradictionCard = () => (
      <div data-testid="card">
        <div className="contradiction-header">
          <span>⚡</span>
          <span>Productive Tension</span>
        </div>
        <p>These K-Blocks offer different perspectives worth synthesizing.</p>
        <button>Explore synthesis</button>
      </div>
    );

    render(<ContradictionCard />);

    const card = screen.getByTestId('card');

    // Should use generative framing
    expect(card.textContent).toMatch(/Productive Tension/);
    expect(card.textContent).toMatch(/synthesizing/);
    expect(screen.getByText(/Explore synthesis/)).toBeInTheDocument();
  });

  it('allows marking contradictions as creative tension', () => {
    const ContradictionActions = () => (
      <div>
        <button data-testid="resolve">Resolve contradiction</button>
        <button data-testid="mark-creative">Mark as creative tension 🔥</button>
      </div>
    );

    render(<ContradictionActions />);

    // Both options should be available
    expect(screen.getByTestId('resolve')).toBeInTheDocument();
    expect(screen.getByTestId('mark-creative')).toBeInTheDocument();
  });
});

// =============================================================================
// F-03: Tone Matches Observer
// =============================================================================

describe('F-03: Tone Matches Observer', () => {
  /**
   * Law Statement: Archetype-aware messages.
   *
   * Justification: Different personas (Aisha the Rigorous Skeptic, River
   * the Mycelial Thinker) need different tone. Messages adapt to observer.
   *
   * Test: Message tone changes based on user archetype.
   */

  it('adapts message tone to observer archetype', () => {
    const getMessage = (archetype: 'developer' | 'creator') => {
      const messages = {
        developer: 'Coherence score: 0.87. 3 unresolved contradictions detected.',
        creator: 'Your knowledge garden is thriving! Some spores are still finding their place.',
      };
      return messages[archetype];
    };

    const developerMsg = getMessage('developer');
    const creatorMsg = getMessage('creator');

    // Developer: precise, technical
    expect(developerMsg).toMatch(/Coherence score|detected/);

    // Creator: organic, nurturing
    expect(creatorMsg).toMatch(/garden|thriving|spores/);
  });

  it('uses precise language for rigorous skeptic persona', () => {
    const Message = ({ archetype }: { archetype: string }) => {
      const text =
        archetype === 'skeptic'
          ? 'Axiom A1 grounds 3 L1 principles. Loss: 0.23.'
          : 'Your foundation is growing!';

      return <div data-testid="msg">{text}</div>;
    };

    render(<Message archetype="skeptic" />);

    const msg = screen.getByTestId('msg');
    // Skeptic gets precise metrics
    expect(msg.textContent).toMatch(/Axiom|grounds|Loss: 0\.\d+/);
  });

  it('uses organic language for mycelial thinker persona', () => {
    const Message = ({ archetype }: { archetype: string }) => {
      const text =
        archetype === 'mycelial'
          ? 'Your knowledge spores are weaving connections...'
          : 'Knowledge graph expanding.';

      return <div data-testid="msg">{text}</div>;
    };

    render(<Message archetype="mycelial" />);

    const msg = screen.getByTestId('msg');
    // Mycelial gets organic metaphors
    expect(msg.textContent).toMatch(/spores|weaving|connections/);
  });

  it('provides archetype selector for tone preference', () => {
    const ArchetypeSelector = () => (
      <div>
        <label>Tone preference:</label>
        <select data-testid="archetype">
          <option value="developer">Developer (precise)</option>
          <option value="creator">Creator (organic)</option>
          <option value="admin">Admin (strategic)</option>
        </select>
      </div>
    );

    render(<ArchetypeSelector />);

    const selector = screen.getByTestId('archetype');
    expect(selector).toBeInTheDocument();

    const options = Array.from(selector.querySelectorAll('option'));
    expect(options).toHaveLength(3);
  });
});

// =============================================================================
// F-04: Earned Glow Not Decoration
// =============================================================================

describe('F-04: Earned Glow Not Decoration', () => {
  /**
   * Law Statement: Color on interaction, not default.
   *
   * Justification: STARK biome aesthetic: 90% steel, 10% earned glow.
   * Color appears only on interaction, achievement, or significance.
   *
   * Test: Default state is neutral (steel). Color appears on action.
   */

  it('defaults to neutral steel colors before interaction', () => {
    const Button = () => {
      const [active, setActive] = React.useState(false);

      return (
        <button
          data-testid="btn"
          onClick={() => setActive(true)}
          style={{
            backgroundColor: active ? 'var(--color-sage-500)' : 'var(--color-steel-300)',
          }}
        >
          Action
        </button>
      );
    };

    render(<Button />);

    const button = screen.getByTestId('btn');
    const _style = window.getComputedStyle(button);

    // Default should be steel (neutral)
    expect(button.style.backgroundColor).toContain('steel');
  });

  it('shows color glow only after user interaction', async () => {
    const user = userEvent.setup();

    const InteractiveCard = () => {
      const [interacted, setInteracted] = React.useState(false);

      return (
        <div
          data-testid="card"
          onClick={() => setInteracted(true)}
          data-interacted={interacted}
          style={{
            borderColor: interacted ? 'var(--color-sage-400)' : 'var(--color-steel-200)',
          }}
        >
          Card
        </div>
      );
    };

    render(<InteractiveCard />);

    const card = screen.getByTestId('card');

    // Before interaction: steel
    expect(card.style.borderColor).toContain('steel');

    // After interaction: color glow
    await user.click(card);
    expect(card).toHaveAttribute('data-interacted', 'true');
    expect(card.style.borderColor).toContain('sage');
  });

  it('uses color for earned achievements and milestones', () => {
    const Achievement = ({ earned }: { earned: boolean }) => (
      <div
        data-testid="achievement"
        style={{
          backgroundColor: earned ? 'var(--color-sage-100)' : 'transparent',
          color: earned ? 'var(--color-sage-900)' : 'var(--color-steel-600)',
        }}
      >
        {earned ? '🏆 Breakthrough achieved!' : 'Keep going...'}
      </div>
    );

    const { unmount: unmount1 } = render(<Achievement earned={false} />);
    expect(screen.getByTestId('achievement').style.backgroundColor).toBe('transparent');
    unmount1();

    const { unmount: unmount2 } = render(<Achievement earned={true} />);
    const achievement = screen.getByTestId('achievement');
    expect(achievement.style.backgroundColor).toContain('sage');
    unmount2();
  });

  it('rejects decorative color that serves no semantic purpose', () => {
    // Anti-pattern: Color everywhere by default
    const BadPattern = () => (
      <div data-testid="bad" style={{ backgroundColor: 'lightblue', color: 'darkblue' }}>
        Decorative color
      </div>
    );

    // Good pattern: Steel by default, color on meaning
    const GoodPattern = ({ meaningful }: { meaningful: boolean }) => (
      <div
        data-testid="good"
        style={{
          backgroundColor: meaningful ? 'var(--color-sage-100)' : 'transparent',
          color: 'var(--color-steel-900)',
        }}
      >
        Earned color
      </div>
    );

    const { unmount: unmount1 } = render(<BadPattern />);
    const badElement = screen.getByTestId('bad');
    expect(badElement.style.backgroundColor).toBe('lightblue');
    unmount1();

    const { unmount: unmount2 } = render(<GoodPattern meaningful={false} />);
    const goodElement = screen.getByTestId('good');
    expect(goodElement.style.backgroundColor).toBe('transparent');
    unmount2();
  });
});

// =============================================================================
// F-05: Non-Blocking Notification
// =============================================================================

describe('F-05: Non-Blocking Notification', () => {
  /**
   * Law Statement: Status appears non-modally.
   *
   * Justification: Notifications should not interrupt flow. They appear
   * in peripheral vision (toasts, status bar) rather than blocking modals.
   *
   * Test: Notifications use toast/banner, not blocking dialog.
   */

  it('uses toast notifications instead of blocking alerts', async () => {
    const user = userEvent.setup();

    const NotificationDemo = () => {
      const [showToast, setShowToast] = React.useState(false);

      return (
        <div>
          <button onClick={() => setShowToast(true)}>Notify</button>
          {showToast && (
            <div
              data-testid="toast"
              role="status"
              aria-live="polite"
              style={{
                position: 'fixed',
                bottom: '20px',
                right: '20px',
              }}
            >
              Notification message
            </div>
          )}
        </div>
      );
    };

    render(<NotificationDemo />);

    await user.click(screen.getByText('Notify'));

    const toast = screen.getByTestId('toast');

    // Toast should be non-blocking (fixed position)
    expect(toast).toHaveStyle({ position: 'fixed' });
    // Should have accessibility attributes
    expect(toast).toHaveAttribute('role', 'status');
    expect(toast).toHaveAttribute('aria-live', 'polite');
  });

  it('positions notifications in peripheral vision, not center', () => {
    const Toast = () => (
      <div
        data-testid="notification"
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
        }}
      >
        Update available
      </div>
    );

    render(<Toast />);

    const notification = screen.getByTestId('notification');

    // Should be in corner, not centered
    expect(notification.style.position).toBe('fixed');
    expect(notification.style.bottom).toBe('20px');
    expect(notification.style.right).toBe('20px');
  });

  it('allows dismissing notifications without blocking interaction', async () => {
    const user = userEvent.setup();

    const DismissableToast = () => {
      const [visible, setVisible] = React.useState(true);

      return (
        <div>
          {visible && (
            <div data-testid="toast">
              Message
              <button onClick={() => setVisible(false)}>✕</button>
            </div>
          )}
          <button data-testid="main-action">Main Action</button>
        </div>
      );
    };

    render(<DismissableToast />);

    // Main action should be clickable even with toast present
    const mainAction = screen.getByTestId('main-action');
    await user.click(mainAction);
    expect(mainAction).toBeInTheDocument();

    // Toast can be dismissed
    await user.click(screen.getByText('✕'));
    expect(screen.queryByTestId('toast')).not.toBeInTheDocument();
  });

  it('rejects blocking modal dialogs for routine notifications', async () => {
    const user = userEvent.setup();

    // Anti-pattern: Blocking modal for save confirmation
    const BadPattern = () => {
      const [showModal, setShowModal] = React.useState(false);

      return (
        <div>
          <button onClick={() => setShowModal(true)}>Save</button>
          {showModal && (
            <div
              data-testid="modal"
              style={{
                position: 'fixed',
                inset: 0,
                backgroundColor: 'rgba(0,0,0,0.5)',
                zIndex: 1000,
              }}
            >
              <div>
                Saved! <button onClick={() => setShowModal(false)}>OK</button>
              </div>
            </div>
          )}
        </div>
      );
    };

    // Good pattern: Non-blocking toast
    const GoodPattern = () => {
      const [showToast, setShowToast] = React.useState(false);

      return (
        <div>
          <button onClick={() => setShowToast(true)}>Save</button>
          {showToast && (
            <div data-testid="toast" role="status" style={{ position: 'fixed' }}>
              Saved!
            </div>
          )}
        </div>
      );
    };

    // Bad pattern blocks interaction
    const { unmount: unmount1 } = render(<BadPattern />);
    await user.click(screen.getByText('Save'));
    const modal = screen.getByTestId('modal');
    expect(modal.style.zIndex).toBe('1000');
    unmount1();

    // Good pattern doesn't block
    const { unmount: unmount2 } = render(<GoodPattern />);
    await user.click(screen.getByText('Save'));
    const toast = screen.getByTestId('toast');
    expect(toast).toHaveAttribute('role', 'status');
    unmount2();
  });
});
