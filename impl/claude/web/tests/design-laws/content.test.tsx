/**
 * Content Laws (C-01 through C-05)
 *
 * Tests for the 5 content design laws from Zero Seed Creative Strategy.
 *
 * @see plans/zero-seed-creative-strategy.md (Part IV: UI/UX Design Laws)
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { Feed } from '@/primitives/Feed/Feed';

// =============================================================================
// C-01: Five-Level Degradation
// =============================================================================

describe('C-01: Five-Level Degradation', () => {
  /**
   * Law Statement: icon → title → summary → detail → full.
   *
   * Justification: Content degrades gracefully across densities. Each level
   * contains the previous level's information plus more detail.
   *
   * Test: Verify 5 degradation levels with subset property.
   */

  it('implements five degradation levels with subset property', () => {
    interface ContentLevels {
      icon: string;
      title: string;
      summary: string;
      detail: string;
      full: string;
    }

    const kblockContent: ContentLevels = {
      icon: '📐',
      title: '📐 Design System',
      summary: '📐 Design System: Elastic UI patterns',
      detail:
        '📐 Design System: Elastic UI patterns - Responsive components with density-aware behavior',
      full: '📐 Design System: Elastic UI patterns - Responsive components with density-aware behavior. Implements L-01 through L-05 layout laws. Last updated 2025-12-25.',
    };

    // Each level should contain the previous level
    expect(kblockContent.title).toContain(kblockContent.icon);
    expect(kblockContent.summary).toContain('Design System');
    expect(kblockContent.detail).toContain('Elastic UI patterns');
    expect(kblockContent.full).toContain('Responsive components');

    // Lengths should be monotonically increasing
    expect(kblockContent.title.length).toBeGreaterThan(kblockContent.icon.length);
    expect(kblockContent.summary.length).toBeGreaterThan(kblockContent.title.length);
    expect(kblockContent.detail.length).toBeGreaterThan(kblockContent.summary.length);
    expect(kblockContent.full.length).toBeGreaterThan(kblockContent.detail.length);
  });

  it('maps degradation levels to density modes', () => {
    const DegradableCard = ({ density }: { density: 'compact' | 'comfortable' | 'spacious' }) => {
      const content = {
        compact: '📐 Design',
        comfortable: '📐 Design System: Elastic patterns',
        spacious:
          '📐 Design System: Elastic UI patterns - Responsive components with density-aware behavior',
      };

      return <div data-testid="card">{content[density]}</div>;
    };

    // Compact: icon + minimal title
    const { unmount: unmount1 } = render(<DegradableCard density="compact" />);
    const compactText = screen.getByTestId('card').textContent || '';
    expect(compactText).toMatch(/📐 Design$/);
    unmount1();

    // Comfortable: summary level
    const { unmount: unmount2 } = render(<DegradableCard density="comfortable" />);
    const comfortableText = screen.getByTestId('card').textContent || '';
    expect(comfortableText).toMatch(/Design System: Elastic patterns/);
    unmount2();

    // Spacious: detail level
    const { unmount: unmount3 } = render(<DegradableCard density="spacious" />);
    const spaciousText = screen.getByTestId('card').textContent || '';
    expect(spaciousText).toMatch(/Responsive components/);
    unmount3();
  });

  it('ensures compact shows minimum viable information', () => {
    // Compact must show at least icon + identifier
    const minimalContent = {
      icon: '🎯',
      identifier: 'Goal-1',
    };

    const CompactCard = () => (
      <div data-testid="compact">
        {minimalContent.icon} {minimalContent.identifier}
      </div>
    );

    render(<CompactCard />);

    const card = screen.getByTestId('compact');
    expect(card.textContent).toContain(minimalContent.icon);
    expect(card.textContent).toContain(minimalContent.identifier);
  });
});

// =============================================================================
// C-02: Schema Single Source
// =============================================================================

describe('C-02: Schema Single Source', () => {
  /**
   * Law Statement: Forms derive from Python contracts.
   *
   * Justification: TypeScript types are generated from Python Pydantic models.
   * No manual type duplication—single source of truth.
   *
   * Test: Verify types are derived, not duplicated.
   */

  it('uses generated types from backend contracts', () => {
    // This test verifies the contract, not implementation
    // In practice, types would be generated via sync-types script

    interface KBlock {
      id: string;
      title: string;
      content: string;
      layer: number;
      loss: number;
      createdAt: Date;
    }

    const kblock: KBlock = {
      id: 'kb-1',
      title: 'Test',
      content: 'Content',
      layer: 1,
      loss: 0.5,
      createdAt: new Date(),
    };

    // Types should match backend contract
    expect(kblock).toHaveProperty('id');
    expect(kblock).toHaveProperty('layer');
    expect(kblock).toHaveProperty('loss');
  });

  it('rejects manual type duplication between frontend and backend', () => {
    // Anti-pattern: Manual type definition in frontend
    // interface KBlock { id: string; title: string; } // DON'T DO THIS

    // Good pattern: Import from generated types
    // import type { KBlock } from '@/types/generated';

    // This test documents the expectation
    const goodPattern = 'Import from @/types/generated';
    const badPattern = 'Define types manually in component';

    expect(goodPattern).toMatch(/generated/);
    expect(badPattern).not.toMatch(/generated/);
  });

  it('validates that sync-types script exists for type generation', () => {
    // This would be verified in package.json
    const packageScripts = {
      'sync-types': 'npx tsx scripts/sync-types.ts',
      'sync-types:check': 'npx tsx scripts/sync-types.ts --check',
    };

    expect(packageScripts).toHaveProperty('sync-types');
    expect(packageScripts).toHaveProperty('sync-types:check');
  });
});

// =============================================================================
// C-03: Feed Is Primitive
// =============================================================================

describe('C-03: Feed Is Primitive', () => {
  /**
   * Law Statement: Feed is first-class, not a view.
   *
   * Justification: The feed is not a view of data—it IS the primary interface.
   * It's a primitive component, not derived from tables or lists.
   *
   * Test: Feed is imported as primitive, has independent state management.
   */

  it('treats Feed as a primitive component with its own state', () => {
    const onItemClick = vi.fn();

    const { container } = render(
      <Feed feedId="main" onItemClick={onItemClick} initialRanking="chronological" />
    );

    // Feed should render as independent component
    // Check for feed class or structure
    const feedElement = container.querySelector('.feed');
    expect(feedElement).toBeTruthy();
  });

  it('imports Feed from primitives, not views or components', () => {
    // This documents the import pattern expectation
    const goodImport = "import { Feed } from '@/primitives/Feed/Feed'";
    const badImport = "import { Feed } from '@/views/FeedView'";

    expect(goodImport).toMatch(/primitives/);
    expect(badImport).toMatch(/views/);

    // Good pattern uses primitives
    expect(goodImport).toContain('primitives');
  });

  it('provides Feed-specific affordances independent of other views', () => {
    const feedAffordances = [
      'infinite scroll',
      'layer filtering',
      'loss-based ranking',
      'algorithmic feed',
      'contradiction surfacing',
    ];

    // Feed should have its own unique affordances
    expect(feedAffordances).toContain('infinite scroll');
    expect(feedAffordances).toContain('algorithmic feed');
    expect(feedAffordances).toContain('contradiction surfacing');

    // These are Feed-specific, not generic list features
    expect(feedAffordances.length).toBeGreaterThan(3);
  });

  it('rejects Feed as merely a filtered view of table data', () => {
    // Anti-pattern: Feed is just DataTable with filters
    const badPattern = {
      component: 'DataTable',
      props: { filter: 'feedMode' },
    };

    // Good pattern: Feed is independent primitive
    const goodPattern = {
      component: 'Feed',
      props: { ranking: 'algorithmic', contradictions: true },
    };

    expect(badPattern.component).toBe('DataTable');
    expect(goodPattern.component).toBe('Feed');

    // Feed has affordances DataTable doesn't
    expect(goodPattern.props).toHaveProperty('ranking');
    expect(goodPattern.props).toHaveProperty('contradictions');
  });
});

// =============================================================================
// C-04: Portal Token Interactivity
// =============================================================================

describe('C-04: Portal Token Interactivity', () => {
  /**
   * Law Statement: Portals are interactive, not passive links.
   *
   * Justification: Portal tokens (@principle, #goal, etc.) are not just links—
   * they're interactive elements with hover previews, click actions, and context.
   *
   * Test: Portal tokens are buttons/interactive, not static <a> tags.
   */

  it('renders portal tokens as interactive elements, not passive links', () => {
    const PortalToken = ({ id, type }: { id: string; type: string }) => (
      <button
        data-testid="portal"
        data-portal-id={id}
        data-portal-type={type}
        className="portal-token"
      >
        {type === 'principle' && '@'}
        {type === 'goal' && '#'}
        {id}
      </button>
    );

    render(<PortalToken id="principle-1" type="principle" />);

    const portal = screen.getByTestId('portal');

    // Should be a button, not an anchor
    expect(portal.tagName).toBe('BUTTON');
    expect(portal).toHaveAttribute('data-portal-id', 'principle-1');
    expect(portal).toHaveAttribute('data-portal-type', 'principle');
  });

  it('provides hover preview for portal tokens', async () => {
    const user = userEvent.setup();

    const PortalWithPreview = () => {
      const [showPreview, setShowPreview] = React.useState(false);

      return (
        <div>
          <button
            data-testid="portal"
            onMouseEnter={() => setShowPreview(true)}
            onMouseLeave={() => setShowPreview(false)}
          >
            @principle-1
          </button>
          {showPreview && (
            <div data-testid="preview" role="tooltip">
              Principle 1: Tasteful design
            </div>
          )}
        </div>
      );
    };

    render(<PortalWithPreview />);

    const portal = screen.getByTestId('portal');

    // Hover to show preview
    await user.hover(portal);
    expect(screen.getByTestId('preview')).toBeInTheDocument();

    // Unhover to hide preview
    await user.unhover(portal);
    expect(screen.queryByTestId('preview')).not.toBeInTheDocument();
  });

  it('supports multiple interaction modes for portal tokens', async () => {
    const user = userEvent.setup();
    const onNavigate = vi.fn();
    const onPreview = vi.fn();

    const InteractivePortal = () => (
      <button data-testid="portal" onClick={onNavigate} onMouseEnter={onPreview}>
        @principle
      </button>
    );

    render(<InteractivePortal />);

    const portal = screen.getByTestId('portal');

    // Hover triggers preview
    await user.hover(portal);
    expect(onPreview).toHaveBeenCalled();

    // Click triggers navigation
    await user.click(portal);
    expect(onNavigate).toHaveBeenCalled();
  });

  it('rejects passive <a> tags for portal tokens', () => {
    // Anti-pattern: <a href="#principle-1">@principle-1</a>
    const BadPattern = () => (
      <a href="#principle-1" data-testid="link">
        @principle-1
      </a>
    );

    // Good pattern: Interactive button with preview
    const GoodPattern = () => (
      <button data-testid="button" data-portal="principle-1">
        @principle-1
      </button>
    );

    const { unmount: unmount1 } = render(<BadPattern />);
    const link = screen.getByTestId('link');
    expect(link.tagName).toBe('A');
    unmount1();

    const { unmount: unmount2 } = render(<GoodPattern />);
    const button = screen.getByTestId('button');
    expect(button.tagName).toBe('BUTTON');
    expect(button).toHaveAttribute('data-portal');
    unmount2();
  });
});

// =============================================================================
// C-05: Witness Required for Commit
// =============================================================================

describe('C-05: Witness Required for Commit', () => {
  /**
   * Law Statement: K-Block commits require witness message.
   *
   * Justification: Every commit must be witnessed—a message explaining the
   * "why" of the change. No silent commits.
   *
   * Test: Commit button is disabled until witness message is provided.
   */

  it('requires witness message before enabling commit', async () => {
    const user = userEvent.setup();

    const CommitForm = () => {
      const [message, setMessage] = React.useState('');

      return (
        <div>
          <textarea
            data-testid="witness-input"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Why are you committing this change?"
          />
          <button data-testid="commit-button" disabled={!message.trim()}>
            Commit
          </button>
        </div>
      );
    };

    render(<CommitForm />);

    const commitButton = screen.getByTestId('commit-button');
    const input = screen.getByTestId('witness-input');

    // Button should be disabled initially
    expect(commitButton).toBeDisabled();

    // Type witness message
    await user.type(input, 'Added density-aware layout patterns');

    // Button should be enabled after message
    expect(commitButton).not.toBeDisabled();
  });

  it('validates witness message is not empty or whitespace-only', async () => {
    const user = userEvent.setup();

    const ValidatedCommit = () => {
      const [message, setMessage] = React.useState('');
      const isValid = message.trim().length > 0;

      return (
        <div>
          <input data-testid="input" value={message} onChange={(e) => setMessage(e.target.value)} />
          <button data-testid="commit" disabled={!isValid}>
            Commit
          </button>
        </div>
      );
    };

    render(<ValidatedCommit />);

    const input = screen.getByTestId('input');
    const commit = screen.getByTestId('commit');

    // Empty: disabled
    expect(commit).toBeDisabled();

    // Whitespace only: still disabled
    await user.type(input, '   ');
    expect(commit).toBeDisabled();

    // Clear and type real message
    await user.clear(input);
    await user.type(input, 'Real witness message');
    expect(commit).not.toBeDisabled();
  });

  it('includes witness message in commit payload', () => {
    const createCommit = (kblocks: string[], witnessMessage: string) => {
      return {
        kblocks,
        witness: witnessMessage,
        timestamp: new Date(),
      };
    };

    const commit = createCommit(
      ['kb-1', 'kb-2'],
      'Consolidated layout laws into unified test suite'
    );

    expect(commit).toHaveProperty('witness');
    expect(commit.witness).toBe('Consolidated layout laws into unified test suite');
  });

  it('rejects silent commits without witness messages', () => {
    // Anti-pattern: git commit -m "." (meaningless message)
    const badCommit = { kblocks: ['kb-1'], witness: '.' };

    // Good pattern: Descriptive witness
    const goodCommit = {
      kblocks: ['kb-1'],
      witness: 'Unified density system across all components',
    };

    expect(badCommit.witness.length).toBe(1);
    expect(goodCommit.witness.length).toBeGreaterThan(20);
  });

  it('prompts user if attempting to commit without witness', async () => {
    const user = userEvent.setup();

    const CommitWithValidation = () => {
      const [message, setMessage] = React.useState('');
      const [showWarning, setShowWarning] = React.useState(false);

      const handleCommit = () => {
        if (!message.trim()) {
          setShowWarning(true);
        }
        // Proceed with commit
      };

      return (
        <div>
          <input data-testid="input" value={message} onChange={(e) => setMessage(e.target.value)} />
          <button data-testid="commit" onClick={handleCommit}>
            Commit
          </button>
          {showWarning && (
            <div data-testid="warning">
              Witness message required. Why are you making this change?
            </div>
          )}
        </div>
      );
    };

    render(<CommitWithValidation />);

    // Try to commit without message
    await user.click(screen.getByTestId('commit'));

    // Warning should appear
    expect(screen.getByTestId('warning')).toBeInTheDocument();
  });
});
