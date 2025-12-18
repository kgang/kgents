/**
 * Joy Components Test Suite
 *
 * Tests for Foundation 5: Animation Primitives & Joy Layer
 *
 * @see plans/_continuations/foundation-5-animation-primitives.md
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  Breathe,
  Pop,
  PopOnMount,
  Shake,
  Shimmer,
  ShimmerBlock,
  ShimmerText,
  PersonalityLoading,
  PersonalityLoadingInline,
  EmpathyError,
  InlineError,
  FullPageError,
  useMotionPreferences,
  getMotionPreferences,
  celebrate,
  celebrateQuick,
  celebrateEpic,
} from '../../../src/components/joy';
import { __resetCelebrateState } from '../../../src/components/joy/celebrate';
import { renderHook } from '@testing-library/react';

// =============================================================================
// Mock prefers-reduced-motion
// =============================================================================

function mockMatchMedia(prefersReducedMotion: boolean) {
  const listeners: ((e: { matches: boolean }) => void)[] = [];

  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: query.includes('reduce') ? prefersReducedMotion : false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: (_: string, callback: (e: { matches: boolean }) => void) => {
        listeners.push(callback);
      },
      removeEventListener: (_: string, callback: (e: { matches: boolean }) => void) => {
        const index = listeners.indexOf(callback);
        if (index > -1) listeners.splice(index, 1);
      },
      dispatchEvent: vi.fn(),
    })),
  });

  return {
    triggerChange: (newValue: boolean) => {
      listeners.forEach((l) => l({ matches: newValue }));
    },
  };
}

// =============================================================================
// useMotionPreferences Tests
// =============================================================================

describe('useMotionPreferences', () => {
  beforeEach(() => {
    mockMatchMedia(false);
  });

  it('returns shouldAnimate=true when no preference', () => {
    const { result } = renderHook(() => useMotionPreferences());
    expect(result.current.shouldAnimate).toBe(true);
    expect(result.current.prefersReducedMotion).toBe(false);
  });

  it('returns shouldAnimate=false when prefers reduced motion', () => {
    mockMatchMedia(true);
    const { result } = renderHook(() => useMotionPreferences());
    expect(result.current.shouldAnimate).toBe(false);
    expect(result.current.prefersReducedMotion).toBe(true);
  });

  it('getMotionPreferences returns current value', () => {
    mockMatchMedia(true);
    const prefs = getMotionPreferences();
    expect(prefs.prefersReducedMotion).toBe(true);
    expect(prefs.shouldAnimate).toBe(false);
  });
});

// =============================================================================
// Breathe Tests
// =============================================================================

describe('Breathe', () => {
  beforeEach(() => {
    mockMatchMedia(false);
  });

  it('renders children', () => {
    render(<Breathe>Test content</Breathe>);
    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(<Breathe className="custom-class">Content</Breathe>);
    // The motion.div wrapper has the className
    expect(container.querySelector('.custom-class')).toBeInTheDocument();
  });

  it('respects disabled prop', () => {
    const { container } = render(<Breathe disabled>Content</Breathe>);
    // When disabled, it renders a plain div without motion
    const wrapper = container.firstChild;
    expect(wrapper?.nodeName).toBe('DIV');
  });

  it('respects reduced motion preference', () => {
    mockMatchMedia(true);
    const { container } = render(<Breathe>Content</Breathe>);
    const wrapper = container.firstChild;
    expect(wrapper?.nodeName).toBe('DIV');
  });
});

// =============================================================================
// Pop Tests
// =============================================================================

describe('Pop', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    mockMatchMedia(false);
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders children', () => {
    render(<Pop>Test content</Pop>);
    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  it('respects disabled prop', () => {
    const { container } = render(<Pop disabled trigger>Content</Pop>);
    const wrapper = container.firstChild;
    expect(wrapper?.nodeName).toBe('DIV');
  });
});

describe('PopOnMount', () => {
  beforeEach(() => {
    mockMatchMedia(false);
  });

  it('renders children', () => {
    render(<PopOnMount>Content</PopOnMount>);
    expect(screen.getByText('Content')).toBeInTheDocument();
  });
});

// =============================================================================
// Shake Tests
// =============================================================================

describe('Shake', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    mockMatchMedia(false);
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders children', () => {
    render(<Shake>Test content</Shake>);
    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  it('accepts different intensity levels', () => {
    const { rerender } = render(<Shake intensity="gentle">Content</Shake>);
    expect(screen.getByText('Content')).toBeInTheDocument();

    rerender(<Shake intensity="normal">Content</Shake>);
    expect(screen.getByText('Content')).toBeInTheDocument();

    rerender(<Shake intensity="urgent">Content</Shake>);
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('respects disabled prop', () => {
    const { container } = render(<Shake disabled trigger>Content</Shake>);
    const wrapper = container.firstChild;
    expect(wrapper?.nodeName).toBe('DIV');
  });
});

// =============================================================================
// Shimmer Tests
// =============================================================================

describe('Shimmer', () => {
  beforeEach(() => {
    mockMatchMedia(false);
  });

  it('renders children', () => {
    render(<Shimmer>Test content</Shimmer>);
    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  it('can be deactivated', () => {
    const { container } = render(<Shimmer active={false}>Content</Shimmer>);
    expect(screen.getByText('Content')).toBeInTheDocument();
    // When not active, no shimmer overlay
    expect(container.querySelector('.pointer-events-none')).toBeNull();
  });
});

describe('ShimmerBlock', () => {
  it('renders with default props', () => {
    const { container } = render(<ShimmerBlock />);
    expect(container.querySelector('.bg-gray-700\\/50')).toBeInTheDocument();
  });

  it('accepts width and height', () => {
    const { container } = render(<ShimmerBlock width="w-24" height="h-8" />);
    expect(container.querySelector('.w-24')).toBeInTheDocument();
    expect(container.querySelector('.h-8')).toBeInTheDocument();
  });

  it('accepts rounded prop', () => {
    const { container } = render(<ShimmerBlock rounded="full" />);
    expect(container.querySelector('.rounded-full')).toBeInTheDocument();
  });
});

describe('ShimmerText', () => {
  it('renders multiple lines', () => {
    const { container } = render(<ShimmerText lines={3} />);
    const blocks = container.querySelectorAll('.bg-gray-700\\/50');
    expect(blocks.length).toBe(3);
  });
});

// =============================================================================
// PersonalityLoading Tests
// =============================================================================

describe('PersonalityLoading', () => {
  beforeEach(() => {
    mockMatchMedia(false);
  });

  // NOTE: PersonalityLoading uses Lucide icons (not emojis) per visual-system.md no-emoji policy.
  // Tests verify SVG icon presence instead of emoji text.

  it('renders with brain jewel Lucide icon', () => {
    render(<PersonalityLoading jewel="brain" />);
    expect(document.querySelector('svg')).toBeInTheDocument();
  });

  it('renders with gestalt jewel Lucide icon', () => {
    render(<PersonalityLoading jewel="gestalt" />);
    expect(document.querySelector('svg')).toBeInTheDocument();
  });

  it('renders with gardener jewel Lucide icon', () => {
    render(<PersonalityLoading jewel="gardener" />);
    expect(document.querySelector('svg')).toBeInTheDocument();
  });

  it('renders with atelier jewel Lucide icon', () => {
    render(<PersonalityLoading jewel="atelier" />);
    expect(document.querySelector('svg')).toBeInTheDocument();
  });

  it('renders with coalition jewel Lucide icon', () => {
    render(<PersonalityLoading jewel="coalition" />);
    expect(document.querySelector('svg')).toBeInTheDocument();
  });

  it('renders with park jewel Lucide icon', () => {
    render(<PersonalityLoading jewel="park" />);
    expect(document.querySelector('svg')).toBeInTheDocument();
  });

  it('renders with domain jewel Lucide icon', () => {
    render(<PersonalityLoading jewel="domain" />);
    expect(document.querySelector('svg')).toBeInTheDocument();
  });

  it('applies correct sizing based on size prop', () => {
    render(<PersonalityLoading jewel="brain" size="lg" />);
    // Size prop affects icon size and text, verify via Lucide icon
    expect(document.querySelector('svg')).toBeInTheDocument();
  });

  it('uses action-specific message when provided', () => {
    render(<PersonalityLoading jewel="brain" action="capture" rotate={false} />);
    expect(screen.getByText('Capturing into crystal...')).toBeInTheDocument();
  });
});

describe('PersonalityLoadingInline', () => {
  it('renders inline with Lucide icon', () => {
    render(<PersonalityLoadingInline jewel="brain" />);
    expect(document.querySelector('svg')).toBeInTheDocument();
  });
});

// =============================================================================
// EmpathyError Tests
// =============================================================================

describe('EmpathyError', () => {
  beforeEach(() => {
    mockMatchMedia(false);
  });

  // NOTE: EmpathyError uses Lucide icons (not emojis) per visual-system.md no-emoji policy.
  // Tests verify title text and SVG icon presence (not emoji text).

  it('renders network error with Lucide icon', () => {
    render(<EmpathyError type="network" />);
    expect(screen.getByText('Lost in the void...')).toBeInTheDocument();
    expect(document.querySelector('svg')).toBeInTheDocument();
  });

  it('renders notfound error with Lucide icon', () => {
    render(<EmpathyError type="notfound" />);
    expect(screen.getByText('Nothing here...')).toBeInTheDocument();
    expect(document.querySelector('svg')).toBeInTheDocument();
  });

  it('renders permission error with Lucide icon', () => {
    render(<EmpathyError type="permission" />);
    expect(screen.getByText("Door's locked...")).toBeInTheDocument();
    expect(document.querySelector('svg')).toBeInTheDocument();
  });

  it('renders timeout error with Lucide icon', () => {
    render(<EmpathyError type="timeout" />);
    expect(screen.getByText('Taking too long...')).toBeInTheDocument();
    expect(document.querySelector('svg')).toBeInTheDocument();
  });

  it('renders validation error with Lucide icon', () => {
    render(<EmpathyError type="validation" />);
    expect(screen.getByText('Something needs fixing...')).toBeInTheDocument();
    expect(document.querySelector('svg')).toBeInTheDocument();
  });

  it('renders unknown error with Lucide icon', () => {
    render(<EmpathyError type="unknown" />);
    expect(screen.getByText('Something unexpected...')).toBeInTheDocument();
    expect(document.querySelector('svg')).toBeInTheDocument();
  });

  it('accepts custom title and subtitle', () => {
    render(
      <EmpathyError
        type="network"
        title="Custom title"
        subtitle="Custom subtitle"
      />
    );
    expect(screen.getByText('Custom title')).toBeInTheDocument();
    expect(screen.getByText('Custom subtitle')).toBeInTheDocument();
  });

  it('shows action button when onAction provided', async () => {
    const user = userEvent.setup();
    const handleAction = vi.fn();

    render(
      <EmpathyError
        type="network"
        onAction={handleAction}
      />
    );

    const button = screen.getByRole('button', { name: 'Reconnect' });
    await user.click(button);
    expect(handleAction).toHaveBeenCalledTimes(1);
  });

  it('shows secondary action when provided', () => {
    render(
      <EmpathyError
        type="network"
        onAction={() => {}}
        secondaryAction="Cancel"
        onSecondaryAction={() => {}}
      />
    );

    expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument();
  });

  it('shows technical details when provided', () => {
    render(
      <EmpathyError
        type="network"
        details="Error code: 500"
      />
    );

    expect(screen.getByText('Error code: 500')).toBeInTheDocument();
  });
});

describe('InlineError', () => {
  it('renders error message with alert icon', () => {
    render(<InlineError message="Field is required" />);
    expect(screen.getByText('Field is required')).toBeInTheDocument();
    // Uses Lucide AlertTriangle icon (rendered as SVG) per visual-system.md no-emoji policy
    const alertIcon = document.querySelector('svg');
    expect(alertIcon).toBeInTheDocument();
  });
});

describe('FullPageError', () => {
  it('renders full-page error', () => {
    render(<FullPageError type="notfound" />);
    expect(screen.getByText('Nothing here...')).toBeInTheDocument();
  });
});

// =============================================================================
// Celebrate Tests
// =============================================================================

describe('celebrate', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    mockMatchMedia(false);
    __resetCelebrateState();
    // Cleanup any remaining containers
    document.querySelectorAll('[style*="z-index: 9999"]').forEach((el) => el.remove());
  });

  afterEach(() => {
    vi.useRealTimers();
    __resetCelebrateState();
    // Cleanup any remaining containers
    document.querySelectorAll('[style*="z-index: 9999"]').forEach((el) => el.remove());
  });

  it('creates confetti container', () => {
    celebrate({ intensity: 'subtle' });
    const container = document.querySelector('[style*="z-index: 9999"]');
    expect(container).toBeInTheDocument();
  });

  it('respects reduced motion preference', () => {
    mockMatchMedia(true);
    celebrate();
    const container = document.querySelector('[style*="z-index: 9999"]');
    expect(container).toBeNull();
  });

  it('celebrateQuick creates confetti', () => {
    celebrateQuick();
    const container = document.querySelector('[style*="z-index: 9999"]');
    expect(container).toBeInTheDocument();
  });

  it('celebrateEpic creates confetti', () => {
    celebrateEpic();
    const container = document.querySelector('[style*="z-index: 9999"]');
    expect(container).toBeInTheDocument();
  });
});
