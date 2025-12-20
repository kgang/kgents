# Claude Code Tool Audit → k-gents / u-gents Infrastructure Brainstorm

This doc audits Claude Code’s system prompts for tool inventory and tool-use patterns, then maps them to kgents architecture to define a parity roadmap and beyond-CLI exploration. It is a planning and design reference, not an implementation spec.

## Audit scope and method
- Sources: `/Users/kentgang/git/claude-code-system-prompts/system-prompts/*` (system prompts, tool descriptions, agent prompts).
- Kgents references: `docs/systems-reference.md`, `docs/architecture-overview.md`, `docs/skills/metaphysical-fullstack.md`.
- Focus: tools, tool orchestration, safety gates, planning flows, and multi-agent patterns.

## Tool inventory (Claude Code)

### File + code intelligence
- ReadFile: read file contents with line numbering.
- Edit: exact string replacement.
- Write: overwrite/create file.
- NotebookEdit: replace/insert/delete Jupyter notebook cell.
- Glob: file name search.
- Grep: content search (rg-backed).
- LSP: go-to-definition, references, hover, symbols, call hierarchy.

### Execution + environment
- Bash: shell commands with sandboxing requirements and strict file op guidance.
- Computer: browser automation (mouse/keyboard + screenshots).

### Planning + orchestration
- EnterPlanMode: explicit plan-first workflow for non-trivial tasks.
- ExitPlanMode / ExitPlanMode v2: plan approval gate.
- Task: spawn subagents with specialized roles.
- Task (async return note): async agent lifecycle.
- TaskList / TaskUpdate: centralized task system.
- TodoWrite: local todo tracking inside a session.
- TeammateTool (operation parameter): team spawn, assign, mailbox, approvals.

### External info
- WebSearch: search with required Sources list.
- WebFetch: fetch + summarize a URL.
- MCP CLI: enforced schema preflight with `mcp-cli info`.
- MCPSearch: load MCP tools before use.

## Tool-use patterns and policies (Claude Code)

### Safety and preflight rules
- **Mandatory schema check for MCP**: `mcp-cli info` before any `mcp-cli call`.
- **Sandbox-first**: Bash defaults to sandbox; only bypass on user request or clear failure.
- **Read-before-edit/write**: must read before Edit/Write.
- **Search hygiene**: dedicated tools for file search and grep, avoid shell tools.
- **No destructive git by default**: explicit user request for commits/PRs.
- **Command injection detection**: classify command prefixes; reject injection.

### Planning workflows
- **Plan mode gating**: exploration only, plan file only, then ExitPlanMode.
- **Parallel exploration**: multiple subagents for broad discovery.
- **Plan clarity requirement**: must resolve ambiguity before exit.

### Orchestration and delegation
- **Task tool**: spawn subagents; read-only or research tasks; return summaries.
- **Team ops**: spawn team, assign tasks, mailbox communications.
- **Tool selection**: prefer specialized tools over Bash for file ops.

### Output policy
- Output style constraints and tone (concise CLI-focused).
- Summarization for verbose command outputs via a dedicated agent prompt.

## Mapping to kgents architecture

### Tool registry → AGENTESE + Affordances
- Claude tools map to `world.tool.*` or `self.tool.*` paths with explicit affordances.
- `protocols/agentese/affordances.py`: define tool verbs + safety metadata.

### Trust gating → Witness Crown Jewel
- Tool operations map to Witness trust levels:
  - L0: dry-run/describe only.
  - L1: read-only (ReadFile, Grep, Glob).
  - L2: reversible writes (Edit, Write).
  - L3: external side effects (network, system tools, browser).

### Tracing + auditability → Différance Engine
- Every tool invocation emits a trace with alternatives and rejection rationale.
- Use `DifferanceStore` for audit timelines + ghost alternatives.

### Eventing + coordination → DataBus + SynergyBus
- Tool invocation events emit on DataBus and optionally SynergyBus:
  - `tool.invoke.started`, `tool.invoke.completed`, `tool.invoke.failed`.
- Stream events to UI projections and task monitors via EventBus.

### Multi-surface projections → Metaphysical Fullstack
- Tooling metadata drives CLI/TUI/Web/API projections from AGENTESE nodes.
- CLI: standardized formatting + summarization patterns.
- Web: tool dashboards + active session timeline.

## Parity checklist (Claude Code CLI capabilities)

### Core tool set parity
- [ ] ReadFile / Edit / Write / NotebookEdit equivalents.
- [ ] Glob / Grep equivalents with similar safety and performance.
- [ ] LSP operations for code intel (definition, refs, symbols).
- [ ] Shell execution with sandbox + policy enforcement.
- [ ] Browser automation and screenshot capture.
- [ ] WebSearch + WebFetch equivalents (with explicit source policy).
- [ ] MCP search + preflight schema enforcement.

### Workflow parity
- [ ] Plan mode gating: plan-only phase + approval transition.
- [ ] Async subagents with specialized roles and read-only constraints.
- [ ] Task list + updates + ownership semantics.
- [ ] Todo list guidance for multi-step tasks.
- [ ] Output summarization pipeline for verbose command output.

### Safety parity
- [ ] Read-before-edit/write enforced at tool layer.
- [ ] Command injection detection.
- [ ] Explicit consent for destructive actions.
- [ ] Sandboxed execution by default.

## Beyond-CLI exploration: u-gents tool infrastructure

### Extended tool ontology
- Tool taxonomy is not just “commands” but **capabilities + intent + cost + risk**:
  - `tool.capability`, `tool.intent`, `tool.risk`, `tool.cost`, `tool.side_effects`.
- Declarative permissions per tool + per user + per context.

### Agentic workflows beyond CLI
- **Continuous toolchains**: long-lived flows (Flux) that auto-retry, backoff, or branch.
- **Temporal branching**: simulate alternate tool paths (Différance ghosts).
- **Shared substrate**: multi-agent tool results persisted to M-gent memory.
- **Consent choreography**: interactive approvals embedded in tool execution.

### Interface expansion
- Real-time tool dashboards: timeline, status, outcomes, budget.
- Semantic tool search: query by intent instead of name.
- Cross-surface continuity: CLI → Web → API with same AGENTESE path.

### Governance + ethics
- Tool calls are governed by K-gent policies and state.
- Adaptive trust: adjust allowed tools by user history or task type.

## Tool infrastructure design targets (for k-gents / u-gents)

### Minimum viable tool kernel
- Tool registry (metadata + schema + risk).
- Preflight gates (read-before-write, schema check, consent).
- Invocation layer (execution + tracing).
- Event pipeline (DataBus + EventBus).
- Output adapters (CLI, Web, API).

### “Level-up” features
- LSP integration for semantic edits.
- Summarization + explainability pipeline.
- Intent-aware tool selection.
- Automated tool discovery + MCP bridging.

## Assessment plan for kgents architecture and systems

### 1) Systems inventory pass
- Read `docs/systems-reference.md` and list current tool-relevant infrastructure.
- Identify already-built capabilities to reuse: buses, AGENTESE, Witness, Différance.

### 2) Architecture alignment pass
- Map tool operations to AGENTESE paths and discuss affordances metadata.
- Identify missing protocol nodes or adapters.

### 3) Prototype design pass
- Define a tool registry schema (capabilities + risk + costs).
- Define a safety policy layer (Trust + consent).

### 4) Projection + experience pass
- Design CLI output format + summarization behavior.
- Define a web dashboard schema for tool invocation history.

### 5) Beyond-CLI exploration pass
- Speculate on autonomous toolchains, temporal branching, and memory-rich workflows.

## Quality enhancements
- **Explicit safety lattice**: define a tool risk matrix with Witness trust thresholds.
- **Standardized tool metadata**: include cost estimates, data sensitivity, and side effects.
- **Automated provenance**: Différance trace per tool invocation.
- **Adaptive summaries**: summarize logs by task intent (test vs build vs deploy).
- **Tool affordance docs**: auto-generate help from metadata for CLI and Web.

## Open questions
- Should k-gents mirror Claude Code’s plan-mode gating verbatim, or embed plan approval within AGENTESE path semantics?
- What should be the canonical tool registry schema (JSON/YAML, in-code, or AGENTESE-native)?
- How strict should the read-before-write gate be for multi-file workflows?
- Should MCP schema preflight be enforced at transport layer or tool layer?
- How do we standardize consent across CLI/Web/API without duplicating logic?
- Which kgents systems (Witness, Différance, DataBus) should be mandatory for any tool invocation?
- How much autonomy should u-gents have by default at each trust tier?
