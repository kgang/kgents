# 5-Part CLI Integration Plan

**Created**: 2025-12-09
**Status**: Planning
**Author**: Claude Code session

---

## Overview

This plan outlines a comprehensive approach to integrating all kgents agents and features through the CLI. The goal is to surface the rich agent infrastructure (18 genera, 7 bootstrap primitives, multiple protocols) through intuitive, composable commands.

### Current State

- **~30 existing CLI commands** (Mirror, Membrane, Daily Companions, Scientific Core)
- **18 agent genera implemented** but NOT CLI-integrated (A, B, C, D, E, F, G, H, I, J, K, L, P, R, T, W)
- **7 bootstrap primitives** NOT CLI-integrated (Id, Compose, Judge, Ground, Contradict, Sublate, Fix)

### Target State

- **~80+ CLI commands** covering all agent genera
- **Full bootstrap integration** with law verification
- **Composition pipelines** definable and runnable from CLI
- **MCP integration** for external tool ecosystems
- **Interactive REPL mode** for exploratory use

---

## Part 1: Bootstrap & Foundation Commands (Tier 0 - Core Identity)

**Philosophy**: These commands expose the 7 bootstrap primitives and kgents' identity at the CLI level. They establish the foundation that all other commands build upon.

**New Commands** (~500 lines, 20 tests):

```bash
# Bootstrap Protocol namespace
kgents bootstrap verify [--agent=<id>]    # Verify category laws hold
kgents bootstrap derive <target>           # Derive impl from spec (generative)
kgents bootstrap witness <operation>       # Witness composition (W-gent)
kgents bootstrap laws                      # Show the 7 laws

# Identity/Meta namespace
kgents meta principles                     # Display 7 principles
kgents meta graph [--genus=<letter>]       # Agent dependency graph
kgents meta health                         # System health check
kgents meta accursed                       # Show exploration budget status

# Judge (from bootstrap)
kgents judge "<input>" [--principles=<path>]   # Run 7-principles value function
```

**Implementation Location**: `impl/claude/protocols/cli/bootstrap_cli.py`

**Key Integration Points**:
- `bootstrap.judge.Judge` → `kgents judge`
- `bootstrap.ground.Ground` → extends `kgents ground`
- `bootstrap.witness.BootstrapWitness` → `kgents bootstrap verify`

---

## Part 2: Agent Genus Commands (Tier 1 - The Alphabet)

**Philosophy**: Each agent genus (A-Z) gets a command namespace. This surfaces the rich agent infrastructure through intuitive verbs.

**New Commands** (~2000 lines, 100 tests):

```bash
# A-gents: Abstract Architecture
kgents abstract scaffold <name>            # Generate agent skeleton
kgents abstract coach [--mode=playful|philosophical|provocative]

# B-gents: Bio/Scientific
kgents bio hypothesize "<observation>"     # Generate testable hypothesis
kgents bio robin "<question>"              # Scientific companion (RobinAgent)

# C-gents: Composition
kgents compose chain "<a> >> <b> >> <c>"   # Define composition pipeline
kgents compose verify <pipeline>           # Verify laws hold
kgents compose parallel <agents...>        # Fan-out execution

# D-gents: Data/State
kgents data persist <key> <value>          # Store persistent data
kgents data snapshot [--name=<id>]         # Create state snapshot
kgents data lens <path>                    # Focus on nested state

# E-gents: Evolution
kgents evolve iterate <agent> [--generations=N]  # Evolutionary improvement
kgents evolve synthesize "<intent>"        # Generate variant from intent
kgents evolve safety-check <code>          # Run safety validators

# F-gents: Forge
kgents forge create "<contract>"           # Contract-driven code gen
kgents forge prototype "<intent>"          # Quick prototype from intent
kgents forge crystallize <agent>           # Lock down design

# G-gents: Grammar/DSL
kgents grammar reify "<domain>" [--constraints="..."]  # Create Tongue
kgents grammar parse "<input>" --tongue=<name>         # Parse with Tongue
kgents grammar evolve <tongue> --examples=<path>       # Refine grammar

# J-gents: JIT
kgents jit compile "<intent>" [--budget=<level>]  # Create ephemeral agent
kgents jit classify "<code>"               # Reality classification (D/P/C)
kgents jit defer <operation>               # Lazy Promise creation

# K-gents: Kent Persona
kgents persona configure [--warmth=<0-1>] [--formality=<0-1>]
kgents persona lift <agent>                # Apply K-gent transformation
kgents persona project "<context>"         # Generate Kent-style response

# L-gents: Library/Catalog
kgents library catalog                     # List registered agents
kgents library discover "<query>"          # Semantic agent search
kgents library register <agent>            # Register custom agent

# P-gents: Parser
kgents parse extract <input> [--strategy=anchor|incremental|stack]
kgents parse repair <malformed>            # Attempt to fix broken output
kgents parse validate <output> --schema=<path>

# R-gents: Refine
kgents refine optimize <agent> [--strategy=mipro|bootstrap]
kgents refine drift-check <agent>          # Check for prompt drift
kgents refine transfer <source> <target>   # Transfer learning

# T-gents: Test/Tools
kgents test verify <agent>                 # Run verification suite
kgents test fuzz <agent> [--iterations=N]  # Adversarial fuzzing
kgents test laws <agent>                   # Verify category laws
kgents tool register <tool>                # Register T-gent tool
kgents tool list                           # List available tools
kgents tool mcp connect <server>           # Connect MCP server

# W-gents: Witness
kgents witness watch <target>              # Non-judgmental observation
kgents witness fidelity <output>           # Check faithfulness
kgents witness sample <stream> [--rate=<n>]  # Sample event stream
```

**Implementation Location**: `impl/claude/protocols/cli/genus/` (one file per letter)

---

## Part 3: Composition & Pipeline Commands (Tier 2 - Orchestration)

**Philosophy**: Enable building, saving, running, and verifying agent pipelines. This is where C-gents shine.

**New Commands** (~600 lines, 30 tests):

```bash
# Pipeline definition
kgents compose define "parse >> judge >> refine" --name=my-pipeline
kgents compose run <pipeline-name> <input>
kgents compose inspect <pipeline-name>      # Show pipeline structure
kgents compose export <pipeline-name> --format=yaml|json

# Session management (D-gent integration)
kgents session start --name=<id>           # Start persistent session
kgents session end <id>                    # End and clean up
kgents session list                        # Show active sessions
kgents session replay <id>                 # Replay session operations

# Agent registry
kgents agent register <path>               # Register .kgent.yaml
kgents agent run <name> <input>            # Run registered agent
kgents agent list [--genus=<letter>]       # List agents by genus
kgents agent inspect <name>                # Show agent details

# Daemon mode (autonomous)
kgents daemon list                         # Show running autonomous agents
kgents daemon send <id> <command>          # Send command to daemon
kgents daemon stop <id>                    # Stop autonomous agent
kgents daemon promote <command> [--interval=<duration>]  # Promote to daemon
```

**Implementation Location**: `impl/claude/protocols/cli/orchestration_cli.py`

**Key Integration Points**:
- `c-gents.compose.ComposedAgent` → `kgents compose`
- `d-gents.persistent.PersistentAgent` → `kgents session`
- `j-gents.jgent.JGent` → `kgents daemon`

---

## Part 4: Discovery & Observability Commands (Tier 2 - Introspection)

**Philosophy**: Make the invisible visible. These commands support understanding what's happening in agent systems.

**New Commands** (~600 lines, 30 tests):

```bash
# Observability (I-gent + W-gent)
kgents observe status [--dimensions=xyz]   # 3D system health
kgents observe trace <operation-id>        # Detailed trace
kgents observe audit [--since=<time>]      # Audit log

# History & Provenance
kgents history [--limit=N]                 # Show operation history
kgents replay <operation-id>               # Replay an operation
kgents explain <result-id>                 # Explain how result was produced
kgents export provenance --format=w3c-prov # Export provenance graph

# Streams (EventStream protocol)
kgents stream git [path]                   # GitStream observation
kgents stream momentum <topic>             # SemanticMomentumTracker
kgents stream witness <stream> [--window=<duration>]  # TemporalWitness

# Debug & Diagnostics
kgents debug ctx                           # (existing) Dump CLI context
kgents debug agent <name>                  # Debug specific agent
kgents debug composition <pipeline>        # Debug composition
kgents debug chaos [--level=low|medium|high]  # Chaosmonger activation
```

**Implementation Location**: `impl/claude/protocols/cli/observability_cli.py`

**Key Integration Points**:
- `protocols.mirror.streams` → `kgents stream`
- `i-gents.observe` → `kgents observe`
- `w-gents.protocol.WitnessProtocol` → `kgents witness`

---

## Part 5: Integration & Extension Points (Tier 3 - Ecosystem)

**Philosophy**: Enable kgents to integrate with external systems (MCP, Obsidian, git) and be extended with plugins/hooks.

**New Commands** (~400 lines, 20 tests):

```bash
# MCP Integration (Model Context Protocol)
kgents mcp connect <server>                # Connect to MCP server
kgents mcp list                            # List connected servers
kgents mcp tools                           # List available MCP tools
kgents mcp invoke <tool> [args...]         # Invoke MCP tool

# Sanctuary & Privacy
kgents sanctuary add <path>                # Add sanctuary path
kgents sanctuary list                      # List sanctuary paths
kgents sanctuary check <path>              # Check if path is sanctuary

# Hooks
kgents hook add pre|post <command> <script>  # Add hook
kgents hook list                           # List hooks
kgents hook remove <hook-id>               # Remove hook

# Plugins
kgents plugin install <name>               # Install plugin
kgents plugin list                         # List installed plugins
kgents plugin remove <name>                # Remove plugin

# Configuration
kgents config show                         # Show current config
kgents config set <key> <value>            # Set config value
kgents config reset                        # Reset to defaults
kgents config export --format=yaml|json    # Export config

# External Integrations
kgents obsidian sync [path]                # Obsidian vault sync
kgents git hook install                    # Install git hooks
kgents claude-code bridge                  # Bridge to Claude Code context

# Interactive Mode
kgents interactive                         # Enter interactive REPL
kgents script <path>                       # Run .kgents script
```

**Implementation Location**: `impl/claude/protocols/cli/integration_cli.py`

**Key Integration Points**:
- `t-gents.mcp_client.MCPClient` → `kgents mcp`
- Configuration hierarchy from spec → `kgents config`
- Hook system → `kgents hook`

---

## Implementation Priority

| Phase | Part | Est. Lines | Est. Tests | Dependencies |
|-------|------|-----------|------------|--------------|
| 1 | Part 1 (Bootstrap) | 500 | 20 | None |
| 2 | Part 2 (G, J, P) | 800 | 40 | Part 1 |
| 3 | Part 3 (Orchestration) | 600 | 30 | Part 2 |
| 4 | Part 2 (B,C,D,E,F,K,L,R,T,W) | 1200 | 60 | Part 3 |
| 5 | Parts 4+5 (Observability+Integration) | 1000 | 50 | Part 4 |

**Total**: ~4100 lines, ~200 tests

---

## Design Principles Applied

| Principle | How This Plan Applies |
|-----------|----------------------|
| **Tasteful** | Each command has justified purpose; no redundancy |
| **Curated** | Commands selected for usefulness, not completeness |
| **Ethical** | Sanctuary commands, explicit privacy controls |
| **Joy-Inducing** | `--explain` flag, interactive mode, contemplative commands |
| **Composable** | Unix piping, explicit composition, session management |
| **Heterarchical** | Functional mode (default) + daemon mode (autonomous) |
| **Generative** | `kgents bootstrap derive`, spec-driven implementation |

---

## Command Summary by Tier

### Tier 0: Identity (Always Available, 0 Tokens)
- `kgents bootstrap laws`
- `kgents meta principles`
- `kgents meta health`

### Tier 1: Daily Companions (0 Tokens, Local Only)
- `kgents pulse` (existing)
- `kgents ground` (existing)
- `kgents breathe` (existing)
- `kgents entropy` (existing)

### Tier 2: Agent Operations (May Use Tokens)
- All genus commands (`kgents grammar`, `kgents compose`, etc.)
- Pipeline operations
- Observability commands

### Tier 3: Ecosystem Integration (External Dependencies)
- MCP integration
- Plugin system
- External tool hooks

---

## See Also

- `spec/protocols/cli.md` - CLI meta-architecture specification
- `spec/principles.md` - The 7 design principles
- `impl/claude/protocols/cli/main.py` - Current CLI implementation
