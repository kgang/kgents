# Project Structure

## Repository Organization

This is a monorepo with the main implementation in `impl/claude/`. The structure follows the **Metaphysical Fullstack** pattern where each agent is a complete vertical slice.

## Top-Level Directories

```
kgents/
├── impl/claude/          # Main implementation (Python + TypeScript)
├── spec/                 # Specifications and design documents
├── docs/                 # Documentation and guides
├── plans/                # Development plans and continuations
├── brainstorming/        # Creative exploration and ideas
├── compiled/             # Generated documentation
├── reflected/            # Self-reflection outputs
├── site/                 # Built documentation site
└── .kiro/               # Kiro IDE configuration and steering
```

## Implementation Structure (`impl/claude/`)

### Core Directories

```
impl/claude/
├── agents/              # Categorical primitives by genus (A-Z, Flux, etc.)
├── services/            # Crown Jewels - complete vertical slices
├── protocols/           # Universal protocols (AGENTESE, CLI, API)
├── models/              # SQLAlchemy ORM definitions
├── bootstrap/           # The 7 bootstrap agents (id, ground, judge, etc.)
├── runtime/             # LLM clients and execution engines
├── shared/              # Cross-cutting utilities (budget, costs, etc.)
├── web/                 # Main website (container functor)
├── testing/             # Test infrastructure and utilities
├── infra/               # Infrastructure components
└── fixtures/            # Pre-computed test data and demos
```

### Agent Genera (`agents/`)

Agents are organized by letter-based genera following category theory principles:

```
agents/
├── a/                   # Alethic - Architecture, functors, archetypes
├── b/                   # (Reserved for future use)
├── c/                   # Category - Composition primitives (Maybe, Either, etc.)
├── d/                   # Data - State, memory, persistence
├── flux/                # Flux - Streams, events, real-time processing
├── i/                   # Interface - TUI, semantic fields
├── k/                   # Kent - Persona, governance, K-gent
├── poly/                # Polynomial - PolyAgent primitives and wiring
├── operad/              # Operads - Composition grammar
├── sheaf/               # Sheaves - Local-to-global emergence
└── ...                  # Other genera (following alphabet)
```

### Service Modules (`services/`)

Each service is a **Crown Jewel** - a complete feature with its own:
- Business logic and adapters
- AGENTESE node registrations
- Frontend components (co-located)
- Database models and migrations

```
services/
├── brain/               # Holographic memory and semantic search
├── gardener/            # Agent lifecycle and health management  
├── town/                # Multi-agent simulation and coordination
├── park/                # Agent playground and experimentation
├── gestalt/             # UI/UX and visualization
├── witness/             # Observability and tracing
├── forge/               # Agent creation and deployment
└── providers.py         # Dependency injection registry
```

### Protocols (`protocols/`)

Universal protocols that enable cross-cutting concerns:

```
protocols/
├── agentese/            # Observer-dependent interaction protocol
│   ├── contexts/        # Five context resolvers (world, self, concept, void, time)
│   ├── metabolism/      # Entropy and fever management
│   └── middleware/      # Request/response processing
├── cli/                 # Command-line interface framework
├── api/                 # FastAPI web server and routes
├── streaming/           # Real-time event streaming
└── synergy/             # Agent coordination and composition
```

### Bootstrap Agents (`bootstrap/`)

The 7 irreducible agents from which all others can be regenerated:

```
bootstrap/
├── id.py               # Identity morphism (unit of composition)
├── compose.py          # Agent composition primitive
├── judge.py            # Value function (embodies 7 principles)
├── ground.py           # Empirical seed (Kent's preferences, world state)
├── contradict.py       # Contradiction recognizer (Hegelian dialectic)
├── sublate.py          # Synthesis generator (Aufhebung)
└── fix.py              # Fixed-point operator (recursive definitions)
```

## Naming Conventions

### Files and Directories
- **Snake_case**: Python modules and packages (`agent_base.py`)
- **kebab-case**: Frontend components and assets (`agent-card.tsx`)
- **PascalCase**: Classes and TypeScript interfaces (`AgentSnapshot`)
- **SCREAMING_SNAKE_CASE**: Constants and environment variables (`ANTHROPIC_API_KEY`)

### Agent Naming
- **Genus prefix**: `A-gent`, `K-gent`, `Flux-agent`
- **Descriptive suffix**: `BrainAgent`, `GardenerAgent`
- **Polynomial agents**: `SoulPolynomial`, `MemoryPolynomial`

### AGENTESE Paths
- **Context.holon.entity.aspect**: `world.town.citizen.greet`
- **Lowercase with dots**: `self.memory.capture`
- **Verbs for aspects**: `manifest`, `witness`, `capture`

## Configuration Files

### Python Configuration
- `pyproject.toml`: Package metadata, dependencies, tool configuration
- `mypy.ini`: Type checking configuration (strict mode)
- `conftest.py`: pytest configuration and fixtures
- `alembic.ini`: Database migration configuration

### Frontend Configuration  
- `package.json`: Dependencies and scripts
- `vite.config.ts`: Build tool configuration
- `tsconfig.json`: TypeScript compiler options
- `tailwind.config.js`: CSS framework configuration
- `eslint.config.js`: Linting rules

### Documentation
- `mkdocs.yml`: Documentation site configuration
- `.markdownlint.json`: Markdown linting rules

## Special Directories

### Testing
```
testing/
├── fixtures.py          # Test data factories
├── strategies.py        # Hypothesis property-based testing
├── sentinel/            # Test tier classification
└── optimization/        # Performance testing
```

### Fixtures (Pre-computed Data)
```
fixtures/
├── agent_snapshots/     # Agent state examples
├── soul_dialogue/       # K-gent conversation examples  
├── cognitive_trees/     # Brain memory structures
├── flux_states/         # Streaming agent states
└── generators/          # Scripts to regenerate fixtures
```

### Infrastructure
```
infra/
├── k8s/                 # Kubernetes manifests and operators
├── stigmergy/           # Pheromone store (Redis coordination)
├── ghost/               # Development utilities
└── providers/           # External service integrations
```

## File Patterns

### Agent Implementation
```python
# agents/k/soul.py
from agents.poly import PolyAgent
from protocols.agentese import node

@dataclass(frozen=True)
class SoulPolynomial(PolyAgent[SoulMode, SoulQuery, SoulInsight]):
    """K-gent soul with 7 eigenvector contexts."""
    
@node("self.soul.challenge")
async def challenge_soul(query: str, umwelt: Umwelt) -> SoulInsight:
    """Challenge the soul with a query."""
```

### Service Module
```python
# services/brain/service.py
from protocols.agentese import node
from .persistence import BrainAdapter
from .models import Crystal

class BrainService:
    def __init__(self, adapter: BrainAdapter):
        self.adapter = adapter

@node("self.memory.capture")
async def capture_memory(content: str, umwelt: Umwelt) -> Crystal:
    """Capture content into holographic memory."""
```

### Frontend Component
```typescript
// services/brain/web/CrystalViewer.tsx
import { Crystal } from '../types';

interface CrystalViewerProps {
  crystal: Crystal;
  onInteract?: (aspect: string) => void;
}

export function CrystalViewer({ crystal, onInteract }: CrystalViewerProps) {
  // Component implementation
}
```

## Import Conventions

### Python Imports
```python
# Standard library
import asyncio
from dataclasses import dataclass
from typing import Generic, TypeVar

# Third-party
import httpx
from fastapi import FastAPI
from sqlalchemy import select

# Local - absolute imports from project root
from agents.poly import PolyAgent
from protocols.agentese import node, Umwelt
from services.brain import BrainService
```

### TypeScript Imports
```typescript
// External libraries
import React from 'react';
import { motion } from 'framer-motion';

// Internal - using path aliases
import { Button } from '@/components/ui/button';
import { CrystalViewer } from '@brain/CrystalViewer';
import { useShell } from '@/shell/ShellProvider';
```

## Architecture Principles in Structure

### Single Source of Truth (AD-011)
- AGENTESE registry (`@node` decorator) defines all paths
- Frontend navigation derives from backend registry
- No hardcoded path lists or aliases

### Metaphysical Fullstack (AD-009)  
- Services own their complete vertical slice
- Frontend components co-located with backend logic
- Main website is shallow container importing from services

### Graceful Degradation
- Optional dependencies clearly marked
- Fallback implementations alongside primary ones
- Infrastructure adapters handle missing services

### Generative Over Enumerative (AD-003)
- Operads define composition grammar
- CLI commands generated from operads
- Tests derived from specifications

### Pre-Computed Richness (AD-004)
- Demo data uses pre-computed LLM outputs in `fixtures/`
- Hotload for development velocity
- Real agent outputs, not synthetic stubs

## Key Architectural Decisions

### AD-002: Polynomial Generalization
Agents generalize from `Agent[A, B]` to `PolyAgent[S, A, B]` where state-dependent behavior is required. Real agents have **modes** - a doctor agent in "diagnosis mode" accepts symptoms; in "treatment mode" it accepts test results.

### AD-006: Unified Categorical Foundation
All domain-specific agent systems instantiate the same pattern: **PolyAgent + Operad + Sheaf**. Agent Town, N-Phase development, K-gent Soul, and D-gent Memory all use identical mathematical structure.

### AD-009: Metaphysical Fullstack Agent
Every agent is a vertical slice from persistence to projection. Service modules own business logic, adapters, and frontend components. The main website is a shallow container functor.

### AD-011: Registry as Single Source of Truth
The AGENTESE registry (`@node` decorator) is the single source of truth for all paths. Frontend, CLI, and API derive from it - never the reverse.