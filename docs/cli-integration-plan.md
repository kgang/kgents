# The Conscious Shell: CLI Integration Plan v2.0

**Created**: 2025-12-09
**Status**: Ready for Implementation
**Philosophy**: Intent Over Implementation, Love in Error Messages, The CLI as Platform

---

## Design Philosophy

### The Fundamental Truths

1. **Users think in verbs**, not taxonomies. "I need to test this" → not "I need a T-gent."
2. **Speed is trust**. A CLI that takes 2 seconds to start has already failed.
3. **Error messages are care made visible**. A tool that loves you catches you when you fall.
4. **Composition belongs in files**, not shell strings. YAML > `"a >> b >> c"`.
5. **Context awareness is memory**. Repeatedly typing the same paths is disrespect.

### The Bootstrap Phases (from Cyborg Cognition)

The CLI must support **phase transitions** in human-AI collaboration:

```
Phase 0: GROUND        Phase 1: OBSERVER      Phase 2: SYNTHESIZER   Phase 3: CHOREOGRAPHER
│                      │                      │                      │
│ Human provides       │ System observes      │ System proposes      │ System orchestrates
│ all decisions        │ patterns, suggests   │ novel combinations   │ multi-agent swarms
│                      │                      │                      │
│ CLI: Manual          │ CLI: Suggestive      │ CLI: Collaborative   │ CLI: Autonomous
└──────────────────────┴──────────────────────┴──────────────────────┘
    Time / Competence / Trust
```

### Dual-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    INTENT LAYER (Primary)                    │
│  kgents new, run, check, think, watch, find, fix, speak     │
│  Users learn ~10 verbs, not 18 genera                       │
├─────────────────────────────────────────────────────────────┤
│                    GENUS LAYER (Power-User)                  │
│  kgents grammar reify, kgents jit classify, etc.            │
│  Full taxonomy access for precision operations              │
└─────────────────────────────────────────────────────────────┘
```

---

## Part 1: The Hollow Shell (Performance Foundation)

### The Cold Start Problem

A CLI wrapping 18 genera, LLM libraries, and vector DBs cannot import everything upfront.
If `kgents --help` takes 2 seconds, the illusion of "no interface" breaks.

### Solution: Lazy Loading Architecture

**The main entry point (`main.py`) must be a "Hollow Shell"—zero heavy imports.**

```python
# main.py - The Hollow Shell (< 50ms startup)
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Only for type hints, never executed at runtime
    from .intent import IntentRouter
    from .flow import FlowRunner

# Command registry: Maps commands to module paths (not imports)
COMMAND_REGISTRY = {
    # Intent Layer
    'new': 'protocols.cli.intent.commands:cmd_new',
    'run': 'protocols.cli.intent.commands:cmd_run',
    'check': 'protocols.cli.intent.commands:cmd_check',
    'think': 'protocols.cli.intent.commands:cmd_think',
    'watch': 'protocols.cli.intent.commands:cmd_watch',
    'find': 'protocols.cli.intent.commands:cmd_find',
    'fix': 'protocols.cli.intent.commands:cmd_fix',
    'speak': 'protocols.cli.intent.commands:cmd_speak',
    'judge': 'protocols.cli.intent.commands:cmd_judge',
    'do': 'protocols.cli.intent.router:cmd_do',

    # Flow commands
    'flow': 'protocols.cli.flow.commands:cmd_flow',

    # Bootstrap commands
    'laws': 'protocols.cli.bootstrap.laws:cmd_laws',
    'principles': 'protocols.cli.bootstrap.principles:cmd_principles',

    # Genus Layer (lazy-loaded subcommands)
    'grammar': 'protocols.cli.genus.g_gent:cmd_grammar',
    'jit': 'protocols.cli.genus.j_gent:cmd_jit',
    'parse': 'protocols.cli.genus.p_gent:cmd_parse',
    'library': 'protocols.cli.genus.l_gent:cmd_library',
    'witness': 'protocols.cli.genus.w_gent:cmd_witness',
    # ... more genera
}

def resolve_command(name: str):
    """Resolve command name to callable, importing only when needed."""
    if name not in COMMAND_REGISTRY:
        return None

    module_path, func_name = COMMAND_REGISTRY[name].rsplit(':', 1)
    module = importlib.import_module(module_path)
    return getattr(module, func_name)

def main():
    """Entry point - fast argument parsing, lazy command resolution."""
    if len(sys.argv) < 2:
        print_help()  # Lightweight, no heavy imports
        return 0

    command = sys.argv[1]
    handler = resolve_command(command)

    if handler is None:
        suggest_similar(command)  # Fuzzy matching
        return 1

    return handler(sys.argv[2:])
```

**Guarantee**: `kgents --help` completes in < 50ms.

### Context Awareness: The `.kgents` Directory

**The Problem**: Repeatedly typing `kgents check src/main.py` is tiresome.

**The Solution**: Workspace context system (like git).

```bash
kgents init                    # Creates .kgents/config.yaml
kgents check                   # Uses context from .kgents
kgents check --target=src/     # Override context
```

**`.kgents/config.yaml`**:
```yaml
version: "1.0"
project:
  name: "my-project"
  root: "."

defaults:
  target: "src/"
  principles: "spec/principles.md"
  budget: "medium"
  output: "rich"  # or json, yaml

registry:
  path: ".kgents/catalog.json"

history:
  enabled: true
  path: ".kgents/history.db"
  retention: "30d"
```

---

## Part 2: Intent Layer Commands

### The 10 Core Verbs

| Command | Intent | Maps To | Example |
|---------|--------|---------|---------|
| `kgents new <name>` | Create something | A-gent scaffold | `kgents new agent "Archimedes"` |
| `kgents run "<intent>"` | Execute intent | J-gent JIT compile | `kgents run "test all functions"` |
| `kgents check <target>` | Verify target | T/J-gent verify | `kgents check src/main.py` |
| `kgents think "<topic>"` | Generate ideas | B-gent hypothesize | `kgents think "optimization strategies"` |
| `kgents watch <target>` | Observe without judging | W-gent witness | `kgents watch ./logs/` |
| `kgents find "<query>"` | Search catalog | L-gent discover | `kgents find "calendar operations"` |
| `kgents fix <target>` | Repair malformed | P-gent repair | `kgents fix input.json` |
| `kgents speak "<domain>"` | Create DSL (Tongue) | G-gent reify | `kgents speak "file operations"` |
| `kgents judge "<input>"` | Evaluate principles | Bootstrap judge | `kgents judge proposal.md` |
| `kgents do "<natural>"` | Intent router | Haiku classifier | `kgents do "check and fix"` |

### The Intent Router: `kgents do`

For complex, multi-step intents, a lightweight router dispatches to the correct flow.

```bash
$ kgents do "take input.py, check it against the laws, and fix any issues"

╭─ Intent Detected ─────────────────────────────────────────────╮
│ Category: Verification + Repair                                │
│ Confidence: 0.92                                               │
│                                                                 │
│ Generated Flow:                                                 │
│   1. kgents check input.py                                     │
│   2. kgents fix input.py (if issues found)                     │
╰─────────────────────────────────────────────────────────────────╯

Execute? [Y/n]
```

**Safety: Dry-Run by Design**

Any command generated by `kgents do` that implies mutation must default to a "Plan View" first.

```bash
$ kgents do "clean up the temp folder"

╭─ Intent Detected ─────────────────────────────────────────────╮
│ Category: File System / Delete                                 │
│ Risk Level: ELEVATED                                           │
│                                                                 │
│ Plan:                                                          │
│   - rm ./temp/*.tmp (3 files)                                  │
│   - rm ./temp/cache.lock                                       │
│                                                                 │
│ ⚠ Destructive operation detected. Review carefully.           │
╰─────────────────────────────────────────────────────────────────╯

Execute? [y/N]  ← Note: default is NO for destructive ops
```

---

## Part 3: The Sympathetic Error System

### Philosophy: Love in Error Messages

A tool that loves you doesn't just fail; it catches you.

**Bad**:
```
KeyError: 'principles' not found in dict at line 47
```

**Good**:
```
╭─ Error at step [judge] ─────────────────────────────────────────╮
│                                                                  │
│ The flow failed because the input is missing the 'principles'   │
│ key that the judge step expects.                                │
│                                                                  │
│ ┌─ Context ────────────────────────────────────────────────────┐ │
│ │ File: input.json                                             │ │
│ │ Step: judge (2 of 3)                                         │ │
│ │ Expected: {"principles": [...], ...}                         │ │
│ │ Got: {"data": [...]}                                         │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ Suggestions:                                                     │
│   → kgents fix input.json                                        │
│   → Check your flowfile schema at line 12                        │
│                                                                  │
│ [Run diagnostic? Y/n]                                            │
╰──────────────────────────────────────────────────────────────────╯
```

### Implementation: The Sympathetic Panic Handler

```python
class SympatheticPanic:
    """Catch unhandled exceptions and transform them into care."""

    def __init__(self, p_gent: Optional[PGent] = None):
        self.parser = p_gent or LightweightErrorParser()

    def handle(self, exc: Exception, context: ExecutionContext) -> ErrorReport:
        """Transform raw exception into sympathetic error report."""

        # Analyze the error
        analysis = self.parser.analyze_error(exc)

        # Generate suggestions
        suggestions = self._generate_suggestions(analysis, context)

        # Build the report
        return ErrorReport(
            title=f"Error at step [{context.current_step}]",
            explanation=analysis.human_explanation,
            context=self._build_context_box(analysis, context),
            suggestions=suggestions,
            offer_diagnostic=analysis.is_diagnosable
        )

    def _generate_suggestions(self, analysis, context) -> list[str]:
        """Generate actionable suggestions based on error type."""
        suggestions = []

        if analysis.error_type == ErrorType.MISSING_KEY:
            suggestions.append(f"kgents fix {context.input_file}")

        if analysis.error_type == ErrorType.SCHEMA_MISMATCH:
            suggestions.append(f"Check your flowfile schema at line {analysis.line_number}")

        if analysis.error_type == ErrorType.MISSING_DEPENDENCY:
            suggestions.append(f"pip install {analysis.missing_package}")

        return suggestions
```

### The Epilogue System

After a successful command, don't just exit. Offer the logical next step.

```bash
$ kgents new agent "Archimedes"
✓ Created agent scaffold at ./agents/archimedes/

╭─ Next Steps ────────────────────────────────────────────────────╮
│                                                                  │
│ Your new agent is ready. You might want to:                     │
│                                                                  │
│   kgents speak "physics" --for=archimedes                       │
│   kgents jit compile "test buoyancy"                            │
│   kgents check ./agents/archimedes/                             │
│                                                                  │
╰──────────────────────────────────────────────────────────────────╯
```

---

## Part 4: Flowfiles (The Composition Backbone)

### Why Flowfiles?

**String composition is an antipattern**:
- `kgents compose chain "a >> b >> c"` breaks shell completion, escaping, visibility.

**Flowfiles are config-as-code**:
- Version controlled
- IDE-aware (YAML schema support)
- Testable
- Composable

### Flowfile Specification

```yaml
# review.flow.yaml
version: "1.0"
name: "Code Review Pipeline"
description: "Parse, judge, and refine code"

# Input schema (for validation)
input:
  type: file
  extensions: [.py, .js, .ts]

# Variables (Jinja2 templated)
variables:
  strictness: "{{ strictness | default('high') }}"
  principles_path: "{{ principles | default('spec/principles.md') }}"

# Pipeline steps
steps:
  - id: parse
    genus: P-gent
    operation: extract
    args:
      strategy: anchor
    debug: true  # Snapshot state for TUI inspection

  - id: judge
    genus: Bootstrap
    operation: judge
    input: "from:parse"
    args:
      principles: "{{ principles_path }}"
      strictness: "{{ strictness }}"

  - id: refine
    genus: R-gent
    operation: optimize
    input: "from:judge"
    condition: "judge.verdict != 'APPROVED'"
    on_error: continue

# Output handling
output:
  format: rich  # or json, yaml
  save_to: ".kgents/artifacts/"

# Hooks
hooks:
  pre: "./scripts/pre-hook.sh"
  post: "./scripts/post-hook.sh"

# Error handling
on_error:
  strategy: halt  # or continue, retry
  notify: true
```

### Jinja2 Templating

Allow variables in flowfiles for reuse with variations:

```bash
kgents flow run review.flow.yaml input.py --var strictness=low
kgents flow run review.flow.yaml input.py --var principles=./custom.md
```

### Flow Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `flow run <file> [input]` | Execute flowfile | `kgents flow run review.yaml src/` |
| `flow validate <file>` | Syntax + reference check | `kgents flow validate review.yaml` |
| `flow explain <file>` | Show execution plan | `kgents flow explain review.yaml` |
| `flow visualize <file>` | ASCII graph of pipeline | `kgents flow visualize review.yaml` |
| `flow new "<intent>"` | Generate from natural language | `kgents flow new "parse then judge"` |
| `flow from-history <id>` | Extract flow from session | `kgents flow from-history sess_abc123` |
| `flow list` | List saved flows | `kgents flow list` |
| `flow save <file> --name=<id>` | Save to registry | `kgents flow save review.yaml --name=review` |

### The Debug/Snapshot Feature

Add `debug: true` or `snapshot: true` to any flow step to dump its state:

```yaml
steps:
  - id: parse
    genus: P-gent
    operation: extract
    debug: true  # Dumps to .kgents/debug/parse/
```

Inspect via dashboard:
```bash
kgents dash --flow=review.yaml  # Shows snapshots in TUI
```

---

## Part 5: Bootstrap & Foundation

### Laws Commands

```bash
kgents laws                          # Display the 7 category laws
kgents laws verify [--agent=<id>]    # Verify laws hold
kgents laws witness <operation>      # Witness a composition
```

### Principles Commands

```bash
kgents principles                    # Display the 7 design principles
kgents principles check "<input>"    # Evaluate against principles
```

### Meta Commands

```bash
kgents meta health                   # System health check
kgents meta graph [--genus=<letter>] # Dependency graph (ASCII art)
kgents meta accursed                 # Exploration budget status
kgents meta derive <target>          # Derive impl from spec
```

---

## Part 6: Genus Layer (Power-User Access)

Full taxonomy access for users who need precision. Namespaced by genus letter/name.

### Core Genera Commands

```bash
# G-gents: Grammar/DSL
kgents grammar reify "<domain>" [--level=schema|command|recursive]
kgents grammar parse "<input>" --tongue=<name>
kgents grammar evolve <tongue> --examples=<path>

# J-gents: JIT
kgents jit compile "<intent>" [--budget=<level>]
kgents jit classify "<code>"        # Reality: DETERMINISTIC/PROBABILISTIC/CHAOTIC
kgents jit defer <operation>

# P-gents: Parser
kgents parse extract <input> [--strategy=anchor|incremental|stack]
kgents parse repair <malformed>
kgents parse validate <output> --schema=<path>

# L-gents: Library/Catalog
kgents library catalog [--type=<entity>]
kgents library discover "<query>"
kgents library register <path>

# W-gents: Witness
kgents witness watch <target>
kgents witness fidelity <output>
kgents witness sample <stream> [--rate=<n>]
```

### Extended Genera Commands

```bash
# A-gents: Abstract Architecture
kgents abstract scaffold <name>
kgents abstract coach [--mode=playful|philosophical|provocative]

# B-gents: Bio/Scientific
kgents bio hypothesize "<observation>"
kgents bio robin "<question>"        # Scientific companion

# C-gents: Composition
kgents compose verify <pipeline>     # Verify laws hold
kgents compose parallel <agents...>  # Fan-out execution
kgents compose inspect <name>        # Show structure

# D-gents: Data/State
kgents data persist <key> <value>
kgents data snapshot [--name=<id>]
kgents data lens <path>

# T-gents: Test/Tools
kgents test verify <agent>
kgents test fuzz <agent> [--iterations=N]
kgents tool list
kgents tool register <tool>
```

---

## Part 7: TUI Dashboard (The Time Machine)

### Philosophy

Real-time logs are good, but agents are fast. By the time you see a mistake, it's gone.

**The TUI should not just be a monitor; it should be a DVR.**

### Launch Commands

```bash
kgents dash                          # Launch TUI dashboard
kgents dash --flow=<file.yaml>       # Launch with flow visualization
kgents dash --replay=<session-id>    # Replay historical session
```

### Layout (using Textual)

```
┌─────────────────────────────────────────────────────────────────┐
│ kgents dash                                    [budget: medium] │
├─────────────────┬───────────────────────────────┬───────────────┤
│ AGENTS          │ THOUGHT STREAM                │ ARTIFACTS     │
│                 │                               │               │
│ ● parse [done]  │ [parse] Extracting structure  │ output.json   │
│ ◐ judge [run]   │ [parse] Found 3 functions     │ report.md     │
│ ○ refine [wait] │ [judge] Evaluating principle  │               │
│                 │   1: TASTEFUL ✓               │               │
│                 │   2: CURATED ✓                │               │
│                 │   3: ETHICAL checking...      │               │
│                 │                               │               │
├─────────────────┴───────────────────────────────┴───────────────┤
│ > _                                              [◀ ▶ scrub]    │
└─────────────────────────────────────────────────────────────────┘
```

### Playback & Scrubbing

All events are logged to a local SQLite/DuckDB session file.

**Keybindings**:
- `←` / `→`: Rewind / fast-forward through thought stream
- `Space`: Pause live stream
- `Enter`: Execute command in context
- `s`: Take snapshot of current state
- `q`: Quit

### Session Persistence

```bash
kgents session start --name=<id>     # Start persistent session
kgents session list                  # Show active sessions
kgents session attach <id>           # Attach to session
kgents session end <id>              # End and clean up
kgents session export <id> --format=flow  # Export as flowfile
```

---

## Part 8: MCP Bidirectional Integration

### Philosophy

kgents should be both MCP **client** AND **server**.
This is the "Killer Feature" that makes this future-proof.

### As MCP Server (Priority: Do This Early!)

**Why Early?**: It allows Claude/Cursor to help you build the rest of the CLI.

```bash
kgents mcp serve [--port=8080]       # Start as MCP server
kgents mcp expose <command>          # Expose command as MCP tool
kgents mcp export --format=manifest  # Export tool manifest
```

**Exposed Tools** (auto-generated from intent layer):
- `kgents_check` - Verify code/agent/flow
- `kgents_judge` - 7-principles evaluation
- `kgents_think` - Generate hypotheses
- `kgents_fix` - Repair code
- `kgents_speak` - Create domain language
- `kgents_find` - Search catalog

**Use Case**:
```
User in Cursor: "@kgents please verify this code using the 7 laws"
→ Cursor hits kgents MCP server
→ kgents runs `kgents judge <code>`
→ Result returned to Cursor
```

### As MCP Client

```bash
kgents mcp connect <server>          # Connect to external server
kgents mcp list                      # List connections
kgents mcp tools                     # List available tools
kgents mcp invoke <tool> [args...]   # Call external tool
```

---

## Part 9: Aesthetic Details (Taste)

### Color Palette

| Purpose | Color | Meaning |
|---------|-------|---------|
| System/Meta | Dim Gray / Slate | Infrastructure, context |
| Success/Growth | Emerald / Forest | Completion, progress |
| Error | Amber | Warning (reserve Red for fatal) |
| Fatal | Crimson | Critical failure |
| Thought/Reasoning | Indigo / Violet | Mysterious, deep processing |
| User Input | Cyan | Active, awaiting |

### Spinners with Personality

Do not use generic spinners. Use text that reflects the specific genus active.

| Genus | Generic | Tasteful |
|-------|---------|----------|
| P-gent | `Parsing...` | `Untangling syntax knots...` |
| B-gent | `Thinking...` | `Formulating hypotheses...` |
| J-gent | `Compiling...` | `Crystallizing intent...` |
| W-gent | `Watching...` | `Observing without judgment...` |
| H-gent | `Processing...` | `Wrestling with contradictions...` |
| G-gent | `Generating...` | `Weaving a tongue...` |

---

## Implementation Roadmap (Breadth-First)

### Priority: Deliver value immediately, build interfaces early.

| Phase | Focus | Est. Lines | Est. Tests | Rationale |
|-------|-------|-----------|------------|-----------|
| **1** | **Hollow Shell + Context** | 400 | 20 | Establish CLI speed, args parsing, `.kgents` context |
| **2** | **Bootstrap & Laws** | 300 | 15 | System must judge itself before building itself |
| **3** | **Flow Engine (Core)** | 600 | 30 | Composition backbone replaces string pipelines |
| **4** | **MCP Server (Early!)** | 400 | 20 | **Crucial**: Enables Claude/Cursor to help build rest |
| **5** | **The Big 5 Genera** | 800 | 40 | J, P, A, G, T - core operations. Others can wait |
| **6** | **Intent Layer** | 500 | 25 | Now that genera exist, wire up the verbs |
| **7** | **TUI Dashboard** | 600 | 20 | The "Wow" factor |
| **8** | **Sympathetic Errors** | 300 | 15 | Polish: error handling, epilogues |

**Total**: ~3900 lines, ~185 tests

### Critical Path

```
Phase 1 (Hollow Shell) ─→ Phase 2 (Bootstrap) ─→ Phase 3 (Flow Engine)
        ↓
Phase 4 (MCP Server) ─→ [Use Claude/Cursor to accelerate...]
        ↓
Phase 5 (Big 5 Genera) ─→ Phase 6 (Intent Layer) ─→ Phase 7 (TUI)
        ↓
Phase 8 (Polish: Errors, Epilogues)
```

---

## Design Principles Applied

| Principle | Application |
|-----------|-------------|
| **Tasteful** | Intent layer reduces cognitive load from 18 genera to 10 verbs |
| **Curated** | Hollow Shell ensures only needed code is loaded |
| **Ethical** | Dry-run for destructive ops, confirmation for `kgents do` |
| **Joy-Inducing** | Sympathetic errors, epilogues, tasteful spinners |
| **Composable** | Flowfiles are the unit of composition, not strings |
| **Heterarchical** | Functional mode (invoke) + Autonomous mode (dash/watch) |
| **Generative** | `flow new` generates flows from intent, MCP exposes capability |

---

## Anti-Patterns Addressed

| Anti-Pattern | Solution |
|--------------|----------|
| "18 Genera" cognitive load | Intent layer with ~10 core verbs |
| Cold start importing everything | Hollow Shell with lazy loading |
| String-based composition | Flowfiles (YAML) |
| Generic error messages | Sympathetic Panic Handler |
| Forgetting context | `.kgents` workspace awareness |
| Linear CLI for async agents | TUI dashboard with playback |
| MCP client only | Bidirectional (client + server) |
| Generic spinners | Genus-specific personality text |

---

## Success Metrics

### Speed Metrics

| Metric | Target |
|--------|--------|
| `kgents --help` | < 50ms |
| Intent command startup | < 200ms |
| Flow validation | < 500ms |
| TUI launch | < 1s |

### UX Metrics

| Metric | Target |
|--------|--------|
| Error → Suggestion | > 80% of errors offer actionable suggestion |
| Epilogue helpfulness | > 70% of commands show relevant next step |
| Context recall | > 90% reduction in repeated path typing |

---

## See Also

- `spec/protocols/cli.md` - CLI meta-architecture specification
- `spec/principles.md` - The 7 design principles
- `impl/claude/protocols/cli/main.py` - Current CLI implementation
- `docs/cyborg_cognition_bootstrapping.md` - Bootstrap phase theory

---

*"The best interface is no interface—until you need one. Then the best interface is one that teaches you how to eventually not need it."*
