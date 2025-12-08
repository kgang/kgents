Simple Regeneration Sequence

  Phase 1: Read Specs (Ground)

  # Read in this order:
  spec/principles.md        # The 7 criteria
  spec/bootstrap.md         # The 7 irreducible agents
  spec/anatomy.md           # What constitutes an agent
  spec/c-gents/composition.md  # Composition laws

  Phase 2: Implement Dependency Graph (Bottom-Up)

  Level 0: bootstrap/types.py      # Agent[A,B] base class
  Level 1: bootstrap/id.py         # No dependencies
           bootstrap/ground.py
  Level 2: bootstrap/compose.py    # Depends on Id
           bootstrap/contradict.py
  Level 3: bootstrap/judge.py      # Depends on compose (7 mini-judges)
           bootstrap/sublate.py
  Level 4: bootstrap/fix.py        # Depends on all others

  Phase 3: Verify Each Level

  # After each level:
  mypy --strict bootstrap/
  python -m pytest impl/claude/bootstrap/

  Phase 4: Validate Behavior Equivalence

  # Test identity laws, composition laws, convergence
  # See REGENERATION_VALIDATION_GUIDE.md for test cases

  ---
  Key Principles to Follow

  1. Spec → Impl (mechanical translation, not creative)
  2. Eager initialization (avoid lazy init that causes flip-flop)
  3. Minimal output (small composable agents, not monoliths)
  4. Fix needs memory (state accumulates between iterations)
  5. Conflicts are data (never swallow exceptions)

  ---
  Critical Constraint

  Never evolve meta-level and object-level code in parallel. Implement bootstrap first, test, commit—then build higher-level agents.
