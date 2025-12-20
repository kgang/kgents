# Claude Code Tool Infra Audit - Execution Results

## Scope executed
- Read kgents references: `docs/systems-reference.md`, `docs/architecture-overview.md`, `docs/skills/metaphysical-fullstack.md`.
- Applied the Assessment plan sections 1-5 from the audit doc.

## 1) Systems inventory pass (tool-relevant infrastructure)
- **Eventing**: DataBus, SynergyBus, EventBus already exist with AGENTESE paths (`self.bus.*`) and bridges; suitable for tool invocation lifecycle events.
- **Trust gating**: Witness Crown Jewel defines L0-L3 trust ladder aligned to tool risk tiers; GitWatcher provides event-driven observation.
- **Tracing/auditability**: Différance Engine provides trace + ghost alternatives with AGENTESE paths (`time.differance.*`, `time.branch.*`).
- **Protocol/registry**: AGENTESE runtime with affordance registry + paths; supports tool metadata and invocation routing.
- **Projection surfaces**: Metaphysical fullstack pattern + reactive widgets + projection gallery; supports CLI/Web/API projection of tool metadata and history.
- **Flow systems**: Flux (streams) and F-gent (chat/research/collab flows) provide continuous toolchain and multi-agent workflow substrate.

## 2) Architecture alignment pass
- **AGENTESE mapping**: Tool ops map to `world.tool.*` paths; leverage `protocols/agentese/affordances.py` for capability/risk metadata.
- **Witness integration**: Trust gate should wrap `world.tool.*` invocation in AGENTESE middleware; L0-L3 aligns with audit L0-L3 risk tiers.
- **Différance integration**: Wrap tool invocations with `DifferanceIntegration` to record outcomes + rejected alternatives.
- **Eventing alignment**: Emit `tool.invoke.*` events on DataBus and optionally SynergyBus; stream to EventBus for UI.
- **Missing adapters**: No explicit tool registry schema or tool invocation service module found in docs; needs service + node layer per fullstack pattern.

## 3) Prototype design pass (registry + safety policy)
- **Tool registry schema (proposed)**:
  - `tool.id`, `tool.intent`, `tool.capability`, `tool.risk`, `tool.cost`, `tool.side_effects`, `tool.inputs`, `tool.outputs`, `tool.requires`.
  - `tool.affordances`: read/write/exec/network/browser/MCP; link to Witness L0-L3.
  - `tool.projections`: CLI/Web/API help + examples; auto-generated from AGENTESE aspects.
- **Safety policy layer**:
  - `read_before_write` gate enforced by AGENTESE aspect metadata (Effect.WRITES).
  - `MCP_preflight` hook enforces `mcp-cli info` before `mcp-cli call`.
  - `consent_required` flag for destructive or L3 tools; route through Witness trust escalation.
  - `command_injection` detection policy for shell tools; classify prefixes and reject suspicious chains.

## 4) Projection + experience pass
- **CLI format**: Standardize tool output summaries using projection functor; brief result + link to trace ID in Différance.
- **Web dashboard**: Build on reactive widgets + projection gallery; show tool timeline, status, cost, and trust level.
- **API surface**: AGENTESE universal protocol already provides transport; no explicit routes needed.
- **Summarization**: Use F-gent flow or specialized summarizer to compress verbose command output.

## 5) Beyond-CLI exploration pass
- **Continuous toolchains**: Use Flux pipelines for long-running tool workflows with retry/backoff.
- **Temporal branching**: Leverage `time.branch.*` to explore alternates as “ghost runs.”
- **Shared substrate**: Use M-gent shared memory to persist tool results across agents.
- **Consent choreography**: Embed trust gates in AGENTESE middleware so CLI/Web/API share the same approval logic.

## Gaps vs Claude Code parity checklist
- **Tool set parity**: No explicit tool registry/service modules found; LSP, browser automation, MCP search/preflight, and NotebookEdit equivalents are not documented as implemented.
- **Workflow parity**: Plan mode gating and task list system are not documented as operational features in kgents core.
- **Safety parity**: Read-before-write and command injection detection exist as concepts but not confirmed as enforced gates.

## Concrete alignment recommendations
- **Create Tool Kernel service**: `services/tooling/` to host registry + invocation layer; expose AGENTESE nodes at `world.tool.*`.
- **Register affordances**: Extend `protocols/agentese/affordances.py` with tool metadata and Witness trust level mapping.
- **Enforce trust gates**: Integrate Witness trust ladder into AGENTESE middleware for all tool invocations.
- **Trace all invocations**: Use Différance to store tool invocation traces, including rejected alternatives.
- **Emit events**: DataBus + EventBus for lifecycle, with SynergyBus for cross-jewel coordination.

## Open questions (from audit, contextualized)
- Plan gating: embed as AGENTESE path semantics or explicit “plan mode” flow in F-gent?
- Registry schema: JSON/YAML vs in-code schema in `services/tooling/registry.py`?
- Read-before-write: enforce per tool invocation or per workflow (multi-file edits)?
- MCP preflight: transport layer vs tool layer enforcement?
- Consent unification: single middleware across CLI/Web/API or per-transport adapters?
- Mandatory systems: Should Witness + Différance be required for all tool calls?

