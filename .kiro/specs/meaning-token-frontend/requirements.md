# Requirements Document: Meaning Token Frontend Architecture

## Introduction

The Meaning Token Frontend Architecture represents a paradigm shift in how kgents renders interfaces. Rather than building traditional component hierarchies, we treat **meaning tokens** as the atomic unit of interface—semantic primitives that project to different rendering layers (CLI, TUI, Web, marimo, VR) through the Projection Protocol.

This architecture unifies the Interactive Text Protocol, Projection Protocol, and Metaphysical Fullstack pattern into a coherent frontend system where:
- Text files ARE interfaces (not descriptions of interfaces)
- Components are projections of meaning, not UI primitives
- The same semantic token renders appropriately across all surfaces
- Formal verification traces connect interactions to correctness proofs

> *"The noun is a lie. There is only the rate of change."*
> *"And the rate of change of a document IS its interactivity."*

## Glossary

- **Meaning_Token**: A semantic primitive that carries meaning independent of rendering—the atomic unit of interface
- **Projection_Functor**: A natural transformation from Meaning_Token to target-specific rendering
- **Token_Registry**: The single source of truth mapping token patterns to affordance generators
- **Affordance**: An interaction possibility offered by a token (hover, click, drag, etc.)
- **Document_Polynomial**: State machine governing document modes (VIEWING, EDITING, SYNCING, CONFLICTING)
- **Document_Sheaf**: Coherence structure ensuring multi-view consistency
- **Semantic_Layer_Stack**: The four-level hierarchy from plain text to gestural interaction
- **Observer_Umwelt**: The observer-dependent context determining projection fidelity
- **Trace_Witness**: A constructive proof of interaction captured for formal verification
- **Container_Functor**: The shallow main website that composes service projections
- **Crown_Jewel**: A complete vertical slice service owning its domain logic and frontend

## Requirements

### Requirement 1: Meaning Token as Atomic Primitive

**User Story:** As a frontend developer, I want to work with meaning tokens as the fundamental building block, so that I can create interfaces that are semantically coherent across all projection surfaces.

#### Acceptance Criteria

1. THE Token_Registry SHALL define exactly six core token types: AGENTESEPath, TaskCheckbox, Image, CodeBlock, PrincipleRef, RequirementRef
2. WHEN a meaning token is defined, THE System SHALL generate affordances for all supported projection targets
3. WHEN a new projection target is added, THE System SHALL automatically project existing tokens to the new target
4. THE System SHALL support custom token type registration through a declarative API
5. WHEN tokens are composed, THE System SHALL preserve semantic meaning through composition
6. THE Token_Registry SHALL be the single source of truth for all token definitions (AD-011)

### Requirement 2: Projection Functor Implementation

**User Story:** As a system architect, I want projections to be natural transformations that preserve semantic structure, so that the same meaning renders consistently across CLI, Web, and other surfaces.

#### Acceptance Criteria

1. WHEN a Meaning_Token is projected, THE Projection_Functor SHALL produce target-specific output while preserving semantic meaning
2. THE System SHALL implement projections for: CLI (Rich), TUI (Textual), Web (React), marimo (anywidget), JSON (API)
3. WHEN state changes occur, THE Projection_Functor SHALL produce consistent changes across all targets (naturality condition)
4. THE System SHALL support density-parameterized projection (compact, comfortable, spacious)
5. WHEN projection fidelity differs between targets, THE System SHALL degrade gracefully with explicit information loss
6. THE Projection_Functor SHALL compose: P(A >> B) = P(A) >> P(B) for horizontal composition

### Requirement 3: Document Polynomial State Machine

**User Story:** As a user, I want documents to have well-defined editing states, so that I can understand and control document behavior during modifications.

#### Acceptance Criteria

1. THE Document_Polynomial SHALL implement four positions: VIEWING, EDITING, SYNCING, CONFLICTING
2. WHEN in VIEWING state, THE System SHALL accept inputs: edit, refresh, hover, click
3. WHEN in EDITING state, THE System SHALL accept inputs: save, cancel, continue_edit
4. WHEN in SYNCING state, THE System SHALL accept inputs: wait, force_local, force_remote
5. WHEN in CONFLICTING state, THE System SHALL accept inputs: resolve, abort
6. WHEN state transitions occur, THE System SHALL emit events through the DataBus

### Requirement 4: Document Sheaf Coherence

**User Story:** As a user editing documents across multiple views, I want all views to remain synchronized, so that I never see inconsistent state.

#### Acceptance Criteria

1. WHEN a document is opened in multiple views, THE Document_Sheaf SHALL maintain coherence across all views
2. WHEN an edit occurs in any view, THE System SHALL propagate changes to all other views within 100ms
3. THE System SHALL use the file on disk as the canonical source of truth
4. WHEN views have overlapping tokens, THE System SHALL verify they agree on token state (compatible condition)
5. WHEN the sheaf condition fails, THE System SHALL identify conflicts and suggest resolution
6. THE Document_Sheaf SHALL support gluing: combining compatible views into global document state

### Requirement 5: AGENTESE Path Token

**User Story:** As a developer, I want AGENTESE paths in text to be interactive, so that I can explore the agent system directly from documentation.

#### Acceptance Criteria

1. WHEN text contains backtick-wrapped AGENTESE paths, THE System SHALL recognize them as AGENTESEPath tokens
2. WHEN hovering an AGENTESEPath, THE System SHALL display polynomial state (current position, valid transitions)
3. WHEN clicking an AGENTESEPath, THE System SHALL navigate to the path's Habitat (AD-010)
4. WHEN right-clicking an AGENTESEPath, THE System SHALL show context menu with invoke, view source, copy options
5. WHEN dragging an AGENTESEPath to REPL, THE System SHALL pre-fill the path for invocation
6. IF an AGENTESEPath references a non-existent node, THEN THE System SHALL render it as a ghost token with reduced affordances

### Requirement 6: Task Checkbox Token with Verification

**User Story:** As a developer, I want task checkboxes to connect to the formal verification system, so that task completion creates trace witnesses.

#### Acceptance Criteria

1. WHEN text contains GitHub-style task lists, THE System SHALL recognize them as TaskCheckbox tokens
2. WHEN clicking a TaskCheckbox, THE System SHALL toggle state and persist to the source file
3. WHEN a task is completed, THE System SHALL capture a Trace_Witness through world.trace.capture
4. WHEN a task has requirement references, THE System SHALL link to verification status
5. WHEN task completion fails verification, THE System SHALL display warning with counter-examples
6. THE TaskCheckbox SHALL display affordances: View changes (git diff), View execution (trace)

### Requirement 7: Image Token as First-Class Context

**User Story:** As a user, I want images in documents to be analyzable and usable as context, so that visual information integrates with the agent system.

#### Acceptance Criteria

1. WHEN text contains markdown images, THE System SHALL recognize them as Image tokens
2. WHEN hovering an Image, THE System SHALL display AI-generated description (cached)
3. WHEN clicking an Image, THE System SHALL expand to full analysis panel
4. WHEN dragging an Image to chat, THE System SHALL add it to K-gent conversation context
5. IF LLM is unavailable, THEN THE System SHALL display image without analysis and show "requires connection" tooltip
6. THE System SHALL support image annotation and text extraction

### Requirement 8: Code Block Token as Live Playground

**User Story:** As a developer, I want code blocks to be executable, so that I can test code directly in documentation.

#### Acceptance Criteria

1. WHEN text contains fenced code blocks, THE System SHALL recognize them as CodeBlock tokens
2. WHEN editing a CodeBlock, THE System SHALL provide syntax-highlighted inline editing
3. WHEN running a CodeBlock, THE System SHALL execute in sandboxed environment
4. WHEN execution completes, THE System SHALL display output panel with result/errors
5. THE System SHALL support importing CodeBlock content into current module
6. WHEN CodeBlock contains AGENTESE invocations, THE System SHALL capture execution traces

### Requirement 9: Semantic Layer Stack

**User Story:** As a system architect, I want a clear layered architecture from plain text to gestural interaction, so that each layer has well-defined responsibilities.

#### Acceptance Criteria

1. THE System SHALL implement Level 1 (Plain Text): valid markdown, git-diffable, readable anywhere
2. THE System SHALL implement Level 2 (Markdown AST): standard markdown with token extraction, roundtrip fidelity
3. THE System SHALL implement Level 3 (Semantic Recognition): token patterns to affordance generators
4. THE System SHALL implement Level 4 (Gestural Interaction): paste, click, hover, drag interactions
5. WHEN parsing and rendering, THE System SHALL preserve roundtrip fidelity: parse(render(parse(doc))) ≡ parse(doc)
6. THE System SHALL support progressive enhancement: each level adds capability without breaking lower levels

### Requirement 10: Container Functor Architecture

**User Story:** As a frontend developer, I want the main website to be a shallow container that composes service projections, so that domain logic stays with domain services.

#### Acceptance Criteria

1. THE Container_Functor (main website) SHALL be a shallow passthrough composing service projections
2. WHEN a Crown_Jewel defines frontend components, THE System SHALL import them from the service module
3. THE Container_Functor SHALL NOT contain business logic—only composition and routing
4. WHEN rendering a page, THE System SHALL compose projections from relevant Crown_Jewels
5. THE System SHALL support elastic composition adapting to viewport density
6. THE Container_Functor SHALL derive navigation from AGENTESE registry (AD-011)

### Requirement 11: Cross-Jewel Event Coordination

**User Story:** As a system architect, I want token interactions to coordinate across Crown Jewels, so that the system behaves as a coherent whole.

#### Acceptance Criteria

1. WHEN a token interaction occurs, THE System SHALL emit events through the DataBus
2. THE System SHALL wire DataBus events to SynergyBus for cross-jewel coordination
3. WHEN a task is completed, THE System SHALL notify: verification (trace), memory (crystallization), witness (observability)
4. THE System SHALL support wildcard subscriptions for event patterns
5. WHEN events cross jewel boundaries, THE System SHALL maintain causal ordering
6. THE System SHALL provide event replay for debugging and verification

### Requirement 12: Formal Verification Integration

**User Story:** As a formal methods researcher, I want token interactions to create verifiable traces, so that I can prove system correctness.

#### Acceptance Criteria

1. WHEN a TaskCheckbox is toggled, THE System SHALL create a Trace_Witness with constructive proof
2. WHEN verification fails, THE System SHALL generate counter-examples with remediation suggestions
3. THE System SHALL link tokens to requirements through RequirementRef tokens
4. WHEN viewing a task, THE System SHALL display verification status and derivation path
5. THE System SHALL integrate with the Verification Graph for derivation visualization
6. THE System SHALL support the Generative Loop: interactions feed back to spec refinement

### Requirement 13: Observer-Dependent Rendering

**User Story:** As a user, I want the interface to adapt to my context and capabilities, so that I receive appropriate affordances.

#### Acceptance Criteria

1. WHEN rendering tokens, THE System SHALL consider Observer_Umwelt (capabilities, density, preferences)
2. WHEN observer has limited bandwidth (CLI), THE System SHALL project with reduced fidelity
3. WHEN observer has high bandwidth (Web), THE System SHALL project with full affordances
4. THE System SHALL support role-based affordance filtering (viewer, editor, admin)
5. WHEN observer preferences change, THE System SHALL re-project without page reload
6. THE System SHALL maintain semantic equivalence across observer projections

### Requirement 14: Graceful Degradation

**User Story:** As a user, I want the system to work even when services are unavailable, so that I can always access my documents.

#### Acceptance Criteria

1. WHEN LLM is unavailable, THE System SHALL render tokens without AI-powered affordances
2. WHEN verification service is unavailable, THE System SHALL allow task toggling with deferred verification
3. WHEN network is unavailable, THE System SHALL work with local file state
4. THE System SHALL clearly indicate degraded functionality with sympathetic messaging
5. WHEN services recover, THE System SHALL reconcile deferred operations
6. THE System SHALL never block document access due to service unavailability

### Requirement 15: Alive Workshop Aesthetic

**User Story:** As a user, I want the interface to feel organic and warm, so that formal verification feels approachable and joyful.

#### Acceptance Criteria

1. WHEN displaying verification results, THE System SHALL use clear, sympathetic language
2. WHEN errors occur, THE System SHALL provide constructive suggestions with examples
3. THE System SHALL use the Living Earth color palette (warm earth tones, living greens, Ghibli glow)
4. WHEN verification succeeds, THE System SHALL celebrate with appropriate feedback
5. THE System SHALL provide progressive disclosure: simple by default, detailed on demand
6. THE System SHALL use breathing animations for graphs and flowing transitions for data

### Requirement 16: Token Parser with Roundtrip Fidelity

**User Story:** As a developer, I want the parser to preserve document structure exactly, so that automated edits don't corrupt formatting.

#### Acceptance Criteria

1. WHEN parsing a document, THE Parser SHALL extract tokens while preserving all whitespace and formatting
2. WHEN rendering a parsed document, THE System SHALL produce byte-identical output to the original
3. THE Parser SHALL support incremental parsing for large documents
4. WHEN tokens are modified, THE System SHALL update only affected regions
5. THE Parser SHALL handle malformed markdown gracefully without crashing
6. THE Parser SHALL provide source maps linking tokens to file positions

### Requirement 17: Crown Jewel Frontend Structure

**User Story:** As a service developer, I want to co-locate frontend components with my service, so that domain knowledge stays together.

#### Acceptance Criteria

1. WHEN a Crown_Jewel has frontend needs, THE System SHALL support components in services/{jewel}/web/
2. THE System SHALL support React components, hooks, and styles in service modules
3. WHEN the main website needs a component, THE System SHALL import from the service module
4. THE System SHALL support hot module replacement for service components
5. WHEN a service is updated, THE System SHALL rebuild only affected components
6. THE System SHALL provide TypeScript types derived from Python models

