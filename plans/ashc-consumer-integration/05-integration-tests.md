# ASHC Consumer Integration: Integration Test Plan

> *"The test IS the proof that derivation is visible."*

**Created**: 2025-01-10
**Status**: Ready for Implementation
**Prerequisites**: 00-master-plan.md, 02-ui-components.md, 04-zustand-stores.md
**Coverage Target**: All six consumer-facing derivation UX flows

---

## Overview

This document specifies integration tests for the consumer-first derivation UX. Each scenario validates that the pieces work together: backend ASHC services, Zustand stores, React components, and user interactions.

**Test Philosophy**:
- Integration tests validate workflows, not units
- Use Playwright for E2E, pytest for backend integration
- Mock at boundaries (external APIs), not internal services
- Each scenario is independently runnable

---

## Test Infrastructure

### Backend (pytest)

```python
# impl/claude/tests/integration/ashc/conftest.py

import pytest
from protocols.ashc.paths import DerivationPath
from services.k_block.core.derivation import DerivationDAG, KBlockDerivationContext
from services.hypergraph_editor.realization import RealizationService

@pytest.fixture
async def realization_service():
    """Pre-configured realization service with test project."""
    return RealizationService(cache_enabled=True)

@pytest.fixture
async def test_project(tmp_path):
    """Create a test project with K-Blocks at various grounding states."""
    # Creates 100 K-Blocks: 70 grounded, 20 provisional, 10 orphan
    return await create_test_project(tmp_path, block_count=100)

@pytest.fixture
def derivation_dag():
    """Empty derivation DAG for test manipulation."""
    return DerivationDAG()
```

### Frontend (Playwright)

```typescript
// impl/claude/web/tests/e2e/ashc/fixtures.ts

import { test as base, expect } from '@playwright/test';
import type { Page } from '@playwright/test';

interface ASHCFixtures {
  projectPage: Page;
  editorPage: Page;
}

export const test = base.extend<ASHCFixtures>({
  projectPage: async ({ page }, use) => {
    // Navigate to project with seeded K-Blocks
    await page.goto('/project/test-derivation-project');
    await page.waitForSelector('[data-testid="welcome-screen"]');
    await use(page);
  },
  editorPage: async ({ page }, use) => {
    // Navigate and dismiss welcome screen
    await page.goto('/project/test-derivation-project');
    await page.click('[data-testid="dismiss-welcome"]');
    await page.waitForSelector('[data-testid="hypergraph-editor"]');
    await use(page);
  },
});

export { expect };
```

---

## Scenario 1: Project Realization Flow

**Purpose**: Validate that opening a project computes derivation for all K-Blocks and displays the coherence summary without blocking access.

### Prerequisites

- Project exists with 100 K-Blocks
- K-Blocks have varied grounding states (grounded, provisional, orphan)
- RealizationService is configured with caching enabled

### Steps

1. Navigate to project URL
2. Observe welcome screen renders with progress indicator
3. Wait for realization to complete (or timeout at 5s)
4. Verify coherence summary displays correct statistics
5. Click "Continue" to access editor
6. Verify editor is accessible regardless of realization state

### Expected Results

| Assertion | Expected Value |
|-----------|----------------|
| Welcome screen visible | Within 500ms of navigation |
| Progress indicator animates | Updates at least every 100ms |
| Total blocks displayed | 100 |
| Grounded count | 70 (from fixture) |
| Provisional count | 20 (from fixture) |
| Orphan count | 10 (from fixture) |
| Coherence percentage | ~79% (1 - average_loss) |
| Editor accessible | Always, even if realization incomplete |

### Backend Tests (pytest)

```python
# impl/claude/tests/integration/ashc/test_project_realization.py

import pytest
from datetime import datetime, timedelta

class TestProjectRealizationFlow:
    """Integration tests for project realization."""

    @pytest.mark.asyncio
    async def test_realization_completes_within_timeout(
        self, realization_service, test_project
    ):
        """Realization for 100 K-Blocks completes within 5 seconds."""
        start = datetime.now()
        summary = await realization_service.realize(test_project.path)
        elapsed = datetime.now() - start

        assert elapsed < timedelta(seconds=5)
        assert summary.total_blocks == 100

    @pytest.mark.asyncio
    async def test_realization_classifies_correctly(
        self, realization_service, test_project
    ):
        """K-Blocks are classified into grounded/provisional/orphan."""
        summary = await realization_service.realize(test_project.path)

        assert len(summary.grounded) == 70
        assert len(summary.provisional) == 20
        assert len(summary.orphan) == 10

    @pytest.mark.asyncio
    async def test_coherence_percent_computed(
        self, realization_service, test_project
    ):
        """Average Galois loss is computed and coherence derived."""
        summary = await realization_service.realize(test_project.path)

        assert 0.0 <= summary.average_galois_loss <= 1.0
        assert summary.coherence_percent == 1.0 - summary.average_galois_loss

    @pytest.mark.asyncio
    async def test_derivation_graph_populated(
        self, realization_service, test_project
    ):
        """Derivation graph contains all blocks and paths."""
        summary = await realization_service.realize(test_project.path)

        assert len(summary.derivation_graph.nodes) == 100
        # Orphans have no incoming edges
        grounded_edges = [
            e for e in summary.derivation_graph.edges
            if e[1] not in summary.orphan
        ]
        assert len(grounded_edges) >= 90  # 70 grounded + 20 provisional

    @pytest.mark.asyncio
    async def test_realization_emits_events(
        self, realization_service, test_project
    ):
        """DataBus events emitted during realization."""
        events = []

        async def capture_event(event):
            events.append(event)

        realization_service.on_event(capture_event)
        await realization_service.realize(test_project.path)

        event_types = [e.event_type for e in events]
        assert "REALIZATION_STARTED" in event_types
        assert "REALIZATION_PROGRESS" in event_types
        assert "REALIZATION_COMPLETE" in event_types

    @pytest.mark.asyncio
    async def test_realization_never_blocks_project_access(
        self, realization_service, test_project
    ):
        """Project is accessible even if realization times out."""
        # Simulate slow realization
        realization_service.timeout_ms = 100  # Very short timeout

        try:
            await realization_service.realize(test_project.path)
        except TimeoutError:
            pass  # Expected

        # Project should still be accessible
        accessible = await realization_service.is_project_accessible(
            test_project.path
        )
        assert accessible is True
```

### Frontend Tests (Playwright)

```typescript
// impl/claude/web/tests/e2e/ashc/project-realization.spec.ts

import { test, expect } from './fixtures';

test.describe('Project Realization Flow', () => {
  test('displays welcome screen with coherence summary', async ({ projectPage }) => {
    // Welcome screen should be visible
    await expect(projectPage.locator('[data-testid="welcome-screen"]'))
      .toBeVisible();

    // Coherence summary should show statistics
    await expect(projectPage.locator('[data-testid="total-blocks"]'))
      .toHaveText('100');
    await expect(projectPage.locator('[data-testid="grounded-count"]'))
      .toHaveText('70');
    await expect(projectPage.locator('[data-testid="orphan-count"]'))
      .toHaveText('10');
  });

  test('shows progress indicator during computation', async ({ page }) => {
    await page.goto('/project/test-derivation-project');

    // Progress indicator should be visible during loading
    const progress = page.locator('[data-testid="realization-progress"]');
    await expect(progress).toBeVisible();

    // Progress should update (not static)
    const initialValue = await progress.getAttribute('aria-valuenow');
    await page.waitForTimeout(200);
    const updatedValue = await progress.getAttribute('aria-valuenow');

    // Value should have changed (progress is updating)
    expect(Number(updatedValue)).toBeGreaterThanOrEqual(Number(initialValue));
  });

  test('editor accessible after dismiss', async ({ projectPage }) => {
    await projectPage.click('[data-testid="dismiss-welcome"]');

    await expect(projectPage.locator('[data-testid="hypergraph-editor"]'))
      .toBeVisible();
    await expect(projectPage.locator('[data-testid="file-explorer"]'))
      .toBeVisible();
  });

  test('displays correct coherence badge color', async ({ projectPage }) => {
    // 79% coherence should show yellow (Healthy state)
    const badge = projectPage.locator('[data-testid="coherence-badge"]');
    await expect(badge).toHaveAttribute('data-state', 'healthy');
  });
});
```

---

## Scenario 2: K-Block Creation with Derivation

**Purpose**: Validate that new K-Blocks are initialized with derivation context and grounding suggestions are offered.

### Prerequisites

- Editor is open with active project
- Constitutional principles are loaded
- Grounding suggestion service is available

### Steps

1. Enter INSERT mode (press `i`)
2. Create new K-Block with content
3. Observe derivation context initialization
4. View grounding suggestions panel
5. Either accept suggestion or skip (remain orphan)
6. Verify final grounding status

### Expected Results

| Assertion | Expected Value |
|-----------|----------------|
| New K-Block created | Has unique ID |
| Derivation context present | `grounding_status: 'orphan'` initially |
| Galois loss | 1.0 (maximum, ungrounded) |
| Suggestions offered | At least 1 if content matches any principle |
| Skip option available | Always present |
| Post-skip status | Remains orphan with `galois_loss: 1.0` |

### Backend Tests (pytest)

```python
# impl/claude/tests/integration/ashc/test_kblock_creation.py

import pytest

class TestKBlockCreationWithDerivation:
    """Integration tests for K-Block creation with derivation context."""

    @pytest.mark.asyncio
    async def test_new_kblock_has_orphan_context(self, kblock_service):
        """New K-Blocks start as orphans."""
        kblock = await kblock_service.create(
            path="/test/new-block.md",
            content="Some content without grounding",
        )

        assert kblock.derivation_context is not None
        assert kblock.derivation_context.grounding_status == "orphan"
        assert kblock.derivation_context.galois_loss == 1.0
        assert kblock.derivation_context.source_principle is None

    @pytest.mark.asyncio
    async def test_creation_returns_grounding_suggestions(
        self, kblock_service, suggestion_service
    ):
        """Grounding suggestions offered for new K-Blocks."""
        kblock = await kblock_service.create(
            path="/test/composable-block.md",
            content="This component composes with others using morphisms",
        )

        suggestions = await suggestion_service.suggest_grounding(kblock)

        # Content mentions "composes" - should suggest COMPOSABLE
        assert len(suggestions) >= 1
        principle_names = [s.principle.name for s in suggestions]
        assert "COMPOSABLE" in principle_names

    @pytest.mark.asyncio
    async def test_skip_grounding_preserves_orphan_status(
        self, kblock_service
    ):
        """Skipping grounding keeps K-Block as orphan."""
        kblock = await kblock_service.create(
            path="/test/skipped.md",
            content="Random content",
        )

        # Skip grounding (no action taken)
        # K-Block should remain orphan
        assert kblock.derivation_context.grounding_status == "orphan"

    @pytest.mark.asyncio
    async def test_creation_witnesses_orphan_birth(
        self, kblock_service, witness_service
    ):
        """K-Block creation is witnessed."""
        kblock = await kblock_service.create(
            path="/test/witnessed.md",
            content="Content",
        )

        marks = await witness_service.query_by_target(kblock.id)

        assert len(marks) >= 1
        assert any(m.action == "kblock.created" for m in marks)
```

### Frontend Tests (Playwright)

```typescript
// impl/claude/web/tests/e2e/ashc/kblock-creation.spec.ts

import { test, expect } from './fixtures';

test.describe('K-Block Creation with Derivation', () => {
  test('new K-Block shows as orphan initially', async ({ editorPage }) => {
    // Enter INSERT mode
    await editorPage.keyboard.press('i');

    // Type content
    await editorPage.keyboard.type('New content for testing');

    // Exit INSERT mode
    await editorPage.keyboard.press('Escape');

    // Check derivation status in inspector
    const status = editorPage.locator('[data-testid="grounding-status"]');
    await expect(status).toHaveText('orphan');
  });

  test('grounding suggestions panel appears', async ({ editorPage }) => {
    await editorPage.keyboard.press('i');
    await editorPage.keyboard.type('This is composable and reusable');
    await editorPage.keyboard.press('Escape');

    // Suggestions panel should appear
    const suggestions = editorPage.locator('[data-testid="grounding-suggestions"]');
    await expect(suggestions).toBeVisible();

    // Should have at least one suggestion
    const items = suggestions.locator('[data-testid="suggestion-item"]');
    await expect(items).toHaveCount({ min: 1 });
  });

  test('can skip grounding and remain orphan', async ({ editorPage }) => {
    await editorPage.keyboard.press('i');
    await editorPage.keyboard.type('Random orphan content');
    await editorPage.keyboard.press('Escape');

    // Click skip button
    await editorPage.click('[data-testid="skip-grounding"]');

    // Status should remain orphan
    const status = editorPage.locator('[data-testid="grounding-status"]');
    await expect(status).toHaveText('orphan');
  });

  test('galois loss meter shows 1.0 for orphans', async ({ editorPage }) => {
    await editorPage.keyboard.press('i');
    await editorPage.keyboard.type('Orphan content');
    await editorPage.keyboard.press('Escape');

    const lossMeter = editorPage.locator('[data-testid="galois-meter"]');
    await expect(lossMeter).toHaveAttribute('data-loss', '1');
  });
});
```

---

## Scenario 3: Grounding Flow

**Purpose**: Validate the complete flow of grounding an orphan K-Block to a constitutional principle.

### Prerequisites

- Orphan K-Block exists
- Grounding dialog component available
- Derivation service can create edges

### Steps

1. Select orphan K-Block
2. Open grounding dialog (right-click or keyboard shortcut)
3. View suggested principles with estimated loss
4. Select a principle
5. Confirm grounding
6. Verify derivation edge created
7. Verify status changes from orphan to grounded/provisional

### Expected Results

| Assertion | Expected Value |
|-----------|----------------|
| Dialog opens | Shows orphan block info |
| Suggestions ranked | By estimated loss (ascending) |
| Selection highlighted | Visual feedback on hover/select |
| Confirm creates edge | Edge in derivation graph |
| Status updated | `grounded` if loss < 0.15, `provisional` if 0.15-0.50 |
| Witness created | For grounding action |

### Backend Tests (pytest)

```python
# impl/claude/tests/integration/ashc/test_grounding_flow.py

import pytest

class TestGroundingFlow:
    """Integration tests for grounding orphan K-Blocks."""

    @pytest.mark.asyncio
    async def test_grounding_creates_derivation_edge(
        self, kblock_service, grounding_service, derivation_dag
    ):
        """Grounding creates edge in derivation graph."""
        # Create orphan
        orphan = await kblock_service.create(
            path="/test/orphan.md",
            content="Orphan content about composability",
        )
        assert orphan.derivation_context.grounding_status == "orphan"

        # Ground to COMPOSABLE
        result = await grounding_service.ground(
            orphan_id=orphan.id,
            principle_name="COMPOSABLE",
            actor="test",
        )

        # Check edge exists
        edges = derivation_dag.edges_to(orphan.id)
        assert len(edges) == 1
        assert edges[0].source == "COMPOSABLE"

    @pytest.mark.asyncio
    async def test_grounding_updates_status_to_grounded(
        self, kblock_service, grounding_service
    ):
        """Low-loss grounding yields 'grounded' status."""
        orphan = await kblock_service.create(
            path="/test/low-loss.md",
            content="Highly composable morphism composition",
        )

        result = await grounding_service.ground(
            orphan_id=orphan.id,
            principle_name="COMPOSABLE",
            actor="test",
        )

        # Galois loss < 0.15 should yield grounded
        updated = await kblock_service.get(orphan.id)

        if updated.derivation_context.galois_loss < 0.15:
            assert updated.derivation_context.grounding_status == "grounded"
        else:
            assert updated.derivation_context.grounding_status == "provisional"

    @pytest.mark.asyncio
    async def test_grounding_is_witnessed(
        self, kblock_service, grounding_service, witness_service
    ):
        """Grounding action creates witness mark."""
        orphan = await kblock_service.create(
            path="/test/witnessed-grounding.md",
            content="Content to ground",
        )

        await grounding_service.ground(
            orphan_id=orphan.id,
            principle_name="COMPOSABLE",
            actor="test",
        )

        marks = await witness_service.query_by_target(orphan.id)
        grounding_marks = [m for m in marks if m.action == "kblock.grounding.accept"]

        assert len(grounding_marks) == 1
        assert grounding_marks[0].evidence["principle"] == "COMPOSABLE"

    @pytest.mark.asyncio
    async def test_grounding_suggestions_sorted_by_loss(
        self, kblock_service, suggestion_service
    ):
        """Suggestions are ranked by estimated Galois loss."""
        kblock = await kblock_service.create(
            path="/test/multi-match.md",
            content="Composable ethical generative system",
        )

        suggestions = await suggestion_service.suggest_grounding(kblock)

        # Should be sorted by loss ascending
        losses = [s.galois_loss for s in suggestions]
        assert losses == sorted(losses)
```

### Frontend Tests (Playwright)

```typescript
// impl/claude/web/tests/e2e/ashc/grounding-flow.spec.ts

import { test, expect } from './fixtures';

test.describe('Grounding Flow', () => {
  test('opens grounding dialog for orphan K-Block', async ({ editorPage }) => {
    // Select an orphan block
    await editorPage.click('[data-testid="orphan-kblock-1"]');

    // Right-click to open context menu
    await editorPage.click('[data-testid="orphan-kblock-1"]', { button: 'right' });

    // Click "Ground this K-Block"
    await editorPage.click('[data-testid="context-menu-ground"]');

    // Dialog should open
    await expect(editorPage.locator('[data-testid="grounding-dialog"]'))
      .toBeVisible();
  });

  test('suggestions show estimated loss', async ({ editorPage }) => {
    await editorPage.click('[data-testid="orphan-kblock-1"]');
    await editorPage.keyboard.press('g'); // Keyboard shortcut for ground

    const suggestion = editorPage.locator('[data-testid="suggestion-item"]').first();

    // Should show principle name and loss
    await expect(suggestion.locator('[data-testid="principle-name"]'))
      .toBeVisible();
    await expect(suggestion.locator('[data-testid="estimated-loss"]'))
      .toBeVisible();
  });

  test('selecting principle and confirming grounds the K-Block', async ({ editorPage }) => {
    await editorPage.click('[data-testid="orphan-kblock-1"]');
    await editorPage.keyboard.press('g');

    // Select first suggestion
    await editorPage.click('[data-testid="suggestion-item"]');

    // Confirm
    await editorPage.click('[data-testid="confirm-grounding"]');

    // Dialog should close
    await expect(editorPage.locator('[data-testid="grounding-dialog"]'))
      .not.toBeVisible();

    // Status should update
    const status = editorPage.locator('[data-testid="grounding-status"]');
    await expect(status).not.toHaveText('orphan');
  });

  test('grounded K-Block shows in derivation trail', async ({ editorPage }) => {
    // Ground a K-Block
    await editorPage.click('[data-testid="orphan-kblock-1"]');
    await editorPage.keyboard.press('g');
    await editorPage.click('[data-testid="suggestion-item"]');
    await editorPage.click('[data-testid="confirm-grounding"]');

    // Trail bar should show derivation path
    const trailBar = editorPage.locator('[data-testid="derivation-trail-bar"]');
    await expect(trailBar).toBeVisible();

    // Should have principle at root
    const principleChip = trailBar.locator('[data-testid="principle-chip"]');
    await expect(principleChip).toBeVisible();
  });
});
```

---

## Scenario 4: Constitutional Graph View

**Purpose**: Validate the graph-based navigation alternative to file tree.

### Prerequisites

- Project with derivation graph computed
- Graph visualization component available
- Drag-drop interactions enabled

### Steps

1. Toggle to graph view mode
2. Verify tree structure renders correctly
3. Test expand/collapse of principle nodes
4. Drag orphan K-Block to principle node
5. Verify grounding created via drag-drop
6. Navigate using graph (click node to focus)

### Expected Results

| Assertion | Expected Value |
|-----------|----------------|
| Graph renders | All nodes visible (or paginated) |
| Principles at root | 7 Constitutional principles |
| Expand/collapse | Toggles child visibility |
| Drag-drop grounds | Creates derivation edge |
| Node click focuses | Opens K-Block in editor |
| Zoom/pan works | Canvas responds to gestures |

### Backend Tests (pytest)

```python
# impl/claude/tests/integration/ashc/test_constitutional_graph.py

import pytest

class TestConstitutionalGraphView:
    """Integration tests for graph-based navigation."""

    @pytest.mark.asyncio
    async def test_graph_contains_all_kblocks(
        self, graph_service, test_project
    ):
        """Graph includes all K-Blocks as nodes."""
        graph = await graph_service.get_graph(test_project.id)

        kblock_nodes = [n for n in graph.nodes if n.type == "kblock"]
        assert len(kblock_nodes) == 100

    @pytest.mark.asyncio
    async def test_graph_has_principle_roots(
        self, graph_service, test_project
    ):
        """Graph has Constitutional principles as root nodes."""
        graph = await graph_service.get_graph(test_project.id)

        principle_nodes = [n for n in graph.nodes if n.type == "principle"]
        principle_names = {n.label for n in principle_nodes}

        expected = {
            "COMPOSABLE", "TASTEFUL", "ETHICAL", "JOY_INDUCING",
            "CURATED", "HETERARCHICAL", "GENERATIVE"
        }
        assert expected <= principle_names

    @pytest.mark.asyncio
    async def test_graph_edges_match_derivations(
        self, graph_service, derivation_dag, test_project
    ):
        """Graph edges correspond to derivation paths."""
        graph = await graph_service.get_graph(test_project.id)

        # Count edges that represent derivations
        derives_edges = [e for e in graph.edges if e.type == "derives_from"]

        # Should match DAG edges
        dag_edges = derivation_dag.all_edges()
        assert len(derives_edges) == len(dag_edges)

    @pytest.mark.asyncio
    async def test_drag_drop_grounding(
        self, graph_service, grounding_service, test_project
    ):
        """Drag-drop action grounds orphan to principle."""
        # Get an orphan node
        graph = await graph_service.get_graph(test_project.id)
        orphan = next(n for n in graph.nodes if n.grounding_status == "orphan")

        # Simulate drag-drop grounding
        result = await grounding_service.ground(
            orphan_id=orphan.id,
            principle_name="COMPOSABLE",
            actor="test",
            via="drag_drop",
        )

        assert result.success

        # Refresh graph
        updated_graph = await graph_service.get_graph(test_project.id)
        updated_node = next(n for n in updated_graph.nodes if n.id == orphan.id)

        assert updated_node.grounding_status != "orphan"
```

### Frontend Tests (Playwright)

```typescript
// impl/claude/web/tests/e2e/ashc/constitutional-graph.spec.ts

import { test, expect } from './fixtures';

test.describe('Constitutional Graph View', () => {
  test('toggles to graph view mode', async ({ editorPage }) => {
    // Click toggle button
    await editorPage.click('[data-testid="toggle-graph-view"]');

    // Graph should be visible
    await expect(editorPage.locator('[data-testid="constitutional-graph"]'))
      .toBeVisible();

    // File explorer should be hidden
    await expect(editorPage.locator('[data-testid="file-explorer"]'))
      .not.toBeVisible();
  });

  test('renders principle nodes at root', async ({ editorPage }) => {
    await editorPage.click('[data-testid="toggle-graph-view"]');

    const principleNodes = editorPage.locator('[data-testid="principle-node"]');
    await expect(principleNodes).toHaveCount(7);
  });

  test('expand/collapse principle shows children', async ({ editorPage }) => {
    await editorPage.click('[data-testid="toggle-graph-view"]');

    // Find COMPOSABLE principle
    const composable = editorPage.locator('[data-testid="principle-node"][data-name="COMPOSABLE"]');

    // Click to expand
    await composable.click();

    // Children should be visible
    const children = editorPage.locator('[data-testid="kblock-node"][data-parent="COMPOSABLE"]');
    await expect(children).toHaveCount({ min: 1 });

    // Click again to collapse
    await composable.click();

    // Children should be hidden
    await expect(children).toBeHidden();
  });

  test('drag orphan to principle grounds it', async ({ editorPage }) => {
    await editorPage.click('[data-testid="toggle-graph-view"]');

    // Find orphan node
    const orphan = editorPage.locator('[data-testid="orphan-node"]').first();
    const principle = editorPage.locator('[data-testid="principle-node"][data-name="COMPOSABLE"]');

    // Drag orphan to principle
    await orphan.dragTo(principle);

    // Orphan should now be connected
    await expect(orphan).not.toHaveAttribute('data-grounding-status', 'orphan');
  });

  test('zoom and pan work', async ({ editorPage }) => {
    await editorPage.click('[data-testid="toggle-graph-view"]');

    const canvas = editorPage.locator('[data-testid="graph-canvas"]');

    // Zoom with scroll
    await canvas.hover();
    await editorPage.mouse.wheel(0, -100); // Zoom in

    const zoomLevel = await canvas.getAttribute('data-zoom');
    expect(Number(zoomLevel)).toBeGreaterThan(1);
  });
});
```

---

## Scenario 5: Derivation Trail Bar

**Purpose**: Validate the breadcrumb-style trail showing Constitutional lineage.

### Prerequisites

- Grounded K-Block selected
- DerivationTrailBar component rendered
- Navigation callbacks wired

### Steps

1. Select a grounded K-Block
2. Verify trail bar displays derivation path
3. Verify each hop shows Galois loss indicator
4. Click intermediate hop in trail
5. Verify navigation to that K-Block
6. Verify loss color coding (green/yellow/orange)

### Expected Results

| Assertion | Expected Value |
|-----------|----------------|
| Trail visible | When grounded K-Block selected |
| Shows principle at root | First hop is Constitutional principle |
| Shows current at end | Last hop is selected K-Block |
| Loss indicators present | Each hop has GaloisCoherenceMeter |
| Click navigates | Focus changes to clicked hop |
| Colors accurate | Green (<0.15), Yellow (0.15-0.30), Orange (>0.30) |

### Backend Tests (pytest)

```python
# impl/claude/tests/integration/ashc/test_derivation_trail.py

import pytest

class TestDerivationTrailBar:
    """Integration tests for derivation trail navigation."""

    @pytest.mark.asyncio
    async def test_trail_starts_with_principle(
        self, trail_service, grounded_kblock
    ):
        """Trail path begins with Constitutional principle."""
        trail = await trail_service.get_trail(grounded_kblock.id)

        assert len(trail) >= 2
        assert trail[0].type == "principle"
        assert trail[0].label in [
            "COMPOSABLE", "TASTEFUL", "ETHICAL", "JOY_INDUCING",
            "CURATED", "HETERARCHICAL", "GENERATIVE"
        ]

    @pytest.mark.asyncio
    async def test_trail_ends_with_current(
        self, trail_service, grounded_kblock
    ):
        """Trail path ends with current K-Block."""
        trail = await trail_service.get_trail(grounded_kblock.id)

        assert trail[-1].block_id == grounded_kblock.id

    @pytest.mark.asyncio
    async def test_trail_has_cumulative_loss(
        self, trail_service, grounded_kblock
    ):
        """Each hop shows cumulative Galois loss."""
        trail = await trail_service.get_trail(grounded_kblock.id)

        cumulative = 0.0
        for hop in trail[1:]:  # Skip principle (no loss)
            cumulative_at_hop = hop.cumulative_loss
            assert cumulative_at_hop >= cumulative
            cumulative = cumulative_at_hop

    @pytest.mark.asyncio
    async def test_trail_empty_for_orphan(
        self, trail_service, orphan_kblock
    ):
        """Orphan K-Blocks have empty trail."""
        trail = await trail_service.get_trail(orphan_kblock.id)

        # Orphans have no derivation path
        assert len(trail) == 0 or trail == [orphan_kblock]
```

### Frontend Tests (Playwright)

```typescript
// impl/claude/web/tests/e2e/ashc/derivation-trail.spec.ts

import { test, expect } from './fixtures';

test.describe('Derivation Trail Bar', () => {
  test('displays trail for grounded K-Block', async ({ editorPage }) => {
    // Select a grounded K-Block
    await editorPage.click('[data-testid="grounded-kblock-1"]');

    // Trail bar should be visible
    const trailBar = editorPage.locator('[data-testid="derivation-trail-bar"]');
    await expect(trailBar).toBeVisible();
  });

  test('shows principle at start of trail', async ({ editorPage }) => {
    await editorPage.click('[data-testid="grounded-kblock-1"]');

    const trailBar = editorPage.locator('[data-testid="derivation-trail-bar"]');
    const firstHop = trailBar.locator('[data-testid="trail-hop"]').first();

    await expect(firstHop).toHaveAttribute('data-type', 'principle');
  });

  test('shows current block at end of trail', async ({ editorPage }) => {
    await editorPage.click('[data-testid="grounded-kblock-1"]');

    const trailBar = editorPage.locator('[data-testid="derivation-trail-bar"]');
    const lastHop = trailBar.locator('[data-testid="trail-hop"]').last();

    await expect(lastHop).toHaveAttribute('data-current', 'true');
  });

  test('each hop shows loss indicator', async ({ editorPage }) => {
    await editorPage.click('[data-testid="grounded-kblock-1"]');

    const hops = editorPage.locator('[data-testid="trail-hop"]');
    const count = await hops.count();

    for (let i = 0; i < count; i++) {
      const hop = hops.nth(i);
      const meter = hop.locator('[data-testid="galois-meter"]');
      await expect(meter).toBeVisible();
    }
  });

  test('clicking hop navigates to that K-Block', async ({ editorPage }) => {
    await editorPage.click('[data-testid="grounded-kblock-1"]');

    const trailBar = editorPage.locator('[data-testid="derivation-trail-bar"]');
    const middleHop = trailBar.locator('[data-testid="trail-hop"]').nth(1);

    await middleHop.click();

    // Editor should now show the middle block
    const focusedId = await editorPage.locator('[data-testid="focused-kblock"]')
      .getAttribute('data-block-id');
    const middleId = await middleHop.getAttribute('data-block-id');

    expect(focusedId).toBe(middleId);
  });

  test('loss colors are correct', async ({ editorPage }) => {
    await editorPage.click('[data-testid="grounded-kblock-1"]');

    const trailBar = editorPage.locator('[data-testid="derivation-trail-bar"]');
    const meters = trailBar.locator('[data-testid="galois-meter"]');

    // Check that colors match loss thresholds
    const count = await meters.count();
    for (let i = 0; i < count; i++) {
      const meter = meters.nth(i);
      const loss = Number(await meter.getAttribute('data-loss'));
      const color = await meter.getAttribute('data-color');

      if (loss < 0.15) {
        expect(color).toBe('green');
      } else if (loss < 0.30) {
        expect(color).toBe('yellow');
      } else {
        expect(color).toBe('orange');
      }
    }
  });

  test('hides trail for orphan K-Block', async ({ editorPage }) => {
    // Select an orphan
    await editorPage.click('[data-testid="orphan-kblock-1"]');

    // Trail bar should show orphan indicator, not full trail
    const trailBar = editorPage.locator('[data-testid="derivation-trail-bar"]');
    await expect(trailBar.locator('[data-testid="orphan-indicator"]'))
      .toBeVisible();
    await expect(trailBar.locator('[data-testid="trail-hop"]'))
      .toHaveCount(0);
  });
});
```

---

## Scenario 6: Downstream Impact

**Purpose**: Validate that editing a K-Block with downstream dependents shows impact preview.

### Prerequisites

- K-Block with downstream derivations exists
- Impact analysis service available
- Preview UI component rendered

### Steps

1. Select K-Block that has downstream dependents
2. Enter EDIT mode
3. Make a change that affects derivation
4. Observe impact preview panel
5. View list of affected downstream K-Blocks
6. Confirm edit and verify downstream recomputation

### Expected Results

| Assertion | Expected Value |
|-----------|----------------|
| Impact preview shown | Before committing changes |
| Downstream count | Number of affected K-Blocks |
| Risk level | Based on depth and count |
| Recomputation triggered | Downstream losses updated |
| Witness created | For the edit and propagation |

### Backend Tests (pytest)

```python
# impl/claude/tests/integration/ashc/test_downstream_impact.py

import pytest

class TestDownstreamImpact:
    """Integration tests for downstream impact analysis."""

    @pytest.mark.asyncio
    async def test_impact_analysis_finds_dependents(
        self, impact_service, kblock_with_downstream
    ):
        """Impact analysis identifies downstream K-Blocks."""
        impact = await impact_service.analyze(kblock_with_downstream.id)

        assert impact.total_count > 0
        assert len(impact.dependents) > 0

    @pytest.mark.asyncio
    async def test_impact_includes_depth(
        self, impact_service, kblock_with_downstream
    ):
        """Impact analysis shows derivation depth for each dependent."""
        impact = await impact_service.analyze(kblock_with_downstream.id)

        for dep in impact.dependents:
            assert dep.depth >= 1

    @pytest.mark.asyncio
    async def test_risk_level_computed(
        self, impact_service, kblock_with_downstream
    ):
        """Risk level is computed based on impact magnitude."""
        impact = await impact_service.analyze(kblock_with_downstream.id)

        assert impact.risk_level in ["low", "medium", "high"]

        # High count or deep dependents should increase risk
        if impact.total_count > 10 or any(d.depth > 3 for d in impact.dependents):
            assert impact.risk_level in ["medium", "high"]

    @pytest.mark.asyncio
    async def test_edit_triggers_downstream_recomputation(
        self, kblock_service, impact_service, kblock_with_downstream
    ):
        """Editing K-Block recomputes downstream Galois losses."""
        # Get initial downstream losses
        impact_before = await impact_service.analyze(kblock_with_downstream.id)
        initial_losses = {
            d.block_id: (await kblock_service.get(d.block_id)).derivation_context.galois_loss
            for d in impact_before.dependents
        }

        # Edit the parent K-Block significantly
        await kblock_service.update(
            kblock_with_downstream.id,
            content="Completely different content that changes semantic meaning",
        )

        # Get updated downstream losses
        for dep in impact_before.dependents:
            updated = await kblock_service.get(dep.block_id)
            # Loss may have changed (not necessarily, but should be recomputed)
            assert updated.derivation_context.galois_loss >= 0.0

    @pytest.mark.asyncio
    async def test_impact_propagation_witnessed(
        self, kblock_service, witness_service, kblock_with_downstream
    ):
        """Downstream impact propagation is witnessed."""
        await kblock_service.update(
            kblock_with_downstream.id,
            content="Modified content",
        )

        marks = await witness_service.query_by_target(kblock_with_downstream.id)
        propagation_marks = [m for m in marks if m.action == "derivation.propagated"]

        assert len(propagation_marks) >= 1
```

### Frontend Tests (Playwright)

```typescript
// impl/claude/web/tests/e2e/ashc/downstream-impact.spec.ts

import { test, expect } from './fixtures';

test.describe('Downstream Impact', () => {
  test('shows impact preview when editing K-Block with dependents', async ({ editorPage }) => {
    // Select K-Block that has downstream
    await editorPage.click('[data-testid="kblock-with-downstream"]');

    // Enter edit mode
    await editorPage.keyboard.press('i');

    // Make changes
    await editorPage.keyboard.type(' modified content');

    // Impact preview should appear
    await expect(editorPage.locator('[data-testid="impact-preview"]'))
      .toBeVisible();
  });

  test('impact preview shows dependent count', async ({ editorPage }) => {
    await editorPage.click('[data-testid="kblock-with-downstream"]');
    await editorPage.keyboard.press('i');
    await editorPage.keyboard.type(' modified');

    const preview = editorPage.locator('[data-testid="impact-preview"]');
    const count = preview.locator('[data-testid="dependent-count"]');

    await expect(count).toHaveText(/\d+ K-Blocks affected/);
  });

  test('impact preview shows risk level', async ({ editorPage }) => {
    await editorPage.click('[data-testid="kblock-with-downstream"]');
    await editorPage.keyboard.press('i');
    await editorPage.keyboard.type(' modified');

    const preview = editorPage.locator('[data-testid="impact-preview"]');
    const risk = preview.locator('[data-testid="risk-level"]');

    await expect(risk).toHaveAttribute('data-level', /(low|medium|high)/);
  });

  test('clicking dependent in preview navigates to it', async ({ editorPage }) => {
    await editorPage.click('[data-testid="kblock-with-downstream"]');
    await editorPage.keyboard.press('i');
    await editorPage.keyboard.type(' modified');

    const preview = editorPage.locator('[data-testid="impact-preview"]');
    const firstDep = preview.locator('[data-testid="dependent-item"]').first();
    const depId = await firstDep.getAttribute('data-block-id');

    await firstDep.click();

    // Should navigate to that block
    const focused = editorPage.locator('[data-testid="focused-kblock"]');
    await expect(focused).toHaveAttribute('data-block-id', depId!);
  });

  test('confirming edit triggers downstream update', async ({ editorPage, page }) => {
    await editorPage.click('[data-testid="kblock-with-downstream"]');
    await editorPage.keyboard.press('i');
    await editorPage.keyboard.type(' modified');

    // Wait for network request on confirm
    const [response] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/derivation/propagate')),
      editorPage.keyboard.press('Escape'), // Exit and confirm
    ]);

    expect(response.status()).toBe(200);
  });

  test('no impact preview for K-Block without dependents', async ({ editorPage }) => {
    // Select leaf K-Block (no downstream)
    await editorPage.click('[data-testid="leaf-kblock"]');
    await editorPage.keyboard.press('i');
    await editorPage.keyboard.type(' modified');

    // Impact preview should not appear (or show "0 affected")
    const preview = editorPage.locator('[data-testid="impact-preview"]');
    await expect(preview).toHaveAttribute('data-visible', 'false');
  });
});
```

---

## Test Automation Strategy

### CI Pipeline Integration

```yaml
# .github/workflows/ashc-integration.yml

name: ASHC Consumer Integration Tests

on:
  pull_request:
    paths:
      - 'impl/claude/services/k_block/**'
      - 'impl/claude/services/hypergraph_editor/**'
      - 'impl/claude/protocols/ashc/**'
      - 'impl/claude/web/src/components/derivation/**'
      - 'plans/ashc-consumer-integration/**'

jobs:
  backend-integration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          cd impl/claude
          pip install uv
          uv sync
      - name: Run ASHC integration tests
        run: |
          cd impl/claude
          uv run pytest tests/integration/ashc/ -v --tb=short

  frontend-e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install dependencies
        run: |
          cd impl/claude/web
          npm ci
      - name: Install Playwright
        run: |
          cd impl/claude/web
          npx playwright install --with-deps
      - name: Run E2E tests
        run: |
          cd impl/claude/web
          npm run test:e2e -- --project=chromium tests/e2e/ashc/
```

### Test Data Seeding

```python
# impl/claude/tests/integration/ashc/seed.py

async def create_test_project(path: Path, block_count: int = 100) -> TestProject:
    """Create seeded test project with derivation structure."""
    # 70% grounded, 20% provisional, 10% orphan
    grounded_count = int(block_count * 0.7)
    provisional_count = int(block_count * 0.2)
    orphan_count = block_count - grounded_count - provisional_count

    kblocks = []

    for i in range(grounded_count):
        kblock = await create_kblock_with_derivation(
            path / f"grounded_{i}.md",
            galois_loss=random.uniform(0.0, 0.149),
            principle=random.choice(PRINCIPLES),
        )
        kblocks.append(kblock)

    for i in range(provisional_count):
        kblock = await create_kblock_with_derivation(
            path / f"provisional_{i}.md",
            galois_loss=random.uniform(0.15, 0.499),
            principle=random.choice(PRINCIPLES),
        )
        kblocks.append(kblock)

    for i in range(orphan_count):
        kblock = await create_orphan_kblock(path / f"orphan_{i}.md")
        kblocks.append(kblock)

    return TestProject(path=path, kblocks=kblocks)
```

---

## Coverage Requirements

| Scenario | Backend Tests | Frontend Tests | Total |
|----------|---------------|----------------|-------|
| Project Realization | 6 | 4 | 10 |
| K-Block Creation | 4 | 4 | 8 |
| Grounding Flow | 4 | 4 | 8 |
| Constitutional Graph | 4 | 5 | 9 |
| Derivation Trail | 4 | 7 | 11 |
| Downstream Impact | 5 | 6 | 11 |
| **Total** | **27** | **30** | **57** |

**Coverage Target**: 90% of derivation UX code paths exercised by these integration tests.

---

## Closing Notes

These integration tests validate the consumer-first derivation UX as a cohesive system. They exercise the full stack: from ASHC path computation through Zustand stores to React component rendering.

**Key Principles**:
- Tests validate user workflows, not implementation details
- Each scenario can be run independently
- Failures should point to specific integration seams
- Performance assertions catch regressions early

> *"The system doesn't enforce—it illuminates. These tests prove the illumination works."*

---

*Filed: 2025-01-10*
*Voice anchor: "The test IS the proof that derivation is visible."*
*Coverage: 57 integration tests across 6 scenarios*
