# 5-Part CLI Integration Plan

**Created**: 2025-12-09
**Status**: Planning (Revised after UX critique)
**Author**: Claude Code session

---

## Overview

This plan outlines a comprehensive approach to integrating all kgents agents and features through the CLI. The goal is to surface the rich agent infrastructure (18 genera, 7 bootstrap primitives, multiple protocols) through **intuitive, intent-based commands**.

### Design Philosophy: Intent Over Implementation

> "The best interface is no interface—until you need one. Then the best interface is one that teaches you how to eventually not need it."
> — spec/protocols/cli.md

**Key Insight**: Users think in **verbs** ("I need to test this"), not in taxonomies ("I need a T-gent"). The CLI should map user intent to agent capabilities, not expose implementation structure.

This plan adopts a **dual-layer architecture**:
1. **Intent Layer** (user-facing): Simple, memorable verbs
2. **Genus Layer** (power-user): Full taxonomy access for precision

### Current State

- **~30 existing CLI commands** (Mirror, Membrane, Daily Companions, Scientific Core)
- **18 agent genera implemented** but NOT CLI-integrated
- **7 bootstrap primitives** NOT CLI-integrated

### Target State

- **~40 intent-based commands** (primary surface)
- **~80+ genus commands** (power-user access)
- **Flowfile-based composition** (config-as-code)
- **TUI dashboard** for complex agent orchestration
- **Bidirectional MCP** (client AND server)

---

## Critical UX Decisions

### The Cognitive Load Problem

**Original Risk**: Mapping CLI 1:1 with internal architecture (18 genera) creates high learning curve.

**Solution**: Two-tier command structure:

```
┌─────────────────────────────────────────────────────────────┐
│                    INTENT LAYER (Primary)                    │
│  kgents new, run, check, think, watch, flow                 │
│  Users learn ~10 verbs, not 18 genera                       │
├─────────────────────────────────────────────────────────────┤
│                    GENUS LAYER (Power-User)                  │
│  kgents grammar reify, kgents compose verify, etc.          │
│  Full taxonomy access for precision operations              │
└─────────────────────────────────────────────────────────────┘
```

### Intent-to-Genus Mapping

| Intent Command | Maps To | Genus |
|----------------|---------|-------|
| `kgents new <name>` | `kgents abstract scaffold` | A-gent |
| `kgents run "<intent>"` | `kgents jit compile` | J-gent |
| `kgents check <target>` | `kgents test verify` + `kgents jit classify` | T/J-gent |
| `kgents think "<topic>"` | `kgents bio hypothesize` | B-gent |
| `kgents watch <target>` | `kgents witness watch` | W-gent |
| `kgents flow <file>` | `kgents compose run` | C-gent |
| `kgents find "<query>"` | `kgents library discover` | L-gent |
| `kgents fix <target>` | `kgents parse repair` | P-gent |
| `kgents speak "<domain>"` | `kgents grammar reify` | G-gent |
| `kgents judge "<input>"` | `kgents bootstrap judge` | Bootstrap |

### String Composition is an Antipattern

**Original Risk**: `kgents compose chain "<a> >> <b> >> <c>"` breaks shell completion, escaping, visibility.

**Solution**: **Flowfiles** (declarative YAML):

```yaml
# review.flow.yaml
name: "Code Review Pipeline"
description: "Parse, judge, and refine code"

steps:
  - id: parse
    genus: P-gent
    operation: extract
    args:
      strategy: anchor

  - id: judge
    genus: Bootstrap
    operation: judge
    input: "from:parse"
    args:
      principles: "./principles.md"

  - id: refine
    genus: R-gent
    operation: optimize
    input: "from:judge"
    condition: "judge.verdict != 'APPROVED'"

on_error:
  strategy: halt  # or: continue, retry
  notify: true
```

**Commands**:
```bash
kgents flow run review.flow.yaml input.py    # Execute flowfile
kgents flow validate review.flow.yaml        # Check flowfile syntax
kgents flow explain review.flow.yaml         # Show what it will do
kgents flow new "parse then judge"           # Generate flowfile from intent
```

### Daemon Management

**Original Risk**: Building process manager in Python is dangerous.

**Solution**: Delegate to standard tools:

```bash
kgents daemon export <agent> --format=supervisord  # Export config
kgents daemon export <agent> --format=systemd      # Export unit file
kgents daemon export <agent> --format=launchd      # macOS plist
kgents daemon export <agent> --format=docker       # Dockerfile

# Simple foreground mode for development
kgents daemon run <agent> --foreground
```

---

## Part 1: Intent Layer (Primary Surface)

**Philosophy**: These are the commands users learn first. Each maps to common intents.

### Core Intent Commands (~300 lines, 15 tests)

```bash
# Creation
kgents new <name> [--template=<type>]     # Create new agent/tongue/flow
kgents speak "<domain>" [--constraints]    # Create domain language (Tongue)

# Execution
kgents run "<intent>" [--budget=<level>]   # JIT compile and execute
kgents flow <file.yaml> [input]            # Run flowfile pipeline
kgents do "<natural language>"             # Intent router (see below)

# Verification
kgents check <target>                      # Verify target (code, agent, flow)
kgents judge "<input>"                     # 7-principles evaluation
kgents laws [--agent=<id>]                 # Verify category laws

# Discovery
kgents find "<query>"                      # Search catalog
kgents think "<topic>"                     # Generate hypotheses
kgents explain <id>                        # Explain how something works

# Observation
kgents watch <target>                      # Non-judgmental observation
kgents status                              # System health summary
kgents history [--limit=N]                 # Operation history

# Repair
kgents fix <target>                        # Attempt to repair
kgents evolve <target> [--generations=N]   # Evolutionary improvement
```

### The Intent Router: `kgents do`

For complex, multi-step intents, a lightweight router dispatches to the correct flow:

```bash
kgents do "take input.py, check it against the laws, and fix any issues"

# Router output:
# > Detected Intent: Check + Fix
# > Generated Flow:
# >   1. kgents check input.py
# >   2. kgents fix input.py (if issues found)
# > Execute? [Y/n]
```

**Implementation**: Uses Haiku/Flash for fast intent classification, maps to flowfile, confirms before execution.

**Principle Alignment**: Joy-Inducing (natural language), Ethical (confirmation before action), Composable (generates flows).

---

## Part 2: Genus Layer (Power-User Access)

**Philosophy**: Full taxonomy access for users who need precision. Namespaced by genus letter/name.

### Genus Commands (~1500 lines, 80 tests)

```bash
# A-gents: Abstract Architecture
kgents abstract scaffold <name>
kgents abstract coach [--mode=playful|philosophical|provocative]

# B-gents: Bio/Scientific
kgents bio hypothesize "<observation>"
kgents bio robin "<question>"              # Scientific companion

# C-gents: Composition
kgents compose verify <pipeline>           # Verify laws hold
kgents compose parallel <agents...>        # Fan-out execution
kgents compose inspect <name>              # Show structure

# D-gents: Data/State
kgents data persist <key> <value>
kgents data snapshot [--name=<id>]
kgents data lens <path>

# E-gents: Evolution
kgents evolve iterate <agent> [--generations=N]
kgents evolve synthesize "<intent>"
kgents evolve safety-check <code>

# F-gents: Forge
kgents forge create "<contract>"
kgents forge prototype "<intent>"
kgents forge crystallize <agent>

# G-gents: Grammar/DSL
kgents grammar reify "<domain>" [--level=schema|command|recursive]
kgents grammar parse "<input>" --tongue=<name>
kgents grammar evolve <tongue> --examples=<path>

# J-gents: JIT
kgents jit compile "<intent>" [--budget=<level>]
kgents jit classify "<code>"               # Reality: D/P/C
kgents jit defer <operation>

# K-gents: Kent Persona
kgents persona configure [--warmth=<0-1>] [--formality=<0-1>]
kgents persona lift <agent>
kgents persona project "<context>"

# L-gents: Library/Catalog
kgents library catalog [--type=<entity>]
kgents library discover "<query>"
kgents library register <path>

# P-gents: Parser
kgents parse extract <input> [--strategy=anchor|incremental|stack]
kgents parse repair <malformed>
kgents parse validate <output> --schema=<path>

# R-gents: Refine
kgents refine optimize <agent> [--strategy=mipro|bootstrap]
kgents refine drift-check <agent>
kgents refine transfer <source> <target>

# T-gents: Test/Tools
kgents test verify <agent>
kgents test fuzz <agent> [--iterations=N]
kgents tool list
kgents tool register <tool>

# W-gents: Witness
kgents witness watch <target>
kgents witness fidelity <output>
kgents witness sample <stream> [--rate=<n>]
```

**Note**: Intent commands are aliases that route to these genus commands internally.

---

## Part 3: Flowfiles & Composition

**Philosophy**: Complex pipelines defined declaratively, not in shell strings.

### Flowfile Specification

```yaml
# flow.kgents.yaml
version: "1.0"
name: "Pipeline Name"
description: "What this pipeline does"

# Input schema (optional, for validation)
input:
  type: file
  extensions: [.py, .js, .ts]

# Environment/context
context:
  principles: "./spec/principles.md"
  budget: medium

# Pipeline steps
steps:
  - id: step_name
    genus: <genus-name>           # e.g., P-gent, J-gent, Bootstrap
    operation: <operation>        # e.g., extract, compile, judge
    input: "from:<step_id>"       # Reference previous step output
    args:                         # Operation-specific arguments
      key: value
    condition: "<expression>"     # Optional: skip if false
    on_error: continue|halt|retry

# Output handling
output:
  format: json|yaml|rich
  save_to: "./output/"

# Hooks
hooks:
  pre: "./scripts/pre-hook.sh"
  post: "./scripts/post-hook.sh"
```

### Flow Commands (~400 lines, 20 tests)

```bash
# Core flow operations
kgents flow run <file.yaml> [input]        # Execute flowfile
kgents flow validate <file.yaml>           # Syntax + reference check
kgents flow explain <file.yaml>            # Show execution plan
kgents flow visualize <file.yaml>          # ASCII graph of pipeline

# Flow generation
kgents flow new "<intent>"                 # Generate from natural language
kgents flow from-history <session-id>      # Extract flow from session
kgents flow export <name> --format=yaml    # Export named pipeline

# Flow registry
kgents flow list                           # List saved flows
kgents flow save <file.yaml> --name=<id>   # Save to registry
kgents flow delete <name>                  # Remove from registry
```

### Session Management (~200 lines, 10 tests)

```bash
kgents session start --name=<id>           # Start persistent session
kgents session list                        # Show active sessions
kgents session attach <id>                 # Attach to session
kgents session end <id>                    # End and clean up
kgents session export <id> --format=flow   # Export as flowfile
```

---

## Part 4: Dashboard TUI

**Philosophy**: Agents are asynchronous and verbose. A linear CLI cannot show parallel agent activity.

### The Cockpit Mode

```bash
kgents dash                                # Launch TUI dashboard
kgents dash --flow=<file.yaml>             # Launch with flow visualization
```

**Layout** (using Textual):

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
│ > _                                                             │
└─────────────────────────────────────────────────────────────────┘
```

**Features**:
- Left pane: Agent/step status (from flowfile)
- Center: Live thought stream (logs, reasoning)
- Right: Artifacts being generated
- Bottom: Command input (can inject commands mid-flow)

**Principle Alignment**: Joy-Inducing (visual delight), Heterarchical (observe autonomous agents), Ethical (transparency of agent reasoning).

---

## Part 5: MCP Bidirectional Integration

**Philosophy**: kgents should be both MCP client AND server.

### As MCP Client

```bash
kgents mcp connect <server>                # Connect to external server
kgents mcp list                            # List connections
kgents mcp tools                           # List available tools
kgents mcp invoke <tool> [args...]         # Call external tool
```

### As MCP Server

```bash
kgents mcp serve [--port=8080]             # Start as MCP server
kgents mcp expose <command>                # Expose command as MCP tool
kgents mcp export --format=mcp-manifest    # Export tool manifest
```

**Use Case**: Claude Desktop, Cursor, or Windsurf can connect to kgents as an MCP server:

```
User in Cursor: "@kgents please verify this code using the 7 laws"
→ Cursor hits kgents MCP server
→ kgents runs `kgents judge <code>`
→ Result returned to Cursor
```

**Exposed Tools** (auto-generated from intent layer):
- `kgents_check` - Verify code/agent/flow
- `kgents_judge` - 7-principles evaluation
- `kgents_think` - Generate hypotheses
- `kgents_fix` - Repair code
- `kgents_speak` - Create domain language

---

## Part 6: Bootstrap & Identity

**Philosophy**: The foundation that all other commands build upon.

### Bootstrap Commands (~300 lines, 15 tests)

```bash
# Laws and verification
kgents laws                                # Display the 7 laws
kgents laws verify [--agent=<id>]          # Verify category laws hold
kgents laws witness <operation>            # Witness composition

# Principles and identity
kgents principles                          # Display 7 principles
kgents principles check "<input>"          # Evaluate against principles

# Meta operations
kgents meta health                         # System health check
kgents meta graph [--genus=<letter>]       # Dependency graph
kgents meta accursed                       # Exploration budget status
kgents meta derive <target>                # Derive impl from spec
```

---

## Implementation Priority (Revised)

| Phase | Focus | Est. Lines | Est. Tests | Key Deliverables |
|-------|-------|-----------|------------|------------------|
| 1 | Intent Layer | 500 | 25 | `new`, `run`, `check`, `find`, `watch` |
| 2 | Flowfiles | 600 | 30 | Flow spec, `flow run`, `flow new` |
| 3 | Bootstrap | 300 | 15 | `laws`, `principles`, `judge` |
| 4 | Genus Layer (core) | 800 | 40 | G, J, P, L, W genus commands |
| 5 | Dashboard TUI | 600 | 20 | `dash` with Textual |
| 6 | MCP Server | 400 | 20 | `mcp serve`, tool exposure |
| 7 | Genus Layer (rest) | 800 | 50 | B, C, D, E, F, K, R, T commands |

**Total**: ~4000 lines, ~200 tests

---

## Design Principles Applied (Revised)

| Principle | Original Plan | After Critique |
|-----------|--------------|----------------|
| **Tasteful** | Each command justified | Intent layer reduces surface area |
| **Curated** | Genus-based selection | Intent-first, genus for power users |
| **Ethical** | Sanctuary commands | + Confirmation for `kgents do` |
| **Joy-Inducing** | `--explain` flag | + TUI dashboard, natural language |
| **Composable** | String pipelines | Flowfiles (config-as-code) |
| **Heterarchical** | Daemon mode | Delegate to supervisord/systemd |
| **Generative** | `bootstrap derive` | + `flow new` from intent |

---

## Anti-Patterns Addressed

| Anti-Pattern | Solution |
|--------------|----------|
| "18 Genera" cognitive load | Intent layer with ~10 core verbs |
| String-based composition | Flowfiles (YAML) |
| Python daemon management | Export to supervisord/systemd |
| MCP client only | Bidirectional (client + server) |
| Linear CLI for async agents | TUI dashboard mode |

---

## See Also

- `spec/protocols/cli.md` - CLI meta-architecture specification
- `spec/principles.md` - The 7 design principles
- `impl/claude/protocols/cli/main.py` - Current CLI implementation
