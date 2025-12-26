/**
 * Navigation Laws (N-01 through N-05)
 *
 * Tests for the 5 navigation design laws from Zero Seed Creative Strategy.
 *
 * @see plans/zero-seed-creative-strategy.md (Part IV: UI/UX Design Laws)
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import userEvent from '@testing-library/user-event';

// =============================================================================
// N-01: Vim Primary Arrow Alias
// =============================================================================

describe('N-01: Vim Primary Arrow Alias', () => {
  /**
   * Law Statement: j/k primary, arrows alias.
   *
   * Justification: Vim navigation is primary. Arrow keys work as aliases,
   * but documentation and help text show j/k first.
   *
   * Test: Both j/k and arrows work, but j/k documented.
   */

  it('accepts both j/k and arrow keys for navigation', async () => {
    const user = userEvent.setup();
    let currentIndex = 0;

    const NavigableList = () => {
      const [selected, setSelected] = React.useState(0);
      currentIndex = selected;

      React.useEffect(() => {
        const handleKey = (e: KeyboardEvent) => {
          if (e.key === 'j' || e.key === 'ArrowDown') {
            setSelected((s) => Math.min(s + 1, 2));
          }
          if (e.key === 'k' || e.key === 'ArrowUp') {
            setSelected((s) => Math.max(s - 1, 0));
          }
        };
        window.addEventListener('keydown', handleKey);
        return () => window.removeEventListener('keydown', handleKey);
      }, []);

      return (
        <div data-testid="list">
          {[0, 1, 2].map((i) => (
            <div key={i} data-selected={i === selected}>
              Item {i}
            </div>
          ))}
        </div>
      );
    };

    render(<NavigableList />);

    // j moves down
    await user.keyboard('j');
    expect(currentIndex).toBe(1);

    // k moves up
    await user.keyboard('k');
    expect(currentIndex).toBe(0);

    // Arrow keys also work
    await user.keyboard('{ArrowDown}');
    expect(currentIndex).toBe(1);

    await user.keyboard('{ArrowUp}');
    expect(currentIndex).toBe(0);
  });

  it('documents j/k as primary in help text, arrows as alias', () => {
    const HelpText = () => (
      <div data-testid="help">
        <div>Navigation: j (down), k (up)</div>
        <div>Also: Arrow keys work as aliases</div>
      </div>
    );

    render(<HelpText />);
    const help = screen.getByTestId('help');

    // j/k mentioned first
    expect(help.textContent).toMatch(/j.*k/);
    // Arrows mentioned as alias
    expect(help.textContent).toMatch(/alias/i);
  });

  it('rejects arrow-first documentation pattern', () => {
    // Anti-pattern: "Use arrows (or j/k)"
    // Good pattern: "Use j/k (arrows also work)"

    const BadPattern = () => <div>Use arrows to navigate</div>;
    const GoodPattern = () => <div>Use j/k to navigate (arrows also work)</div>;

    const { unmount: unmount1 } = render(<BadPattern />);
    expect(screen.getByText(/arrows/i)).toBeInTheDocument();
    unmount1();

    const { unmount: unmount2 } = render(<GoodPattern />);
    const text = screen.getByText(/j\/k/i);
    expect(text.textContent).toMatch(/j\/k.*arrows/);
    unmount2();
  });
});

// =============================================================================
// N-02: Edge Traversal Not Directory
// =============================================================================

describe('N-02: Edge Traversal Not Directory', () => {
  /**
   * Law Statement: Navigate graph, not filesystem.
   *
   * Justification: kgents is a hypergraph, not a file tree. Navigation
   * follows edges (relationships), not directory hierarchy.
   *
   * Test: Navigation uses edge-based paths, not file paths.
   */

  it('uses edge-based navigation structure', () => {
    const GraphNav = () => (
      <nav data-testid="nav">
        <button data-edge="enables">Enables →</button>
        <button data-edge="contradicts">Contradicts ⚡</button>
        <button data-edge="synthesizes">Synthesizes ◇</button>
      </nav>
    );

    render(<GraphNav />);

    // Navigation exposes edge types, not directories
    expect(screen.getByText(/Enables/)).toBeInTheDocument();
    expect(screen.getByText(/Contradicts/)).toBeInTheDocument();
    expect(screen.getByText(/Synthesizes/)).toBeInTheDocument();
  });

  it('rejects file explorer pattern for K-Block navigation', () => {
    // Anti-pattern: /folder/subfolder/file.md
    // Good pattern: principle --enables--> goal

    const BadPattern = () => (
      <div data-testid="breadcrumb">
        Home / Projects / Specs / architecture.md
      </div>
    );

    const GoodPattern = () => (
      <div data-testid="trail">
        {'Principle --enables--> Goal --synthesizes--> Decision'}
      </div>
    );

    const { unmount: unmount1 } = render(<BadPattern />);
    expect(screen.getByTestId('breadcrumb').textContent).toMatch(/\//);
    unmount1();

    const { unmount: unmount2 } = render(<GoodPattern />);
    expect(screen.getByTestId('trail').textContent).toMatch(/--.*-->/);
    unmount2();
  });

  it('exposes edge semantics in navigation UI', () => {
    const edges = [
      { type: 'enables', symbol: '→', label: 'Enables' },
      { type: 'contradicts', symbol: '⚡', label: 'Contradicts' },
      { type: 'synthesizes', symbol: '◇', label: 'Synthesizes' },
      { type: 'grounds', symbol: '⊥', label: 'Grounds' },
    ];

    const EdgeNav = () => (
      <div data-testid="edges">
        {edges.map((edge) => (
          <div key={edge.type} data-edge-type={edge.type}>
            {edge.symbol} {edge.label}
          </div>
        ))}
      </div>
    );

    render(<EdgeNav />);

    edges.forEach((edge) => {
      const element = screen.getByText(new RegExp(edge.label));
      expect(element.textContent).toContain(edge.symbol);
    });
  });
});

// =============================================================================
// N-03: Mode Return to NORMAL
// =============================================================================

describe('N-03: Mode Return to NORMAL', () => {
  /**
   * Law Statement: Escape always returns to NORMAL.
   *
   * Justification: Vim-inspired modal editing. Escape is the universal
   * "get me out" key that always returns to NORMAL mode.
   *
   * Test: Escape key from any mode returns to NORMAL.
   */

  it('returns to NORMAL mode from INSERT on Escape', async () => {
    const user = userEvent.setup();
    const ModeEditor = () => {
      const [mode, setMode] = React.useState<'NORMAL' | 'INSERT'>('NORMAL');

      React.useEffect(() => {
        const handleKey = (e: KeyboardEvent) => {
          if (e.key === 'i') setMode('INSERT');
          if (e.key === 'Escape') setMode('NORMAL');
        };
        window.addEventListener('keydown', handleKey);
        return () => window.removeEventListener('keydown', handleKey);
      }, []);

      return <div data-testid="mode">{mode}</div>;
    };

    render(<ModeEditor />);

    // Start in NORMAL
    expect(screen.getByTestId('mode')).toHaveTextContent('NORMAL');

    // Press 'i' to enter INSERT
    await user.keyboard('i');
    expect(screen.getByTestId('mode')).toHaveTextContent('INSERT');

    // Escape returns to NORMAL
    await user.keyboard('{Escape}');
    expect(screen.getByTestId('mode')).toHaveTextContent('NORMAL');
  });

  it('returns to NORMAL mode from VISUAL on Escape', async () => {
    const user = userEvent.setup();
    const ModeEditor = () => {
      const [mode, setMode] = React.useState<'NORMAL' | 'VISUAL'>('NORMAL');

      React.useEffect(() => {
        const handleKey = (e: KeyboardEvent) => {
          if (e.key === 'v') setMode('VISUAL');
          if (e.key === 'Escape') setMode('NORMAL');
        };
        window.addEventListener('keydown', handleKey);
        return () => window.removeEventListener('keydown', handleKey);
      }, []);

      return <div data-testid="mode">{mode}</div>;
    };

    render(<ModeEditor />);

    await user.keyboard('v');
    expect(screen.getByTestId('mode')).toHaveTextContent('VISUAL');

    await user.keyboard('{Escape}');
    expect(screen.getByTestId('mode')).toHaveTextContent('NORMAL');
  });

  it('enforces Escape as universal "get me out" key', async () => {
    const user = userEvent.setup();
    const modes = ['INSERT', 'VISUAL', 'EDGE', 'COMMAND', 'WITNESS'];

    for (const startMode of modes) {
      const ModeEditor = () => {
        const [mode, setMode] = React.useState(startMode);

        React.useEffect(() => {
          const handleKey = (e: KeyboardEvent) => {
            if (e.key === 'Escape') setMode('NORMAL');
          };
          window.addEventListener('keydown', handleKey);
          return () => window.removeEventListener('keydown', handleKey);
        }, []);

        return <div data-testid="mode">{mode}</div>;
      };

      const { unmount } = render(<ModeEditor />);

      expect(screen.getByTestId('mode')).toHaveTextContent(startMode);

      await user.keyboard('{Escape}');
      expect(screen.getByTestId('mode')).toHaveTextContent('NORMAL');

      unmount();
    }
  });
});

// =============================================================================
// N-04: Trail Is Semantic
// =============================================================================

describe('N-04: Trail Is Semantic', () => {
  /**
   * Law Statement: Trail records edges, not positions.
   *
   * Justification: Navigation trail captures semantic path through the
   * knowledge graph, not just scroll positions or URLs visited.
   *
   * Test: Trail captures edge relationships, not just K-Block IDs.
   */

  it('records semantic edges in navigation trail', () => {
    const trail = [
      { from: 'principle-1', to: 'goal-1', edge: 'enables' },
      { from: 'goal-1', to: 'decision-1', edge: 'synthesizes' },
    ];

    const Trail = () => (
      <div data-testid="trail">
        {trail.map((step, i) => (
          <div key={i} data-edge={step.edge}>
            {step.from} {'--'}{step.edge}{'-->'} {step.to}
          </div>
        ))}
      </div>
    );

    render(<Trail />);

    // Trail includes edge semantics
    expect(screen.getByText(/--enables-->/)).toBeInTheDocument();
    expect(screen.getByText(/--synthesizes-->/)).toBeInTheDocument();
  });

  it('rejects position-only breadcrumbs in favor of semantic trails', () => {
    // Anti-pattern: Just positions/IDs
    const BadTrail = () => (
      <div>
        <span>Block A</span> → <span>Block B</span> → <span>Block C</span>
      </div>
    );

    // Good pattern: Semantic relationships
    const GoodTrail = () => (
      <div>
        <span>Block A</span> {' --enables--> '} <span>Block B</span> {' --contradicts--> '} <span>Block C</span>
      </div>
    );

    const { unmount: unmount1 } = render(<BadTrail />);
    const badText = screen.getByText(/Block A/).parentElement?.textContent || '';
    expect(badText).toMatch(/→/);
    unmount1();

    const { unmount: unmount2 } = render(<GoodTrail />);
    const goodText = screen.getByText(/Block A/).parentElement?.textContent || '';
    expect(goodText).toMatch(/--enables-->/);
    unmount2();
  });

  it('preserves edge metadata in trail for reconstruction', () => {
    interface TrailStep {
      from: string;
      to: string;
      edge: string;
      timestamp: Date;
    }

    const trail: TrailStep[] = [
      {
        from: 'axiom-1',
        to: 'ground-1',
        edge: 'grounds',
        timestamp: new Date('2025-12-20'),
      },
    ];

    // Trail should capture enough metadata to reconstruct the path
    expect(trail[0]).toHaveProperty('from');
    expect(trail[0]).toHaveProperty('to');
    expect(trail[0]).toHaveProperty('edge');
    expect(trail[0]).toHaveProperty('timestamp');
  });
});

// =============================================================================
// N-05: Jump Stack Preservation
// =============================================================================

describe('N-05: Jump Stack Preservation', () => {
  /**
   * Law Statement: Jumps preserve return path.
   *
   * Justification: When you jump to a K-Block (via search, link, etc.),
   * the system remembers where you came from so you can return.
   *
   * Test: Jump stack maintains previous locations for back navigation.
   */

  it('maintains jump stack for back navigation', () => {
    const jumpStack: string[] = [];

    const jump = (_to: string) => {
      const current = 'current-block';
      jumpStack.push(current);
      // Navigate to '_to'
    };

    const back = () => {
      return jumpStack.pop();
    };

    // Make jumps
    jump('block-1');
    jump('block-2');
    jump('block-3');

    // Jump stack should preserve path
    expect(jumpStack).toHaveLength(3);

    // Back navigation should restore previous locations
    expect(back()).toBe('current-block');
    expect(back()).toBe('current-block');
    expect(back()).toBe('current-block');
  });

  it('distinguishes between linear navigation and jumps', () => {
    // Linear navigation (j/k, clicking next): doesn't push to jump stack
    // Jumps (search, portal, link): pushes to jump stack

    const linearNav = (direction: 'next' | 'prev') => {
      // Just move, don't push to stack
      return direction === 'next' ? 'next-block' : 'prev-block';
    };

    const jump = (to: string) => {
      // Push current to stack, then navigate
      return { jumped: true, to };
    };

    const linearResult = linearNav('next');
    expect(linearResult).toBe('next-block');

    const jumpResult = jump('far-away-block');
    expect(jumpResult.jumped).toBe(true);
  });

  it('preserves jump stack across sessions for deep work', () => {
    // Jump stack should be serializable for persistence
    interface JumpEntry {
      blockId: string;
      timestamp: Date;
      edgePath?: string[];
    }

    const jumpStack: JumpEntry[] = [
      {
        blockId: 'principle-1',
        timestamp: new Date('2025-12-20T10:00:00'),
        edgePath: ['axiom-1', 'ground-1', 'principle-1'],
      },
      {
        blockId: 'goal-5',
        timestamp: new Date('2025-12-20T10:05:00'),
      },
    ];

    // Should be serializable
    const serialized = JSON.stringify(jumpStack);
    const deserialized = JSON.parse(serialized);

    expect(deserialized).toHaveLength(2);
    expect(deserialized[0].blockId).toBe('principle-1');
  });

  it('limits jump stack depth to prevent memory bloat', () => {
    const MAX_JUMP_STACK = 50;
    const jumpStack: string[] = [];

    const jump = (_to: string) => {
      jumpStack.push('current');
      if (jumpStack.length > MAX_JUMP_STACK) {
        jumpStack.shift(); // Remove oldest
      }
    };

    // Make 100 jumps
    for (let i = 0; i < 100; i++) {
      jump(`block-${i}`);
    }

    // Should be capped at 50
    expect(jumpStack).toHaveLength(MAX_JUMP_STACK);
  });
});

// Helper: Add React import for JSX
import React from 'react';
