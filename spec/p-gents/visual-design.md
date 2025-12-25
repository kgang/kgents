# P-gent Visual Design Guide

**Status**: Design Specification (Brutalist Edition)
**Session**: 2025-12-25

---

## Design Philosophy

Your UI is **brutalist**: monospace fonts, no decorative elements, simple glyphs, data-attribute driven. P-gent visualization follows this pattern exactly.

### Core Principles

1. **Text-first**: Glyphs + text, never fancy gauges
2. **Monospace**: Berkeley Mono / JetBrains Mono
3. **No decoration**: No rounded corners, no glows, no shadows
4. **Data attributes**: State via `data-*` attributes, CSS selects on them
5. **BEM naming**: `.parse-result__icon`, `.parse-result--success`

---

## Color Mapping

Use existing `STATE_COLORS` and `HEALTH_COLORS` from `constants/colors.ts`:

| Parse State | Color Variable | Value |
|-------------|---------------|-------|
| Success (>0.8) | `STATE_COLORS.success` | `#22C55E` |
| Warning (0.5-0.8) | `STATE_COLORS.warning` | `#F59E0B` |
| Failed (<0.5) | `STATE_COLORS.error` | `#EF4444` |
| Streaming | `STATE_COLORS.info` | `#06B6D4` |
| Pending | `STATE_COLORS.pending` | `#64748B` |

For health-based confidence, use `getHealthColor(confidence)`:
- `>= 0.8`: healthy (green)
- `>= 0.6`: degraded (yellow)
- `>= 0.4`: warning (orange)
- `< 0.4`: critical (red)

---

## Components

### 1. ParseResultBadge (Primary)

Inline badge following `CachedBadge` pattern:

```tsx
/**
 * ParseResultBadge — Inline parse status indicator
 *
 * Follows CachedBadge pattern: inline-flex, monospace, simple glyph + text.
 *
 * Displays: [icon] [PARSED confidence% | strategy | repairs]
 */

interface ParseResultBadgeProps {
  result: ParseResult<unknown>;
  position?: 'inline' | 'absolute';
  showDetails?: boolean;
}

const PARSE_ICONS: Record<string, string> = {
  success: '✓',
  partial: '◐',
  failed: '✗',
  streaming: '⟳',
};

export function ParseResultBadge({ result, position = 'inline' }: ParseResultBadgeProps) {
  const status = result.success
    ? (result.confidence >= 0.8 ? 'success' : 'partial')
    : 'failed';
  const icon = PARSE_ICONS[status];
  const conf = Math.round(result.confidence * 100);
  const repairs = result.repairs.length;

  return (
    <span
      className="parse-result-badge"
      data-status={status}
      data-position={position}
      title={`Strategy: ${result.strategy}, Repairs: ${repairs}`}
      aria-label={`Parse ${status}: ${conf}% confidence`}
    >
      <span className="parse-result-badge__icon">{icon}</span>
      [PARSED {conf}%{repairs > 0 ? ` | ${repairs} repairs` : ''} | {result.strategy}]
    </span>
  );
}
```

**CSS** (following ConfidenceIndicator.css brutalist pattern):

```css
.parse-result-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border: 1px solid var(--brutalist-border, #333);
  border-radius: 0;
  background: var(--brutalist-surface, #141414);
  font-family: 'Berkeley Mono', 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 600;
  color: var(--brutalist-text, #e0e0e0);
}

.parse-result-badge[data-status="success"] {
  border-color: #22C55E;
  color: #22C55E;
}

.parse-result-badge[data-status="partial"] {
  border-color: #F59E0B;
  color: #F59E0B;
}

.parse-result-badge[data-status="failed"] {
  border-color: #EF4444;
  color: #EF4444;
}

.parse-result-badge[data-status="streaming"] {
  border-color: #06B6D4;
  color: #06B6D4;
}

.parse-result-badge[data-position="absolute"] {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 10;
}

.parse-result-badge__icon {
  font-size: 10px;
}
```

**Output examples**:
```
✓ [PARSED 92% | anchor]
◐ [PARSED 67% | 2 repairs | reflection]
✗ [PARSED 0% | failed]
⟳ [PARSING...]
```

---

### 2. ParseResultIndicator (Extended)

Following `ConfidenceIndicator` pattern for detailed view:

```tsx
/**
 * ParseResultIndicator — Extended parse result display
 *
 * Follows ConfidenceIndicator pattern: badge + optional details.
 */

interface ParseResultIndicatorProps {
  result: ParseResult<unknown>;
  showDetails?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export function ParseResultIndicator({
  result,
  showDetails = false,
  size = 'md',
}: ParseResultIndicatorProps) {
  const status = result.success
    ? (result.confidence >= 0.8 ? 'success' : 'partial')
    : 'failed';
  const icon = PARSE_ICONS[status];
  const conf = Math.round(result.confidence * 100);

  return (
    <div
      className="parse-result-indicator"
      data-status={status}
      data-size={size}
      role="status"
      aria-label={`Parse ${status}: ${conf}% confidence`}
    >
      {/* Main badge */}
      <div className="parse-result-indicator__badge">
        <span className="parse-result-indicator__icon">{icon}</span>
        <span className="parse-result-indicator__label">
          {result.success ? 'PARSED' : 'FAILED'}
        </span>
        <span className="parse-result-indicator__value">
          (P={result.confidence.toFixed(2)})
        </span>
      </div>

      {/* Details breakdown */}
      {showDetails && (
        <div className="parse-result-indicator__details">
          <div className="parse-result-indicator__detail-row">
            <span className="parse-result-indicator__detail-label">Strategy:</span>
            <span className="parse-result-indicator__detail-value">{result.strategy}</span>
          </div>
          {result.repairs.length > 0 && (
            <div className="parse-result-indicator__detail-row">
              <span className="parse-result-indicator__detail-label">Repairs:</span>
              <span className="parse-result-indicator__detail-value">{result.repairs.length}</span>
            </div>
          )}
          {result.partial && (
            <div className="parse-result-indicator__detail-row">
              <span className="parse-result-indicator__detail-label">Partial:</span>
              <span className="parse-result-indicator__detail-value">Yes</span>
            </div>
          )}
        </div>
      )}

      {/* Repair list */}
      {showDetails && result.repairs.length > 0 && (
        <div className="parse-result-indicator__repairs">
          {result.repairs.map((repair, i) => (
            <div key={i} className="parse-result-indicator__repair">
              {i + 1}. {repair}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

**CSS**:

```css
.parse-result-indicator {
  display: inline-flex;
  flex-direction: column;
  gap: 6px;
  padding: 4px 8px;
  border: 1px solid var(--brutalist-border, #333);
  border-radius: 0;
  background: var(--brutalist-surface, #141414);
  font-family: 'Berkeley Mono', 'JetBrains Mono', monospace;
  font-size: 12px;
  color: var(--brutalist-text, #e0e0e0);
}

.parse-result-indicator--sm { padding: 2px 6px; font-size: 11px; }
.parse-result-indicator--lg { padding: 6px 10px; font-size: 13px; }

.parse-result-indicator__badge {
  display: flex;
  align-items: center;
  gap: 6px;
}

.parse-result-indicator__label {
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.parse-result-indicator__value {
  font-weight: 700;
  color: var(--brutalist-accent, #fff);
}

.parse-result-indicator__details {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-top: 6px;
  border-top: 1px solid var(--brutalist-border, #333);
  font-size: 11px;
}

.parse-result-indicator__detail-row {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.parse-result-indicator__detail-label {
  font-weight: 400;
  color: var(--brutalist-text-dim, #888);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 10px;
}

.parse-result-indicator__detail-value {
  font-weight: 700;
}

.parse-result-indicator__repairs {
  padding-top: 4px;
  border-top: 1px solid var(--brutalist-border, #333);
  font-size: 10px;
  color: var(--brutalist-text-dim, #888);
}

.parse-result-indicator__repair {
  padding: 2px 0;
}

/* Status colors */
.parse-result-indicator[data-status="success"] { border-left: 2px solid #22C55E; }
.parse-result-indicator[data-status="partial"] { border-left: 2px solid #F59E0B; }
.parse-result-indicator[data-status="failed"] { border-left: 2px solid #EF4444; }
```

---

### 3. StrategyTrace (Fallback Chain)

Following `PortalToken` expandable pattern:

```tsx
/**
 * StrategyTrace — Expandable strategy chain display
 *
 * Shows which strategies were tried and which succeeded.
 * Follows PortalToken pattern: toggle + GrowingContainer.
 */

interface StrategyStep {
  name: string;
  success: boolean;
  error?: string;
}

interface StrategyTraceProps {
  strategies: StrategyStep[];
  defaultExpanded?: boolean;
}

export function StrategyTrace({ strategies, defaultExpanded = false }: StrategyTraceProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const successIndex = strategies.findIndex(s => s.success);
  const successStrategy = successIndex >= 0 ? strategies[successIndex] : null;

  return (
    <div className="strategy-trace" data-expanded={expanded}>
      <button
        type="button"
        className="strategy-trace__toggle"
        onClick={() => setExpanded(!expanded)}
        aria-expanded={expanded}
      >
        <span className="strategy-trace__icon">{expanded ? '▼' : '▶'}</span>
        <span className="strategy-trace__summary">
          [strategies] ──→ {successStrategy ? `✓ ${successStrategy.name}` : '✗ all failed'}
          {successIndex > 0 && ` (${successIndex} tried)`}
        </span>
      </button>

      {expanded && (
        <GrowingContainer>
          <ul className="strategy-trace__list">
            {strategies.map((step, i) => (
              <li
                key={step.name}
                className="strategy-trace__step"
                data-success={step.success}
              >
                <span className="strategy-trace__step-icon">
                  {step.success ? '✓' : '✗'}
                </span>
                <span className="strategy-trace__step-name">{step.name}</span>
                {step.error && (
                  <span className="strategy-trace__step-error">: {step.error}</span>
                )}
              </li>
            ))}
          </ul>
        </GrowingContainer>
      )}
    </div>
  );
}
```

**CSS**:

```css
.strategy-trace {
  font-family: 'Berkeley Mono', 'JetBrains Mono', monospace;
  font-size: 12px;
}

.strategy-trace__toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  border: none;
  background: transparent;
  color: var(--brutalist-text, #e0e0e0);
  cursor: pointer;
  font-family: inherit;
  font-size: inherit;
}

.strategy-trace__toggle:hover {
  color: var(--brutalist-accent, #fff);
}

.strategy-trace__icon {
  font-size: 10px;
}

.strategy-trace__summary {
  font-weight: 600;
}

.strategy-trace__list {
  list-style: none;
  margin: 0;
  padding: 4px 0 4px 20px;
  border-left: 1px solid var(--brutalist-border, #333);
}

.strategy-trace__step {
  padding: 2px 0;
  color: var(--brutalist-text-dim, #888);
}

.strategy-trace__step[data-success="true"] {
  color: #22C55E;
}

.strategy-trace__step[data-success="false"] {
  color: #EF4444;
}

.strategy-trace__step-icon {
  margin-right: 6px;
}

.strategy-trace__step-error {
  font-size: 10px;
  color: var(--brutalist-text-dim, #888);
}
```

**Output**:
```
▶ [strategies] ──→ ✓ anchor (2 tried)

▼ [strategies] ──→ ✓ anchor (2 tried)
   ✗ json: Expected } at position 42
   ✓ anchor
```

---

### 4. StreamingParseBadge

For active streaming:

```tsx
/**
 * StreamingParseBadge — Active streaming indicator
 *
 * Shows parse progress during streaming.
 */

interface StreamingParseBadgeProps {
  tokenCount: number;
  partialConfidence?: number;
  stackDepth?: number;
}

export function StreamingParseBadge({
  tokenCount,
  partialConfidence,
  stackDepth = 0,
}: StreamingParseBadgeProps) {
  return (
    <span
      className="streaming-parse-badge"
      data-status="streaming"
      aria-label={`Parsing: ${tokenCount} tokens`}
    >
      <span className="streaming-parse-badge__icon" data-spin="true">⟳</span>
      [PARSING {tokenCount} tokens
      {partialConfidence !== undefined && ` | ~${Math.round(partialConfidence * 100)}%`}
      {stackDepth > 0 && ` | depth:${stackDepth}`}]
    </span>
  );
}
```

**CSS**:

```css
.streaming-parse-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border: 1px solid #06B6D4;
  border-radius: 0;
  background: var(--brutalist-surface, #141414);
  font-family: 'Berkeley Mono', 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 600;
  color: #06B6D4;
}

.streaming-parse-badge__icon[data-spin="true"] {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

**Output**:
```
⟳ [PARSING 1247 tokens | ~82% | depth:3]
```

---

## Integration Patterns

### With Existing Components

**Using GrowingContainer** (for expandable details):
```tsx
import { GrowingContainer } from '../joy';

{expanded && (
  <GrowingContainer>
    <div className="parse-result-indicator__details">
      ...
    </div>
  </GrowingContainer>
)}
```

**Using Shake** (for parse failures):
```tsx
import { Shake } from '../joy';

{result.success === false && (
  <Shake intensity="gentle">
    <ParseResultBadge result={result} />
  </Shake>
)}
```

**Using Shimmer** (for streaming):
```tsx
import { Shimmer } from '../joy';

{isStreaming && (
  <Shimmer>
    <StreamingParseBadge tokenCount={tokens} />
  </Shimmer>
)}
```

### CLI Output

For CLI/text contexts, format as plain text:

```typescript
function formatParseResult(result: ParseResult<unknown>): string {
  const icon = result.success
    ? (result.confidence >= 0.8 ? '✓' : '◐')
    : '✗';
  const conf = Math.round(result.confidence * 100);
  const repairs = result.repairs.length > 0
    ? ` | ${result.repairs.length} repairs`
    : '';

  return `${icon} PARSED ${conf}%${repairs} | ${result.strategy}`;
}

// Output: ✓ PARSED 87% | 2 repairs | anchor
```

---

## Glyphs

Standard glyphs from existing components:

| Glyph | Meaning | Usage |
|-------|---------|-------|
| `✓` | Success | High confidence parse |
| `◐` | Partial | Medium confidence, repairs applied |
| `✗` | Failed | Parse failed |
| `⟳` | Processing | Streaming/parsing in progress |
| `○` | Pending | Waiting to parse |
| `▶` / `▼` | Expand/Collapse | Strategy trace toggle |
| `──→` | Flow | Strategy chain arrow |

---

## File Structure

```
impl/claude/web/src/components/parse/
├── ParseResultBadge.tsx       # Inline badge
├── ParseResultBadge.css
├── ParseResultIndicator.tsx   # Extended display
├── ParseResultIndicator.css
├── StrategyTrace.tsx          # Fallback chain
├── StrategyTrace.css
├── StreamingParseBadge.tsx    # Active streaming
├── StreamingParseBadge.css
└── index.ts                   # Exports
```

---

## Implementation Checklist

### Phase 1: Core Badges
- [ ] `ParseResultBadge.tsx` (inline, follows CachedBadge)
- [ ] `ParseResultBadge.css` (brutalist styling)
- [ ] Integration with existing color constants

### Phase 2: Extended Display
- [ ] `ParseResultIndicator.tsx` (follows ConfidenceIndicator)
- [ ] `ParseResultIndicator.css`
- [ ] Details expansion with GrowingContainer

### Phase 3: Strategy Visualization
- [ ] `StrategyTrace.tsx` (follows PortalToken)
- [ ] `StrategyTrace.css`
- [ ] Fallback chain display

### Phase 4: Streaming
- [ ] `StreamingParseBadge.tsx`
- [ ] `StreamingParseBadge.css`
- [ ] Spin animation for processing

---

## Anti-Patterns (Removed from Original)

The original design included elements that don't fit your UI:

- ~~Circular gauges/meters~~ → Use text + percentage
- ~~Confetti celebrations~~ → Use simple success glyph
- ~~Living Earth colors~~ → Use STATE_COLORS/HEALTH_COLORS
- ~~Lens metaphors~~ → Use simple badges
- ~~Custom animations~~ → Use existing joy components
- ~~Rounded corners~~ → Brutalist: border-radius: 0
- ~~Glow effects~~ → No shadows, no glows

---

---

## Hypergraph Editor Integration

P-gent visualization integrates with the hypergraph editor and K-Block structure at four levels.

### Level 1: Status Bar (Always Visible)

Parse status appears in the STATUS bar region during streaming or after completion:

```
┌─────────────────────────────────────────────────────────────────┐
│ STATUS: :ag self.brain.hypothesize    ✓ PARSED 87% | anchor    │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation**:
```tsx
// In HypergraphEditor status bar
<div className="status-bar">
  <span className="status-bar__command">{commandBuffer}</span>
  {parseResult && <ParseResultBadge result={parseResult} />}
  <span className="status-bar__position">{row},{col}</span>
</div>
```

### Level 2: Gutter Annotations (Edge-Level)

When a node contains parsed LLM output, the LEFT GUTTER shows parse confidence:

```
┌───────┬─────────────────────────────────────────────────────────┐
│       │                                                         │
│ [der] │   ## Hypothesis                                         │
│ [ext] │                                                         │
│ ✓ 92% │   Generated by B-gent with high confidence              │
│       │   Parsed via anchor strategy                            │
│       │                                                         │
│ ◐ 67% │   {"name": "related", "confidence": 0.67}               │
│       │   ↑ 2 repairs applied                                   │
│       │                                                         │
└───────┴─────────────────────────────────────────────────────────┘
```

**Implementation**:
```tsx
// GutterAnnotation for parse results
interface ParseGutterAnnotation {
  line: number;
  confidence: number;
  strategy: string;
  repairs: number;
}

function renderParseGutter(annotation: ParseGutterAnnotation) {
  const icon = annotation.confidence >= 0.8 ? '✓' : '◐';
  const conf = Math.round(annotation.confidence * 100);
  return `${icon} ${conf}%`;
}
```

### Level 3: K-Block Views (Parse View)

Add **Parse** as a sixth view type in KBlockSheaf:

```python
class KBlockSheaf(SheafProtocol[View]):
    """Views within K-Block glue to form coherent content."""

    # Standard views
    PROSE: ViewType = "prose"       # Markdown rendering
    GRAPH: ViewType = "graph"       # Concept DAG
    CODE: ViewType = "code"         # TypeSpec/implementation
    DIFF: ViewType = "diff"         # Delta from base
    OUTLINE: ViewType = "outline"   # Hierarchical structure
    PARSE: ViewType = "parse"       # P-gent parse results (NEW)
```

**Parse View displays**:
- All parsed regions in the node
- Per-region confidence scores
- Strategy waterfall for each parse
- Repair history
- Re-parse actions

```
┌─────────────────────────────────────────────────────────────────┐
│ PARSE VIEW: spec/hypothesis.md                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Region 1: lines 12-18                                           │
│   ✓ PARSED (P=0.92) | Strategy: anchor                         │
│   ▶ [strategies] ──→ ✓ anchor (1 tried)                         │
│   No repairs                                                     │
│                                                                  │
│ Region 2: lines 24-31                                           │
│   ◐ PARSED (P=0.67) | Strategy: reflection                     │
│   ▶ [strategies] ──→ ✓ reflection (2 tried)                     │
│   Repairs:                                                       │
│     1. Added missing quote (line 26)                            │
│     2. Closed unclosed bracket (line 28)                        │
│   [Re-parse]                                                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Level 4: Portal Token Integration (Inline)

Parse results appear as expandable Portal Tokens within node content:

```
▶ [parsed] ──→ 87% | anchor | 2 repairs

▼ [parsed] ──→ 87% | anchor | 2 repairs
   ✗ json: Expected } at position 42
   ✓ anchor
   Repairs:
     1. Added missing quote
     2. Closed bracket
```

**Implementation**:
```tsx
// ParsePortalToken follows PortalToken pattern
interface ParsePortalTokenProps {
  result: ParseResult<unknown>;
  defaultExpanded?: boolean;
}

export function ParsePortalToken({ result, defaultExpanded = false }: ParsePortalTokenProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const conf = Math.round(result.confidence * 100);
  const repairs = result.repairs.length;

  return (
    <div className="portal-token" data-edge-type="parsed">
      <button
        className="portal-token__toggle"
        onClick={() => setExpanded(!expanded)}
        aria-expanded={expanded}
      >
        <span className="portal-token__icon">{expanded ? '▼' : '▶'}</span>
        <span className="portal-token__edge-type">[parsed]</span>
        <span className="portal-token__arrow">──→</span>
        <span className="portal-token__summary">
          {conf}% | {result.strategy}{repairs > 0 ? ` | ${repairs} repairs` : ''}
        </span>
      </button>

      {expanded && (
        <GrowingContainer>
          <StrategyTrace strategies={result.strategyTrace} />
          {result.repairs.length > 0 && (
            <div className="portal-token__repairs">
              Repairs:
              {result.repairs.map((r, i) => (
                <div key={i}>{i + 1}. {r}</div>
              ))}
            </div>
          )}
        </GrowingContainer>
      )}
    </div>
  );
}
```

---

## Mode Integration

### COMMAND Mode (`:parse`)

Invoke P-gent from COMMAND mode:

```
:parse                    Parse current selection with default strategy
:parse json               Parse with specific strategy
:parse fallback:json,anchor  Parse with fallback chain
:parse --region 12-18     Parse specific line range
```

**Implementation**:
```typescript
const PARSE_COMMANDS = {
  'parse': async (args: string[]) => {
    const strategy = args[0] || 'fallback:json,anchor,reflection';
    const selection = getSelection();
    const result = await pgent.parse(selection.text, strategy);

    // Add parse result to K-Block metadata
    nav.kblock?.addParseResult(selection.range, result);

    // Witness the parse
    await witness.mark({
      action: 'parse.invoked',
      path: nav.current_node.path,
      range: selection.range,
      confidence: result.confidence,
      strategy: result.strategy,
    });

    return result;
  },
};
```

### INSERT Mode (Auto-Parse on LLM Output)

When LLM-generated content is inserted, auto-parse and annotate:

```typescript
async function onLLMInsert(content: string, source: string): Promise<void> {
  // Auto-parse LLM output
  const result = await pgent.parse(content, 'fallback:json,anchor,reflection');

  // Add to K-Block with parse metadata
  nav.kblock?.insert(content, {
    source,
    parseResult: result,
  });

  // Show parse badge in status bar
  setStatusParseResult(result);
}
```

### WITNESS Mode (Parse Marks)

Add parse-specific quick marks:

```typescript
const QUICK_MARKS = {
  'E': 'eureka',
  'G': 'gotcha',
  'T': 'taste',
  'F': 'friction',
  'J': 'joy',
  'V': 'veto',
  'P': 'parse',  // NEW: Mark parse decision
};

// gw mP → "Mark parse: why this strategy worked/failed"
```

---

## K-Block Witness Integration

Parse operations integrate with K-Block's witnessed operations:

```python
@dataclass
class ParseWitness:
    """Witness trace for parse operations within K-Block."""
    block_id: str
    operation: Literal["parse.invoked", "parse.succeeded", "parse.failed", "parse.repaired"]
    timestamp: datetime
    range: tuple[int, int]  # Line range
    input_hash: str         # Hash of input text
    confidence: float
    strategy: str
    repairs: list[str]
    reasoning: str | None

class WitnessedKBlock:
    async def parse_region(
        self,
        range: tuple[int, int],
        strategy: str,
        reasoning: str | None = None
    ) -> ParseResult:
        """Parse region with witness trace."""
        text = self.get_text(range)
        result = await pgent.parse(text, strategy)

        # Witness the parse
        await self.witness.mark(
            action="parse.succeeded" if result.success else "parse.failed",
            block_id=self.id,
            range=range,
            confidence=result.confidence,
            strategy=result.strategy,
            repairs=result.repairs,
            reasoning=reasoning,
        )

        # Store result in K-Block metadata
        self.parse_results[range] = result

        return result
```

---

## File Structure (Updated)

P-gent components integrate into existing structure:

```
impl/claude/web/src/components/
├── parse/                          # NEW: P-gent components
│   ├── ParseResultBadge.tsx        # Inline badge (status bar, inline)
│   ├── ParseResultBadge.css
│   ├── ParseResultIndicator.tsx    # Extended display (details panel)
│   ├── ParseResultIndicator.css
│   ├── ParsePortalToken.tsx        # Portal token integration
│   ├── StrategyTrace.tsx           # Fallback chain display
│   ├── StrategyTrace.css
│   ├── ParseGutterAnnotation.tsx   # Gutter integration
│   ├── ParseView.tsx               # K-Block view type
│   └── index.ts
├── tokens/
│   └── PortalToken.tsx             # Existing (ParsePortalToken follows pattern)
├── joy/
│   └── GrowingContainer.tsx        # Existing (used for expansion)
└── ...

impl/claude/services/hypergraph_editor/
├── modes/
│   ├── command.py                  # Add :parse command
│   └── ...
├── web/
│   ├── UnifiedEditor.tsx           # Add ParseResultBadge to status bar
│   ├── Gutter.tsx                  # Add ParseGutterAnnotation
│   └── ViewTabs.tsx                # Add Parse view option
└── ...

impl/claude/services/k_block/
├── views/
│   └── parse.py                    # NEW: Parse view renderer
├── witness/
│   └── parse_trace.py              # NEW: Parse witness integration
└── ...
```

---

**End of Visual Design Guide (Brutalist Edition)**

*Following your actual patterns: monospace, glyphs, data-attributes, BEM.*
*Integrated with: Hypergraph Editor, K-Block, Portal Tokens, Witness.*
