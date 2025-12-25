# P-gent Implementation Plan

**Status**: Implementation Roadmap
**Session**: 2025-12-25 - The Parsing Renaissance
**Voice Anchor**: *"Daring, bold, creative, opinionated but not gaudy"*

---

## Executive Summary

This plan upgrades P-gents from a solid technical foundation to a **delightful, fully-integrated parsing ecosystem**. The key insight: P-gents trivially supercharge agents by providing reliability guarantees that compose with any tool or harness.

### Current State
- ✅ Core types implemented (`ParseResult`, `Parser`, `ParserConfig`)
- ✅ 10 parsing strategies functional
- ✅ Composition patterns working (`FallbackParser`, `FusionParser`, `SwitchParser`)
- ✅ Good test coverage

### Target State
- 🎯 Visual experience with Translation Lens metaphor
- 🎯 Harness integration for evidence-based parsing
- 🎯 Tool faceting for U-gent reliability
- 🎯 AGENTESE paths for universal access
- 🎯 Joy-inducing UI moments

---

## Phase 1: Core Enhancements (Week 1)

### 1.1 FacetedTool Pattern

Create the tool faceting capability:

**File**: `impl/claude/agents/p/faceting.py`

```python
@dataclass
class FacetedTool(Tool[Input, ParseResult[Output]]):
    """
    Wrap any tool with P-gent parsing for guaranteed reliability.

    Instead of raw tool output that may fail to parse,
    FacetedTool always returns ParseResult with confidence.
    """
    tool: Tool[Input, str]
    parser: Parser[Output]

    async def invoke(self, input: Input) -> ParseResult[Output]:
        raw = await self.tool.invoke(input)
        return self.parser.parse(raw)


def facet(tool: Tool, parser: Parser) -> FacetedTool:
    """Convenience function to facet a tool."""
    return FacetedTool(tool=tool, parser=parser)
```

**Tests**: `_tests/test_faceting.py`
- Test basic faceting works
- Test fallback chain with faceted tool
- Test confidence propagation
- Test error handling

### 1.2 Witness Integration

Add witness marks to parsing operations:

**File**: `impl/claude/agents/p/witnessed.py`

```python
class WitnessedParser(Parser[A]):
    """Parser that emits witness marks for every parse operation."""

    def __init__(self, base_parser: Parser[A], witness: WitnessService):
        self.base_parser = base_parser
        self.witness = witness

    async def parse(self, text: str) -> ParseResult[A]:
        result = self.base_parser.parse(text)

        await self.witness.mark(
            action="parsed_llm_output",
            result=result.success,
            confidence=result.confidence,
            strategy=result.strategy,
            repairs=result.repairs,
            metadata={
                "input_length": len(text),
                "partial": result.partial,
            }
        )

        return result
```

### 1.3 Harness Evidence Bridge

Connect P-gent to exploration harness:

**File**: `impl/claude/protocols/derivation/parse_bridge.py`

```python
class ParseEvidence:
    """Evidence from parsing operations."""

    @staticmethod
    def from_parse_result(result: ParseResult) -> Evidence:
        return Evidence(
            source="p_gent_parse",
            content=f"Parsed with {result.confidence:.0%} confidence via {result.strategy}",
            strength=EvidenceStrength.from_confidence(result.confidence),
            metadata={
                "confidence": result.confidence,
                "strategy": result.strategy,
                "repairs": result.repairs,
            }
        )


class EvidenceStrength:
    @staticmethod
    def from_confidence(conf: float) -> str:
        if conf >= 0.9: return "strong"
        if conf >= 0.7: return "moderate"
        return "weak"
```

---

## Phase 2: AGENTESE Paths (Week 1-2)

### 2.1 Self.Parse Context

**File**: `impl/claude/protocols/agentese/contexts/self_parse.py`

```python
@node("self.parse", dependencies=("parser_registry",))
class ParseNode:
    """AGENTESE node for parsing capabilities."""

    def __init__(self, parser_registry: ParserRegistry):
        self.registry = parser_registry

    @aspect("manifest")
    async def manifest(self, observer: Observer) -> dict:
        """Current parser configuration and stats."""
        return {
            "strategies": self.registry.available_strategies(),
            "default_config": self.registry.default_config.to_dict(),
            "stats": self.registry.stats(),
        }

    @aspect("invoke")
    async def invoke(
        self,
        observer: Observer,
        text: str,
        strategy: str = "fallback:json,anchor,reflection"
    ) -> ParseResult:
        """Parse text with configured strategy."""
        parser = self.registry.build_parser(strategy)
        return parser.parse(text)

    @aspect("stream")
    async def stream(
        self,
        observer: Observer,
        tokens: AsyncIterator[str],
        strategy: str = "stack_balance"
    ) -> AsyncIterator[ParseResult]:
        """Parse token stream with live results."""
        parser = self.registry.build_parser(strategy)
        async for result in parser.parse_stream(tokens):
            yield result

    @aspect("configure")
    async def configure(self, observer: Observer, **config) -> dict:
        """Update parser configuration."""
        self.registry.update_config(**config)
        return {"status": "configured", "config": config}

    @aspect("history")
    async def history(self, observer: Observer, limit: int = 10) -> list:
        """Recent parse attempts with results."""
        return self.registry.get_history(limit)

    @aspect("strategies")
    async def strategies(self, observer: Observer) -> list:
        """Available parsing strategies."""
        return [
            {"name": s.name, "phase": s.phase, "description": s.description}
            for s in self.registry.all_strategies()
        ]
```

### 2.2 Concept.Parse Catalog

**File**: `impl/claude/protocols/agentese/contexts/concept_parse.py`

```python
@node("concept.parse", dependencies=())
class ParseConceptNode:
    """AGENTESE node for parsing concepts and composition."""

    @aspect("json")
    async def json_strategies(self, observer: Observer) -> dict:
        """JSON parsing strategy catalog."""
        return {
            "strict": "Standard JSON parser, confidence=0.85",
            "stack_balance": "Streaming with auto-close, confidence=0.75",
            "reflection": "LLM-assisted repair, confidence varies",
            "probabilistic_ast": "Per-node confidence scoring",
        }

    @aspect("html")
    async def html_strategies(self, observer: Observer) -> dict:
        """HTML parsing strategy catalog."""
        return {
            "stack_balance": "Auto-close unclosed tags",
            "diff_based": "Apply patches to template",
            "anchor": "Extract content between anchors",
        }

    @aspect("code")
    async def code_strategies(self, observer: Observer) -> dict:
        """Code parsing strategy catalog."""
        return {
            "pydantic": "Type-guided with validation",
            "reflection": "LLM fixes syntax errors",
            "incremental": "Progressive AST building",
        }

    @aspect("compose")
    async def compose(
        self,
        observer: Observer,
        strategies: list[str],
        mode: str = "fallback"
    ) -> str:
        """Compose strategies into pipeline."""
        # Returns a strategy string like "fallback:json,anchor,reflection"
        return f"{mode}:{','.join(strategies)}"
```

---

## Phase 3: Visual Components (Week 2-3)

### 3.1 ConfidenceMeter Component

**File**: `impl/claude/web/src/components/parse/ConfidenceMeter.tsx`

```tsx
import { useEffect, useState } from 'react';
import './ConfidenceMeter.css';

interface ConfidenceMeterProps {
  confidence: number;
  strategy: string;
  repairCount: number;
  state: 'idle' | 'parsing' | 'success' | 'repair' | 'failed';
  size?: 'sm' | 'md' | 'lg';
}

export function ConfidenceMeter({
  confidence,
  strategy,
  repairCount,
  state,
  size = 'md'
}: ConfidenceMeterProps) {
  const [displayConfidence, setDisplayConfidence] = useState(0);

  useEffect(() => {
    // Animate confidence value
    const timer = setTimeout(() => setDisplayConfidence(confidence), 100);
    return () => clearTimeout(timer);
  }, [confidence]);

  const sizeClass = `confidence-meter--${size}`;
  const stateClass = `confidence-meter--${state}`;
  const color = confidenceToColor(confidence);

  return (
    <div className={`confidence-meter ${sizeClass} ${stateClass}`}>
      <svg viewBox="0 0 100 100">
        {/* Background arc */}
        <circle
          className="confidence-meter__bg"
          cx="50" cy="50" r="45"
          strokeDasharray="283"
          strokeDashoffset="70"
        />
        {/* Confidence arc */}
        <circle
          className="confidence-meter__value"
          cx="50" cy="50" r="45"
          stroke={color}
          strokeDasharray="283"
          strokeDashoffset={283 - (displayConfidence * 213)}
          style={{ transition: 'stroke-dashoffset 0.6s ease-out' }}
        />
      </svg>
      <div className="confidence-meter__content">
        <span className="confidence-meter__percent">
          {Math.round(displayConfidence * 100)}%
        </span>
        <span className="confidence-meter__strategy">{strategy}</span>
        {repairCount > 0 && (
          <span className="confidence-meter__repairs">
            {repairCount} repair{repairCount > 1 ? 's' : ''}
          </span>
        )}
      </div>
    </div>
  );
}

function confidenceToColor(confidence: number): string {
  if (confidence >= 0.85) return 'var(--parse-confidence-high)';
  if (confidence >= 0.7) return 'var(--parse-confidence-medium)';
  if (confidence >= 0.5) return 'var(--parse-confidence-low)';
  return 'var(--parse-confidence-failed)';
}
```

### 3.2 ParseResultCard Component

**File**: `impl/claude/web/src/components/parse/ParseResultCard.tsx`

```tsx
import { ParseResult } from '@/types/parse';
import { ConfidenceMeter } from './ConfidenceMeter';
import { RepairList } from './RepairList';
import './ParseResultCard.css';

interface ParseResultCardProps {
  result: ParseResult<unknown>;
  showRaw?: boolean;
  showDiff?: boolean;
  actions?: Array<'diff' | 'reparse' | 'copy' | 'expand'>;
  expandable?: boolean;
}

export function ParseResultCard({
  result,
  showRaw = false,
  showDiff = false,
  actions = ['copy', 'expand'],
  expandable = true
}: ParseResultCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className={`parse-result-card ${result.success ? 'success' : 'failed'}`}>
      <div className="parse-result-card__header">
        <span className="parse-result-card__icon">🔍</span>
        <span className="parse-result-card__title">Parse Result</span>
        <ConfidenceMeter
          confidence={result.confidence}
          strategy={result.strategy || 'unknown'}
          repairCount={result.repairs.length}
          state={result.success ? 'success' : 'failed'}
          size="sm"
        />
      </div>

      <div className="parse-result-card__body">
        <div className="parse-result-card__strategy">
          Strategy: {result.strategy}
        </div>

        {result.repairs.length > 0 && (
          <RepairList repairs={result.repairs} />
        )}

        <div className="parse-result-card__value">
          <pre>{JSON.stringify(result.value, null, 2)}</pre>
        </div>
      </div>

      <div className="parse-result-card__actions">
        {actions.includes('copy') && (
          <button onClick={() => copyToClipboard(result.value)}>
            Copy Value
          </button>
        )}
        {actions.includes('diff') && showDiff && (
          <button onClick={() => setShowDiffView(true)}>
            View Diff
          </button>
        )}
        {expandable && (
          <button onClick={() => setExpanded(!expanded)}>
            {expanded ? 'Collapse' : 'Expand'}
          </button>
        )}
      </div>
    </div>
  );
}
```

### 3.3 StrategyWaterfall Component

**File**: `impl/claude/web/src/components/parse/StrategyWaterfall.tsx`

```tsx
interface StrategyStep {
  name: string;
  success: boolean;
  error?: string;
  confidence?: number;
}

interface StrategyWaterfallProps {
  strategies: StrategyStep[];
  animated?: boolean;
  compact?: boolean;
}

export function StrategyWaterfall({
  strategies,
  animated = true,
  compact = false
}: StrategyWaterfallProps) {
  return (
    <div className={`strategy-waterfall ${compact ? 'compact' : ''}`}>
      {strategies.map((step, i) => (
        <React.Fragment key={step.name}>
          <StrategyStep
            step={step}
            index={i}
            animated={animated}
            isLast={i === strategies.length - 1}
          />
          {i < strategies.length - 1 && (
            <Arrow success={step.success} />
          )}
        </React.Fragment>
      ))}
    </div>
  );
}
```

---

## Phase 4: Joy-Inducing Features (Week 3)

### 4.1 Save Counter

Track and celebrate parse saves:

**File**: `impl/claude/web/src/components/parse/SaveCounter.tsx`

```tsx
import { useParseStats } from '@/hooks/useParseStats';
import './SaveCounter.css';

export function SaveCounter() {
  const { savesToday, lastSave } = useParseStats();
  const [animating, setAnimating] = useState(false);

  useEffect(() => {
    if (lastSave) {
      setAnimating(true);
      setTimeout(() => setAnimating(false), 500);
    }
  }, [lastSave]);

  return (
    <div className={`save-counter ${animating ? 'animating' : ''}`}>
      <span className="save-counter__icon">💫</span>
      <span className="save-counter__value">
        {savesToday.toLocaleString()}
      </span>
      <span className="save-counter__label">
        parse failures prevented today
      </span>
    </div>
  );
}
```

### 4.2 Perfect Parse Celebration

**File**: `impl/claude/web/src/components/parse/PerfectParseCelebration.tsx`

```tsx
import { Confetti } from '@/components/joy';
import { useEffect, useState } from 'react';

interface PerfectParseCelebrationProps {
  result: ParseResult<unknown>;
}

export function PerfectParseCelebration({ result }: PerfectParseCelebrationProps) {
  const [celebrating, setCelebrating] = useState(false);

  const isPerfect = result.success &&
    result.confidence >= 0.95 &&
    result.repairs.length === 0;

  useEffect(() => {
    if (isPerfect) {
      setCelebrating(true);
      setTimeout(() => setCelebrating(false), 2000);
    }
  }, [isPerfect]);

  if (!celebrating) return null;

  return (
    <div className="perfect-parse-celebration">
      <Confetti
        count={30}
        duration={1500}
        colors={['#00CC88', '#4488FF', '#FFCC00']}
      />
      <div className="perfect-parse-message">
        🎉 Perfect parse! ({Math.round(result.confidence * 100)}% confidence)
      </div>
    </div>
  );
}
```

### 4.3 Repair Narrative

**File**: `impl/claude/agents/p/narrative.py`

```python
def repair_narrative(repairs: list[str]) -> str:
    """Transform repair list into a narrative story."""
    if not repairs:
        return "Clean parse, no repairs needed!"

    if len(repairs) == 1:
        return f"Fixed: {repairs[0]}. All good now."

    # Build narrative flow
    parts = []
    for i, repair in enumerate(repairs):
        if i == 0:
            parts.append(f"Found {repair}")
        elif i == len(repairs) - 1:
            parts.append(f"finally {repair}")
        else:
            parts.append(repair)

    return " → ".join(parts) + " → Valid!"


def strategy_story(strategies: list[dict]) -> str:
    """Create a story from strategy attempts."""
    successful = next((s for s in strategies if s["success"]), None)
    if not successful:
        return "All strategies failed 😢"

    failed_count = strategies.index(successful)
    if failed_count == 0:
        return f"First try with {successful['name']}! 🎯"

    return f"Tried {failed_count} strategies, {successful['name']} saved the day! 💪"
```

---

## Phase 5: Integration & Polish (Week 4)

### 5.1 CLI Handler

**File**: `impl/claude/protocols/cli/handlers/parse.py`

```python
def cmd_parse(args, console):
    """Parse text with P-gent strategies."""
    subcommand = args.get("subcommand", "status")

    handlers = {
        "status": _handle_status,
        "invoke": _handle_invoke,
        "stream": _handle_stream,
        "strategies": _handle_strategies,
        "history": _handle_history,
        "stats": _handle_stats,
    }

    handler = handlers.get(subcommand, _handle_status)
    return handler(args, console)


def _handle_invoke(args, console):
    """Parse text with specified strategy."""
    text = args.get("text")
    strategy = args.get("strategy", "fallback:json,anchor,reflection")

    parser = build_parser(strategy)
    result = parser.parse(text)

    # Rich output
    if result.success:
        console.print(f"[green]✓[/green] Parsed with {result.confidence:.0%} confidence")
        console.print(f"Strategy: {result.strategy}")
        if result.repairs:
            console.print(f"Repairs: {', '.join(result.repairs)}")
        console.print(Panel(JSON(result.value), title="Value"))
    else:
        console.print(f"[red]✗[/red] Parse failed: {result.error}")

    return result
```

### 5.2 Portal Token Integration

**File**: `impl/claude/web/src/components/parse/ParseResultToken.tsx`

```tsx
import { PortalToken } from '@/components/tokens/PortalToken';
import { ParseResultCard } from './ParseResultCard';

interface ParseResultTokenProps {
  result: ParseResult<unknown>;
}

export function ParseResultToken({ result }: ParseResultTokenProps) {
  const color = confidenceToColor(result.confidence);
  const summary = `${Math.round(result.confidence * 100)}% | ${result.repairs.length} repairs`;

  return (
    <PortalToken
      icon="🔍"
      iconColor={color}
      label="Parse Result"
      summary={summary}
      expandable={true}
      contextType="parse_result"
    >
      <ParseResultCard
        result={result}
        showDiff={true}
        actions={['diff', 'reparse', 'copy']}
      />
    </PortalToken>
  );
}
```

### 5.3 Test Suite

**File**: `impl/claude/agents/p/_tests/test_visual_integration.py`

```python
import pytest
from agents.p import FacetedTool, WitnessedParser, ParseEvidence


class TestFaceting:
    def test_faceted_tool_always_returns_parse_result(self):
        """FacetedTool wraps any tool with parsing guarantees."""
        mock_tool = MockTool(output='{"name": "test"}')
        parser = JsonParser()

        faceted = FacetedTool(tool=mock_tool, parser=parser)
        result = faceted.invoke({})

        assert isinstance(result, ParseResult)
        assert result.success
        assert result.confidence > 0

    def test_faceted_tool_handles_malformed_output(self):
        """FacetedTool degrades gracefully on malformed output."""
        mock_tool = MockTool(output='{"name: broken')
        parser = FallbackParser(JsonParser(), AnchorBasedParser())

        faceted = FacetedTool(tool=mock_tool, parser=parser)
        result = faceted.invoke({})

        # Should still return ParseResult, not raise
        assert isinstance(result, ParseResult)


class TestWitnessIntegration:
    async def test_witnessed_parser_emits_marks(self):
        """WitnessedParser emits witness marks for all parses."""
        mock_witness = MockWitness()
        parser = WitnessedParser(JsonParser(), mock_witness)

        result = parser.parse('{"test": true}')

        assert len(mock_witness.marks) == 1
        mark = mock_witness.marks[0]
        assert mark["action"] == "parsed_llm_output"
        assert mark["result"] == True
        assert mark["confidence"] > 0


class TestEvidenceBridge:
    def test_parse_result_to_evidence(self):
        """ParseResult converts to Evidence for harness."""
        result = ParseResult(
            success=True,
            value={"test": True},
            confidence=0.85,
            strategy="json",
        )

        evidence = ParseEvidence.from_parse_result(result)

        assert evidence.strength == "moderate"
        assert "85%" in evidence.content
```

---

## Success Metrics

### Functional
- [ ] All 10 strategies work with FacetedTool pattern
- [ ] AGENTESE paths registered and functional
- [ ] Witness marks emitted for all parses
- [ ] Evidence bridge connects to exploration harness
- [ ] CLI handler provides full functionality

### Visual
- [ ] ConfidenceMeter renders at all three sizes
- [ ] StrategyWaterfall animates correctly
- [ ] ParseResultCard shows all information
- [ ] Portal Token integration works
- [ ] Three-mode responsive switching works

### Delight
- [ ] Save counter increments on successful repairs
- [ ] Perfect parse celebration triggers correctly
- [ ] Repair narrative generates readable stories
- [ ] Animations respect reduced-motion preference

### Performance
- [ ] Parse operations < 100ms for simple inputs
- [ ] Streaming adds < 10ms per chunk
- [ ] UI components render < 16ms (60fps)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking existing tests | Run full test suite after each phase |
| Performance regression | Add performance baselines as tests |
| Visual inconsistency | Design review before implementing |
| AGENTESE conflicts | Check path namespace before registration |
| Witness overhead | Make witnessing optional via config |

---

## Timeline

| Week | Phase | Deliverables |
|------|-------|--------------|
| 1 | Core + AGENTESE | FacetedTool, WitnessedParser, `self.parse.*` paths |
| 2 | AGENTESE + Visual | `concept.parse.*` paths, ConfidenceMeter, ParseResultCard |
| 3 | Visual + Delight | StrategyWaterfall, SaveCounter, celebrations |
| 4 | Integration | CLI, Portal Token, tests, polish |

---

**End of Implementation Plan**

*"The lens reveals. The repair sparkles. The confidence glows."*
