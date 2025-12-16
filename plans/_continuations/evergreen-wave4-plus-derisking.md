# Evergreen Prompt System: Waves 4+ De-Risking Plan

> *"De-risk early. Fail fast. Build on solid foundations."*

**Status:** Research & De-risking
**Prerequisite:** Wave 3 (Soft Section Protocol) - In Progress by Another Builder
**Date:** 2025-12-16
**Guard:** `[phase=RESEARCH][entropy=0.15][parallel=true]`

---

## Executive Summary

This document de-risks Waves 4-6 of the Evergreen Prompt System reformation while Wave 3 is in progress. We focus on:

1. **Resolving open questions** from the reformation document
2. **Prototyping high-risk components** before full implementation
3. **Identifying reusable infrastructure** already in kgents
4. **Defining integration points** with Wave 3 outputs

---

## Part I: Existing Infrastructure Inventory

### Already Built (DO NOT REBUILD)

| Component | Location | Reuse For |
|-----------|----------|-----------|
| **Checkpoint/Storage** | `protocols/prompt/rollback/` | Wave 5 rollback registry |
| **M-gent Crystals** | `agents/m/crystal.py` | Habit storage, semantic search |
| **L-gent Embeddings** | `agents/m/importers/markdown.py` | Semantic similarity |
| **CLI Handler Pattern** | `protocols/cli/handlers/grow.py` | Wave 6 `/prompt` commands |
| **AGENTESE Contexts** | `protocols/agentese/contexts/` | `concept.prompt.*` paths |
| **Cortex Persistence** | `protocols/cli/instance_db/` | Policy persistence |
| **Rich Output** | Used throughout handlers | Pretty CLI output |

### Checkpoint Module Status (Already Started!)

The rollback foundation is **partially implemented**:

```
impl/claude/protocols/prompt/rollback/
├── __init__.py       # Package exports
├── checkpoint.py     # Checkpoint, CheckpointSummary, CheckpointId ✓
└── storage.py        # JSONCheckpointStorage, InMemoryCheckpointStorage ✓
```

**What's done:**
- `Checkpoint` dataclass with full serialization
- Content-addressable IDs (SHA-256 hash)
- Unified diff computation
- `CheckpointSummary` for lightweight history browsing
- `JSONCheckpointStorage` with index.json
- `InMemoryCheckpointStorage` for testing

**What's missing for Wave 5:**
- `RollbackRegistry` class (orchestration layer)
- Integration with `PromptCompiler`
- Forward-rollback (time travel beyond simple restore)
- Tests

### M-gent Semantic Search (Reusable for Wave 4)

```python
# agents/m/crystal.py - Already supports semantic search
crystal = create_crystal(dimension=384, use_numpy=False)
matches = crystal.query(query_vector, top_k=10)

# agents/m/importers/markdown.py - L-gent embedder
embedder = create_lgent_embedder()  # sentence-transformers
embedding = embedder.embed(text)    # Returns 384-dim vector
```

**Can reuse for:**
- GitPatternAnalyzer: Embed commit messages, find clusters
- SessionPatternAnalyzer: Embed session summaries, find patterns
- TextGRAD: Embed feedback, find similar past improvements

---

## Part II: Open Questions Resolution

### Q1: Where are Claude Code session logs stored?

**Investigation needed.** Claude Code likely stores session logs in:

```bash
# Possible locations (to verify)
~/.claude/sessions/           # User-level session storage
~/.config/claude-code/        # XDG config dir
.claude/sessions/             # Project-level sessions
```

**De-risking action:**
1. Search for session storage documentation
2. Prototype `SessionPatternAnalyzer` with mock data first
3. Make session analysis optional (graceful degradation)

### Q2: Semantic Similarity Backend

**Decision:** Use M-gent's L-gent integration.

```python
# Already available via:
from agents.m.importers.markdown import create_lgent_embedder

# Fallback if sentence-transformers not installed:
# Hash-based embeddings (lower quality but zero dependencies)
```

**De-risking action:**
1. Create `HabitEncoder` with embedder injection
2. Test with both L-gent and hash fallback
3. Cache embeddings aggressively (semantic content rarely changes)

### Q3: Checkpoint Storage Format

**Already decided:** JSON files in `protocols/prompt/rollback/storage.py`

```
storage_path/
├── index.json          # Ordered list of checkpoint IDs
└── checkpoints/
    ├── abc123.json     # Individual checkpoint files
    └── def456.json
```

**No further de-risking needed.** Implementation exists.

### Q4: LLM Source Caching

**Design needed.** For Wave 4's `LLMSource` (inferred sections):

```python
@dataclass
class CachedLLMSource:
    """Cache inferred content with TTL."""

    cache_key: str          # Hash of (section_name, context_hash)
    content: str            # The inferred content
    generated_at: datetime  # When this was generated
    ttl_hours: float = 24   # Cache expiry
    reasoning_trace: str    # Why this was inferred

    def is_valid(self) -> bool:
        age = datetime.now() - self.generated_at
        return age.total_seconds() < self.ttl_hours * 3600
```

**De-risking action:**
1. Design cache invalidation triggers (file change, explicit refresh)
2. Consider storing in M-gent crystal for semantic deduplication
3. Add `--force-refresh` flag to compilation

### Q5: Spec Update Timing

**Decision:** Update spec **after** Wave 4 validates the architecture.

**Rationale:**
- Wave 3 tests soft sections concept
- Wave 4 tests habit encoding and TextGRAD
- If both succeed, update `spec/protocols/evergreen-prompt-system.md`
- If issues arise, iterate before formalizing

---

## Part III: Wave 4 De-Risking (Habit Encoder + TextGRAD)

### 3.1 GitPatternAnalyzer Prototype

**Risk:** Git history analysis complexity; what patterns are actually useful?

**Prototype Design:**

```python
from dataclasses import dataclass
from pathlib import Path
import subprocess

@dataclass
class GitPattern:
    """A detected pattern from git history."""
    pattern_type: str           # "commit_style", "file_focus", "timing"
    description: str            # Human-readable
    confidence: float           # 0.0-1.0
    evidence: tuple[str, ...]   # Supporting commits/files

@dataclass
class GitPatternAnalyzer:
    """Analyze git history for developer patterns."""

    repo_path: Path
    lookback_commits: int = 100

    async def analyze(self) -> list[GitPattern]:
        """Extract patterns from recent commits."""
        patterns = []

        # 1. Commit message style
        patterns.append(await self._analyze_commit_style())

        # 2. File change frequency (what areas get attention)
        patterns.append(await self._analyze_file_focus())

        # 3. Commit timing patterns
        patterns.append(await self._analyze_timing())

        return patterns

    async def _analyze_commit_style(self) -> GitPattern:
        """Analyze commit message conventions."""
        # Use: git log --oneline -100
        result = subprocess.run(
            ["git", "log", "--oneline", f"-{self.lookback_commits}"],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
        )
        messages = result.stdout.strip().split("\n")

        # Detect patterns:
        # - Conventional commits (feat:, fix:, etc.)
        # - Length preferences
        # - Emoji usage
        # - Imperative vs past tense

        # ... pattern detection logic ...

        return GitPattern(
            pattern_type="commit_style",
            description="Uses conventional commits with emoji",
            confidence=0.85,
            evidence=tuple(messages[:5]),
        )

    async def _analyze_file_focus(self) -> GitPattern:
        """Analyze which files get most attention."""
        # Use: git log --name-only --pretty=format: -100
        result = subprocess.run(
            ["git", "log", "--name-only", "--pretty=format:", f"-{self.lookback_commits}"],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
        )

        # Count file frequencies, find hot paths
        # ...

        return GitPattern(
            pattern_type="file_focus",
            description="Focus on impl/claude/protocols/",
            confidence=0.90,
            evidence=("protocols/agentese/", "protocols/prompt/"),
        )
```

**Test Plan:**
1. Run on kgents repo itself
2. Verify patterns match known developer preferences
3. Check performance (< 1s for 100 commits)

### 3.2 PolicyVector Design

**Risk:** What dimensions should the policy vector capture?

**Proposed Dimensions:**

```python
@dataclass(frozen=True)
class PolicyVector:
    """Learned preferences that influence prompt compilation."""

    # Style preferences (0.0 = terse, 1.0 = verbose)
    verbosity: float = 0.5

    # Section priorities (higher = more important)
    section_weights: dict[str, float] = field(default_factory=dict)
    # e.g., {"principles": 1.0, "skills": 0.8, "forest": 0.6}

    # Focus areas (which domains get attention)
    domain_focus: dict[str, float] = field(default_factory=dict)
    # e.g., {"agentese": 0.9, "cli": 0.7, "web": 0.3}

    # Formality (0.0 = casual, 1.0 = formal)
    formality: float = 0.6

    # Risk tolerance (0.0 = conservative, 1.0 = experimental)
    risk_tolerance: float = 0.4

    # Provenance
    learned_from: tuple[str, ...] = ()  # ["git", "sessions", "code"]
    confidence: float = 0.5
    reasoning_trace: tuple[str, ...] = ()

    def merge_with(self, other: "PolicyVector", weight: float = 0.5) -> "PolicyVector":
        """Heuristic merge of two policy vectors."""
        # Per taste decision: merge heuristically, not hard precedence
        return PolicyVector(
            verbosity=self.verbosity * (1 - weight) + other.verbosity * weight,
            section_weights={
                k: self.section_weights.get(k, 0.5) * (1 - weight) +
                   other.section_weights.get(k, 0.5) * weight
                for k in set(self.section_weights) | set(other.section_weights)
            },
            # ... merge other fields ...
        )
```

**De-risking action:**
1. Start with 5-7 dimensions, not too many
2. Make each dimension interpretable
3. Store policy in M-gent crystal for persistence

### 3.3 TextGRAD Feedback Parser

**Risk:** Parsing natural language feedback into actionable improvements.

**Simplified Approach:**

```python
@dataclass
class FeedbackTarget:
    """A section targeted by feedback."""
    section_name: str
    feedback_type: str      # "add", "remove", "modify", "emphasize"
    specifics: str          # What to change
    confidence: float       # How sure we are about interpretation

async def parse_feedback(feedback: str, prompt: CompiledPrompt) -> list[FeedbackTarget]:
    """
    Parse natural language feedback into targets.

    Uses keyword matching + section name detection.
    Falls back to LLM parsing for complex feedback.
    """
    targets = []
    feedback_lower = feedback.lower()

    # Simple keyword matching first
    section_names = {s.name for s in prompt.sections}

    # Detect mentioned sections
    for section in section_names:
        if section in feedback_lower:
            # Determine feedback type
            if any(kw in feedback_lower for kw in ["add", "include", "more"]):
                fb_type = "add"
            elif any(kw in feedback_lower for kw in ["remove", "delete", "less"]):
                fb_type = "remove"
            elif any(kw in feedback_lower for kw in ["change", "update", "modify"]):
                fb_type = "modify"
            else:
                fb_type = "emphasize"

            targets.append(FeedbackTarget(
                section_name=section,
                feedback_type=fb_type,
                specifics=feedback,  # Pass full feedback to improver
                confidence=0.7,
            ))

    # If no sections detected, use LLM for interpretation
    if not targets:
        targets = await _llm_parse_feedback(feedback, prompt)

    return targets
```

**De-risking action:**
1. Prototype with simple keyword matching
2. Add LLM fallback only when needed
3. Log all feedback → target mappings for learning

---

## Part IV: Wave 5 De-Risking (Multi-Source Fusion + Rollback)

### 4.1 RollbackRegistry (Build on Existing)

**Existing:** `protocols/prompt/rollback/checkpoint.py`, `storage.py`

**Missing:** Registry orchestration

```python
# protocols/prompt/rollback/registry.py (NEW)

from .checkpoint import Checkpoint, CheckpointId
from .storage import CheckpointStorage, JSONCheckpointStorage

@dataclass
class RollbackRegistry:
    """
    Full history with instant rollback capability.

    Wraps CheckpointStorage with higher-level operations.
    """

    storage: CheckpointStorage

    @classmethod
    def create(cls, storage_path: Path) -> "RollbackRegistry":
        """Factory with default JSON storage."""
        return cls(storage=JSONCheckpointStorage(storage_path))

    def checkpoint(
        self,
        before: CompiledPrompt,
        after: CompiledPrompt,
        reason: str,
    ) -> CheckpointId:
        """Save state before auto-change."""
        cp = Checkpoint.create(
            before_content=before.content,
            after_content=after.content,
            before_sections=tuple(s.name for s in before.sections),
            after_sections=tuple(s.name for s in after.sections),
            reason=reason,
            reasoning_traces=tuple(after.reasoning_traces),
            parent_id=self.storage.get_latest_id(),
        )
        self.storage.save(cp)
        return cp.id

    def rollback(self, checkpoint_id: CheckpointId) -> CompiledPrompt:
        """
        Restore to checkpoint.

        Does NOT delete forward history - you can roll forward again.
        """
        checkpoint = self.storage.load(checkpoint_id)
        if not checkpoint:
            raise ValueError(f"Checkpoint not found: {checkpoint_id}")

        # Create rollback checkpoint (records the rollback itself)
        current = self._get_current()
        if current:
            self.checkpoint(
                before=current,
                after=CompiledPrompt.from_content(checkpoint.before_content),
                reason=f"Rollback to {checkpoint_id[:8]}",
            )

        return CompiledPrompt.from_content(checkpoint.before_content)

    def history(self, limit: int = 20) -> list[CheckpointSummary]:
        """Show evolution history with diffs and reasoning."""
        return self.storage.list_summaries(limit)

    def diff(self, id1: CheckpointId, id2: CheckpointId) -> str:
        """Show diff between any two checkpoints."""
        cp1 = self.storage.load(id1)
        cp2 = self.storage.load(id2)
        if not cp1 or not cp2:
            raise ValueError("Checkpoint not found")
        return Checkpoint.compute_diff(cp1.after_content, cp2.after_content)
```

**De-risking action:**
1. Write tests for registry using InMemoryCheckpointStorage
2. Verify forward-history preservation
3. Test concurrent access patterns

### 4.2 PromptFusion Semantic Similarity

**Risk:** Semantic similarity computation cost and accuracy.

**Design:**

```python
from agents.m.importers.markdown import create_lgent_embedder

@dataclass
class PromptFusion:
    """Fuse multiple sources with heuristic conflict resolution."""

    embedder: Any = None  # L-gent embedder
    similarity_threshold: float = 0.9

    def __post_init__(self):
        if self.embedder is None:
            self.embedder = create_lgent_embedder()

    async def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute semantic similarity between two texts."""
        if self.embedder is None:
            # Fallback: character-level Jaccard similarity
            set1 = set(text1.split())
            set2 = set(text2.split())
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            return intersection / union if union > 0 else 0.0

        # L-gent embedding similarity
        emb1 = self.embedder.embed(text1)
        emb2 = self.embedder.embed(text2)
        return self._cosine_similarity(emb1, emb2)

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x ** 2 for x in a) ** 0.5
        norm_b = sum(x ** 2 for x in b) ** 0.5
        return dot / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0.0
```

**De-risking action:**
1. Benchmark similarity computation (target: <100ms per comparison)
2. Test accuracy on known similar/dissimilar section pairs
3. Tune threshold based on empirical results

---

## Part V: Wave 6 De-Risking (Living CLI)

### 5.1 CLI Handler Structure

**Pattern (from grow.py):**

```python
def cmd_prompt(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    /prompt: View and manage the compiled CLAUDE.md.
    """
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    subcommand = args[0].lower() if args else "show"

    match subcommand:
        case "show" | "":
            return _handle_show(args[1:], ctx)
        case "reasoning":
            return _handle_reasoning(args[1:], ctx)
        case "habits":
            return _handle_habits(args[1:], ctx)
        case "feedback":
            return _handle_feedback(args[1:], ctx)
        case "history":
            return _handle_history(args[1:], ctx)
        case "rollback":
            return _handle_rollback(args[1:], ctx)
        case "preview":
            return _handle_preview(args[1:], ctx)
        case "improve":
            return _handle_auto_improve(args[1:], ctx)
        case _:
            print(f"Unknown subcommand: {subcommand}")
            return 1
```

**De-risking action:**
1. Create stub handlers early
2. Wire up AGENTESE paths (`concept.prompt.*`)
3. Test with mock data before full integration

### 5.2 AGENTESE Path Registration

**Pattern (from existing contexts):**

```python
# protocols/agentese/contexts/prompt.py (NEW)

from protocols.agentese.node import LogosNode, aspect, AspectCategory, Effect

@logos.node("concept.prompt")
class PromptNode(LogosNode):
    """AGENTESE node for prompt system operations."""

    @aspect(AspectCategory.PERCEPTION)
    async def manifest(self, observer) -> str:
        """Return current compiled CLAUDE.md."""
        compiler = PromptCompiler()
        result = compiler.compile(CompilationContext.default())
        return result.content

    @aspect(AspectCategory.GENERATION, effects=[Effect.WRITES("prompt")])
    async def evolve(self, observer, proposal: str) -> dict:
        """Propose prompt evolution."""
        # Parse proposal, create improvement, checkpoint
        ...

    @aspect(AspectCategory.PERCEPTION)
    async def validate(self, observer) -> dict:
        """Run category law checks."""
        ...

    @aspect(AspectCategory.PERCEPTION)
    async def history(self, observer, limit: int = 20) -> list:
        """Show version history."""
        registry = RollbackRegistry.create(CHECKPOINT_PATH)
        return [str(s) for s in registry.history(limit)]
```

**De-risking action:**
1. Create minimal PromptNode with `manifest` only
2. Wire to CLI handler
3. Add other aspects incrementally

---

## Part VI: Integration Points with Wave 3

Wave 3 (SoftSection Protocol) will output:

| Output | Location | Wave 4+ Consumer |
|--------|----------|-----------------|
| `SoftSection` dataclass | `protocols/prompt/soft_section.py` | HabitsSection uses it |
| `SectionSource` abstraction | `protocols/prompt/sources/` | GitSource, SessionSource |
| `MergeStrategy` enum | `protocols/prompt/soft_section.py` | PromptFusion uses it |
| `reasoning_trace` field | On Section | TextGRAD reads/writes it |
| `ForestSection` | `protocols/prompt/sections/forest.py` | Used as-is |
| `ContextSection` | `protocols/prompt/sections/context.py` | Used as-is |

**Integration contract:**

```python
# Wave 4 expects this from Wave 3:
@dataclass(frozen=True)
class SoftSection:
    name: str
    rigidity: float  # 0.0-1.0
    sources: tuple[SectionSource, ...]
    merge_strategy: MergeStrategy
    reasoning_trace: tuple[str, ...]

    async def crystallize(self, context: CompilationContext) -> Section:
        """Convert soft section to hard section."""
        ...

# Wave 4 will add:
class HabitsSection(SectionCompiler):
    """Section that reads from PolicyVector."""

    def compile(self, context: CompilationContext) -> Section:
        policy = self.habit_encoder.encode()
        # Generate section content from policy
        ...
```

---

## Part VII: Prototyping Schedule

| Week | Focus | Deliverable |
|------|-------|-------------|
| 1 | GitPatternAnalyzer | Working prototype on kgents repo |
| 1 | PolicyVector | Dataclass + merge tests |
| 2 | RollbackRegistry | Complete Wave 5 foundation |
| 2 | FeedbackParser | Keyword matching + tests |
| 3 | CLI Stub | `cmd_prompt` with mock data |
| 3 | PromptNode | AGENTESE `concept.prompt.manifest` |
| 4 | Integration | Connect to Wave 3 outputs |

---

## Part VIII: Risk Matrix

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Session logs inaccessible | High | Medium | Make session analysis optional |
| Semantic similarity too slow | Medium | Low | Cache embeddings, use hash fallback |
| Git analysis complexity | Medium | Low | Start simple, iterate |
| TextGRAD produces bad changes | High | Medium | Always checkpoint, require approval |
| Wave 3 API changes | Medium | Medium | Define integration contract early |

---

## Part IX: Success Criteria

### De-Risking Complete When:

1. **GitPatternAnalyzer** runs successfully on kgents repo
2. **PolicyVector** has merge semantics tested
3. **RollbackRegistry** has 90%+ test coverage
4. **FeedbackParser** handles 5 common feedback patterns
5. **CLI stub** shows mock prompt with `--show-reasoning`
6. **PromptNode.manifest** returns compiled prompt via AGENTESE
7. **Integration contract** agreed with Wave 3 builder

### Tests to Write

```bash
# Add to protocols/prompt/_tests/

test_git_analyzer.py          # GitPatternAnalyzer prototype tests
test_policy_vector.py         # PolicyVector merge semantics
test_rollback_registry.py     # RollbackRegistry with InMemoryStorage
test_feedback_parser.py       # FeedbackParser keyword matching
test_prompt_cli.py            # CLI handler stub tests
test_prompt_node.py           # AGENTESE path tests
```

---

## Begin

To start de-risking, run:

```bash
# 1. Prototype GitPatternAnalyzer
cd impl/claude
python -c "from pathlib import Path; print(Path('.').resolve())"

# 2. Test existing rollback module
uv run python -m pytest protocols/prompt/rollback/ -v

# 3. Verify L-gent embedder availability
python -c "from agents.m.importers.markdown import create_lgent_embedder; print(create_lgent_embedder())"
```

---

## Part X: De-Risking Results (2025-12-16)

### Completed De-Risking Items

| Item | Status | Result |
|------|--------|--------|
| **GitPatternAnalyzer** | ✅ COMPLETE | 19 tests passing, works on kgents repo |
| **PolicyVector** | ✅ COMPLETE | Merge semantics tested, from_git_patterns works |
| **RollbackRegistry** | ✅ ALREADY DONE | 20 tests passing, full implementation exists |
| **L-gent Embedder** | ✅ VERIFIED | 384-dim sentence-transformer embeddings available |
| **Full Test Suite** | ✅ PASSING | 124 tests pass (including Wave 3 soft sections) |

### GitPatternAnalyzer on kgents Repo

```
commit_style: Uses conventional commits (avg 60 chars)
  - conventional_ratio: 1.00
  - emoji_ratio: 0.00

file_focus: Concentrated focus on impl/claude/ (68% of changes)
  - 2446 changes in impl/claude/
  - 262 unique directories touched

timing: Primarily afternoon (59%), includes weekend work
  - weekday_ratio: 0.35
```

### Derived PolicyVector for kgents

```python
PolicyVector(
    verbosity=0.50,     # Normal (avg commit length ~60 chars)
    formality=0.80,     # High (100% conventional commits)
    risk_tolerance=0.40,
    domain_focus={'claude': 1.0},  # Focus on impl/claude/
    confidence=0.76,
)
```

### Open Questions Resolved

| Question | Resolution |
|----------|------------|
| Session log storage | **Defer** - Make session analysis optional |
| Semantic similarity | **L-gent** - 384-dim embeddings, `create_lgent_embedder()` |
| Checkpoint storage | **JSON** - Already implemented in Wave 3 |
| LLM caching | **Design pending** - Add to Wave 4 |

### Ready for Wave 4

All critical de-risking is complete. Wave 4 can proceed with:

1. **HabitEncoder** - Use GitPatternAnalyzer (done) + PolicyVector (done)
2. **TextGRAD Improver** - Use L-gent embeddings for similarity (verified)
3. **PromptFusion** - Build on RollbackRegistry (done)

### Test Coverage Summary

```
protocols/prompt/_tests/
├── test_compiler.py        # 14 tests - Wave 1
├── test_polynomial.py      # 27 tests - Wave 1
├── test_dynamic_sections.py # 26 tests - Wave 2
├── test_habits.py          # 19 tests - Wave 4 de-risk ✨ NEW
├── test_rollback.py        # 20 tests - Wave 3/5
├── test_soft_section.py    # 18 tests - Wave 3
─────────────────────────────
Total: 124 tests passing
```

---

*"De-risk the hard parts first. What seems risky now will feel inevitable later."*

*De-Risking Plan v1.1 — 2025-12-16 (Results Added)*
