# Implementation Plan: Kiro-kgents Deep Integration

## Overview

This implementation plan creates the bidirectional bridge between Kiro's IDE-level specification infrastructure and kgents' agent-level cognitive infrastructure. The implementation follows the Metaphysical Fullstack pattern where each component is a complete vertical slice.

**Language**: Python 3.12+ (matching kgents stack)
**Testing Framework**: pytest with Hypothesis for property-based testing

## Tasks

- [ ] 1. Set up integration infrastructure
  - [ ] 1.1 Create integration service module structure
    - Create `impl/claude/services/kiro/` directory
    - Create `__init__.py`, `service.py`, `models.py`, `adapters.py`
    - Register with services/providers.py
    - _Requirements: 1.1, 10.1_

  - [ ] 1.2 Define core data models
    - Create `SpecRegistry`, `IntegrationState`, `SyncResult` dataclasses
    - Create `KiroSpec`, `AgentesePath`, `WitnessTrace` types
    - Add Pydantic validation schemas
    - _Requirements: 1.4, 8.3_

  - [ ] 1.3 Write property test for registry consistency
    - **Property 3: Registry Bidirectional Consistency**
    - **Validates: Requirements 1.4**

- [ ] 2. Implement directory discovery and indexing
  - [ ] 2.1 Create directory scanner
    - Implement `~/.kiro` discovery (argv.json, extensions, powers, steering)
    - Implement `~/.kgents` discovery (config.yaml, soul, brain, witness, data)
    - Handle graceful degradation when directories unavailable
    - _Requirements: 1.1, 1.6, 14.1, 14.2_

  - [ ] 2.2 Create unified registry
    - Implement SpecRegistry with bidirectional mapping
    - Support Kiro spec → spec/ file mapping
    - Support spec/ file → Kiro spec reverse lookup
    - _Requirements: 1.4, 8.1_

  - [ ] 2.3 Write property test for spec sync round-trip
    - **Property 1: Spec Sync Round-Trip**
    - **Validates: Requirements 1.2, 8.1, 8.3**

- [ ] 3. Checkpoint - Ensure infrastructure tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Implement spec compiler
  - [ ] 4.1 Create EARS pattern parser
    - Parse EARS patterns (Ubiquitous, Event-driven, State-driven, etc.)
    - Extract trigger, system, response components
    - Support Complex patterns with clause ordering
    - _Requirements: 2.2_

  - [ ] 4.2 Create AGENTESE path generator
    - Generate AGENTESE paths from requirements
    - Preserve traceability (path → requirement reference)
    - Support all five contexts (world, self, concept, void, time)
    - _Requirements: 2.1, 2.4_

  - [ ] 4.3 Create node handler generator
    - Translate EARS patterns to AGENTESE node handlers
    - Generate @node decorator registrations
    - Support async handlers with Umwelt parameter
    - _Requirements: 2.2_

  - [ ] 4.4 Write property test for compilation traceability
    - **Property 4: Compilation Traceability**
    - **Validates: Requirements 2.1, 2.4**

  - [ ] 4.5 Write property test for EARS pattern translation
    - **Property 5: EARS Pattern Translation Preservation**
    - **Validates: Requirements 2.2**

- [ ] 5. Implement categorical law verification
  - [ ] 5.1 Create composition verifier
    - Verify associativity: (f ∘ g) ∘ h = f ∘ (g ∘ h)
    - Verify identity laws: f ∘ id = f and id ∘ f = f
    - Generate counter-examples on violation
    - _Requirements: 2.6, 13.1, 13.2_

  - [ ] 5.2 Create functor law verifier
    - Verify F(f ∘ g) = F(f) ∘ F(g)
    - Verify F(id) = id
    - Support operad coherence verification
    - _Requirements: 13.3, 13.4_

  - [ ] 5.3 Write property test for categorical law preservation
    - **Property 8: Categorical Law Preservation**
    - **Validates: Requirements 2.6, 13.1, 13.2, 13.3, 13.4**

- [ ] 6. Checkpoint - Ensure compiler tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement steering syncer
  - [ ] 7.1 Create steering file parser
    - Parse front-matter (inclusion, fileMatchPattern)
    - Parse `#[[file:...]]` references
    - Support conditional inclusion patterns
    - _Requirements: 6.2, 6.4_

  - [ ] 7.2 Create bidirectional sync engine
    - Sync `.kiro/steering/` ↔ `~/.kgents/steering/`
    - Apply precedence: workspace > user > global
    - Detect and flag conflicts
    - _Requirements: 6.1, 6.3_

  - [ ] 7.3 Create reference resolver
    - Resolve `#[[file:...]]` in both Kiro and kgents contexts
    - Support relative and absolute paths
    - Handle missing references gracefully
    - _Requirements: 6.2, 8.4_

  - [ ] 7.4 Write property test for steering synchronization
    - **Property 15: Steering Synchronization**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6**

- [ ] 8. Implement power mapper
  - [ ] 8.1 Create power registry reader
    - Read `~/.kiro/powers/registry.json`
    - Parse power metadata (name, description, MCP servers)
    - Track installation status
    - _Requirements: 7.1_

  - [ ] 8.2 Create AGENTESE path exposer
    - Expose power tools under `world.power.{name}.*`
    - Generate @node registrations for each tool
    - Support tool argument mapping
    - _Requirements: 7.2_

  - [ ] 8.3 Create compatibility verifier
    - Verify power compatibility with existing compositions
    - Detect breaking changes on power updates
    - Generate compatibility reports
    - _Requirements: 7.5_

  - [ ] 8.4 Write property test for power registration
    - **Property 16: Power Registration Completeness**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.5**

- [ ] 9. Checkpoint - Ensure sync and power tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Implement soul lens
  - [ ] 10.1 Create eigenvector loader
    - Load eigenvectors from `~/.kgents/soul/soul.json`
    - Support aesthetic, categorical, gratitude, heterarchy, generativity, joy
    - Handle missing soul gracefully
    - _Requirements: 4.1_

  - [ ] 10.2 Create requirement prioritizer
    - Apply eigenvector weights to requirements
    - Sort by weighted priority
    - Maintain consistent ordering
    - _Requirements: 4.1, 4.2_

  - [ ] 10.3 Create conflict detector
    - Detect conflicts with soul values
    - Check against "dislikes" list
    - Generate conflict reports with suggestions
    - _Requirements: 4.3, 4.4_

  - [ ] 10.4 Create audit trail logger
    - Log all personalization decisions
    - Record eigenvector weights used
    - Support audit queries
    - _Requirements: 4.6_

  - [ ] 10.5 Write property test for soul prioritization
    - **Property 11: Soul Eigenvector Prioritization Consistency**
    - **Validates: Requirements 4.1, 4.2**

  - [ ] 10.6 Write property test for soul conflict detection
    - **Property 12: Soul Conflict Detection**
    - **Validates: Requirements 4.3, 4.4**

- [ ] 11. Implement brain pattern integrator
  - [ ] 11.1 Create pattern loader
    - Load patterns from `~/.kgents/brain/patterns.json`
    - Support pattern metadata (type, confidence, source)
    - Handle missing brain gracefully
    - _Requirements: 5.1_

  - [ ] 11.2 Create pattern-spec correlator
    - Correlate patterns with existing specs
    - Detect contradictions between patterns and requirements
    - Respect holographic principle (distributed patterns)
    - _Requirements: 5.1, 5.3, 5.6_

  - [ ] 11.3 Create similarity finder
    - Find similar specs for pattern suggestions
    - Use semantic similarity (embeddings if available)
    - Support fuzzy matching fallback
    - _Requirements: 5.5_

  - [ ] 11.4 Write property test for brain pattern correlation
    - **Property 14: Brain Pattern Correlation**
    - **Validates: Requirements 5.1, 5.3, 5.5, 5.6**

- [ ] 12. Checkpoint - Ensure soul and brain tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 13. Implement witness integrator
  - [ ] 13.1 Create trace capturer
    - Capture witness traces during AGENTESE execution
    - Link traces to source requirements
    - Write to `~/.kgents/witness.log`
    - _Requirements: 3.1, 9.1_

  - [ ] 13.2 Create compliance validator
    - Validate traces against requirements
    - Detect behavioral violations
    - Generate counter-examples with requirement references
    - _Requirements: 3.3, 9.2_

  - [ ] 13.3 Create trace corpus manager
    - Maintain corpus of verified traces per requirement
    - Support trace queries by requirement
    - Apply retention policies
    - _Requirements: 3.4, 11.4_

  - [ ] 13.4 Write property test for witness trace capture
    - **Property 9: Witness Trace Capture Completeness**
    - **Validates: Requirements 3.1, 9.1, 9.2, 9.3, 9.5**

- [ ] 14. Implement drift detection and reconciliation
  - [ ] 14.1 Create drift detector
    - Detect divergence between Kiro specs and spec/ files
    - Generate diff reports
    - Flag for reconciliation
    - _Requirements: 1.3, 8.2_

  - [ ] 14.2 Create reconciliation engine
    - Provide reconciliation tools
    - Support merge strategies
    - Generate repair suggestions for broken links
    - _Requirements: 1.5, 8.4_

  - [ ] 14.3 Write property test for drift detection
    - **Property 2: Drift Detection Consistency**
    - **Validates: Requirements 1.3, 8.2**

- [ ] 15. Checkpoint - Ensure witness and drift tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 16. Implement configuration unification
  - [ ] 16.1 Create config loader
    - Load from `.kgents/config.yaml` and `.kiro/` settings
    - Apply precedence: workspace > user > defaults
    - Support environment variable overrides
    - _Requirements: 10.1, 10.2, 10.3_

  - [ ] 16.2 Create config validator
    - Validate against schema
    - Generate validation errors with suggestions
    - Support partial validation
    - _Requirements: 10.5_

  - [ ] 16.3 Create config migrator
    - Migrate between Kiro and kgents formats
    - Preserve semantic equivalence
    - Support rollback
    - _Requirements: 10.6_

  - [ ] 16.4 Write property test for configuration resolution
    - **Property 18: Configuration Resolution**
    - **Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5, 10.6**

- [ ] 17. Implement history integration
  - [ ] 17.1 Create session archiver
    - Archive Kiro session context to `~/.kgents/prompt-history/`
    - Support checkpoint-based history
    - Apply retention policies
    - _Requirements: 11.1, 11.3, 11.4_

  - [ ] 17.2 Create similarity detector
    - Detect similar prompts
    - Suggest relevant historical context
    - Support semantic search
    - _Requirements: 11.2, 11.5_

  - [ ] 17.3 Create privacy filter
    - Filter PII from stored history
    - Support configurable PII patterns
    - Audit PII filtering decisions
    - _Requirements: 11.6_

  - [ ] 17.4 Write property test for history management
    - **Property 19: History Management**
    - **Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5, 11.6**

- [ ] 18. Implement graceful degradation
  - [ ] 18.1 Create availability monitor
    - Monitor component availability
    - Provide clear status indicators
    - Support health checks
    - _Requirements: 14.4_

  - [ ] 18.2 Create degradation handler
    - Handle `~/.kiro` unavailability
    - Handle `~/.kgents` unavailability
    - Handle network unavailability
    - _Requirements: 14.1, 14.2, 14.3_

  - [ ] 18.3 Create reconnection handler
    - Reconcile state on reconnection
    - Prioritize data integrity
    - Queue sync operations during offline
    - _Requirements: 14.5, 14.6_

  - [ ] 18.4 Write property test for graceful reconnection
    - **Property 20: Graceful Reconnection**
    - **Validates: Requirements 14.5, 14.6**

- [ ] 19. Implement semantic linking
  - [ ] 19.1 Create link manager
    - Maintain bidirectional links using `#[[file:...]]` syntax
    - Verify link integrity
    - Generate repair suggestions
    - _Requirements: 8.3, 8.4_

  - [ ] 19.2 Create semantic search
    - Search across Kiro specs and spec/ files
    - Support fuzzy matching
    - Rank by relevance
    - _Requirements: 8.5_

  - [ ] 19.3 Create principle verifier
    - Verify spec alignment with `spec/principles.md`
    - Flag principle violations
    - Suggest corrections
    - _Requirements: 8.6_

  - [ ] 19.4 Write property test for semantic link integrity
    - **Property 17: Semantic Link Integrity**
    - **Validates: Requirements 8.4, 8.5, 8.6**

- [ ] 20. Implement feedback loop
  - [ ] 20.1 Create pattern analyzer
    - Analyze accumulated traces for patterns
    - Identify spec refinement opportunities
    - Generate refinement proposals
    - _Requirements: 3.2, 3.5_

  - [ ] 20.2 Create loop closer
    - Complete Spec → Impl → Trace → Pattern → Refined Spec cycle
    - Verify essential structure preservation
    - Support incremental refinement
    - _Requirements: 3.6_

  - [ ] 20.3 Write property test for feedback loop closure
    - **Property 10: Feedback Loop Closure**
    - **Validates: Requirements 3.6**

- [ ] 21. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 22. Create AGENTESE node registrations
  - [ ] 22.1 Register integration paths
    - Register `self.kiro.sync` for spec synchronization
    - Register `self.kiro.compile` for spec compilation
    - Register `self.kiro.status` for integration status
    - _Requirements: 2.1, 10.1_

  - [ ] 22.2 Register power paths
    - Register `world.power.*` for installed powers
    - Support dynamic registration on power install
    - _Requirements: 7.2_

  - [ ] 22.3 Wire to existing services
    - Wire to Brain service for pattern integration
    - Wire to Witness service for trace capture
    - Wire to Soul service for personalization
    - _Requirements: 5.1, 3.1, 4.1_

- [ ] 23. Create spec/ semantic links
  - [ ] 23.1 Create spec/k-gents/kiro-integration.md
    - Document integration architecture
    - Link to `.kiro/specs/kiro-kgents-integration/`
    - Include semantic backlinks
    - _Requirements: 8.1, 8.3_

  - [ ] 23.2 Update spec/infrastructure/ files
    - Add kiro integration references
    - Update architecture diagrams
    - Maintain semantic coherence
    - _Requirements: 8.6_

## Notes

- All tasks including property tests are required for comprehensive testing
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- All specs MUST maintain semantic links with spec/ files

