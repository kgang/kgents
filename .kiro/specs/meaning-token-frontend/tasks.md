# Implementation Plan: Meaning Token Frontend Architecture

## Overview

This implementation plan transforms the radical design into actionable coding tasks. We are building a **projection-based architecture** that eliminates traditional frontend concepts entirely. The implementation follows the Metaphysical Fullstack pattern where meaning tokens project to any observer surface.

**Key Principle**: There is no frontend. There are only meaning tokens and projection functors.

## Tasks

- [x] 1. Set up project structure and core interfaces
  - Create `services/interactive_text/` directory structure
  - Define core type interfaces (MeaningToken, Affordance, Observer)
  - Set up testing framework with Hypothesis
  - _Requirements: 1.1, 1.6_

- [x] 2. Implement Token Registry and Core Token Types
  - [x] 2.1 Implement TokenRegistry as single source of truth
    - Create `services/interactive_text/registry.py`
    - Implement pattern matching and priority ordering
    - Implement token definition registration
    - _Requirements: 1.1, 1.6_

  - [x] 2.2 Write property test for token recognition completeness
    - **Property 1: Token Recognition Completeness**
    - **Validates: Requirements 1.1, 5.1, 6.1, 7.1, 8.1**

  - [x] 2.3 Implement MeaningToken base class
    - Create `services/interactive_text/tokens/base.py`
    - Define abstract methods: token_type, source_text, source_position, get_affordances, project
    - Implement on_interact with trace witness capture
    - _Requirements: 1.2, 6.3, 12.1_

  - [x] 2.4 Implement AGENTESEPath token
    - Create `services/interactive_text/tokens/agentese_path.py`
    - Implement hover (polynomial state), click (navigate), right-click (context menu), drag (REPL)
    - Handle ghost tokens for non-existent paths
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

  - [x] 2.5 Write property test for AGENTESE path affordances
    - **Property 10: AGENTESE Path Affordances**
    - **Validates: Requirements 5.2, 5.3, 5.4, 5.5**

  - [x] 2.6 Write property test for ghost token rendering
    - **Property 11: Ghost Token Rendering**
    - **Validates: Requirements 5.6**

  - [x] 2.7 Implement TaskCheckbox token
    - Create `services/interactive_text/tokens/task_checkbox.py`
    - Implement toggle with file persistence
    - Integrate trace witness capture
    - Link to verification status
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

  - [x] 2.8 Write property test for task checkbox toggle with trace
    - **Property 12: Task Checkbox Toggle with Trace**
    - **Validates: Requirements 6.2, 6.3, 12.1**

  - [x] 2.9 Implement Image token
    - Create `services/interactive_text/tokens/image.py`
    - Implement hover (AI description), click (expand), drag (add to context)
    - Handle graceful degradation when LLM unavailable
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

  - [x] 2.10 Write property test for image token graceful degradation
    - **Property 14: Image Token Graceful Degradation**
    - **Validates: Requirements 7.2, 7.5, 14.1**

  - [x] 2.11 Implement CodeBlock token
    - Create `services/interactive_text/tokens/code_block.py`
    - Implement inline editing, sandboxed execution, output display
    - Capture execution traces for AGENTESE invocations
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

  - [x] 2.12 Write property test for code block execution sandboxing
    - **Property 15: Code Block Execution Sandboxing**
    - **Validates: Requirements 8.3, 8.4, 8.6**

  - [x] 2.13 Implement PrincipleRef and RequirementRef tokens
    - Create `services/interactive_text/tokens/principle_ref.py`
    - Create `services/interactive_text/tokens/requirement_ref.py`
    - Link to verification graph and derivation paths
    - _Requirements: 12.3, 12.4, 12.5_

- [x] 3. Checkpoint - Ensure all token tests pass ✅
  - All 120 tests pass
  - Fixed ghost token navigation to return `success=False` with error message

- [x] 4. Implement Document Polynomial State Machine
  - [x] 4.1 Implement DocumentPolynomial class
    - Create `services/interactive_text/polynomial.py`
    - Define four positions: VIEWING, EDITING, SYNCING, CONFLICTING
    - Implement directions() for valid inputs per state
    - Implement transition() for state × input → (new_state, output)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 4.2 Write property test for document polynomial state validity
    - **Property 6: Document Polynomial State Validity**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

  - [x] 4.3 Implement event emission on state transitions
    - Wire transitions to DataBus event emission
    - Define DocumentEvent dataclass
    - _Requirements: 3.6, 11.1_

  - [x] 4.4 Write property test for polynomial event emission
    - **Property 7: Document Polynomial Event Emission**
    - **Validates: Requirements 3.6, 11.1**

- [x] 5. Implement Document Sheaf Coherence
  - [x] 5.1 Implement DocumentSheaf class
    - Create `services/interactive_text/sheaf.py`
    - Implement overlap() for shared tokens between views
    - Implement compatible() for sheaf condition verification
    - Implement verify_sheaf_condition() for pairwise compatibility
    - _Requirements: 4.1, 4.4, 4.5_

  - [x] 5.2 Write property test for document sheaf coherence
    - **Property 8: Document Sheaf Coherence**
    - **Validates: Requirements 4.1, 4.4, 4.5, 4.6**

  - [x] 5.3 Implement glue() and change propagation
    - Implement glue() to combine compatible views
    - Implement on_file_change() for file watcher integration
    - Implement on_view_edit() for edit propagation
    - _Requirements: 4.2, 4.3, 4.6_

  - [x] 5.4 Write property test for sheaf propagation
    - **Property 9: Document Sheaf Propagation**
    - **Validates: Requirements 4.2, 4.3**

- [x] 6. Checkpoint - Ensure polynomial and sheaf tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement Projection Functor System
  - [x] 7.1 Implement ProjectionFunctor base class
    - Create `services/interactive_text/projectors/base.py`
    - Define abstract methods: project_token, project_document
    - Implement project_composition for horizontal/vertical composition
    - _Requirements: 2.1, 2.6_

  - [x] 7.2 Write property test for projection functor composition law
    - **Property 3: Projection Functor Composition Law**
    - **Validates: Requirements 1.5, 2.6**

  - [x] 7.3 Write property test for projection naturality condition
    - **Property 4: Projection Naturality Condition**
    - **Validates: Requirements 2.1, 2.3**

  - [x] 7.4 Implement CLIProjectionFunctor
    - Create `services/interactive_text/projectors/cli.py`
    - Project tokens to Rich terminal markup
    - Support density-parameterized output
    - _Requirements: 2.2, 2.4_

  - [x] 7.5 Implement WebProjectionFunctor
    - Create `services/interactive_text/projectors/web.py`
    - Project tokens to ReactElement specifications
    - Include affordance wiring as data attributes
    - _Requirements: 2.2, 2.4_

  - [x] 7.6 Implement JSONProjectionFunctor
    - Create `services/interactive_text/projectors/json.py`
    - Project tokens to API-friendly JSON structures
    - _Requirements: 2.2_

  - [x] 7.7 Write property test for density-parameterized projection
    - **Property 5: Density-Parameterized Projection**
    - **Validates: Requirements 2.4, 2.5**

  - [x] 7.8 Write property test for observer-dependent projection
    - **Property 18: Observer-Dependent Projection**
    - **Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.6**

- [-] 8. Implement Parser with Roundtrip Fidelity
  - [ ] 8.1 Implement markdown parser with token extraction
    - Create `services/interactive_text/parser.py`
    - Parse markdown preserving all whitespace and formatting
    - Extract tokens with accurate source positions
    - _Requirements: 16.1, 16.6_

  - [ ] 8.2 Write property test for roundtrip fidelity
    - **Property 16: Roundtrip Fidelity**
    - **Validates: Requirements 9.2, 9.5, 16.1, 16.2**

  - [ ] 8.3 Implement incremental parsing
    - Support partial re-parsing for changed regions
    - Implement localized token modification
    - _Requirements: 16.3, 16.4_

  - [ ] 8.4 Write property test for localized token modification
    - **Property 22: Localized Token Modification**
    - **Validates: Requirements 16.4**

  - [ ] 8.5 Write property test for parser robustness
    - **Property 21: Parser Robustness**
    - **Validates: Requirements 16.5, 16.6**

- [ ] 9. Checkpoint - Ensure projection and parser tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Implement AGENTESE Integration
  - [ ] 10.1 Implement InteractiveTextNode
    - Create `services/interactive_text/agentese_nodes.py`
    - Implement manifest aspect for document rendering
    - Implement toggle_task aspect with verification integration
    - Implement hover_token aspect
    - _Requirements: 5.2, 5.3, 6.2, 6.3, 6.4, 6.5_

  - [ ] 10.2 Write property test for task verification integration
    - **Property 13: Task Verification Integration**
    - **Validates: Requirements 6.4, 6.5, 12.2, 12.4**

  - [ ] 10.3 Implement DataBus event wiring
    - Create `services/interactive_text/events.py`
    - Define SYNERGY_WIRING for cross-jewel coordination
    - Wire document events to verification, memory, witness services
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

  - [ ] 10.4 Write property test for cross-jewel event coordination
    - **Property 20: Cross-Jewel Event Coordination**
    - **Validates: Requirements 11.2, 11.3, 11.4, 11.5**

- [ ] 11. Implement Semantic Layer Stack
  - [ ] 11.1 Implement Layer 1 (Plain Text)
    - Ensure all documents are valid markdown, git-diffable
    - _Requirements: 9.1_

  - [ ] 11.2 Implement Layer 2 (Markdown AST)
    - Standard markdown parsing with token extraction
    - Roundtrip fidelity guarantee
    - _Requirements: 9.2_

  - [ ] 11.3 Implement Layer 3 (Semantic Recognition)
    - Token patterns to affordance generators
    - _Requirements: 9.3_

  - [ ] 11.4 Implement Layer 4 (Gestural Interaction)
    - Paste, click, hover, drag interactions
    - _Requirements: 9.4_

  - [ ] 11.5 Write property test for progressive enhancement
    - **Property 17: Progressive Enhancement**
    - **Validates: Requirements 9.6**

- [ ] 12. Implement Graceful Degradation
  - [ ] 12.1 Implement service availability detection
    - Create `services/interactive_text/degradation.py`
    - Detect LLM, verification, network availability
    - _Requirements: 14.1, 14.2, 14.3_

  - [ ] 12.2 Implement sympathetic error handling
    - Create `services/interactive_text/errors.py`
    - Implement SYMPATHETIC_MESSAGES with warm language
    - Implement handle_error() for error conversion
    - _Requirements: 14.4, 15.1, 15.2_

  - [ ] 12.3 Implement deferred operation reconciliation
    - Queue operations when services unavailable
    - Reconcile when services recover
    - _Requirements: 14.5, 14.6_

  - [ ] 12.4 Write property test for graceful degradation
    - **Property 19: Graceful Degradation**
    - **Validates: Requirements 14.1, 14.2, 14.3, 14.4, 14.5, 14.6**

- [ ] 13. Checkpoint - Ensure integration tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 14. Implement Web Projection Receiver
  - [ ] 14.1 Create minimal web receiver
    - Create `impl/claude/web/src/receiver.tsx`
    - Implement ProjectionReceiver component (~50 lines)
    - Implement useProjection hook for observer connection
    - _Requirements: 10.1, 10.3_

  - [ ] 14.2 Implement observer connection
    - Create `impl/claude/web/src/observer.ts`
    - Connect to projection functor via WebSocket/SSE
    - Handle projection updates
    - _Requirements: 10.2, 10.4_

  - [ ] 14.3 Implement minimal shell
    - Create `impl/claude/web/src/shell.tsx`
    - Derive routing from AGENTESE registry
    - _Requirements: 10.6_

- [ ] 15. Implement Token Affordance Generation
  - [ ] 15.1 Implement affordance generation for all token types
    - Generate affordances based on observer capabilities
    - Support role-based filtering
    - _Requirements: 1.2, 1.3, 13.4_

  - [ ] 15.2 Write property test for token affordance generation
    - **Property 2: Token Affordance Generation**
    - **Validates: Requirements 1.2, 1.3**

- [ ] 16. Implement Container Functor Architecture
  - [ ] 16.1 Refactor main website as container functor
    - Ensure website is shallow passthrough
    - Import components from service modules
    - _Requirements: 10.1, 10.2, 10.3, 10.4_

  - [ ] 16.2 Implement elastic composition
    - Adapt to viewport density
    - _Requirements: 10.5_

- [ ] 17. Final Integration and Wiring
  - [ ] 17.1 Wire all components together
    - Connect token registry to parser
    - Connect parser to projection functors
    - Connect projectors to observers
    - _Requirements: All_

  - [ ] 17.2 Implement Alive Workshop aesthetic
    - Apply Living Earth color palette
    - Implement breathing animations
    - Implement progressive disclosure
    - _Requirements: 15.3, 15.4, 15.5, 15.6_

- [ ] 18. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
  - Run full property-based test suite with 100+ iterations
  - Verify all 22 correctness properties

## Notes

- All tasks are required for comprehensive implementation
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties (22 total)
- Unit tests validate specific examples and edge cases
- Implementation uses Python with Hypothesis for property-based testing
- Web receiver uses minimal TypeScript/React (~50 lines total)
