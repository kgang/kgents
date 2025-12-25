# LLM-Backed Analysis Operad: Implementation Plan

> *"Analysis that can analyze itself is the only analysis worth having. Now we prove it with real LLM calls."*

**Status**: Planning
**Date**: 2025-12-24
**Goal**: Fully LLM-backed Analysis Operad with ASHC integration, CLI, and UI

---

## Executive Summary

Transform the structural Analysis Operad into a **fully LLM-backed system** that:
1. Uses Claude to perform actual categorical, epistemic, dialectical, and generative analysis
2. Integrates with **ASHC** for Bayesian confidence and economic accountability
3. Provides seamless **CLI** experience for Kent and agents (`kg analyze`)
4. Surfaces insights through **UI components** integrated with existing Director/Hypergraph

---

## Part 1: Architecture

### 1.1 The LLM-Analysis Bridge

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LLM-BACKED ANALYSIS ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  User Request                                                                │
│       │                                                                      │
│       ▼                                                                      │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  kg analyze spec/theory/zero-seed.md --full                          │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│       │                                                                      │
│       ▼                                                                      │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  CLI Handler (protocols/cli/handlers/analyze.py)                     │   │
│  │  - Parse args, validate target                                        │   │
│  │  - Route to appropriate mode(s)                                       │   │
│  │  - Format output (rich/json)                                          │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│       │                                                                      │
│       ▼                                                                      │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  Analysis Service (services/analysis/)                               │   │
│  │  - Orchestrate LLM calls per mode                                     │   │
│  │  - Integrate with ASHC for confidence                                 │   │
│  │  - Emit Witness marks for each analysis                               │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│       │                                                                      │
│       ├────────────┬────────────┬────────────┬────────────┐                 │
│       ▼            ▼            ▼            ▼            ▼                 │
│  ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐            │
│  │ CAT    │   │ EPI    │   │ DIA    │   │ GEN    │   │ ASHC   │            │
│  │ LLM    │   │ LLM    │   │ LLM    │   │ LLM    │   │ Bridge │            │
│  │ Agent  │   │ Agent  │   │ Agent  │   │ Agent  │   │        │            │
│  └────────┘   └────────┘   └────────┘   └────────┘   └────────┘            │
│       │            │            │            │            │                 │
│       └────────────┴────────────┴────────────┴────────────┘                 │
│                           │                                                  │
│                           ▼                                                  │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  ASHC Evidence Layer                                                  │   │
│  │  - AdaptiveCompiler: Bayesian stopping                               │   │
│  │  - ASHCBet: Economic accountability for confidence                   │   │
│  │  - CausalLearner: Learn analysis patterns                            │   │
│  │  - PolicyTrace: Every analysis step is witnessed                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                           │                                                  │
│                           ▼                                                  │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  Witness Integration                                                  │   │
│  │  - Emit marks for each analysis mode                                  │   │
│  │  - Store in Brain for retrieval                                       │   │
│  │  - Build lineage graph                                                │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 LLM Agents per Mode

Each analysis mode gets a specialized LLM prompt:

| Mode | LLM Agent Role | ASHC Integration |
|------|----------------|------------------|
| **Categorical** | "You are a category theorist. Extract laws, verify composition, find fixed points." | Bet on law verification with 0.8 confidence |
| **Epistemic** | "You are an epistemologist. Determine layer, build Toulmin structure, trace grounding." | Track confidence per claim |
| **Dialectical** | "You are a dialectician. Find tensions, classify contradictions, synthesize resolutions." | Paraconsistent tolerance scoring |
| **Generative** | "You are a compression analyst. Extract grammar, measure compression, test regeneration." | Verify with pytest/mypy |

### 1.3 ASHC Integration Points

```python
# Analysis with ASHC evidence accumulation
async def analyze_with_ashc(target: str, mode: str) -> AnalysisResult:
    # 1. Create ASHC bet (economic accountability)
    bet = ASHCBet.create(
        spec=f"Analysis of {target} in {mode} mode",
        confidence=0.8,  # Initial confidence
        stake=Decimal("0.05"),
    )

    # 2. Run adaptive analysis (Bayesian stopping)
    result = await adaptive_compile_with_llm(
        spec=build_analysis_prompt(target, mode),
        config=StoppingConfig(n_diff=2, confidence=0.95),
    )

    # 3. Resolve bet based on analysis success
    resolved = bet.resolve(success=result.verified)

    # 4. Emit witness mark
    mark = await emit_analysis_mark(
        target=target,
        mode=mode,
        result=result,
        confidence=resolved.final_confidence,
    )

    return AnalysisResult(
        report=result.output,
        confidence=resolved.final_confidence,
        mark_id=mark.id,
        bet_id=resolved.bet_id,
    )
```

---

## Part 2: CLI Design

### 2.1 Command Structure

```bash
# Basic usage
kg analyze <path>                      # Full 4-mode analysis
kg analyze <path> --mode categorical   # Single mode
kg analyze <path> --mode cat,epi       # Multiple modes

# ASHC integration
kg analyze <path> --ashc               # With evidence accumulation
kg analyze <path> --bet 0.1            # With economic stake
kg analyze <path> --confidence 0.95    # Bayesian confidence threshold

# Output formats
kg analyze <path> --json               # Machine-readable
kg analyze <path> --rich               # Pretty terminal output
kg analyze <path> --report             # Full markdown report

# Agent-friendly
kg analyze <path> --json --quiet       # Minimal output for agents
kg analyze --self                      # Self-analysis (meta-applicability)

# Composition
kg analyze spec/*.md --parallel        # Analyze multiple specs
kg analyze <path> --compare <other>    # Differential analysis
```

### 2.2 CLI Handler Implementation

```python
# protocols/cli/handlers/analyze.py

@handler("analyze", is_async=True, tier=1, description="Four-mode spec analysis")
async def cmd_analyze(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Analyze specs using four rigorous modes.

    AGENTESE Paths:
        kg analyze          -> concept.analysis.full
        kg analyze --cat    -> concept.analysis.categorical
        kg analyze --epi    -> concept.analysis.epistemic
        kg analyze --dia    -> concept.analysis.dialectical
        kg analyze --gen    -> concept.analysis.generative
    """
    target = _parse_target(args)
    modes = _parse_modes(args)
    use_ashc = "--ashc" in args
    use_llm = "--llm" in args or not "--structural" in args

    if use_llm:
        result = await analyze_with_llm(target, modes, use_ashc)
    else:
        result = await analyze_structural(target, modes)

    _format_output(result, args)
    return 0 if result.is_valid else 1
```

### 2.3 AGENTESE Integration

```python
# AGENTESE paths for analysis
concept.analysis.full.{spec_path}           # Full four-mode analysis
concept.analysis.categorical.{spec_path}    # Categorical only
concept.analysis.epistemic.{spec_path}      # Epistemic only
concept.analysis.dialectical.{spec_path}    # Dialectical only
concept.analysis.generative.{spec_path}     # Generative only
concept.analysis.meta.{analysis_id}         # Analyze a previous analysis
concept.analysis.compare.{a}.{b}            # Differential analysis
```

---

## Part 3: UI/UX Strategy

### 3.1 Existing Asset Integration

| Existing Component | Analysis Integration |
|--------------------|---------------------|
| **DirectorDashboard** | Add "Analyze" action to document cards |
| **DocumentDetail** | Show AnalysisReport with expandable modes |
| **AnalysisSummary** | Extend with four-mode indicators |
| **HypergraphEditor** | Analysis nodes in spec graph |
| **WitnessPanel** | Show analysis marks with confidence |
| **BrainPage** | Stream analysis events in real-time |

### 3.2 New UI Components

```
web/src/components/analysis/
├── AnalysisModeCard.tsx       # Card per mode (categorical/epistemic/etc)
├── AnalysisProgress.tsx       # Progress indicator during LLM analysis
├── AnalysisTimeline.tsx       # History of analyses on a spec
├── ConfidenceBadge.tsx        # ASHC confidence display
├── TensionGraph.tsx           # Dialectical tensions visualization
├── LawVerification.tsx        # Categorical law status
├── GroundingChain.tsx         # Epistemic grounding visualization
├── CompressionMeter.tsx       # Generative compression ratio
└── AnalysisModal.tsx          # Full analysis modal overlay
```

### 3.3 DevEx Strategy

| Persona | Primary Interface | Key Features |
|---------|-------------------|--------------|
| **Kent (Human)** | CLI + TUI | Rich output, interactive prompts, `--explain` flag |
| **Agents (LLM)** | CLI `--json` | Structured output, `--quiet`, error codes |
| **Web Users** | UI Dashboard | Click-to-analyze, visual reports, confidence meters |
| **Pipelines** | AGENTESE API | `logos.invoke("concept.analysis.full", ...)` |

---

## Part 4: Implementation Phases

### Phase 1: LLM Analysis Service (Priority)

**Files to Create:**
```
impl/claude/services/analysis/
├── __init__.py
├── service.py              # Main AnalysisService class
├── prompts.py              # LLM prompt templates per mode
├── llm_agents.py           # LLM agent wrappers
├── ashc_bridge.py          # ASHC integration
└── _tests/
    ├── test_service.py
    └── test_llm_agents.py
```

**Key Implementation:**
```python
# services/analysis/service.py

class AnalysisService:
    """
    LLM-backed four-mode analysis service.

    Integrates with ASHC for evidence accumulation.
    """

    def __init__(
        self,
        llm: LLMProvider,
        ashc: ASHCBridge | None = None,
        witness: WitnessService | None = None,
    ):
        self.llm = llm
        self.ashc = ashc
        self.witness = witness

    async def analyze_categorical(self, spec: str) -> CategoricalReport:
        """LLM-backed categorical analysis."""
        prompt = CATEGORICAL_PROMPT.format(spec=spec)
        response = await self.llm.complete(prompt)
        return parse_categorical_response(response)

    async def analyze_full(self, spec: str) -> FullAnalysisReport:
        """Run all four modes and synthesize."""
        # Run in parallel where possible
        cat, epi = await asyncio.gather(
            self.analyze_categorical(spec),
            self.analyze_epistemic(spec),
        )
        dia, gen = await asyncio.gather(
            self.analyze_dialectical(spec, tensions_from=cat),
            self.analyze_generative(spec),
        )
        return self._synthesize(cat, epi, dia, gen)
```

### Phase 2: CLI Handler

**File:** `protocols/cli/handlers/analyze.py`

### Phase 3: ASHC Integration

**File:** `services/analysis/ashc_bridge.py`

```python
class AnalysisASHCBridge:
    """Bridge Analysis Operad with ASHC evidence system."""

    async def analyze_with_evidence(
        self,
        target: str,
        mode: str,
        confidence: float = 0.8,
        stake: Decimal = Decimal("0.05"),
    ) -> EvidencedAnalysis:
        """
        Perform analysis with ASHC evidence accumulation.

        Creates bet, runs adaptive analysis, resolves bet,
        emits marks, and returns evidenced result.
        """
        ...
```

### Phase 4: UI Components

**Priority Order:**
1. AnalysisModeCard (show individual mode results)
2. ConfidenceBadge (ASHC confidence)
3. AnalysisModal (full analysis overlay)
4. TensionGraph (dialectical visualization)

### Phase 5: Integration Testing

- End-to-end: CLI → LLM → ASHC → Witness → UI
- Performance: Analysis latency < 30s for full mode
- Accuracy: Self-analysis produces valid result

---

## Part 5: Agent Orchestration

### Sub-Agent Tasks

| Agent | Task | Deliverable |
|-------|------|-------------|
| **analysis-service** | Implement `services/analysis/` | Service with LLM integration |
| **analysis-cli** | Implement `protocols/cli/handlers/analyze.py` | CLI handler |
| **analysis-ashc** | Integrate with ASHC | Evidence bridge |
| **analysis-ui** | Create UI components | React components |
| **analysis-test** | Write tests | Test coverage |

### Parallel Execution Strategy

```
Phase 1 (Core):
  ├── [analysis-service] Build LLM service ──────────────────────┐
  └── [analysis-cli] Build CLI handler ─────────────────────────┼─► Integration
                                                                  │
Phase 2 (Integration):                                            │
  ├── [analysis-ashc] ASHC bridge ───────────────────────────────┤
  └── [analysis-ui] UI components ───────────────────────────────┤
                                                                  │
Phase 3 (Testing):                                                │
  └── [analysis-test] End-to-end tests ──────────────────────────┘
```

---

## Part 6: Success Criteria

| Criterion | Target |
|-----------|--------|
| **CLI Usability** | `kg analyze spec.md` works in < 30s |
| **LLM Integration** | All four modes use real LLM calls |
| **ASHC Confidence** | Confidence scores attached to all analyses |
| **Witness Integration** | Every analysis emits marks |
| **UI Visualization** | Analysis modal shows all four modes |
| **Self-Analysis** | `kg analyze --self` returns valid |
| **Agent-Friendly** | `--json` output parseable by LLMs |

---

## Appendix A: LLM Prompt Templates

### Categorical Prompt

```
You are a category theorist analyzing a specification.

SPECIFICATION:
{spec}

TASK:
1. Extract all composition laws (explicit and implicit)
2. Verify each law holds (PASSED, STRUCTURAL, FAILED)
3. Identify fixed points if spec is self-referential
4. Check for Lawvere fixed-point implications

OUTPUT (JSON):
{
  "laws": [{"name": "...", "equation": "...", "status": "PASSED|STRUCTURAL|FAILED"}],
  "fixed_point": {"is_self_referential": true, "description": "..."},
  "summary": "..."
}
```

### Epistemic Prompt

```
You are an epistemologist analyzing justification structure.

SPECIFICATION:
{spec}

TASK:
1. Determine which layer this spec occupies (L1-L7)
2. Build Toulmin structure (claim, grounds, warrant, backing, qualifier, rebuttals)
3. Trace grounding chain to axioms
4. Analyze bootstrap if self-referential

OUTPUT (JSON):
{
  "layer": 4,
  "toulmin": {"claim": "...", "grounds": [...], ...},
  "grounding_chain": [{"layer": 1, "node": "...", "edge": "grounds"}, ...],
  "bootstrap": {"is_valid": true, "explanation": "..."},
  "summary": "..."
}
```

### Dialectical Prompt

```
You are a dialectician identifying and resolving tensions.

SPECIFICATION:
{spec}

TASK:
1. Extract all tensions (thesis vs antithesis pairs)
2. Classify each: APPARENT, PRODUCTIVE, PROBLEMATIC, PARACONSISTENT
3. Attempt synthesis for each tension
4. Determine tolerance for unresolved contradictions

OUTPUT (JSON):
{
  "tensions": [
    {"thesis": "...", "antithesis": "...", "classification": "PRODUCTIVE", "synthesis": "...", "resolved": true}
  ],
  "summary": "..."
}
```

### Generative Prompt

```
You are a compression analyst testing regenerability.

SPECIFICATION:
{spec}

TASK:
1. Extract generative grammar (primitives, operations, laws)
2. Estimate compression ratio (spec size / impl size)
3. Identify minimal kernel of axioms
4. Test if spec can be regenerated from axioms

OUTPUT (JSON):
{
  "grammar": {"primitives": [...], "operations": [...], "laws": [...]},
  "compression_ratio": 0.25,
  "minimal_kernel": ["axiom1", "axiom2"],
  "regeneration_test": {"passed": true, "missing": []},
  "summary": "..."
}
```

---

*"Analysis that can analyze itself is the only analysis worth having. Now we prove it with real LLM calls."*
