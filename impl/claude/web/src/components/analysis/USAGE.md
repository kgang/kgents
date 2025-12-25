# AnalysisQuadrant Component

Four-panel visualization for Zero Seed node analysis using the Analysis Operad.

## Architecture

```
┌─────────────────┬─────────────────┐
│  CATEGORICAL    │  EPISTEMIC      │
│  Laws Hold? ✓   │  Grounded? ✓    │
├─────────────────┼─────────────────┤
│  DIALECTICAL    │  GENERATIVE     │
│  Tensions: 2    │  Regenerable? ✓ │
└─────────────────┴─────────────────┘
```

## API Integration

**Backend Endpoint**: `GET /api/zero-seed/nodes/{node_id}/analysis`

**Response Model**: `NodeAnalysisResponse` (see `/impl/claude/protocols/api/zero_seed.py`)

## Usage

### Basic Usage

```tsx
import { AnalysisQuadrant } from '@/components/analysis';

function MyPage() {
  return <AnalysisQuadrant nodeId="zn-axiom-001" />;
}
```

### With Close Handler

```tsx
function MyModal() {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <AnalysisQuadrant
      nodeId="zn-goal-042"
      onClose={() => setIsOpen(false)}
    />
  );
}
```

### Custom Styling

```tsx
<AnalysisQuadrant
  nodeId="zn-spec-123"
  className="my-custom-class"
/>
```

## Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `nodeId` | `string` | Yes | Zero Seed node ID to analyze |
| `onClose` | `() => void` | No | Close handler (shows X button if provided) |
| `className` | `string` | No | Additional CSS class |

## Design System

Uses **STARK BIOME** palette:

- **Background**: Steel scale (`--steel-900`, `--steel-850`)
- **Text**: Steel scale (`--steel-100`, `--steel-400`)
- **Mode Accents** (Earned Glow):
  - Categorical: `--status-normal` (blue)
  - Epistemic: `--status-insert` (green)
  - Dialectical: `--status-visual` (purple)
  - Generative: `--status-edge` (orange)
- **Status Colors**:
  - Pass: `--status-insert` (green)
  - Fail: `--status-error` (red)

## Four Modes

### 1. Categorical (Top Left)

- **Icon**: ⊚
- **Color**: Blue (`--status-normal`)
- **Shows**: Law verifications, fixed points
- **Pass Criteria**: No failed laws

### 2. Epistemic (Top Right)

- **Icon**: Varies
- **Color**: Green (`--status-insert`)
- **Shows**: Layer, grounding chain, evidence tier
- **Pass Criteria**: Terminates at axiom

### 3. Dialectical (Bottom Left)

- **Icon**: Varies
- **Color**: Purple (`--status-visual`)
- **Shows**: Tensions, classifications, syntheses
- **Pass Criteria**: No problematic contradictions

### 4. Generative (Bottom Right)

- **Icon**: Varies
- **Color**: Orange (`--status-edge`)
- **Shows**: Compression ratio, minimal kernel, regeneration test
- **Pass Criteria**: Regeneration test passes

## State Management

The component uses the `useAnalysis` hook internally, which:

1. Fetches from `/api/zero-seed/nodes/{nodeId}/analysis`
2. Transforms `NodeAnalysisResponse` to rich report types
3. Handles loading and error states
4. Provides a `refresh()` function

## Backend Integration

The backend endpoint supports two modes:

1. **Mock Mode** (default): Returns synthetic data for UI testing
2. **LLM Mode**: Uses `AnalysisService` with Claude API

```python
# Enable LLM mode
GET /api/zero-seed/nodes/{node_id}/analysis?use_llm=true
```

## Responsive Behavior

- **Desktop**: 2x2 grid
- **Mobile (< 768px)**: Stacks into single column

## Example: Embedding in Zero Seed Page

```tsx
import { AnalysisQuadrant } from '@/components/analysis';

function ZeroSeedNodePage({ nodeId }: { nodeId: string }) {
  return (
    <div className="node-page">
      <NodeHeader nodeId={nodeId} />
      <AnalysisQuadrant nodeId={nodeId} />
      <NodeContent nodeId={nodeId} />
    </div>
  );
}
```

## Philosophy

> "Analysis is not one thing but four: verification of laws, grounding of claims,
>  resolution of tensions, and regeneration from axioms."

Each quadrant represents a distinct mode of analysis from the Analysis Operad:

- **Categorical**: Does X satisfy its own composition laws?
- **Epistemic**: Is X grounded in axioms? What evidence tier?
- **Dialectical**: What tensions exist? Are they productive or problematic?
- **Generative**: Can X be regenerated from a minimal kernel?

## Related Components

- `CategoricalPanel` - Individual categorical analysis panel
- `EpistemicPanel` - Individual epistemic analysis panel
- `DialecticalPanel` - Individual dialectical analysis panel
- `GenerativePanel` - Individual generative analysis panel
- `useAnalysis` - Hook for fetching analysis data

## See Also

- Backend API: `/impl/claude/protocols/api/zero_seed.py`
- Analysis Service: `/impl/claude/services/analysis/`
- Analysis Operad: `/impl/claude/agents/operad/domains/analysis.py`
- STARK BIOME Palette: `/impl/claude/web/STARK_BIOME_PALETTE.md`
