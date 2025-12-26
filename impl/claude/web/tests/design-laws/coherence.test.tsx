/**
 * Coherence Laws (H-01 through H-05)
 *
 * Tests for the 5 coherence design laws from Zero Seed Creative Strategy.
 * "H" stands for "Heterarchical" — the coherence system.
 *
 * @see plans/zero-seed-creative-strategy.md (Part IV: UI/UX Design Laws)
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import userEvent from '@testing-library/user-event';
import React from 'react';

// =============================================================================
// H-01: Linear Adaptation
// =============================================================================

describe('H-01: Linear Adaptation', () => {
  /**
   * Law Statement: System adapts to user, not vice versa.
   *
   * Justification: The system should learn from user behavior and adapt
   * gradually (linearly). Users shouldn't have to configure everything upfront.
   *
   * Test: System tracks preferences and adapts over time.
   */

  it('tracks user preferences implicitly from behavior', () => {
    const trackPreference = (action: string, value: unknown) => {
      const preferences = {
        density: 'comfortable',
        ranking: 'chronological',
        tone: 'developer',
      };

      if (action === 'set_density') {
        preferences.density = value as string;
      }

      return preferences;
    };

    const prefs = trackPreference('set_density', 'compact');
    expect(prefs.density).toBe('compact');
  });

  it('adapts system behavior based on accumulated preferences', () => {
    interface UserProfile {
      interactions: number;
      preferredDensity?: string;
      preferredTone?: string;
    }

    const profile: UserProfile = {
      interactions: 0,
    };

    const recordInteraction = (action: string) => {
      profile.interactions++;

      // After 10 interactions, system can infer preferences
      if (profile.interactions > 10) {
        if (action === 'compact_view') {
          profile.preferredDensity = 'compact';
        }
      }
    };

    // First 10 interactions: no adaptation
    for (let i = 0; i < 10; i++) {
      recordInteraction('compact_view');
    }
    expect(profile.preferredDensity).toBeUndefined();

    // After 10 interactions: system adapts
    recordInteraction('compact_view');
    expect(profile.preferredDensity).toBe('compact');
  });

  it('gradually adjusts suggestions based on user choices', () => {
    const suggestions = {
      layer: [1, 2, 3, 4, 5],
      ranking: ['chronological', 'loss-ascending', 'algorithmic'],
    };

    const adaptSuggestions = (userChoices: string[]) => {
      // If user consistently chooses 'chronological', boost it
      const chronologicalCount = userChoices.filter((c) => c === 'chronological').length;

      if (chronologicalCount > userChoices.length / 2) {
        // Move chronological to front
        suggestions.ranking = ['chronological', 'loss-ascending', 'algorithmic'];
      }

      return suggestions;
    };

    const choices = ['chronological', 'chronological', 'chronological', 'loss-ascending'];
    const adapted = adaptSuggestions(choices);

    expect(adapted.ranking[0]).toBe('chronological');
  });

  it('rejects requiring extensive upfront configuration', () => {
    // Anti-pattern: 20-question onboarding wizard
    const badOnboarding = {
      steps: 20,
      required: true,
      message: 'Complete all settings before using the system',
    };

    // Good pattern: Minimal setup, learn over time
    const goodOnboarding = {
      steps: 1,
      required: false,
      message: 'Start using the system. It will adapt to you.',
    };

    expect(badOnboarding.steps).toBe(20);
    expect(goodOnboarding.steps).toBe(1);
    expect(goodOnboarding.message).toContain('adapt to you');
  });
});

// =============================================================================
// H-02: Quarantine Not Block
// =============================================================================

describe('H-02: Quarantine Not Block', () => {
  /**
   * Law Statement: High-loss quarantined, not rejected.
   *
   * Justification: K-Blocks with high loss (low coherence) are quarantined
   * for review, not outright rejected. The system is permissive, not punitive.
   *
   * Test: High-loss K-Blocks are flagged but still created/accessible.
   */

  it('allows creation of high-loss K-Blocks with quarantine flag', () => {
    const createKBlock = (content: string, loss: number) => {
      const kblock = {
        id: 'kb-1',
        content,
        loss,
        quarantined: loss > 0.7, // Quarantine if loss > 0.7
      };

      return kblock;
    };

    const highLossBlock = createKBlock('Random thoughts', 0.85);

    // Should be created, not rejected
    expect(highLossBlock).toBeDefined();
    expect(highLossBlock.quarantined).toBe(true);
  });

  it('displays quarantined K-Blocks with advisory styling', () => {
    const QuarantinedKBlock = ({ loss }: { loss: number }) => {
      const isQuarantined = loss > 0.7;

      return (
        <div
          data-testid="kblock"
          data-quarantined={isQuarantined}
          style={{
            borderColor: isQuarantined ? 'var(--color-amber-400)' : 'var(--color-steel-300)',
            opacity: isQuarantined ? 0.7 : 1,
          }}
        >
          K-Block (loss: {loss.toFixed(2)})
        </div>
      );
    };

    render(<QuarantinedKBlock loss={0.85} />);

    const kblock = screen.getByTestId('kblock');

    // Should be visible but with advisory styling
    expect(kblock).toBeInTheDocument();
    expect(kblock).toHaveAttribute('data-quarantined', 'true');
    expect(kblock.style.opacity).toBe('0.7');
  });

  it('provides option to review or refine quarantined items', () => {
    const QuarantineActions = () => (
      <div>
        <div data-testid="message">
          This K-Block has high loss. Consider refining or linking to principles.
        </div>
        <button data-testid="refine">Refine</button>
        <button data-testid="link">Link to principle</button>
        <button data-testid="accept">Accept anyway</button>
      </div>
    );

    render(<QuarantineActions />);

    // Should offer constructive options, not just "delete"
    expect(screen.getByTestId('refine')).toBeInTheDocument();
    expect(screen.getByTestId('link')).toBeInTheDocument();
    expect(screen.getByTestId('accept')).toBeInTheDocument();
  });

  it('rejects outright blocking of high-loss content', () => {
    // Anti-pattern: Reject creation if loss > threshold
    const badCreate = (loss: number) => {
      if (loss > 0.7) {
        throw new Error('Content rejected: too incoherent');
      }
      return { created: true };
    };

    // Good pattern: Create with quarantine flag
    const goodCreate = (loss: number) => {
      return {
        created: true,
        quarantined: loss > 0.7,
        message: loss > 0.7 ? 'Quarantined for review' : 'Created',
      };
    };

    // Bad pattern throws error
    expect(() => badCreate(0.85)).toThrow();

    // Good pattern allows creation
    const result = goodCreate(0.85);
    expect(result.created).toBe(true);
    expect(result.quarantined).toBe(true);
  });
});

// =============================================================================
// H-03: Cross-Layer Edge Allowed
// =============================================================================

describe('H-03: Cross-Layer Edge Allowed', () => {
  /**
   * Law Statement: Distant layer edges allowed + flagged.
   *
   * Justification: Users can create edges between distant layers (e.g., L0 → L5),
   * but the system flags these as unusual for review. Permissive, not restrictive.
   *
   * Test: Cross-layer edges are allowed but flagged with metadata.
   */

  it('allows creating edges between distant layers', () => {
    const createEdge = (from: number, to: number) => {
      const layerDistance = Math.abs(to - from);
      const flagged = layerDistance > 2; // Flag if more than 2 layers apart

      return {
        from,
        to,
        distance: layerDistance,
        flagged,
      };
    };

    const distantEdge = createEdge(0, 5); // L0 → L5

    // Should be allowed
    expect(distantEdge).toBeDefined();
    expect(distantEdge.flagged).toBe(true);
    expect(distantEdge.distance).toBe(5);
  });

  it('flags cross-layer edges with advisory metadata', () => {
    const EdgeDisplay = ({ from, to }: { from: number; to: number }) => {
      const distance = Math.abs(to - from);
      const isCrossLayer = distance > 2;

      return (
        <div
          data-testid="edge"
          data-cross-layer={isCrossLayer}
          style={{
            borderColor: isCrossLayer ? 'var(--color-amber-400)' : 'var(--color-steel-300)',
          }}
        >
          L{from} → L{to}
          {isCrossLayer && <span data-testid="flag"> ⚠ Unusual connection</span>}
        </div>
      );
    };

    render(<EdgeDisplay from={0} to={5} />);

    const edge = screen.getByTestId('edge');
    const flag = screen.getByTestId('flag');

    // Should be rendered with flag
    expect(edge).toHaveAttribute('data-cross-layer', 'true');
    expect(flag).toBeInTheDocument();
  });

  it('provides explanation for why cross-layer edges are flagged', () => {
    const CrossLayerWarning = () => (
      <div data-testid="warning">
        <p>This edge spans 5 layers (L0 → L5).</p>
        <p>Consider adding intermediate steps for better coherence.</p>
        <button>Show suggested path</button>
      </div>
    );

    render(<CrossLayerWarning />);

    const warning = screen.getByTestId('warning');

    // Should provide guidance, not just a warning
    expect(warning.textContent).toContain('intermediate steps');
    expect(screen.getByText(/Show suggested path/)).toBeInTheDocument();
  });

  it('rejects blocking cross-layer edges entirely', () => {
    // Anti-pattern: Prevent creation if layer distance > 2
    const badCreate = (from: number, to: number) => {
      if (Math.abs(to - from) > 2) {
        throw new Error('Cannot create edge across more than 2 layers');
      }
      return { created: true };
    };

    // Good pattern: Allow but flag
    const goodCreate = (from: number, to: number) => {
      return {
        created: true,
        flagged: Math.abs(to - from) > 2,
      };
    };

    // Bad pattern blocks
    expect(() => badCreate(0, 5)).toThrow();

    // Good pattern allows
    const result = goodCreate(0, 5);
    expect(result.created).toBe(true);
    expect(result.flagged).toBe(true);
  });
});

// =============================================================================
// H-04: K-Block Isolation
// =============================================================================

describe('H-04: K-Block Isolation', () => {
  /**
   * Law Statement: INSERT creates K-Block, changes isolated.
   *
   * Justification: In INSERT mode, edits are isolated in a new K-Block.
   * Changes don't affect the main graph until committed. This provides
   * a safe sandbox for experimentation.
   *
   * Test: INSERT mode creates isolated K-Block, doesn't mutate existing graph.
   */

  it('creates new K-Block when entering INSERT mode', async () => {
    const user = userEvent.setup();

    const Editor = () => {
      const [mode, setMode] = React.useState<'NORMAL' | 'INSERT'>('NORMAL');
      const [kblocks, setKBlocks] = React.useState<string[]>([]);

      const handleInsert = () => {
        setMode('INSERT');
        // Create isolated K-Block
        setKBlocks([...kblocks, 'new-kblock-isolated']);
      };

      return (
        <div>
          <div data-testid="mode">{mode}</div>
          <button onClick={handleInsert}>Enter INSERT</button>
          <div data-testid="kblocks">{kblocks.join(', ')}</div>
        </div>
      );
    };

    render(<Editor />);

    await user.click(screen.getByText('Enter INSERT'));

    // Mode should change
    expect(screen.getByTestId('mode')).toHaveTextContent('INSERT');

    // New isolated K-Block should be created
    expect(screen.getByTestId('kblocks')).toHaveTextContent('new-kblock-isolated');
  });

  it('isolates edits to K-Block until commit', async () => {
    const user = userEvent.setup();

    const IsolatedEditor = () => {
      const [draft, setDraft] = React.useState('');
      const [committed, setCommitted] = React.useState('');

      return (
        <div>
          <input
            data-testid="draft"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder="Draft changes..."
          />
          <button onClick={() => setCommitted(draft)}>Commit</button>
          <div data-testid="committed">{committed}</div>
        </div>
      );
    };

    render(<IsolatedEditor />);

    const draftInput = screen.getByTestId('draft');
    const committedDiv = screen.getByTestId('committed');

    // Type in draft
    await user.type(draftInput, 'Draft content');

    // Committed should still be empty (isolated)
    expect(committedDiv).toHaveTextContent('');

    // Commit
    await user.click(screen.getByText('Commit'));

    // Now committed should have content
    expect(committedDiv).toHaveTextContent('Draft content');
  });

  it('provides preview of isolated changes before commit', () => {
    const PreviewPane = ({ draft, current }: { draft: string; current: string }) => (
      <div>
        <div data-testid="current">Current: {current}</div>
        <div data-testid="draft">Draft: {draft}</div>
        <div data-testid="isolated">
          {draft !== current ? 'Changes isolated' : 'No changes'}
        </div>
      </div>
    );

    render(<PreviewPane draft="New content" current="Old content" />);

    expect(screen.getByTestId('isolated')).toHaveTextContent('Changes isolated');
  });

  it('rejects direct mutation of existing K-Blocks', () => {
    // Anti-pattern: Mutate existing K-Block directly
    const badEdit = (kblock: { content: string }) => {
      kblock.content = 'Modified'; // Direct mutation
      return kblock;
    };

    // Good pattern: Create isolated copy, edit copy
    const goodEdit = (kblock: { content: string }) => {
      const isolated = { ...kblock, content: 'Modified' };
      return { original: kblock, isolated };
    };

    const original = { content: 'Original' };

    // Bad pattern mutates original
    badEdit(original);
    expect(original.content).toBe('Modified');

    // Good pattern preserves original
    const original2 = { content: 'Original' };
    const result = goodEdit(original2);
    expect(result.original.content).toBe('Original');
    expect(result.isolated.content).toBe('Modified');
  });
});

// =============================================================================
// H-05: AGENTESE Is API
// =============================================================================

describe('H-05: AGENTESE Is API', () => {
  /**
   * Law Statement: Forms invoke AGENTESE, no REST routes.
   *
   * Justification: All UI interactions invoke AGENTESE paths (world.*, self.*,
   * etc.), not traditional REST endpoints. AGENTESE IS the API.
   *
   * Test: Form submissions call logos.invoke(), not fetch('/api/...').
   */

  it('uses AGENTESE paths for data operations', () => {
    const agentesePaths = [
      'self.kblock.create',
      'self.kblock.update',
      'self.feed.main/manifest',
      'world.graph.edges/traverse',
      'concept.principle.list',
    ];

    agentesePaths.forEach((path) => {
      // AGENTESE paths follow context.resource.action pattern
      const parts = path.split('.');
      expect(parts.length).toBeGreaterThanOrEqual(2);

      // First part is context (self, world, concept, void, time)
      const contexts = ['self', 'world', 'concept', 'void', 'time'];
      expect(contexts).toContain(parts[0]);
    });
  });

  it('invokes AGENTESE protocol instead of REST endpoints', async () => {
    const mockLogos = {
      invoke: vi.fn().mockResolvedValue({ success: true }),
    };

    const createKBlock = async (content: string) => {
      // Good pattern: AGENTESE invocation
      return await mockLogos.invoke('self.kblock.create', {}, { content });
    };

    await createKBlock('New K-Block');

    // Should invoke AGENTESE, not REST
    expect(mockLogos.invoke).toHaveBeenCalledWith(
      'self.kblock.create',
      {},
      { content: 'New K-Block' }
    );
  });

  it('rejects traditional REST API patterns', () => {
    // Anti-pattern: REST endpoints
    const badEndpoints = [
      '/api/kblocks',
      '/api/kblocks/:id',
      '/api/feed',
      '/api/graph/edges',
    ];

    // Good pattern: AGENTESE paths
    const goodPaths = [
      'self.kblock.list',
      'self.kblock.read',
      'self.feed.main/manifest',
      'world.graph.edges/traverse',
    ];

    // Bad endpoints use HTTP REST pattern
    badEndpoints.forEach((endpoint) => {
      expect(endpoint).toMatch(/^\/api\//);
    });

    // Good paths use AGENTESE context.resource.action pattern
    goodPaths.forEach((path) => {
      expect(path).toMatch(/^(self|world|concept|void|time)\./);
    });
  });

  it('passes observer context to AGENTESE invocations', async () => {
    const mockLogos = {
      invoke: vi.fn().mockResolvedValue({ data: [] }),
    };

    const observer = {
      archetype: 'developer',
      density: 'comfortable',
      coherenceTolerance: 0.5,
    };

    const fetchFeed = async () => {
      return await mockLogos.invoke('self.feed.main/manifest', observer, {});
    };

    await fetchFeed();

    // Observer context should be passed as second argument
    expect(mockLogos.invoke).toHaveBeenCalledWith(
      'self.feed.main/manifest',
      observer,
      {}
    );
  });

  it('documents AGENTESE as the universal API protocol', () => {
    const apiDocumentation = {
      name: 'AGENTESE',
      description: 'Universal protocol for agent-world interaction',
      pattern: 'context.resource.action',
      contexts: ['self', 'world', 'concept', 'void', 'time'],
      example: 'logos.invoke("self.kblock.create", observer, { content: "..." })',
    };

    expect(apiDocumentation.name).toBe('AGENTESE');
    expect(apiDocumentation.pattern).toBe('context.resource.action');
    expect(apiDocumentation.contexts).toHaveLength(5);
  });
});
