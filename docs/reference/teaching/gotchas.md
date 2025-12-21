# Teaching Moments (Gotchas)

> *"Gotchas live in docstrings, not wikis."*

## 🚨 Critical (75)

### persistence
*Module: services.brain.persistence*

Dual-track storage means Crystal table AND D-gent must both succeed. If one fails after the other succeeds, you get "ghost" memories.

**Evidence**: `test_brain_persistence.py::test_heal_ghosts`

---

### persistence
*Module: services.brain.persistence*

capture() returns immediately but trace recording is fire-and-forget. Never await the trace task or you'll block the hot path.

**Evidence**: `test_brain_persistence.py::test_capture_performance`

---

### session_walk
*Module: services.witness.session_walk*

advance_walk() returns False silently for sessions without Walk. It does NOT raise an exception. Always check has_walk() first if you need to know whether the Walk exists.

**Evidence**: `test_session_walk.py::TestLaw3OptionalBinding::test_advance_walk_returns_false_without_walk`

---

### playbook
*Module: services.witness.playbook*

Always verify Grant is GRANTED status before creating Playbook. Passing a PENDING or REVOKED Grant raises MissingGrant.

**Evidence**: `test_ritual.py::test_ritual_requires_grant`

---

### playbook
*Module: services.witness.playbook*

from_dict() does NOT restore _grant and _scope objects. You must reattach them manually after deserialization.

**Evidence**: `test_ritual.py::test_ritual_roundtrip`

---

### grant
*Module: services.witness.grant*

GateFallback.DENY is the SAFE DEFAULT for timeout. If a ReviewGate times out, the fallback determines behavior. DENY blocks, ALLOW_LIMITED reduces scope, ESCALATE delegates. Always set explicit fallback.

**Evidence**: `test_covenant.py::test_covenant_gate_fallback`

---

### persistence
*Module: services.conductor.persistence*

Corrupted JSON data returns None from load_window(), not an exception. Always handle the None case when loading - the user may have edited the underlying storage or the data may be from an incompatible version.

**Evidence**: `test_persistence.py::TestWindowPersistenceLoad::test_load_window_handles_corrupted_data`

---

### presence
*Module: services.conductor.presence*

Invalid state transitions are REJECTED silently (return False). WAITING cannot go directly to SUGGESTING - it must pass through WORKING or FOLLOWING first. Always check transition_to() return value.

**Evidence**: `test_presence.py::TestAgentCursor::test_transition_to_invalid`

---

### file_guard
*Module: services.conductor.file_guard*

Edits without prior read fail with EditError.NOT_READ. The guard returns a structured error response rather than raising, so you MUST check response.success before assuming the edit worked.

**Evidence**: `test_file_guard.py::TestEditOperations::test_edit_requires_prior_read`

---

### TeachingMoment
*Module: services.living_docs.types*

Always include evidence when creating TeachingMoments.

**Evidence**: `test_types.py::test_teaching_moment_evidence`

---

### extractor
*Module: services.living_docs.extractor*

Teaching section must use 'gotcha:' keyword for extraction.

**Evidence**: `test_extractor.py::test_teaching_pattern`

---

### spec_extractor
*Module: services.living_docs.spec_extractor*

Anti-patterns are warnings, Laws are critical. Severity mapping matters for proper prioritization.

**Evidence**: `test_spec_extractor.py::test_severity_mapping`

---

### LivingDocsNode
*Module: services.living_docs.node*

Observer kind must be one of: human, agent, ide.

**Evidence**: `test_node.py::test_observer_validation`

---

### service
*Module: services.interactive_text.service*

Line numbers are 1-indexed for human ergonomics. The toggle_task_at_line() method converts to 0-indexed internally. Off-by-one errors are common when directly manipulating the lines list—always use (line_number - 1).

**Evidence**: `test_parser.py::TestTokenRecognition::test_task_checkbox_checked`

---

### service
*Module: services.interactive_text.service*

TraceWitness is ALWAYS captured on successful toggle, even in text mode where no file is modified. The trace captures previous_state → new_state for audit. If you need to skip trace capture, you must use the internal _toggle_task_at_line() method directly (not recommended for production use).

**Evidence**: `test_tokens_base.py::TestTraceWitness::test_create_witness`

---

### events
*Module: services.interactive_text.events*

_safe_notify() swallows exceptions—handlers must not rely on error propagation. Errors increment _error_count but don't fail emission or other handlers.

**Evidence**: `test_properties.py::test_handler_exception_isolation`

---

### __init__
*Module: services.interactive_text.__init__*

Observer.density affects projection output—COMPACT truncates, SPACIOUS shows all. Always pass observer to projection; don't assume COMFORTABLE default.

**Evidence**: `test_projectors.py::test_density_affects_output`

---

### parser
*Module: services.interactive_text.parser*

Roundtrip fidelity is THE invariant. parse(text).render() MUST equal text exactly—byte-for-byte, including all whitespace, tabs, and newlines. If rendering changes even one character, you've broken the contract.

**Evidence**: `test_parser.py::TestRoundtripFidelity::test_roundtrip_preserves_whitespace`

---

### parser
*Module: services.interactive_text.parser*

Empty documents are valid. parse("") returns ParsedDocument with empty spans tuple, not None. Always check token_count, not truthiness of document.

**Evidence**: `test_parser.py::TestRoundtripFidelity::test_roundtrip_empty_document`

---

### contracts
*Module: services.interactive_text.contracts*

TokenPattern validates on __post_init__—empty name raises ValueError. Always provide a non-empty name when constructing TokenPattern.

**Evidence**: `test_contracts.py::test_token_pattern_validation`

---

### contracts
*Module: services.interactive_text.contracts*

MeaningToken.token_id default uses position (type:start:end). Custom implementations may override but must remain unique per doc.

**Evidence**: `test_contracts.py::test_token_id_uniqueness`

---

### sheaf
*Module: services.interactive_text.sheaf*

glue() RAISES SheafConditionError if views are incompatible. Always call verify_sheaf_condition() first if you want to handle conflicts gracefully. Don't assume glue() will merge conflicts—it refuses to produce invalid state.

**Evidence**: `test_properties.py::TestProperty8DocumentSheafCoherence::test_incompatible_views_cannot_be_glued`

---

### sheaf
*Module: services.interactive_text.sheaf*

A single view is ALWAYS coherent with itself. verify_sheaf_condition() on a sheaf with one view returns success with checked_pairs=0. The sheaf condition is about agreement between views, not internal consistency.

**Evidence**: `test_properties.py::TestProperty8DocumentSheafCoherence::test_single_view_always_coherent`

---

### base
*Module: services.interactive_text.projectors.base*

ProjectionFunctor must satisfy functor laws: P(id) = id, P(f∘g) = P(f)∘P(g). project_composition() relies on _compose() to preserve associativity.

**Evidence**: `test_projectors.py::test_composition_law`

---

### graph_engine
*Module: services.verification.graph_engine*

Contradictions use HEURISTIC detection, not formal logic. The engine looks for keyword pairs like "synchronous/asynchronous" or "must/must not" in descriptions. A contradiction may be a false positive if context disambiguates the usage.

**Evidence**: `test_graph_engine.py::TestContradictionDetection::test_detect_exclusive_conflicts`

---

### graph_engine
*Module: services.verification.graph_engine*

Principle nodes are ALWAYS created (7 kgents principles) regardless of spec content. They are the roots of the derivation graph. Implementation nodes without paths to these principles are flagged as orphaned.

**Evidence**: `test_graph_engine.py::TestVerificationGraphCorrectness::test_principle_nodes_created`

---

### categorical_checker
*Module: services.verification.categorical_checker*

Empty counter-example list returns {"strategies": [], "analysis": "No violations found"}. Always check the analysis message - an empty list is success, not an error.

**Evidence**: `test_categorical_checker.py::TestCounterExampleGeneration::test_empty_counter_examples_handled`

---

### ProviderConfig
*Module: services.morpheus.gateway*

The `prefix` is the ONLY routing mechanism. Model names must START with this prefix. If you register prefix="claude-", then "claude-opus" routes but "anthropic-claude" does not.

**Evidence**: `test_rate_limit.py::TestGatewayRateLimiting`

---

### GatewayConfig
*Module: services.morpheus.gateway*

The `rate_limit_by_archetype` dict is the source of truth for per-observer limits. Unknown archetypes fall back to `rate_limit_rpm`. Always ensure new archetypes are added here BEFORE use.

**Evidence**: `test_rate_limit.py::TestGatewayRateLimiting`

---

### MorpheusGateway
*Module: services.morpheus.gateway*

Streaming errors are yielded as content, not raised as exceptions. This is intentional—SSE clients expect data, not connection drops. Always check first chunk for error messages.

**Evidence**: `test_streaming.py::test_gateway_stream_unknown_model_yields_error`

---

### CompletionResult
*Module: services.morpheus.persistence*

The `telemetry_span_id` is only populated when telemetry is enabled. Always check for None before using for tracing correlation.

**Evidence**: `test_node.py::TestMorpheusNodeComplete`

---

### MorpheusPersistence
*Module: services.morpheus.persistence*

RateLimitError is re-raised after recording metrics. The caller must handle it—it's not silently swallowed.

**Evidence**: `test_rate_limit.py::TestPersistenceRateLimiting`

---

### ChatChoice
*Module: services.morpheus.types*

`finish_reason="length"` means max_tokens was hit—output may be incomplete. Always check finish_reason before assuming full response.

**Evidence**: `test_streaming.py::TestStreamChunk`

---

### ChatResponse
*Module: services.morpheus.types*

`usage` may be None for some providers or streaming. Always null-check before accessing token counts.

**Evidence**: `test_node.py::TestMorpheusNodeComplete`

---

### checker
*Module: services.ashc.checker*

Always clean up temp files—even on exceptions. Use try/finally.

---

### checker
*Module: services.ashc.checker*

Verus `verus!` blocks inside `impl` sections are silently ignored. Always wrap the entire `impl` block.

---

### DafnyChecker
*Module: services.ashc.checker*

Always unlink temp files in finally block—exceptions happen.

---

### DafnyChecker
*Module: services.ashc.checker*

--verification-time-limit not always respected; prefer --resource-limit for reliable bounded verification. Example: >>> checker = DafnyChecker() >>> if checker.is_available: ... result = await checker.check("lemma Trivial() ensures true {}") ... assert result.success

---

### Lean4Checker
*Module: services.ashc.checker*

Exact toolchain matching required. Project and deps must use same Lean version or cache won't work.

---

### Lean4Checker
*Module: services.ashc.checker*

Without mathlib cache, builds take 20+ minutes. Always use `lake exe cache get` when working with mathlib projects. Example: >>> checker = Lean4Checker() >>> if checker.is_available: ... result = await checker.check("theorem trivial : ∀ x : Nat, x = x := fun _ => rfl") ... assert result.success

---

### VerusChecker
*Module: services.ashc.checker*

All verified code must be inside the verus! macro.

---

### VerusChecker
*Module: services.ashc.checker*

vstd imports must be explicit.

---

### VerusChecker
*Module: services.ashc.checker*

CRITICAL: verus! blocks inside `impl` sections are SILENTLY IGNORED. Always wrap the entire impl, not just methods.

---

### types
*Module: agents.poly.types*

Result.unwrap() raises RuntimeError on Err. Always check is_ok() first or use unwrap_or(default) for safe extraction.

**Evidence**: `test_primitives.py::test_result_unwrap_error`

---

### core
*Module: agents.operad.core*

Operad.compose() raises KeyError for unknown operations, not None. Always check `operad.get(op_name)` first if unsure.

**Evidence**: `test_core.py::TestOperad::test_operad_compose_unknown_op_raises`

---

### protocol
*Module: agents.sheaf.protocol*

restrict() raises RestrictionError if no positions valid in subcontext Position filter must match at least one position, or restriction fails. Check your filter predicate before calling restrict().

**Evidence**: `test_emergence.py::TestSheafRestriction::test_restrict_to_context`

---

### functor
*Module: agents.flux.functor*

Flux.unlift() does NOT stop a running flux. It just returns the inner agent. Always call flux.stop() first if the flux is running.

**Evidence**: `Structural - unlift docstring explicitly warns`

---

### pipeline
*Module: agents.flux.pipeline*

Empty pipelines raise FluxPipelineError immediately in __post_init__. You cannot create FluxPipeline([]). Always have at least one stage.

**Evidence**: `test_pipeline.py::TestPipelineValidation::test_empty_pipeline_raises`

---

### agent
*Module: agents.flux.agent*

start() returns AsyncIterator[B], NOT None. You MUST consume the iterator with `async for`. Just calling start() does nothing.

**Evidence**: `test_agent.py::TestFluxAgentStartReturnsAsyncIterator`

---

### agent
*Module: agents.flux.agent*

Cannot start() a FLOWING flux. You'll get FluxStateError. The flux must be DORMANT or STOPPED first. Use flux.stop() to reset.

**Evidence**: `test_agent.py::TestFluxAgentStateTransitions::test_cannot_start_while_flowing`

---

### soul
*Module: agents.k.soul*

Budget tiers are NOT just token limits - they gate LLM access entirely. DORMANT and WHISPER never call the LLM; they use templates. Set budget=BudgetTier.DIALOGUE to actually invoke the LLM.

**Evidence**: `test_soul.py::test_soul_dialogue_template - templates bypass LLM`

---

### soul
*Module: agents.k.soul*

intercept_deep() ALWAYS escalates dangerous operations regardless of LLM recommendations. The DANGEROUS_KEYWORDS set is hardcoded and cannot be overridden. This is a safety invariant.

**Evidence**: `test_soul.py::test_deep_intercept_dangerous_operation`

---

### gatekeeper
*Module: agents.k.gatekeeper*

Only ERROR and CRITICAL severities cause result.passed=False. INFO and WARNING violations are informational and DO NOT fail validation. Check by_severity counts if you need warning-level enforcement.

**Evidence**: `test_gatekeeper.py::TestSeverity::test_pass_fail_threshold`

---

### flux
*Module: agents.k.flux*

Metadata events ALWAYS pass through filter(), take(), map() unchanged. Only data events are filtered/transformed. This preserves token counts and completion signals. Don't filter expecting metadata to be blocked.

**Evidence**: `test_soul_streaming_integration.py::test_pipeline_preserves_metadata`

---

### protocol
*Module: agents.m.protocol*

ACTIVE -> COMPOSTING is INVALID transition (must go through DORMANT) Lifecycle transitions have strict rules. Memory must be DORMANT before it can be demoted to COMPOSTING during consolidation.

**Evidence**: `test_lifecycle.py::TestValidTransitions::test_active_to_composting_invalid`

---

### AgenteseGateway
*Module: protocols.agentese.gateway*

Discovery endpoints MUST be defined BEFORE catch-all routes. FastAPI matches routes in definition order, so /discover must come before /{path:path}/* or it gets swallowed.

**Evidence**: `test_gateway.py::TestGatewayDiscovery`

---

### NodeMetadata
*Module: protocols.agentese.registry*

Dependencies are resolved by ServiceContainer at instantiation. If a dependency isn't registered, the node SILENTLY SKIPS! Always verify deps exist in providers.py.

**Evidence**: `test_registry.py::test_resolve_dependent_node_fails_without_container`

---

### AgentesePath
*Module: protocols.agentese.logos*

AgentesePath creates UnboundComposedPath via >>. You must call .bind(logos) or .run(observer, logos) to execute.

**Evidence**: `test_logos.py::test_unbound_composition`

---

### LogosNode
*Module: protocols.agentese.node*

LogosNode must be stateless. Any state access must go through D-gent Lens (dependency injection). This enables composition.

**Evidence**: `test_node.py::test_logos_node_stateless`

---

### monads
*Module: spec.agents.monads*

Law (Identity): StateFunctor.lift(Id) ≅ Id

---

### monads
*Module: spec.agents.monads*

Law (Composition): lift(f >> g) ≅ lift(f) >> lift(g)

---

### monad_laws
*Module: spec.agents.monads*

Law (Identity): StateFunctor.lift(Id) ≅ Id

---

### monad_laws
*Module: spec.agents.monads*

Law (Composition): lift(f >> g) ≅ lift(f) >> lift(g)

---

### d_gent_the_data_agent
*Module: spec.agents.d-gent*

Law (GetPut): lens.set(s, lens.get(s)) == s

---

### d_gent_the_data_agent
*Module: spec.agents.d-gent*

Law (PutGet): lens.get(lens.set(s, a)) == a

---

### d_gent_the_data_agent
*Module: spec.agents.d-gent*

Law (PutPut): lens.set(lens.set(s, a), b) == lens.set(s, b)

---

### d_gent_the_data_agent
*Module: spec.agents.d-gent*

Law (Functor): spec/agents/functor-catalog.md` §14 (State Functor)

---

### n_phase_cycle_protocol
*Module: spec.protocols.n-phase-cycle*

Law (Identity): Empty phase (pass-through)

---

### n_phase_cycle_protocol
*Module: spec.protocols.n-phase-cycle*

Law (Law): Every cycle MUST reach `⟂` eventually.

---

### living_docs_documentation_as_projection
*Module: spec.protocols.living-docs*

Law (Functor): project(compose(a, b)) ≡ compose(project(a), project(b))

---

### living_docs_documentation_as_projection
*Module: spec.protocols.living-docs*

Law (Freshness): Claims re-verified within 7 days are valid

---

### living_docs_documentation_as_projection
*Module: spec.protocols.living-docs*

Law (Provenance): ∀ TeachingMoment: evidence ≠ None → test exists

---

### laws
*Module: spec.protocols.living-docs*

Law (Functor): project(compose(a, b)) ≡ compose(project(a), project(b))

---

### laws
*Module: spec.protocols.living-docs*

Law (Freshness): Claims re-verified within 7 days are valid

---

### laws
*Module: spec.protocols.living-docs*

Law (Provenance): ∀ TeachingMoment: evidence ≠ None → test exists

---

## ⚠️ Warning (45)

### design_principles
*Module: spec.principles*

Anti-pattern: Agents that do "everything"

---

### design_principles
*Module: spec.principles*

Anti-pattern: Kitchen-sink configurations

---

### design_principles
*Module: spec.principles*

Anti-pattern: Agents added "just in case"

---

### bootstrap_agents
*Module: spec.bootstrap*

Anti-pattern: ❌ Unbounded history accumulation in Fix (use bounded/sampled history)

---

### bootstrap_agents
*Module: spec.bootstrap*

Anti-pattern: ❌ Sequential execution of independent checks (parallelize Judge/Contradict)

---

### bootstrap_agents
*Module: spec.bootstrap*

Anti-pattern: ❌ Re-computing static Ground data (cache persona seed)

---

### bootstrap_agents
*Module: spec.bootstrap*

Anti-pattern: ❌ Deep composition chains without flattening (use flatten() for debugging)

---

### bootstrap_agents
*Module: spec.bootstrap*

Anti-pattern: ✅ Ground caching (v1.0+): cache=True parameter

---

### bootstrap_agents
*Module: spec.bootstrap*

Anti-pattern: ✅ Judge parallelization (v1.0+): parallel=True parameter

---

### bootstrap_agents
*Module: spec.bootstrap*

Anti-pattern: ⏳ Bounded Fix history: Future enhancement

---

### bootstrap_agents
*Module: spec.bootstrap*

Anti-pattern: ⏳ Id composition optimization: Future enhancement

---

### d_gent_the_data_agent
*Module: spec.agents.d-gent*

Anti-pattern: ❌ Hardcoded paths

---

### d_gent_the_data_agent
*Module: spec.agents.d-gent*

Anti-pattern: ❌ Multiple databases per project

---

### d_gent_the_data_agent
*Module: spec.agents.d-gent*

Anti-pattern: ❌ Direct file I/O

---

### d_gent_the_data_agent
*Module: spec.agents.d-gent*

Anti-pattern: ❌ Bypassing Symbiont state threading

---

### agentic_self_hosting_compiler_ashc
*Module: spec.protocols.agentic-self-hosting-compiler*

Anti-pattern: One-shot compilation: Running once and trusting the output. Evidence requires repetition.

---

### agentic_self_hosting_compiler_ashc
*Module: spec.protocols.agentic-self-hosting-compiler*

Anti-pattern: Ignoring verification failures: A failed test is data, not noise.

---

### agentic_self_hosting_compiler_ashc
*Module: spec.protocols.agentic-self-hosting-compiler*

Anti-pattern: Manual code review: The evidence corpus IS the review. Trust the process.

---

### agentic_self_hosting_compiler_ashc
*Module: spec.protocols.agentic-self-hosting-compiler*

Anti-pattern: Formal proof obsession: We're not doing Coq. We're doing science.

---

### agentic_self_hosting_compiler_ashc
*Module: spec.protocols.agentic-self-hosting-compiler*

Anti-pattern: Prompt over-engineering: Writing prompts is easy. Gathering evidence is hard.

---

### repository_archaeology_priors_for_the_self_hosting_compiler
*Module: spec.protocols.repo-archaeology*

Anti-pattern: Treating history as truth: History is evidence, not gospel. Patterns may not generalize.

---

### repository_archaeology_priors_for_the_self_hosting_compiler
*Module: spec.protocols.repo-archaeology*

Anti-pattern: Ignoring failures: Abandoned features teach as much as successes.

---

### repository_archaeology_priors_for_the_self_hosting_compiler
*Module: spec.protocols.repo-archaeology*

Anti-pattern: Over-automation: Some judgment calls require Kent's taste.

---

### repository_archaeology_priors_for_the_self_hosting_compiler
*Module: spec.protocols.repo-archaeology*

Anti-pattern: Completionism: Not every commit needs analysis—sample the important ones.

---

### cross_pollination_protocol
*Module: spec.protocols.cross-pollination*

Anti-pattern: Tight coupling: Agent A imports Agent B directly

---

### cross_pollination_protocol
*Module: spec.protocols.cross-pollination*

Anti-pattern: Orchestrator bottleneck: One agent coordinates all others

---

### cross_pollination_protocol
*Module: spec.protocols.cross-pollination*

Anti-pattern: Hidden state: Agents hold state the field can't observe

---

### cross_pollination_protocol
*Module: spec.protocols.cross-pollination*

Anti-pattern: Bypass economics: Operations without metering

---

### cross_pollination_protocol
*Module: spec.protocols.cross-pollination*

Anti-pattern: Cosmetic personality: K-gent only changes output voice, not decisions

---

### checker_bridges_the_gatekeeper_protocol
*Module: spec.protocols.checker-bridges*

Anti-pattern: Blocking subprocess calls: Use asyncio.create_subprocess_exec, not subprocess.run

---

### checker_bridges_the_gatekeeper_protocol
*Module: spec.protocols.checker-bridges*

Anti-pattern: Ignoring exit codes: Parse exit code, not output presence (Dafny outputs to stderr even on success)

---

### checker_bridges_the_gatekeeper_protocol
*Module: spec.protocols.checker-bridges*

Anti-pattern: Silent failures: Raise CheckerUnavailable explicitly, don't return empty results

---

### checker_bridges_the_gatekeeper_protocol
*Module: spec.protocols.checker-bridges*

Anti-pattern: Uncleaned temp files: Always use try/finally for cleanup

---

### checker_bridges_the_gatekeeper_protocol
*Module: spec.protocols.checker-bridges*

Anti-pattern: Hardcoded timeouts: Accept timeout_ms parameter, respect it

---

### proof_generating_ashc
*Module: spec.protocols.proof-generation*

Anti-pattern: Proving everything: Too expensive; prioritize critical paths

---

### proof_generating_ashc
*Module: spec.protocols.proof-generation*

Anti-pattern: Ignoring failed proofs: Signal of spec ambiguity—investigate, don't suppress

---

### proof_generating_ashc
*Module: spec.protocols.proof-generation*

Anti-pattern: Manual proof editing: Proofs should regenerate from spec (Generative principle)

---

### proof_generating_ashc
*Module: spec.protocols.proof-generation*

Anti-pattern: Proof hoarding: Share lemmas across services via SynergyBus

---

### proof_generating_ashc
*Module: spec.protocols.proof-generation*

Anti-pattern: Skipping the checker: LLM claims are worthless without mechanical verification

---

### witness_primitives_the_audit_core
*Module: spec.protocols.witness-primitives*

Anti-pattern: Mark is not a log entry — it has causal links and umwelt context

---

### witness_primitives_the_audit_core
*Module: spec.protocols.witness-primitives*

Anti-pattern: Walk is not just a session — it binds to plans and tracks N-Phase

---

### witness_primitives_the_audit_core
*Module: spec.protocols.witness-primitives*

Anti-pattern: Playbook is not a pipeline — it has guards and requires contracts

---

### witness_primitives_the_audit_core
*Module: spec.protocols.witness-primitives*

Anti-pattern: Grant is not an API key — it's negotiated and revocable

---

### witness_primitives_the_audit_core
*Module: spec.protocols.witness-primitives*

Anti-pattern: Scope is not a context dump — it has explicit budget constraints

---

### witness_primitives_the_audit_core
*Module: spec.protocols.witness-primitives*

Anti-pattern: Lesson is not documentation — it's versioned knowledge that evolves

---

## ℹ️ Info (263)

### persistence
*Module: services.brain.persistence*

search() updates access_count via touch(). High-frequency searches will cause write amplification. Consider batching access updates.

**Evidence**: `test_brain_persistence.py::test_access_tracking`

---

### BrainNode
*Module: services.brain.node*

BrainNode REQUIRES brain_persistence dependency. Without it, instantiation fails with TypeError—this is intentional! It enables Logos fallback to SelfMemoryContext when DI isn't configured.

**Evidence**: `test_node.py::TestBrainNodeRegistration::test_node_requires_persistence`

---

### BrainNode
*Module: services.brain.node*

Affordances vary by observer archetype. Guests can only search, newcomers can capture, developers can delete. Check archetype before assuming full access.

**Evidence**: `test_node.py::TestBrainNodeAffordances`

---

### BrainNode
*Module: services.brain.node*

Every BrainNode invocation emits a Mark (WARP Law 3). Don't add manual tracing—the gateway handles it at _invoke_path().

**Evidence**: `test_node.py::TestBrainWARPIntegration`

---

### BrainNode
*Module: services.brain.node*

crystal_id can come from either "crystal_id" or "id" kwargs. The get/delete aspects check both for backward compatibility.

**Evidence**: `test_node.py::TestBrainNodeGet::test_get_without_id_returns_error`

---

### mark
*Module: services.witness.mark*

Marks are IMMUTABLE (frozen=True). You cannot modify a Mark after creation. To "update" metadata, create a new Mark linked via CONTINUES relation to the original.

**Evidence**: `test_trace_node.py::test_mark_immutability`

---

### mark
*Module: services.witness.mark*

MarkLink.source can be MarkId OR PlanPath. This allows linking marks to Forest plan files directly. When traversing links, check the type before assuming you have a MarkId.

**Evidence**: `test_session_walk.py::TestForestIntegration::test_walk_with_root_plan`

---

### session_walk
*Module: services.witness.session_walk*

Starting a second Walk for a session with active Walk raises ValueError. Complete or abandon the current Walk first. Check has_walk() before calling start_walk_for_session().

**Evidence**: `test_session_walk.py::TestLaw1SessionOwnsWalk::test_cannot_start_second_walk_when_active`

---

### playbook
*Module: services.witness.playbook*

Phase transitions are DIRECTED—you cannot skip phases. SENSE → ACT → REFLECT → SENSE (cycle). InvalidPhaseTransition if wrong.

**Evidence**: `test_ritual.py::test_invalid_transitions_blocked`

---

### playbook
*Module: services.witness.playbook*

Guards evaluate at phase boundaries, not during phase. Budget exhaustion during ACT phase only fails at ACT → REFLECT.

**Evidence**: `test_ritual.py::test_guard_evaluation_recorded`

---

### grant
*Module: services.witness.grant*

Grant status lifecycle is DIRECTIONAL. EXPIRED is terminal unless explicitly renewed. REVOKED can be re-granted, but EXPIRED cannot. Check is_active property rather than status == GRANTED for safety.

**Evidence**: `test_ritual.py::test_grant_revocation_invalidates_ritual`

---

### persistence
*Module: services.conductor.persistence*

Window persistence is independent from ChatSession lifecycle. A window can exist in D-gent even after its session is gone. Use exists() to check before assuming a load will succeed.

**Evidence**: `test_persistence.py::TestWindowPersistenceIntegration::test_exists_check`

---

### bus_bridge
*Module: services.conductor.bus_bridge*

wire_a2a_to_global_synergy() is idempotent - calling it twice returns the SAME unsubscribe function. This prevents duplicate bridging but means you cannot create multiple independent bridges.

**Evidence**: `test_bus_bridge.py::TestBusBridgeLifecycle::test_double_wire_is_idempotent`

---

### bus_bridge
*Module: services.conductor.bus_bridge*

Malformed A2A events do NOT crash the bridge - graceful degradation. Missing fields like from_agent/to_agent are replaced with "unknown". The bridge continues processing after errors, so a bad event won't break the entire A2A visibility pipeline.

**Evidence**: `test_bus_bridge.py::TestBridgeErrorHandling::test_malformed_event_doesnt_crash_bridge`

---

### presence
*Module: services.conductor.presence*

States cannot transition to themselves - no self-loops allowed. The directed graph enforces this constraint to prevent infinite loops.

**Evidence**: `test_presence.py::TestCursorStateTransitions::test_no_self_transitions`

---

### file_guard
*Module: services.conductor.file_guard*

Non-unique old_string returns EditError.NOT_UNIQUE, not an exception. Use replace_all=True when you intentionally want to replace all occurrences. The error response includes a suggestion to help the user.

**Evidence**: `test_file_guard.py::TestEditOperations::test_edit_string_not_unique`

---

### teaching
*Module: services.living_docs.teaching*

Evidence paths are relative to impl/claude.

**Evidence**: `test_teaching.py::test_evidence_path_resolution`

---

### DocNode
*Module: services.living_docs.types*

agentese_path is extracted from "AGENTESE: <path>" in docstrings. Not all symbols have AGENTESE paths—only exposed nodes do.

**Evidence**: `test_extractor.py::test_agentese_path_extraction`

---

### DocNode
*Module: services.living_docs.types*

related_symbols should be kept small (max 5). Too many cross-references makes navigation confusing.

**Evidence**: `test_types.py::test_related_symbols_limit`

---

### extractor
*Module: services.living_docs.extractor*

AST parsing requires valid Python syntax.

**Evidence**: `test_extractor.py::test_invalid_syntax`

---

### DocstringExtractor
*Module: services.living_docs.extractor*

Tier determination now includes agents/ and protocols/ as RICH.

**Evidence**: `test_extractor.py::test_tier_rich_expanded`

---

### generator
*Module: services.living_docs.generator*

generate_to_directory() creates directories if they don't exist. It will NOT overwrite existing files unless overwrite=True.

**Evidence**: `test_generator.py::test_no_overwrite_by_default`

---

### hydrator
*Module: services.living_docs.hydrator*

hydrate_context() is keyword-based, not semantic. Use Brain vectors for semantic similarity (future work).

**Evidence**: `test_hydrator.py::test_keyword_matching`

---

### hydrator
*Module: services.living_docs.hydrator*

Voice anchors are curated, not mined. They come from _focus.md, not git history.

**Evidence**: `test_hydrator.py::test_voice_anchors`

---

### HydrationContext
*Module: services.living_docs.hydrator*

to_markdown() output is designed for system prompts. It's not a reference doc—it's a focus lens.

**Evidence**: `test_hydrator.py::test_markdown_format`

---

### Hydrator
*Module: services.living_docs.hydrator*

Hydrator prefers keyword matching; Brain is supplemental. Semantic matching is best-effort—graceful degradation if unavailable.

**Evidence**: `test_hydrator.py::test_keyword_extraction`

---

### projector
*Module: services.living_docs.projector*

Projection is a single function, not a class hierarchy.

**Evidence**: `test_projector.py::test_single_function`

---

### projector
*Module: services.living_docs.projector*

Density only applies to human observers.

**Evidence**: `test_projector.py::test_density_human_only`

---

### spec_extractor
*Module: services.living_docs.spec_extractor*

Spec files have different structure than Python docstrings. Use markdown-aware parsing, not AST.

**Evidence**: `test_spec_extractor.py::test_markdown_structure`

---

### SpecExtractor
*Module: services.living_docs.spec_extractor*

The extractor processes spec/ files, not impl/ Python files. Use DocstringExtractor for Python, SpecExtractor for markdown.

**Evidence**: `test_spec_extractor.py::test_file_type_separation`

---

### linter
*Module: services.living_docs.linter*

Only lint public symbols (no _ prefix). Private helpers don't need documentation.

**Evidence**: `test_linter.py::test_skip_private_symbols`

---

### linter
*Module: services.living_docs.linter*

AST parsing fails gracefully—returns empty results, not exceptions. Invalid Python is already caught by ruff.

**Evidence**: `test_linter.py::test_invalid_syntax_graceful`

---

### DocstringLinter
*Module: services.living_docs.linter*

The linter uses AST, not runtime imports. This means it can lint broken code without crashes.

**Evidence**: `test_linter.py::test_lint_broken_imports`

---

### brain_adapter
*Module: services.living_docs.brain_adapter*

Brain requires async session; Hydrator is sync. Use asyncio.run() or async API for integration.

**Evidence**: `test_brain_adapter.py::TestSemanticTeaching::test_returns_teaching_from_brain_results`

---

### brain_adapter
*Module: services.living_docs.brain_adapter*

Brain may return empty if no crystals exist. Fall back to keyword matching gracefully.

**Evidence**: `test_brain_adapter.py::TestSemanticTeaching::test_returns_empty_without_brain`

---

### service
*Module: services.interactive_text.service*

Toggle requires EITHER file_path OR text, not both. When using file mode, you need file_path + (task_id OR line_number). Text mode needs text + line_number. Mixing modes or missing required params returns error response with success=False.

**Evidence**: `test_properties.py::TestProperty6DocumentPolynomialStateValidity`

---

### registry
*Module: services.interactive_text.registry*

TokenRegistry uses ClassVar—singleton pattern with class-level state. All instances share _tokens dict. Use clear() between tests.

**Evidence**: `test_registry.py::test_register_duplicate_raises`

---

### registry
*Module: services.interactive_text.registry*

_ensure_initialized() is lazy—core tokens not registered until first get(). Call get_all() or recognize() to trigger initialization.

**Evidence**: `test_registry.py::test_core_tokens_lazy_init`

---

### registry
*Module: services.interactive_text.registry*

recognize() returns sorted by (position, -priority)—priority breaks ties. Higher priority wins when patterns overlap at same position.

**Evidence**: `test_registry.py::test_priority_ordering`

---

### registry
*Module: services.interactive_text.registry*

register() raises ValueError on duplicate; use register_or_replace() for updates. This prevents accidental token definition clobbering.

**Evidence**: `test_registry.py::test_register_or_replace`

---

### events
*Module: services.interactive_text.events*

DocumentEventBus.emit() uses asyncio.create_task—fire-and-forget. Handlers run in background; emit() returns immediately.

**Evidence**: `test_properties.py::test_event_emission_non_blocking`

---

### events
*Module: services.interactive_text.events*

Buffer is bounded (DEFAULT_BUFFER_SIZE=1000)—old events are dropped. replay() only sees events still in buffer; don't rely on full history.

**Evidence**: `test_properties.py::test_buffer_eviction`

---

### events
*Module: services.interactive_text.events*

get_document_event_bus() returns global singleton—reset between tests. Call reset_document_event_bus() in test fixtures to avoid state leakage.

**Evidence**: `test_properties.py::test_global_bus_reset`

---

### __init__
*Module: services.interactive_text.__init__*

Six core token types are lazy-registered via TokenRegistry._ensure_initialized(). First call to get()/recognize() triggers registration of CORE_TOKEN_DEFINITIONS.

**Evidence**: `test_registry.py::test_core_tokens_registered`

---

### __init__
*Module: services.interactive_text.__init__*

DocumentPolynomial is stateless—state lives in caller, not polynomial. Each transition() call takes state as input, returns (new_state, output).

**Evidence**: `test_properties.py::test_polynomial_stateless`

---

### __init__
*Module: services.interactive_text.__init__*

DocumentSheaf.glue() requires compatible local views—SheafConditionError if conflict. Verify sheaf conditions before attempting multi-view merge.

**Evidence**: `test_properties.py::test_sheaf_conflict_detection`

---

### parser
*Module: services.interactive_text.parser*

Token priority determines winner on overlap. When two patterns match overlapping text (e.g., nested backticks with AGENTESE path inside), _remove_overlapping_matches() keeps the match with HIGHER priority. Sort order is: (start_pos, -priority) so higher priority wins at same position.

**Evidence**: `test_parser.py::TestEdgeCases::test_nested_backticks`

---

### parser
*Module: services.interactive_text.parser*

IncrementalParser expands affected region to line boundaries. When applying edits, _find_affected_region() extends start backward to previous newline and end forward to next newline. This prevents partial token corruption but means even small edits may re-parse entire lines.

**Evidence**: `test_parser.py::TestIncrementalParser::test_edit_preserves_tokens_before`

---

### contracts
*Module: services.interactive_text.contracts*

Observer.capabilities is frozenset—immutable by design. Create new Observer with updated capabilities, don't mutate.

**Evidence**: `test_contracts.py::test_observer_immutability`

---

### contracts
*Module: services.interactive_text.contracts*

InteractionResult.not_available() vs failure()—semantic difference. not_available = affordance disabled; failure = execution error.

**Evidence**: `test_contracts.py::test_interaction_result_types`

---

### node
*Module: services.interactive_text.node*

The node depends on "interactive_text_service" in the DI container. If this dependency isn't registered in providers.py, the node will be SILENTLY SKIPPED during gateway setup. No error, just missing paths.

**Evidence**: `test_agentese_path.py::TestAGENTESEPathTokenCreation::test_create_token`

---

### node
*Module: services.interactive_text.node*

Archetype-based affordances: developer/operator/admin/editor get full access (parse + task_toggle). architect/researcher get parse only. Everyone else (guest) gets parse only. Case-insensitive matching.

**Evidence**: `test_agentese_path.py::TestAGENTESEPathActions::test_right_click_admin_has_edit`

---

### node
*Module: services.interactive_text.node*

_invoke_aspect returns DICT, not Renderable. The rendering classes (ParseRendering, TaskToggleRendering) call .to_dict() immediately. This is for JSON serialization compatibility with the API layer.

**Evidence**: `test_agentese_path.py::TestAGENTESEPathProjection::test_project_json`

---

### polynomial
*Module: services.interactive_text.polynomial*

Invalid inputs return (same_state, NoOp), NOT an exception. The polynomial is total—every (state, input) pair produces a valid output. Check the output type to detect invalid transitions: isinstance(output, NoOp).

**Evidence**: `test_properties.py::TestProperty6DocumentPolynomialStateValidity::test_invalid_inputs_produce_noop`

---

### polynomial
*Module: services.interactive_text.polynomial*

The polynomial is STATELESS—it defines the transition function, not current state. DocumentSheaf or your own state holder tracks actual document state. DocumentPolynomial.transition(state, input) is a pure function.

**Evidence**: `test_properties.py::TestProperty6DocumentPolynomialStateValidity::test_transitions_are_deterministic`

---

### polynomial
*Module: services.interactive_text.polynomial*

Each state has a FIXED set of valid directions. VIEWING accepts {edit, refresh, hover, click, drag}. EDITING accepts {save, cancel, continue_edit, hover}. SYNCING accepts {wait, force_local, force_remote}. CONFLICTING accepts {resolve, abort, view_diff}. Sending wrong input to wrong state → NoOp.

**Evidence**: `test_properties.py::TestProperty6DocumentPolynomialStateValidity::test_viewing_state_accepts_correct_inputs`

---

### polynomial
*Module: services.interactive_text.polynomial*

TransitionOutput subclasses are FROZEN dataclasses. Once created, they're immutable. This enables safe composition and prevents state corruption when outputs are passed between components.

**Evidence**: `test_properties.py::TestProperty6DocumentPolynomialStateValidity::test_transition_outputs_are_serializable`

---

### sheaf
*Module: services.interactive_text.sheaf*

TokenState equality compares (token_id, token_type, content, position) but IGNORES metadata. Two tokens with different metadata but same core fields are considered equal. This is intentional—metadata is view-local decoration.

**Evidence**: `test_properties.py::TestProperty8DocumentSheafCoherence::test_token_state_equality`

---

### sheaf
*Module: services.interactive_text.sheaf*

compatible() is SYMMETRIC: compatible(v1, v2) == compatible(v2, v1). Same for overlap(). But verify_sheaf_condition() checks ALL pairs, not just the ones you pass in. Adding a third view requires checking 3 pairs.

**Evidence**: `test_properties.py::TestProperty8DocumentSheafCoherence::test_compatible_is_symmetric`

---

### sheaf
*Module: services.interactive_text.sheaf*

Views for DIFFERENT documents cannot be added to the same sheaf. add_view() raises ValueError if view.document_path != sheaf.document_path. Create separate sheafs per document.

**Evidence**: `sheaf.py::DocumentSheaf::add_view validation`

---

### base
*Module: services.interactive_text.projectors.base*

DensityParams.for_density() is the canonical way to get parameters. Don't hardcode padding/font_size—use DENSITY_PARAMS lookup.

**Evidence**: `test_projectors.py::test_density_params_lookup`

---

### base
*Module: services.interactive_text.projectors.base*

_compose() is abstract and target-specific: CLI joins with newlines, JSON wraps in arrays, Web nests components. Override per target.

**Evidence**: `test_projectors.py::test_cli_compose_newlines`

---

### agentese_path
*Module: services.interactive_text.tokens.agentese_path*

Ghost tokens (non-existent paths) still render but with reduced affordances. is_ghost=True disables invoke/navigate; shows "not yet implemented".

**Evidence**: `test_agentese_path.py::test_ghost_token_affordances`

---

### agentese_path
*Module: services.interactive_text.tokens.agentese_path*

Path validation uses regex matching context (world|self|concept|void|time). Invalid context prefix won't match—token won't be recognized.

**Evidence**: `test_agentese_path.py::test_path_validation`

---

### agentese_path
*Module: services.interactive_text.tokens.agentese_path*

_check_path_exists() is async and may hit registry—cache results. Repeated hover events should not repeatedly query path existence.

**Evidence**: `test_agentese_path.py::test_path_check_caching`

---

### base
*Module: services.interactive_text.tokens.base*

on_interact() validates affordances BEFORE calling _execute_action. Order matters: check enabled + action match, THEN execute.

**Evidence**: `test_tokens_base.py::test_on_interact_validates_affordance`

---

### base
*Module: services.interactive_text.tokens.base*

capture_trace defaults to True—every interaction creates a TraceWitness. Set capture_trace=False for high-frequency operations (hover spam).

**Evidence**: `test_tokens_base.py::test_capture_trace_default`

---

### base
*Module: services.interactive_text.tokens.base*

token_id uses source_position (start:end), NOT content hash. Renumbering or editing document invalidates existing token IDs.

**Evidence**: `test_tokens_base.py::test_token_id_format`

---

### base
*Module: services.interactive_text.tokens.base*

filter_affordances_by_observer returns DISABLED affordances, not empty. UI can show "locked" affordances with capability requirements.

**Evidence**: `test_tokens_base.py::test_filter_affordances_disabled`

---

### stigmergy
*Module: services.liminal.coffee.stigmergy*

Pheromone field is in-memory by default. Persist to D-gent for cross-session stigmergy.

**Evidence**: `test_voice_stigmergy.py::test_field_persists`

---

### stigmergy
*Module: services.liminal.coffee.stigmergy*

Decay rate is 5% per day (0.002 per hour). This matches the spec's "reinforcement vs decay" balance.

**Evidence**: `test_voice_stigmergy.py::TestPheromoneDecay::test_daily_decay_reduces_intensity`

---

### circadian
*Module: services.liminal.coffee.circadian*

Day-of-week matters more than raw recency. Monday mornings resonate with Monday mornings.

**Evidence**: `test_circadian.py::test_weekday_resonance`

---

### circadian
*Module: services.liminal.coffee.circadian*

FOSSIL layer (> 14 days) is the serendipity goldmine. Recent voices are too familiar; ancient ones surprise.

**Evidence**: `test_circadian.py::test_fossil_serendipity`

---

### generative_loop
*Module: services.verification.generative_loop*

Roundtrip may LOSE nodes during compression if node count is small. The compression allows up to 50% node loss for small topologies (<=2 nodes). This is intentional - consolidation is valid compression.

**Evidence**: `test_generative_loop.py::TestGenerativeLoopRoundTrip::test_roundtrip_preserves_node_count`

---

### generative_loop
*Module: services.verification.generative_loop*

Refinement increments the PATCH version, not major/minor. Version goes from 1.0.0 to 1.0.1 after refinement. This is semantic versioning for specs - refinements are backwards compatible.

**Evidence**: `test_generative_loop.py::TestSpecRefinement::test_refine_increments_version`

---

### categorical_checker
*Module: services.verification.categorical_checker*

Functor verification may return DIFFERENT law names for different checks. Check for law_name in ["functor_laws", "functor_identity", "functor_composition"] rather than exact equality.

**Evidence**: `test_categorical_checker.py::TestFunctorLaws::test_functor_verification_returns_result`

---

### ProviderConfig
*Module: services.morpheus.gateway*

The `public` flag controls visibility to non-admin observers. Private providers (public=False) still work but aren't listed for guests. Use for internal/experimental providers.

**Evidence**: `test_node.py::TestMorpheusNodeProviders`

---

### GatewayConfig
*Module: services.morpheus.gateway*

Limits are PER-MINUTE sliding windows, not hard resets. A burst of 10 requests will block for ~60s, not until the next minute boundary.

**Evidence**: `test_rate_limit.py::TestRateLimitState`

---

### RateLimitState
*Module: services.morpheus.gateway*

Each archetype has its OWN window. Exhausting "guest" limits does not affect "admin" limits. This is by design—archetypes represent trust levels, not resource pools.

**Evidence**: `test_rate_limit.py::test_check_and_record_separate_archetypes`

---

### RateLimitState
*Module: services.morpheus.gateway*

The sliding window implementation means old entries are pruned on EVERY check. High-traffic archetypes may see O(n) cleanup cost. For production at scale, consider external rate limiting (Redis).

**Evidence**: `test_rate_limit.py::TestRateLimitState`

---

### RateLimitError
*Module: services.morpheus.gateway*

The `retry_after` field is a HINT, not a guarantee. The sliding window may clear sooner if earlier requests age out. Clients should use exponential backoff, not fixed waits.

**Evidence**: `test_rate_limit.py::TestRateLimitError`

---

### RateLimitError
*Module: services.morpheus.gateway*

In streaming mode, rate limit errors are YIELDED as content, not raised. Check the first chunk for "Rate limit exceeded".

**Evidence**: `test_rate_limit.py::test_stream_respects_rate_limit`

---

### MorpheusGateway
*Module: services.morpheus.gateway*

Providers are matched by PREFIX, first match wins. Register more specific prefixes BEFORE generic ones. "claude-3-opus" before "claude-".

**Evidence**: `test_rate_limit.py::TestGatewayRateLimiting`

---

### MorpheusGateway
*Module: services.morpheus.gateway*

The gateway is stateless except for rate limiting. Provider registration order matters for matching, but requests are independent.

**Evidence**: `test_node.py::TestMorpheusNodeComplete`

---

### CompletionResult
*Module: services.morpheus.persistence*

`latency_ms` includes network and processing time, not just LLM inference. For streaming, this is total time from request to last chunk.

**Evidence**: `test_streaming.py::TestPersistenceStreaming`

---

### ProviderStatus
*Module: services.morpheus.persistence*

`available` is checked at query time via adapter.is_available(). This may involve network calls—cache results if calling frequently.

**Evidence**: `test_node.py::TestMorpheusNodeProviders`

---

### ProviderStatus
*Module: services.morpheus.persistence*

`request_count` comes from the adapter's health_check(), not the gateway's counters. Adapters track their own metrics independently.

**Evidence**: `test_node.py::test_admin_sees_all_providers`

---

### MorpheusStatus
*Module: services.morpheus.persistence*

`healthy` is True when AT LEAST ONE provider is available. This means "degraded but functional"—not "fully healthy". Check providers_healthy vs providers_total for full picture.

**Evidence**: `test_node.py::TestMorpheusNodeManifest`

---

### MorpheusStatus
*Module: services.morpheus.persistence*

`uptime_seconds` is from MorpheusPersistence creation, not system boot. Each persistence instance tracks its own uptime.

**Evidence**: `test_node.py::test_manifest_returns_status`

---

### MorpheusPersistence
*Module: services.morpheus.persistence*

Telemetry is ENABLED by default. Pass telemetry_enabled=False for tests to avoid OTEL overhead and side effects.

**Evidence**: `test_streaming.py::persistence_with_streaming`

---

### MorpheusPersistence
*Module: services.morpheus.persistence*

This class accesses gateway._providers and gateway._route_model() which are private. This is intentional—persistence OWNS the gateway and needs internal access for telemetry tagging.

**Evidence**: `test_node.py::TestMorpheusNodeProviders`

---

### MorpheusMetricsState
*Module: services.morpheus.observability*

This is SEPARATE from OTEL counters. reset_morpheus_metrics() clears this state but OTEL counters keep incrementing.

**Evidence**: `test_observability.py - if exists`

---

### MorpheusMetricsState
*Module: services.morpheus.observability*

The _lock is per-instance but the global _state is a singleton. All record_* functions share this lock—contention possible at scale.

**Evidence**: `persistence.py record_completion calls`

---

### MorpheusTelemetry
*Module: services.morpheus.observability*

The context managers are async but use sync tracer.start_as_current_span. This is intentional—OTEL spans are sync, only our I/O is async.

**Evidence**: `persistence.py::complete uses trace_completion`

---

### MorpheusTelemetry
*Module: services.morpheus.observability*

Duration is recorded in the finally block, so it includes error handling time. For precise LLM latency, check provider metrics.

**Evidence**: `test_observability.py::test_tracing - if exists`

---

### ChatMessage
*Module: services.morpheus.types*

The `name` field is ONLY for function calls, not user display names. Using it for other purposes may confuse downstream providers.

**Evidence**: `test_streaming.py::TestMockAdapterStreaming`

---

### ChatRequest
*Module: services.morpheus.types*

The `stream` flag is informational here—streaming is controlled by which method you call (complete vs stream), not by this flag.

**Evidence**: `test_streaming.py::TestGatewayStreaming`

---

### ChatRequest
*Module: services.morpheus.types*

The `user` field is for rate limiting correlation, not auth. Use observer archetype for access control, user for per-user limits.

**Evidence**: `test_rate_limit.py::TestGatewayRateLimiting`

---

### Usage
*Module: services.morpheus.types*

For streaming, token counts are ESTIMATES unless the provider sends a final usage summary. Don't rely on exact counts during stream.

**Evidence**: `test_streaming.py::TestStreamChunk`

---

### ChatResponse
*Module: services.morpheus.types*

The `id` field is generated uniquely per response. Use it for correlating logs and telemetry across the request lifecycle.

**Evidence**: `test_streaming.py::test_to_dict_serialization`

---

### MorpheusError
*Module: services.morpheus.types*

Error types match OpenAI: "invalid_request_error", "rate_limit_error", "authentication_error", "server_error". Use these for client compatibility.

**Evidence**: `test_rate_limit.py::TestRateLimitError`

---

### StreamDelta
*Module: services.morpheus.types*

Both `role` and `content` can be None in the same delta—this is valid for the final chunk. Check for finish_reason instead.

**Evidence**: `test_streaming.py::test_final_creates_finish_chunk`

---

### StreamChoice
*Module: services.morpheus.types*

`finish_reason` is ONLY set on the final chunk. During streaming, all chunks have finish_reason=None until the last one.

**Evidence**: `test_streaming.py::test_stream_returns_chunks`

---

### StreamChunk
*Module: services.morpheus.types*

All chunks in a stream share the SAME `id`. Use this to group chunks from the same completion. Don't use it for uniqueness.

**Evidence**: `test_streaming.py::test_from_text_creates_chunk`

---

### StreamChunk
*Module: services.morpheus.types*

Use to_sse() for Server-Sent Events format. The trailing \n\n is required by SSE spec—don't strip it.

**Evidence**: `test_streaming.py::test_to_sse_format`

---

### MorpheusManifestResponse
*Module: services.morpheus.contracts*

These contract types are for AGENTESE OpenAPI schema generation. They are NOT the same as the internal types in types.py/persistence.py.

**Evidence**: `node.py uses MorpheusManifestRendering, not this`

---

### CompleteRequest
*Module: services.morpheus.contracts*

`messages` is a list of dicts, not ChatMessage objects. The node converts these to ChatMessage internally.

**Evidence**: `node.py::_handle_complete converts dicts`

---

### CompleteResponse
*Module: services.morpheus.contracts*

`response` is the extracted text, not the full ChatResponse. Use world.morpheus.manifest to see detailed response metadata.

**Evidence**: `node.py::_handle_complete extracts response_text`

---

### StreamRequest
*Module: services.morpheus.contracts*

Same structure as CompleteRequest, but the node sets stream=True internally and returns an async generator instead of a response.

**Evidence**: `node.py::_handle_stream sets request.stream = True`

---

### StreamResponse
*Module: services.morpheus.contracts*

The actual content is delivered via SSE, not in this response. This is just metadata confirming the stream started.

**Evidence**: `node.py::_handle_stream returns stream generator`

---

### ProvidersResponse
*Module: services.morpheus.contracts*

The `filter` field indicates which filter was applied based on observer archetype: "all" (admin), "enabled" (dev), "public" (guest).

**Evidence**: `test_node.py::TestMorpheusNodeProviders`

---

### MetricsResponse
*Module: services.morpheus.contracts*

This aspect requires "developer" or "admin" archetype. Guests calling metrics get a Forbidden error.

**Evidence**: `test_node.py::TestMorpheusNodeMetrics`

---

### HealthResponse
*Module: services.morpheus.contracts*

"healthy" means at least one provider is available—not that all are. "degraded" = some providers down, "unhealthy" = all providers down.

**Evidence**: `test_node.py::TestMorpheusNodeHealth`

---

### RouteRequest
*Module: services.morpheus.contracts*

This is a query aspect, not a mutation. It tells you WHERE a model would route without actually making a request.

**Evidence**: `test_node.py::TestMorpheusNodeRoute`

---

### RouteResponse
*Module: services.morpheus.contracts*

`available` is false if no provider matches the model prefix. Check `available` before making a complete/stream request.

**Evidence**: `test_node.py::test_route_for_unknown_model`

---

### RateLimitResponse
*Module: services.morpheus.contracts*

`reset_at` is a timestamp hint, not a guarantee. Sliding window limits may clear earlier as old requests age out.

**Evidence**: `gateway.py RateLimitState uses 60s sliding window`

---

### MorpheusManifestRendering
*Module: services.morpheus.node*

This is a Renderable, not a Response. It has both to_dict() and to_text() for multi-target projection (JSON/CLI/TUI).

**Evidence**: `test_node.py::TestMorpheusNodeManifest`

---

### CompletionRendering
*Module: services.morpheus.node*

The `response_text` is extracted from choices[0].message.content. Multi-choice completions (n>1) are not yet supported in rendering.

**Evidence**: `test_node.py::TestMorpheusNodeComplete`

---

### ProvidersRendering
*Module: services.morpheus.node*

The `filter_applied` field indicates which filter was used: "all" (admin), "enabled" (developer), or "public" (guest). Use this to explain why some providers aren't visible.

**Evidence**: `test_node.py::TestMorpheusNodeProviders`

---

### MorpheusNode
*Module: services.morpheus.node*

The `morpheus_persistence` dependency is injected by the DI container. If it's not registered in providers.py, you'll get None and all aspects will return error dicts.

**Evidence**: `test_node.py::TestMorpheusNodeHandle`

---

### MorpheusNode
*Module: services.morpheus.node*

Observer archetype determines affordances AND filtering. A "guest" calling "providers" gets filtered results, not an error. An error only occurs for truly forbidden aspects like "configure".

**Evidence**: `test_node.py::TestMorpheusNodeAffordances`

---

### MorpheusNode
*Module: services.morpheus.node*

The stream aspect returns a dict with a generator, not raw SSE. The transport layer (HTTP/CLI) is responsible for iterating.

**Evidence**: `test_streaming.py::TestPersistenceStreaming`

---

### obligation
*Module: services.ashc.obligation*

Context extraction is bounded to 5 lines. Large tracebacks would bloat obligations and slow proof search. Prefer relevant excerpts over complete dumps.

---

### obligation
*Module: services.ashc.obligation*

Assertion parsing is pattern-based, not AST-based. This is intentional—we want readable properties, not compiled forms.

---

### persistence
*Module: services.ashc.persistence*

find_related() increments usage_count for returned lemmas. This is intentional—lemmas that help more become more visible.

**Evidence**: `test_lemma_db.py::test_stigmergic_reinforcement`

---

### persistence
*Module: services.ashc.persistence*

store() is idempotent on id. If a lemma with the same id exists, it's updated (not duplicated). This supports proof regeneration.

**Evidence**: `test_lemma_db.py::test_store_idempotent`

---

### persistence
*Module: services.ashc.persistence*

Keyword matching uses simple word overlap for now. Brain vectors are deferred to Phase 5 for semantic similarity.

**Evidence**: `test_lemma_db.py::test_keyword_matching`

---

### PostgresLemmaDatabase
*Module: services.ashc.persistence*

PostgresLemmaDatabase is stateless between calls. All state is in the database. Safe for concurrent access.

**Evidence**: `test_lemma_db.py::test_concurrent_access`

---

### contracts
*Module: services.ashc.contracts*

All contracts are frozen dataclasses. Create new instances with updated fields, don't mutate existing ones. This enables safe composition and audit trails.

---

### ProofStatus
*Module: services.ashc.contracts*

Use auto() for status values—we care about the semantic meaning, not the underlying integer. Comparison is by enum member, not value.

---

### ProofObligation
*Module: services.ashc.contracts*

ProofObligation is immutable. Create new obligations with updated context, don't mutate existing ones. Example: >>> obl = ProofObligation( ... id=ObligationId("obl-001"), ... property="∀ x: int. x + 0 == x", ... source=ObligationSource.TEST, ... source_location="test_math.py:42", ... ) >>> obl.property '∀ x: int. x + 0 == x'

---

### ProofAttempt
*Module: services.ashc.contracts*

We store failed attempts too—they inform future searches. "What didn't work" is as valuable as "what worked." The tactics_that_failed set helps avoid repeating mistakes. Laws: 1. Attempts are immutable records 2. Failed attempts inform future searches (stigmergic learning) 3. duration_ms enables performance analysis

---

### VerifiedLemma
*Module: services.ashc.contracts*

VerifiedLemma includes the full proof—not just the statement. This enables proof reuse and composition.

---

### ProofSearchResult
*Module: services.ashc.contracts*

ProofSearchResult is the ONLY mutable contract. It accumulates attempts during search, then becomes effectively immutable once search completes.

---

### ProofSearchConfig
*Module: services.ashc.contracts*

Tactic progressions are tuples (immutable). Quick phase uses simple tactics; deeper phases add more sophisticated ones.

---

### ProofSearchConfig
*Module: services.ashc.contracts*

Temperature is a hyper-parameter for LLM proof generation. Lower (0.1-0.3) for deterministic proofs, higher (0.5-0.7) for creative exploration. Not hardcoded per Kent's decision.

---

### CheckerResult
*Module: services.ashc.contracts*

Dafny outputs to stderr even on success. Parse exit code, not output presence, to determine success.

---

### search
*Module: services.ashc.search*

Temperature is a hyper-parameter in ProofSearchConfig, not hardcoded. Different obligations may benefit from different temperatures.

**Evidence**: `test_search.py::test_temperature_configurable`

---

### search
*Module: services.ashc.search*

Failed tactics are tracked SEPARATELY, not in obligation.context. This enables cross-attempt learning without bloating obligations.

**Evidence**: `test_search.py::test_failed_tactics_not_repeated`

---

### LemmaDatabase
*Module: services.ashc.search*

Protocol > ABC for interfaces. Enables duck typing without inheritance coupling. See meta.md: "Protocol > ABC"

---

### InMemoryLemmaDatabase
*Module: services.ashc.search*

This is a STUB, not the final implementation. It stores lemmas in memory only—they're lost on restart. Phase 4 adds D-gent persistence.

---

### ProofSearcher
*Module: services.ashc.search*

The searcher is stateless between calls. Each search() invocation is independent. Failed tactics are tracked PER SEARCH, not across searches.

**Evidence**: `test_search.py::test_searcher_stateless`

---

### ProofSearcher
*Module: services.ashc.search*

Budget is ATTEMPTS, not wall time. A slow checker can exhaust budget quickly. Monitor avg_attempt_duration_ms. (Evidence: test_search.py::test_budget_is_attempt_count) Example: >>> searcher = ProofSearcher(gateway, checker, lemma_db) >>> obl = ProofObligation(property="∀ x. x == x", ...) >>> result = await searcher.search(obl) >>> if result.succeeded: ... print(f"Proved! Lemma: {result.lemma.statement}")

---

### checker
*Module: services.ashc.checker*

Dafny outputs to stderr even on success. Parse exit code, not output presence, to determine success.

---

### checker
*Module: services.ashc.checker*

Set process timeouts to prevent zombie processes.

---

### checker
*Module: services.ashc.checker*

Z3 timeouts are unreliable. Use resource limits instead of time limits for Dafny/Verus. Timeouts may not be respected.

---

### checker
*Module: services.ashc.checker*

Lean4 requires `lake env lean` for project files, not bare `lean`. The bare command won't find project dependencies.

---

### checker
*Module: services.ashc.checker*

Platform non-determinism: Same proof may verify on macOS but timeout on Linux due to Z3 behavior differences.

---

### ProofChecker
*Module: services.ashc.checker*

Protocol > ABC for interfaces. Enables duck typing without inheritance coupling. See meta.md: "Protocol > ABC"

---

### DafnyChecker
*Module: services.ashc.checker*

Dafny outputs to stderr even on success. Parse exit code, not output presence, to determine success.

---

### DafnyChecker
*Module: services.ashc.checker*

Use asyncio.create_subprocess_exec, not subprocess.run, to avoid blocking the event loop.

---

### DafnyChecker
*Module: services.ashc.checker*

Noisy error cascades—first error message is the key one.

---

### MockChecker
*Module: services.ashc.checker*

Use DI pattern (inject checker) rather than mocking. This mock checker IS the test double.

---

### CheckerRegistry
*Module: services.ashc.checker*

Lazy initialization—don't instantiate checkers until needed. This avoids startup cost when checkers aren't used.

---

### Lean4Checker
*Module: services.ashc.checker*

Use 'lake env lean' not just 'lean' to get correct environment.

---

### Lean4Checker
*Module: services.ashc.checker*

Proofs containing 'sorry' are incomplete—treat as FAILED.

---

### Lean4Checker
*Module: services.ashc.checker*

Lean uses unicode (∀, →, ×); ensure UTF-8 encoding.

---

### VerusChecker
*Module: services.ashc.checker*

Verus requires Rust toolchain; may need rustup setup.

---

### VerusChecker
*Module: services.ashc.checker*

Z3 timeouts are unreliable. May diverge regardless of limit.

---

### VerusChecker
*Module: services.ashc.checker*

cargo verus verify --error-format=json is broken (Issue #1572). Use direct verus invocation for structured error output. Example: >>> checker = VerusChecker() >>> if checker.is_available: ... result = await checker.check("proof fn trivial() ensures true {}") ... assert result.success

---

### primitives
*Module: agents.poly.primitives*

All state Enums follow the pattern: initial state, intermediate states, terminal state(s). The directions function uses this to control valid inputs per state.

**Evidence**: `test_primitives.py::TestPrimitiveProperties::test_all_primitives_have_directions`

---

### primitives
*Module: agents.poly.primitives*

PRIMITIVES is a registry dict, not a list. Use get_primitive("id") to retrieve by name, not PRIMITIVES[0].

**Evidence**: `test_primitives.py::TestPrimitiveRegistry::test_get_primitive_by_name`

---

### primitives
*Module: agents.poly.primitives*

The primitive module imports from .protocol—if you see circular import errors, check that protocol.py doesn't import primitives.

**Evidence**: `test_primitives.py::TestPrimitiveRegistry::test_all_17_primitives_registered`

---

### PolyAgentProtocol
*Module: agents.poly.protocol*

This is a typing.Protocol, not ABC. Use isinstance() checks with @runtime_checkable, not inheritance verification.

**Evidence**: `test_protocol.py::TestPolyAgentConstruction`

---

### PolyAgentProtocol
*Module: agents.poly.protocol*

The directions function returns valid inputs for each state. This enables MODE-DEPENDENT behavior—the key polynomial insight. Different states accept different inputs.

**Evidence**: `test_protocol.py::TestStateDependentBehavior`

---

### PolyAgent
*Module: agents.poly.protocol*

PolyAgent[S,A,B] > Agent[A,B] because state enables mode-dependent behavior. A stateless agent is just PolyAgent[str, A, B] with positions={"ready"}.

**Evidence**: `test_protocol.py::test_stateless_agent_type_alias`

---

### PolyAgent
*Module: agents.poly.protocol*

Use frozenset({Any}) in _directions to accept any input. The _accepts_input helper checks for Any type marker.

**Evidence**: `test_protocol.py::test_identity_construction`

---

### PolyAgent
*Module: agents.poly.protocol*

invoke() validates state and input BEFORE calling transition. Invalid state/input raises ValueError, not silent failure.

**Evidence**: `test_protocol.py::test_invoke_invalid_state_raises`

---

### WiringDiagram
*Module: agents.poly.protocol*

compose() creates a new PolyAgent with PRODUCT state space. If left has 3 states and right has 4, composed has 12 states.

**Evidence**: `test_protocol.py::TestWiringDiagram`

---

### WiringDiagram
*Module: agents.poly.protocol*

Output of left feeds into input of right. This is sequential composition. For parallel (same input to both), use parallel().

**Evidence**: `test_protocol.py::TestSequentialComposition`

---

### PolyAgentWrapper
*Module: agents.poly.protocol*

State is MUTABLE in the wrapper (via self._state). The underlying PolyAgent is immutable, but the wrapper tracks current state across invocations.

**Evidence**: `test_protocol.py::test_to_bootstrap_agent_stateful`

---

### types
*Module: agents.poly.types*

Agent is a Protocol, not a base class. Use structural typing. Don't inherit from Agent—implement the invoke() method.

**Evidence**: `test_protocol.py::test_agent_structural_typing`

---

### types
*Module: agents.poly.types*

ComposedAgent flattens automatically. (a >> b) >> c = a >> (b >> c). This is associativity. Verify with BootstrapWitness.verify_composition_laws().

**Evidence**: `test_primitives.py::test_composition_associativity`

---

### types
*Module: agents.poly.types*

Type variables A_contra and B_co have variance for Protocol correctness. Using invariant type vars in Protocol causes mypy errors.

**Evidence**: `test_protocol.py::test_variance_correctness`

---

### algebra
*Module: agents.operad.algebra*

CLIAlgebra.to_cli() requires an agent_resolver to map names to agents. The default resolver uses poly.get_primitive(). If your agents aren't registered primitives, provide a custom resolver or you'll get None.

**Evidence**: `Structural - _default_resolver calls get_primitive`

---

### algebra
*Module: agents.operad.algebra*

Command names are auto-generated from operad name + operation name. The operad name is lowercased and "operad" is stripped, so "SoulOperad" + "introspect" becomes "kg soul introspect". (Evidence: Structural - to_cli() line 133)

---

### core
*Module: agents.operad.core*

Operations require EXACT arity. An Operation with arity=2 rejects 1 or 3 arguments with ValueError, even if semantically valid.

**Evidence**: `test_core.py::TestOperation::test_operation_wrong_arity_raises`

---

### core
*Module: agents.operad.core*

State composition via seq/par creates NESTED tuple states. Left-assoc seq(seq(a,b),c) gives state ((s_a,s_b),s_c), right-assoc gives (s_a,(s_b,s_c)). Results are equivalent but state shapes differ.

**Evidence**: `test_core.py::TestCompositionLaws::test_seq_associativity_behavioral`

---

### core
*Module: agents.operad.core*

OperadRegistry uses class-level state. For parallel test execution (xdist), call OperadRegistry.reset() + re-import in conftest to ensure clean state.

**Evidence**: `test_xdist_registry_canary.py`

---

### core
*Module: agents.operad.core*

Law verification is STRUCTURAL, not behavioral. verify_law() checks composition structure but doesn't execute with test inputs by default. For behavioral verification, pass agents AND invoke the result.

**Evidence**: `test_core.py::TestLawVerification::test_verify_law_by_name`

---

### soul
*Module: agents.operad.domains.soul*

Domain operads EXTEND the universal AGENT_OPERAD, not replace it. SOUL_OPERAD includes all 5 universal operations (seq, par, branch, fix, trace) PLUS the soul-specific ones. Check for duplicates.

**Evidence**: `test_domains.py::TestSoulOperad::test_has_universal_operations`

---

### soul
*Module: agents.operad.domains.soul*

dialectic uses parallel() then sequential(sublate). The input goes to BOTH thesis and antithesis agents, then their pair output goes to sublation. Don't assume thesis runs before antithesis.

**Evidence**: `test_domains.py::TestSoulOperad::test_dialectic_composes_parallel_then_sublate`

---

### protocol
*Module: agents.sheaf.protocol*

glue() raises GluingError if locals fail compatibility check Compatible means: agents on overlapping contexts produce equivalent outputs on the overlap. Call compatible() first to diagnose issues.

**Evidence**: `test_emergence.py::TestSheafGluing::test_glue_local_souls`

---

### protocol
*Module: agents.sheaf.protocol*

Context is hashable - use as dict key or in sets Context uses frozen capabilities, so it's safe for hash-based containers.

**Evidence**: `test_emergence.py::TestContext::test_context_hashable`

---

### protocol
*Module: agents.sheaf.protocol*

eigenvector_overlap() returns None for non-overlapping contexts No shared capabilities = no overlap. This is expected for disjoint contexts. Use this to detect when gluing is unnecessary.

**Evidence**: `test_emergence.py::TestEigenvectorOverlap::test_no_overlap`

---

### protocol
*Module: agents.sheaf.protocol*

Glued agent positions are UNION of local positions Position "ready" appearing in multiple locals appears once in glued agent. The first-registered local handles dispatch for shared positions.

**Evidence**: `test_emergence.py::TestSheafGluing::test_glued_has_union_positions`

---

### functor
*Module: agents.flux.functor*

Flux.lift() creates a NEW FluxAgent each time. Lifting the same agent twice gives two independent flux instances with separate state. If you need shared state, lift once and reuse the FluxAgent. (Evidence: Structural - lift() calls FluxAgent constructor)

---

### functor
*Module: agents.flux.functor*

Functor law verification is complex for FluxFunctor because it operates on streams. Identity law holds per-element, not for the whole stream. Composition law requires collecting stream outputs.

**Evidence**: `test_integration.py::TestFluxFunctorLaws`

---

### functor
*Module: agents.flux.functor*

FluxFunctor.pure() returns a single-element AsyncIterator, not a FluxAgent. Use it for stream-level identity, not agent lifting.

**Evidence**: `Structural - pure returns async generator`

---

### pipeline
*Module: agents.flux.pipeline*

Pipeline can only be started ONCE. Re-calling start() on a running pipeline raises FluxPipelineError. Create a new pipeline or stop first. (Evidence: Structural - start() checks self._started flag)

---

### pipeline
*Module: agents.flux.pipeline*

stop() stops stages in REVERSE order (last to first). This allows proper draining of intermediate data. If any stage fails to stop, errors are collected and raised as a combined FluxPipelineError.

**Evidence**: `test_pipeline.py::TestPipelineStop::test_stop_all_stages`

---

### pipeline
*Module: agents.flux.pipeline*

Piping a pipeline into another pipeline MERGES them into a single pipeline, not a nested structure. (p1 | p2) has len(p1)+len(p2) stages.

**Evidence**: `test_pipeline.py::TestPipelineCombination::test_pipeline_or_pipeline`

---

### agent
*Module: agents.flux.agent*

invoke() behavior changes based on state. DORMANT = direct call, FLOWING = perturbation injected into stream. Same method, different semantics. Check flux.state before assuming behavior.

**Evidence**: `test_agent.py::TestFluxAgentInvokeOnDormant`

---

### agent
*Module: agents.flux.agent*

Entropy exhaustion causes COLLAPSED state, which is TERMINAL. Unlike STOPPED, you cannot restart from COLLAPSED. Call reset() first, which restores entropy_budget and clears counters.

**Evidence**: `test_agent.py::TestFluxAgentEntropyManagement::test_entropy_collapse`

---

### agent
*Module: agents.flux.agent*

Core processing is EVENT-DRIVEN, not timer-driven. No asyncio.sleep() in _process_flux. If you add polling loops, you're fighting the design. Use event sources and let the stream drive execution.

**Evidence**: `test_agent.py::TestNoAsyncSleepInCore`

---

### errors
*Module: agents.flux.errors*

All Flux exceptions carry a `context` dict with structured data. Don't just catch and log the message - check context for state info, buffer sizes, stage indices, etc. Useful for debugging pipelines.

**Evidence**: `Structural - FluxError.__init__ stores context`

---

### errors
*Module: agents.flux.errors*

FluxStateError contains current_state and attempted_operation fields. When debugging "cannot X from state Y" errors, these tell you exactly what the flux was doing and what you tried to do.

**Evidence**: `Structural - FluxStateError stores these fields`

---

### perturbation
*Module: agents.flux.perturbation*

Perturbation priority ordering is REVERSED for asyncio.PriorityQueue. Higher priority values come FIRST (e.g., priority=100 before priority=10). This is because PriorityQueue is a min-heap, so we flip comparison.

**Evidence**: `test_perturbation.py::TestPerturbationOrdering::test_higher_priority_comes_first`

---

### perturbation
*Module: agents.flux.perturbation*

set_result/set_exception/cancel are IDEMPOTENT. Calling them on an already-done Future is safe (no-op). This prevents race conditions between flux processing and caller cancellation.

**Evidence**: `test_perturbation.py::TestPerturbationResult::test_set_result_idempotent`

---

### perturbation
*Module: agents.flux.perturbation*

create_perturbation() uses priority=100 by default, not 0. This means helper-created perturbations are HIGH priority. If you want normal priority, explicitly pass priority=0.

**Evidence**: `test_perturbation.py::TestCreatePerturbation::test_create_with_data`

---

### state
*Module: agents.flux.state*

COLLAPSED is TERMINAL - no transitions out. Unlike STOPPED (which allows restart via start()), COLLAPSED requires explicit reset() to return to DORMANT. Entropy exhaustion = permanent death.

**Evidence**: `can_transition_to returns empty set for COLLAPSED`

---

### state
*Module: agents.flux.state*

allows_perturbation() is only True for FLOWING state. DORMANT uses direct invoke (not perturbation), PERTURBED rejects (already handling one), and terminal states reject entirely. Check state first.

**Evidence**: `Structural - allows_perturbation implementation`

---

### state
*Module: agents.flux.state*

DRAINING is a transient state between source exhaustion and STOPPED. is_processing() returns True for DRAINING because output buffer may still have items. Wait for STOPPED before assuming completion.

**Evidence**: `Structural - is_processing includes DRAINING`

---

### base
*Module: agents.flux.sources.base*

Sources should be EVENT-DRIVEN, not timer-driven. If your __anext__() uses asyncio.sleep() in a loop to poll, you're doing it wrong. Await the actual event (file watcher, message queue, etc.) instead.

**Evidence**: `Structural - module docstring emphasizes event-driven`

---

### base
*Module: agents.flux.sources.base*

close() is NOT async. If your source needs async cleanup, do it in __aexit__ (the async context manager exit) instead.

**Evidence**: `Structural - close signature is sync`

---

### protocol
*Module: agents.d.protocol*

put() overwrites existing datum with same ID This is intentional for graceful degradation updates, not a bug. Use content-addressed IDs (SHA-256) if you need immutability.

**Evidence**: `test_backends.py::TestPut::test_put_overwrites_existing`

---

### protocol
*Module: agents.d.protocol*

causal_chain() returns empty list for missing parent, not error If a datum has causal_parent pointing to a deleted datum, you get just the child in the chain. Handle orphaned data gracefully.

**Evidence**: `test_backends.py::TestCausalChain::test_causal_chain_orphaned_datum`

---

### protocol
*Module: agents.d.protocol*

list() returns newest first (sorted by created_at descending) This affects pagination. Use `after` param for time-based filtering.

**Evidence**: `test_backends.py::TestList::test_list_sorted_by_created_at_desc`

---

### protocol
*Module: agents.d.protocol*

DgentRouter silently falls back to memory backend If preferred backend unavailable (e.g., Postgres URL missing), it uses MEMORY without error. Check selected_backend after put().

**Evidence**: `test_router.py::TestBackendSelection::test_falls_back_to_memory`

---

### protocol
*Module: agents.d.protocol*

DataBus subscriber errors don't block other subscribers A failing handler is logged but doesn't prevent event delivery. Check bus.stats["total_errors"] for silent failures.

**Evidence**: `test_bus.py::TestErrorHandling::test_subscriber_error_does_not_block`

---

### protocol
*Module: agents.d.protocol*

get() and list() are silent reads - no DataBus events emitted Only put() and delete() emit events. If you need read tracking, instrument at a higher layer (e.g., M-gent reinforcement).

**Evidence**: `test_bus.py::TestBusEnabledDgent::test_get_does_not_emit`

---

### soul
*Module: agents.k.soul*

Auto-LLM creation spawns subprocesses which are SLOW in tests. Set KGENTS_NO_AUTO_LLM=1 or pass auto_llm=False in test fixtures. The test suite does this via environment variable.

**Evidence**: `test_soul.py::TestLLMDialogue - uses auto_llm=False`

---

### soul
*Module: agents.k.soul*

Empty/whitespace messages return templates, NOT errors. This is intentional graceful degradation - "What's on your mind?" Do not rely on dialogue() to validate user input.

**Evidence**: `test_soul.py::test_soul_dialogue_empty_message`

---

### soul
*Module: agents.k.soul*

Low LLM confidence (< 0.7) forces escalation even if LLM says "approve". This prevents overconfident auto-approval of ambiguous operations.

**Evidence**: `test_soul.py::test_deep_intercept_low_confidence_escalates`

---

### soul
*Module: agents.k.soul*

Without LLM, intercept_deep() silently falls back to shallow intercept. Check result.was_deep to know which path was taken.

**Evidence**: `test_soul.py::test_deep_intercept_fallback_without_llm`

---

### gatekeeper
*Module: agents.k.gatekeeper*

LLM failures in semantic analysis are SILENT - they return empty list. The gatekeeper gracefully degrades to heuristic-only validation. Check if self._llm is set AND use_llm=True to confirm LLM is active.

**Evidence**: `gatekeeper.py::_check_semantic catches all exceptions`

---

### flux
*Module: agents.k.flux*

FluxStream is single-use. Once consumed (iterated), _consumed=True and re-iteration raises StopAsyncIteration immediately. Create a new FluxStream for each consumption via factory function. (Evidence: test_soul_streaming_integration.py::TestPipeAssociativity uses create_stream() factory to avoid reuse)

---

### protocol
*Module: agents.m.protocol*

forget() returns False for cherished memories - they're protected Call cherish() to pin important memories from the forgetting cycle. This is intentional: cherished memories have relevance=1.0 and can't compost.

**Evidence**: `test_associative.py::TestForget::test_forget_cherished_returns_false`

---

### protocol
*Module: agents.m.protocol*

recall() reinforces accessed memories (increases access_count) Every recall is a touch - relevance increases through repeated access. This is the stigmergy pattern: use strengthens memory.

**Evidence**: `test_associative.py::TestRecall::test_recall_reinforces_memory`

---

### protocol
*Module: agents.m.protocol*

Consolidation applies relevance decay to non-cherished memories only Cherished memories keep relevance=1.0 through sleep cycles. Use cherish() sparingly - it's a commitment to preserve.

**Evidence**: `test_consolidation_engine.py::TestConsolidationBasic::test_consolidate_protects_cherished`

---

### protocol
*Module: agents.m.protocol*

similarity() returns 0.0 for mismatched embedding dimensions If you mix embeddings of different sizes, comparisons silently fail. Ensure all embeddings use consistent dimension (e.g., 64 for HashEmbedder).

**Evidence**: `test_memory.py::TestSimilarity::test_similarity_mismatched_dimensions`

---

### protocol
*Module: agents.m.protocol*

Memory.embedding is a tuple, not list (converted on creation) Pass list to create(), get tuple back. This ensures hashability.

**Evidence**: `test_memory.py::TestMemoryCreation::test_embedding_list_to_tuple`

---

### AgenteseGateway
*Module: protocols.agentese.gateway*

Law 3 (Completeness)—every AGENTESE invocation emits exactly one Mark via _emit_trace(). This happens in _invoke_path(), not at the endpoint level, ensuring consistent tracing.

**Evidence**: `test_gateway.py::TestGatewayMarkEmission`

---

### HTTPException
*Module: protocols.agentese.gateway*

This stub exists for graceful degradation—gateway.py can be imported even without FastAPI for type checking.

**Evidence**: `test_gateway.py::TestGatewayMounting::test_gateway_mounts_successfully`

---

### NodeExample
*Module: protocols.agentese.registry*

Examples are defined in @node decorator, not in node class. Pass examples=[(aspect, kwargs, label), ...] to @node().

**Evidence**: `test_registry.py::TestNodeExamples`

---

### NodeRegistry
*Module: protocols.agentese.registry*

@node decorator runs at import time. If a module isn't imported, its node won't be registered. Call _import_node_modules() first (done automatically by gateway.mount_on()).

**Evidence**: `test_registry.py::test_auto_registration`

---

### NodeRegistry
*Module: protocols.agentese.registry*

After reset_registry() in tests, call repopulate_registry() to restore nodes for subsequent tests on the same xdist worker.

**Evidence**: `test_registry.py::TestNodeRegistry::test_clear + fixture pattern`

---

### container
*Module: protocols.agentese.container*

Dependencies are REQUIRED by default (no default in __init__). Missing required deps raise DependencyNotFoundError immediately. To make a dependency optional, add a default: `brain: Brain | None = None`

**Evidence**: `test_container.py::TestNodeCreation::test_required_deps_fail_immediately`

---

### container
*Module: protocols.agentese.container*

Optional dependencies are skipped gracefully if not registered. The node's __init__ default is used. This is intentional for graceful degradation (e.g., SoulNode without LLM).

**Evidence**: `test_container.py::TestNodeCreation::test_optional_deps_skipped_gracefully`

---

### container
*Module: protocols.agentese.container*

Singleton is the DEFAULT. Every register() call creates a cached singleton unless singleton=False is explicitly passed. This means provider functions are called ONCE and the result is reused forever.

**Evidence**: `test_container.py::TestDependencyResolution::test_singleton_caching`

---

### container
*Module: protocols.agentese.container*

Dependency names are CASE-SENSITIVE and EXACT-MATCH. If your @node declares dependencies=("brain_Crystal",) but you register "brain_crystal", the dependency silently fails to resolve.

**Evidence**: `test_container.py::TestProviderRegistration::test_has_unregistered`

---

### logos
*Module: protocols.agentese.logos*

@node runs at import time. If the module isn't imported, the node won't be registered. Call _import_node_modules() first.

**Evidence**: `test_logos.py::test_node_discovery`

---

### logos
*Module: protocols.agentese.logos*

Resolution checks NodeRegistry BEFORE SimpleRegistry. @node decorators in services/ override any manual registration.

**Evidence**: `test_logos.py::test_resolution_order`

---

### logos
*Module: protocols.agentese.logos*

Observer can be None in v3 API—it defaults to Observer.guest(). But guest observers have minimal affordances. Be explicit.

**Evidence**: `test_logos.py::test_guest_observer`

---

### logos
*Module: protocols.agentese.logos*

ComposedPath.invoke() enforces Minimal Output Principle by default. Arrays break composition. Use without_enforcement() if you need them.

**Evidence**: `test_logos.py::test_minimal_output_enforcement`

---

### logos
*Module: protocols.agentese.logos*

Aliases are PREFIX expansion only. "me.challenge" → "self.soul.challenge". You cannot alias an aspect, only a path prefix.

**Evidence**: `test_logos.py::test_alias_expansion`

---

### UnboundComposedPath
*Module: protocols.agentese.logos*

UnboundComposedPath is lazy—no Logos, no execution. Call .bind(logos) to get ComposedPath, or .run() to execute.

**Evidence**: `test_logos.py::test_unbound_composition`

---

### ComposedPath
*Module: protocols.agentese.logos*

ComposedPath.invoke() enforces Minimal Output Principle by default. Arrays break composition. Use .without_enforcement() if needed.

**Evidence**: `test_logos.py::test_minimal_output_enforcement`

---

### IdentityPath
*Module: protocols.agentese.logos*

IdentityPath is useful for conditional pipelines: base = logos.identity() if skip else logos.path("step1") pipeline = base >> "step2"

**Evidence**: `test_logos.py::test_identity_composition`

---

### RegistryProtocol
*Module: protocols.agentese.logos*

This is a Protocol (structural typing). Any class with get/register/update methods satisfies it—no inheritance needed.

**Evidence**: `test_logos.py::test_registry_protocol`

---

### SimpleRegistry
*Module: protocols.agentese.logos*

SimpleRegistry is for testing. In production, NodeRegistry from registry.py is the authoritative source—Logos checks NodeRegistry BEFORE SimpleRegistry.

**Evidence**: `test_logos.py::test_resolution_order`

---

### Logos
*Module: protocols.agentese.logos*

Resolution checks NodeRegistry BEFORE SimpleRegistry. @node decorators in services/ override any manual registration.

**Evidence**: `test_logos.py::test_resolution_order`

---

### Logos
*Module: protocols.agentese.logos*

Aliases are PREFIX expansion only. "me.challenge" → "self.soul.challenge". You cannot alias an aspect, only a path prefix.

**Evidence**: `test_logos.py::test_alias_expansion`

---

### PlaceholderNode
*Module: protocols.agentese.logos*

PlaceholderNode is for tests only. Production nodes should extend BaseLogosNode or use @node decorator.

**Evidence**: `test_logos.py::test_placeholder_node`

---

### Observer
*Module: protocols.agentese.node*

Observer can be None in v3 API—Logos.invoke() defaults to Observer.guest(). But guest observers have minimal affordances. Be explicit about archetype for non-trivial operations.

**Evidence**: `test_logos.py::test_guest_observer`

---

### Observer
*Module: protocols.agentese.node*

Observer is frozen (immutable). To change capabilities, create a new Observer instance. This enables safe sharing.

**Evidence**: `test_node.py::test_observer_immutable`

---

### PolynomialManifest
*Module: protocols.agentese.node*

Default polynomial() returns single 'default' position with all affordances as directions. Override in PolyAgent subclasses (e.g., Gardener) to expose real state machine structure.

**Evidence**: `test_node.py::test_polynomial_default`

---

### AgentMeta
*Module: protocols.agentese.node*

AgentMeta is the v1 affordance API. New code should use Observer directly—BaseLogosNode._umwelt_to_meta() bridges both for backward compatibility.

**Evidence**: `test_node.py::test_agentmeta_to_observer`

---

### Renderable
*Module: protocols.agentese.node*

Renderable is a Protocol (structural typing), not ABC. Any class with to_dict() and to_text() methods satisfies it.

**Evidence**: `test_node.py::test_renderable_protocol`

---

### AffordanceSet
*Module: protocols.agentese.node*

AffordanceSet is observer-specific. Different observers get different verbs from the same node—this is intentional.

**Evidence**: `test_node.py::test_affordance_polymorphism`

---

### BaseLogosNode
*Module: protocols.agentese.node*

BaseLogosNode provides default implementations for help, alternatives, and polynomial aspects. Override polynomial() in PolyAgent subclasses to expose real state machine.

**Evidence**: `test_node.py::test_base_logos_node_defaults`

---

### JITLogosNode
*Module: protocols.agentese.node*

JIT nodes track usage_count and success_rate for promotion. Use should_promote() to check if node is ready for permanent implementation in impl/.

**Evidence**: `test_jit.py::test_jit_promotion_threshold`

---

### Ghost
*Module: protocols.agentese.node*

Ghosts are limited to 5 per invocation. BaseLogosNode._get_alternatives() truncates to prevent UI overload.

**Evidence**: `test_node.py::test_ghost_limit`

---

### BasicRendering
*Module: protocols.agentese.node*

BasicRendering is the fallback for nodes without specialized rendering. Use BlueprintRendering/PoeticRendering/EconomicRendering for archetype-specific output.

**Evidence**: `test_node.py::test_basic_rendering_fallback`

---

### BlueprintRendering
*Module: protocols.agentese.node*

BlueprintRendering is returned when observer.archetype == "architect". Contains dimensions, materials, and structural analysis.

**Evidence**: `test_node.py::test_archetype_rendering`

---

### PoeticRendering
*Module: protocols.agentese.node*

PoeticRendering is returned when observer.archetype == "poet". Contains metaphors and mood for aesthetic interpretation.

**Evidence**: `test_node.py::test_archetype_rendering`

---

### EconomicRendering
*Module: protocols.agentese.node*

EconomicRendering is returned when observer.archetype == "economist". Contains market value, comparable sales, and forecasts.

**Evidence**: `test_node.py::test_archetype_rendering`

---

### AspectAgent
*Module: protocols.agentese.node*

AspectAgent enables >> composition of node aspects. a.lens("manifest") >> b.lens("refine") composes.

**Evidence**: `test_node.py::test_aspect_agent_composition`

---

### ComposedAspectAgent
*Module: protocols.agentese.node*

ComposedAspectAgent preserves associativity: (a >> b) >> c == a >> (b >> c). This is enforced by the flattening logic in __rshift__.

**Evidence**: `test_node.py::test_composition_associativity`

---

### wiring
*Module: protocols.agentese.wiring*

WiredLogos validates paths by DEFAULT. Invalid paths raise PathSyntaxError before ever reaching resolution. To debug, check context (world/self/concept/ void/time), then holon, then aspect. Use validate_paths=False if you need to bypass validation (e.g., during testing or spec evolution).

**Evidence**: `test_wiring.py::TestPathValidation::test_invalid_context_raises_error`

---

### wiring
*Module: protocols.agentese.wiring*

Graceful degradation without L-gent registry. If create_wired_logos() is called without lgent_registry, tracking is silently disabled (track_usage=False is the default for create_minimal_wired_logos). Check integration_status() to see what's available.

**Evidence**: `test_wiring.py::TestLgentIntegration::test_graceful_degradation_without_registry`

---

### wiring
*Module: protocols.agentese.wiring*

Membrane bridge is AUTO-CREATED if not provided. The bridge connects CLI commands to AGENTESE paths. If you need to customize command mapping, pass your own MembraneAgenteseBridge to create_agentese_integrations().

**Evidence**: `test_wiring.py::TestWiredLogosCreation::test_membrane_bridge_auto_created`

---

### wiring
*Module: protocols.agentese.wiring*

invoke() accepts None observer (v3 API). Missing observer defaults to guest archetype. This won't raise ObserverRequiredError, but the guest may lack affordances for the requested aspect.

**Evidence**: `test_wiring.py::TestInvoke::test_invoke_accepts_none_observer`

---

*Total: 383 teaching moments*