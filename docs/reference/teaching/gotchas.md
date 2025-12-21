# Teaching Moments (Gotchas)

> *"Gotchas live in docstrings, not wikis."*

## 🚨 Critical (25)

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

### playbook
*Module: services.witness.playbook*

Always verify Grant is GRANTED status before creating Playbook. Passing a PENDING or REVOKED Grant raises MissingGrant.

**Evidence**: `test_playbook.py::test_grant_required`

---

### playbook
*Module: services.witness.playbook*

from_dict() does NOT restore _grant and _scope objects. You must reattach them manually after deserialization.

**Evidence**: `test_playbook.py::test_serialization_roundtrip`

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

### types
*Module: agents.poly.types*

Result.unwrap() raises RuntimeError on Err. Always check is_ok() first or use unwrap_or(default) for safe extraction.

**Evidence**: `test_primitives.py::test_result_unwrap_error`

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

## ⚠️ Warning (35)

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

## ℹ️ Info (21)

### persistence
*Module: services.brain.persistence*

search() updates access_count via touch(). High-frequency searches will cause write amplification. Consider batching access updates.

**Evidence**: `test_brain_persistence.py::test_access_tracking`

---

### playbook
*Module: services.witness.playbook*

Phase transitions are DIRECTED—you cannot skip phases. SENSE → ACT → REFLECT → SENSE (cycle). InvalidPhaseTransition if wrong.

**Evidence**: `test_playbook.py::test_phase_ordering`

---

### playbook
*Module: services.witness.playbook*

Guards evaluate at phase boundaries, not during phase. Budget exhaustion during ACT phase only fails at ACT → REFLECT.

**Evidence**: `test_playbook.py::test_guard_evaluation`

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

*Total: 81 teaching moments*