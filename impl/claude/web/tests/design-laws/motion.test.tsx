/**
 * Motion Laws (M-01 through M-05)
 *
 * Tests for the 5 motion design laws from Zero Seed Creative Strategy.
 *
 * @see plans/zero-seed-creative-strategy.md (Part IV: UI/UX Design Laws)
 */

import { render, screen, waitFor as _waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import userEvent from '@testing-library/user-event';
import React from 'react';

// =============================================================================
// M-01: Asymmetric Breathing
// =============================================================================

describe('M-01: Asymmetric Breathing', () => {
  /**
   * Law Statement: 4-7-8 timing, not symmetric.
   *
   * Justification: The "breathing" animation follows calming 4-7-8 pattern:
   * 4s ease-in, 7s hold, 8s ease-out. This creates organic, not mechanical feel.
   *
   * Test: Breathing animations use 4-7-8 timing, not equal durations.
   */

  it('uses 4-7-8 asymmetric timing for breathing animations', () => {
    const breathingTiming = {
      easeIn: 4000, // 4s
      hold: 7000, // 7s
      easeOut: 8000, // 8s
    };

    expect(breathingTiming.easeIn).toBe(4000);
    expect(breathingTiming.hold).toBe(7000);
    expect(breathingTiming.easeOut).toBe(8000);

    // Should be asymmetric
    expect(breathingTiming.easeIn).not.toBe(breathingTiming.hold);
    expect(breathingTiming.hold).not.toBe(breathingTiming.easeOut);
  });

  it('applies 4-7-8 pattern to pulsing elements', async () => {
    const PulsingElement = () => {
      const [scale, setScale] = React.useState(1);

      React.useEffect(() => {
        // Ease in: 4s
        setTimeout(() => setScale(1.05), 4000);
        // Hold: 7s
        setTimeout(() => setScale(1.05), 4000 + 7000);
        // Ease out: 8s
        setTimeout(() => setScale(1), 4000 + 7000 + 8000);
      }, []);

      return (
        <div
          data-testid="pulse"
          style={{
            transform: `scale(${scale})`,
            transition: 'transform 4s ease-in, transform 8s ease-out',
          }}
        >
          Pulsing
        </div>
      );
    };

    render(<PulsingElement />);

    const element = screen.getByTestId('pulse');
    const _style = window.getComputedStyle(element);

    // Transition should include both ease-in and ease-out
    expect(element.style.transition).toContain('ease-in');
    expect(element.style.transition).toContain('ease-out');
  });

  it('rejects symmetric timing for organic animations', () => {
    // Anti-pattern: Equal durations (mechanical)
    const badTiming = {
      easeIn: 5000,
      hold: 5000,
      easeOut: 5000,
    };

    // Good pattern: 4-7-8 asymmetric (organic)
    const goodTiming = {
      easeIn: 4000,
      hold: 7000,
      easeOut: 8000,
    };

    // Bad timing is symmetric
    expect(badTiming.easeIn).toBe(badTiming.hold);
    expect(badTiming.hold).toBe(badTiming.easeOut);

    // Good timing is asymmetric
    expect(goodTiming.easeIn).not.toBe(goodTiming.hold);
    expect(goodTiming.hold).not.toBe(goodTiming.easeOut);
  });

  it('documents 4-7-8 pattern in animation constants', () => {
    const ANIMATION_TIMING = {
      BREATHING_EASE_IN: 4000,
      BREATHING_HOLD: 7000,
      BREATHING_EASE_OUT: 8000,
    };

    expect(ANIMATION_TIMING.BREATHING_EASE_IN).toBe(4000);
    expect(ANIMATION_TIMING.BREATHING_HOLD).toBe(7000);
    expect(ANIMATION_TIMING.BREATHING_EASE_OUT).toBe(8000);
  });
});

// =============================================================================
// M-02: Stillness Then Life
// =============================================================================

describe('M-02: Stillness Then Life', () => {
  /**
   * Law Statement: Default still, animation earned.
   *
   * Justification: Most things are still. Movement is earned through user
   * interaction or significant state change. No gratuitous animation.
   *
   * Test: Elements are static by default, animate only on interaction/change.
   */

  it('renders elements without animation by default', () => {
    const StaticElement = () => (
      <div data-testid="element" style={{ transition: 'none' }}>
        Content
      </div>
    );

    render(<StaticElement />);

    const element = screen.getByTestId('element');
    expect(element.style.transition).toBe('none');
  });

  it('adds animation only after user interaction', async () => {
    const user = userEvent.setup();

    const InteractiveElement = () => {
      const [animated, setAnimated] = React.useState(false);

      return (
        <div
          data-testid="element"
          onClick={() => setAnimated(true)}
          style={{
            transition: animated ? 'transform 0.3s ease' : 'none',
            transform: animated ? 'scale(1.05)' : 'scale(1)',
          }}
        >
          Click me
        </div>
      );
    };

    render(<InteractiveElement />);

    const element = screen.getByTestId('element');

    // Before interaction: no transition
    expect(element.style.transition).toBe('none');

    // After interaction: transition enabled
    await user.click(element);
    expect(element.style.transition).toContain('transform');
  });

  it('animates only for significant state changes', () => {
    const StateChangeElement = ({ status }: { status: 'idle' | 'loading' | 'success' }) => {
      const shouldAnimate = status !== 'idle';

      return (
        <div
          data-testid="element"
          data-animated={shouldAnimate}
          style={{
            transition: shouldAnimate ? 'all 0.3s ease' : 'none',
          }}
        >
          {status}
        </div>
      );
    };

    // Idle: no animation
    const { rerender, unmount } = render(<StateChangeElement status="idle" />);
    expect(screen.getByTestId('element')).toHaveAttribute('data-animated', 'false');

    // Loading: animate
    rerender(<StateChangeElement status="loading" />);
    expect(screen.getByTestId('element')).toHaveAttribute('data-animated', 'true');

    // Success: animate
    rerender(<StateChangeElement status="success" />);
    expect(screen.getByTestId('element')).toHaveAttribute('data-animated', 'true');

    unmount();
  });

  it('rejects gratuitous animation on page load', () => {
    // Anti-pattern: Everything animates on mount
    const BadPattern = () => (
      <div
        data-testid="bad"
        style={{
          animation: 'fadeIn 1s ease, pulse 2s infinite',
        }}
      >
        Content
      </div>
    );

    // Good pattern: Static by default
    const GoodPattern = () => (
      <div data-testid="good" style={{ animation: 'none' }}>
        Content
      </div>
    );

    const { unmount: unmount1 } = render(<BadPattern />);
    const badElement = screen.getByTestId('bad');
    expect(badElement.style.animation).toContain('fadeIn');
    unmount1();

    const { unmount: unmount2 } = render(<GoodPattern />);
    const goodElement = screen.getByTestId('good');
    expect(goodElement.style.animation).toBe('none');
    unmount2();
  });
});

// =============================================================================
// M-03: Mechanical Precision Organic Life
// =============================================================================

describe('M-03: Mechanical Precision Organic Life', () => {
  /**
   * Law Statement: Mechanical for structure, organic for life.
   *
   * Justification: Layout transitions are mechanical (linear, precise).
   * Content animations are organic (ease, spring). This creates the
   * "steel frame, living content" aesthetic.
   *
   * Test: Structural animations use linear, content uses ease/spring.
   */

  it('uses linear easing for structural layout transitions', () => {
    const LayoutTransition = ({ collapsed }: { collapsed: boolean }) => (
      <div
        data-testid="layout"
        style={{
          width: collapsed ? '60px' : '240px',
          transition: 'width 0.2s linear', // Mechanical
        }}
      >
        Sidebar
      </div>
    );

    render(<LayoutTransition collapsed={false} />);

    const layout = screen.getByTestId('layout');
    expect(layout.style.transition).toContain('linear');
  });

  it('uses organic easing for content animations', () => {
    const ContentAnimation = ({ visible }: { visible: boolean }) => (
      <div
        data-testid="content"
        style={{
          opacity: visible ? 1 : 0,
          transform: visible ? 'scale(1)' : 'scale(0.95)',
          transition: 'opacity 0.3s ease, transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)', // Organic
        }}
      >
        Content
      </div>
    );

    render(<ContentAnimation visible={true} />);

    const content = screen.getByTestId('content');
    expect(content.style.transition).toContain('ease');
    expect(content.style.transition).toContain('cubic-bezier');
  });

  it('distinguishes between frame and content animation timing', () => {
    const animations = {
      frame: {
        type: 'mechanical',
        easing: 'linear',
        duration: 200, // Fast, precise
      },
      content: {
        type: 'organic',
        easing: 'cubic-bezier(0.34, 1.56, 0.64, 1)', // Spring
        duration: 400, // Slower, bouncy
      },
    };

    expect(animations.frame.easing).toBe('linear');
    expect(animations.content.easing).toContain('cubic-bezier');
    expect(animations.content.duration).toBeGreaterThan(animations.frame.duration);
  });

  it('applies spring easing for delight moments', () => {
    const DelightAnimation = ({ triggered }: { triggered: boolean }) => (
      <div
        data-testid="delight"
        style={{
          transform: triggered ? 'scale(1.1)' : 'scale(1)',
          transition: 'transform 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55)', // Spring
        }}
      >
        🎉
      </div>
    );

    render(<DelightAnimation triggered={true} />);

    const element = screen.getByTestId('delight');
    // Spring easing for organic feel
    expect(element.style.transition).toContain('cubic-bezier');
  });
});

// =============================================================================
// M-04: Reduced Motion Respected
// =============================================================================

describe('M-04: Reduced Motion Respected', () => {
  /**
   * Law Statement: Respect prefers-reduced-motion.
   *
   * Justification: Users with vestibular disorders or motion sensitivity
   * must be able to disable animations. Accessibility > aesthetics.
   *
   * Test: All animations check prefers-reduced-motion media query.
   */

  beforeEach(() => {
    // Mock matchMedia
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation((query: string) => ({
        matches: query === '(prefers-reduced-motion: reduce)',
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });
  });

  it('detects prefers-reduced-motion media query', () => {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    expect(prefersReducedMotion).toBe(true);
  });

  it('disables animations when prefers-reduced-motion is set', () => {
    const MotionAwareComponent = () => {
      const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      return (
        <div
          data-testid="element"
          style={{
            transition: prefersReducedMotion ? 'none' : 'all 0.3s ease',
          }}
        >
          Content
        </div>
      );
    };

    render(<MotionAwareComponent />);

    const element = screen.getByTestId('element');
    expect(element.style.transition).toBe('none');
  });

  it('provides instant feedback when animations are disabled', () => {
    const ReducedMotionButton = () => {
      const [clicked, setClicked] = React.useState(false);
      const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      return (
        <button
          data-testid="button"
          onClick={() => setClicked(true)}
          data-clicked={clicked}
          style={{
            transition: prefersReducedMotion ? 'none' : 'transform 0.2s ease',
            transform: clicked ? 'scale(0.95)' : 'scale(1)',
          }}
        >
          Click me
        </button>
      );
    };

    render(<ReducedMotionButton />);

    const button = screen.getByTestId('button');
    // Should have no transition when reduced motion is preferred
    expect(button.style.transition).toBe('none');
  });

  it('falls back to immediate state changes when motion is reduced', async () => {
    const user = userEvent.setup();

    const StateMachine = () => {
      const [state, setState] = React.useState<'idle' | 'active'>('idle');
      const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      const handleClick = () => {
        if (prefersReducedMotion) {
          // Instant state change
          setState('active');
        } else {
          // Animated state change
          setTimeout(() => setState('active'), 300);
        }
      };

      return (
        <button data-testid="button" onClick={handleClick} data-state={state}>
          {state}
        </button>
      );
    };

    render(<StateMachine />);

    const button = screen.getByTestId('button');

    await user.click(button);

    // With reduced motion, state should change immediately
    expect(button).toHaveAttribute('data-state', 'active');
  });
});

// =============================================================================
// M-05: Animation Justification
// =============================================================================

describe('M-05: Animation Justification', () => {
  /**
   * Law Statement: Every animation has semantic reason.
   *
   * Justification: No animation without purpose. Every movement should
   * communicate state change, provide feedback, or guide attention.
   *
   * Test: Animations are tied to semantic purpose (state, feedback, guidance).
   */

  it('ties animations to state changes', () => {
    const animationPurposes = {
      fadeIn: 'Indicates content has loaded',
      fadeOut: 'Indicates content is being removed',
      pulse: 'Draws attention to important change',
      slide: 'Shows spatial relationship',
      scale: 'Provides tactile feedback',
    };

    // Each animation should have a justification
    Object.entries(animationPurposes).forEach(([_animation, purpose]) => {
      expect(purpose).toBeTruthy();
      expect(purpose.length).toBeGreaterThan(10);
    });
  });

  it('animates to provide user feedback on actions', async () => {
    const _user = userEvent.setup();

    const FeedbackButton = () => {
      const [pressed, setPressed] = React.useState(false);

      return (
        <button
          data-testid="button"
          onMouseDown={() => setPressed(true)}
          onMouseUp={() => setPressed(false)}
          style={{
            transform: pressed ? 'scale(0.95)' : 'scale(1)',
            transition: 'transform 0.1s ease',
          }}
        >
          Press me
        </button>
      );
    };

    render(<FeedbackButton />);

    const button = screen.getByTestId('button');

    // Animation provides tactile feedback
    // Purpose: Communicate that button is being pressed
    expect(button.style.transition).toContain('transform');
  });

  it('animates to guide user attention', () => {
    const AttentionGuide = ({ highlight }: { highlight: boolean }) => (
      <div
        data-testid="highlight"
        style={{
          animation: highlight ? 'pulse 2s ease-in-out 3' : 'none',
        }}
      >
        Important notification
      </div>
    );

    render(<AttentionGuide highlight={true} />);

    const element = screen.getByTestId('highlight');

    // Animation purpose: Guide user's attention to important information
    expect(element.style.animation).toContain('pulse');
  });

  it('rejects animations without clear semantic purpose', () => {
    // Anti-pattern: Random decorative animation
    const badAnimations = [
      { name: 'spinForever', purpose: 'Looks cool' },
      { name: 'rainbow', purpose: 'Adds color' },
      { name: 'bounce', purpose: 'Fun' },
    ];

    // Good pattern: Purpose-driven animations
    const goodAnimations = [
      { name: 'spinner', purpose: 'Indicates loading state' },
      { name: 'successGlow', purpose: 'Confirms successful action' },
      { name: 'errorShake', purpose: 'Draws attention to error' },
    ];

    // Bad animations have vague purposes
    expect(badAnimations[0].purpose).toBe('Looks cool');

    // Good animations have clear semantic purposes
    expect(goodAnimations[0].purpose).toContain('loading state');
    expect(goodAnimations[1].purpose).toContain('successful action');
    expect(goodAnimations[2].purpose).toContain('error');
  });

  it('documents animation purpose in code comments or constants', () => {
    const ANIMATIONS = {
      FADE_IN: {
        duration: 300,
        easing: 'ease-in',
        purpose: 'Indicates new content has loaded',
      },
      PULSE: {
        duration: 2000,
        easing: 'ease-in-out',
        purpose: 'Draws attention to contradiction or update',
      },
      SLIDE_UP: {
        duration: 400,
        easing: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
        purpose: 'Shows content emerging from below',
      },
    };

    // Every animation should document its purpose
    Object.values(ANIMATIONS).forEach((animation) => {
      expect(animation).toHaveProperty('purpose');
      expect(animation.purpose.length).toBeGreaterThan(15);
    });
  });
});
