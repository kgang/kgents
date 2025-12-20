# Design Document: Meaning Token Frontend Architecture

## Overview

The Meaning Token Frontend Architecture represents a **radical departure** from traditional frontend development. We are not building a better React app—we are eliminating the concept of "frontend" as a separate concern entirely.

**The Revolutionary Insight**: There is no frontend. There is no backend. There are only **meaning tokens** that project to whatever surface observes them. The CLI, the web browser, the marimo notebook, the VR headset—these are not different applications. They are different **observers** receiving projections of the same semantic reality.

This design unifies:
- **Interactive Text Protocol** — Text files ARE interfaces
- **Projection Protocol** — Rendering is observation, not construction
- **Formal Verification Metatheory** — Interactions are proofs
- **AGENTESE** — The protocol IS the API
- **Metaphysical Fullstack** — Every agent is a complete vertical slice

> *"The noun is a lie. There is only the rate of change."*
> *"And the rate of change of a document IS its interactivity."*

### What We Are Eliminating

| Traditional Concept | Radical Replacement |
|---------------------|---------------------|
| React components | Meaning token projections |
| REST API routes | AGENTESE paths (protocol IS API) |
| State management (Redux/Zustand) | Document Polynomial + Sheaf coherence |
| CSS styling | Density-parameterized projection |
| Frontend/backend split | Metaphysical Fullstack (no split) |
| UI component library | Token affordance registry |
| Page routing | AGENTESE path navigation |
| Form handling | Token mutation with trace witnesses |
| Error boundaries | Sympathetic degradation |
| Loading states | Polynomial position (SYNCING) |

### The Paradigm Shift

**Before**: Build UI components → Connect to API → Manage state → Handle errors
**After**: Define meaning tokens → Register affordances → Project to observers → Coherence is automatic

The entire frontend becomes a **projection functor**—a mathematical transformation that preserves structure while adapting to the observer's capacity to receive.

## Architecture

### The Radical Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OBSERVER SURFACES                                    │
│   Human eyes see CLI, Web, VR. But these are not "frontends."               │
│   They are OBSERVERS receiving projections of semantic reality.              │
│                                                                              │
│   CLI (Rich) │ TUI (Textual) │ Web │ marimo │ JSON │ VR │ Audio │ Haptic   │
└──────┬───────┴───────┬───────┴──┬──┴────┬───┴───┬──┴──┬─┴───┬───┴────┬─────┘
       │               │          │       │       │     │     │        │
       └───────────────┴──────────┴───────┴───────┴─────┴─────┴────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE PROJECTION FUNCTOR                                    │
│                                                                              │
│   P : (MeaningToken × Observer) → Renderable                                │
│                                                                              │
│   This is NOT a rendering engine. It is a NATURAL TRANSFORMATION.           │
│   The functor preserves structure: P(f ∘ g) = P(f) ∘ P(g)                   │
│   The functor respects identity: P(id) = id                                 │
│   The functor is LOSSY by design: different observers, different fidelity   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MEANING TOKEN UNIVERSE                                    │
│                                                                              │
│   Tokens are not UI components. They are SEMANTIC PRIMITIVES.               │
│   They carry meaning independent of how they are rendered.                   │
│                                                                              │
│   ┌──────────────┬──────────────┬──────────────┬──────────────┐            │
│   │ AGENTESEPath │ TaskCheckbox │    Image     │  CodeBlock   │            │
│   │  (portal)    │   (proof)    │  (context)   │  (action)    │            │
│   ├──────────────┼──────────────┼──────────────┼──────────────┤            │
│   │ PrincipleRef │RequirementRef│   Entity     │   Relation   │            │
│   │  (anchor)    │   (trace)    │  (noun)      │   (verb)     │            │
│   └──────────────┴──────────────┴──────────────┴──────────────┘            │
│                                                                              │
│   Token Registry: The SINGLE SOURCE OF TRUTH (AD-011)                       │
│   No component library. No design system. Just tokens and affordances.      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DOCUMENT AS POLYNOMIAL FUNCTOR                            │
│                                                                              │
│   Documents are not files. They are STATE MACHINES with mode-dependent I/O. │
│                                                                              │
│   DocumentPolynomial[S, A, B] where:                                        │
│     S = {VIEWING, EDITING, SYNCING, CONFLICTING}                            │
│     A(s) = valid inputs for state s                                         │
│     B(s) = outputs produced in state s                                      │
│                                                                              │
│   This is AD-002 applied to documents: real documents have MODES.           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DOCUMENT SHEAF (COHERENCE GUARANTEE)                      │
│                                                                              │
│   Multiple views of the same document MUST cohere.                          │
│   This is not "state sync"—it is SHEAF THEORY from algebraic topology.      │
│                                                                              │
│   Gluing Condition: Local views combine into global truth                   │
│   Separation Axiom: Global truth determines local views                     │
│                                                                              │
│   The file on disk is the TERMINAL OBJECT in the category of views.         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE SEMANTIC LAYER STACK                                  │
│                                                                              │
│   L4: GESTURAL ─── paste, click, hover, drag (embodied interaction)         │
│         │                                                                    │
│   L3: SEMANTIC ─── token patterns → affordance generators                   │
│         │                                                                    │
│   L2: STRUCTURAL ─ markdown AST with token extraction                       │
│         │                                                                    │
│   L1: TEXTUAL ──── valid markdown, git-diffable, readable anywhere          │
│                                                                              │
│   Each layer is a FUNCTOR. L4 ∘ L3 ∘ L2 ∘ L1 = Full Interactive Experience │
│   But L1 alone is ALWAYS valid. Progressive enhancement, not degradation.   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VERIFICATION AS FIRST-CLASS CITIZEN                       │
│                                                                              │
│   Every interaction is a PROOF. Every toggle is a TRACE WITNESS.            │
│   The UI is not separate from verification—it IS verification.              │
│                                                                              │
│   TraceWitness: Interaction → Constructive proof of behavior                │
│   VerificationGraph: Token → Derivation path from principles                │
│   GenerativeLoop: Interactions → Spec refinement → Better tokens            │
│                                                                              │
│   This closes the loop: USE the system → IMPROVE the system                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The Death of "Frontend"

Traditional frontend development assumes:
1. There is a "backend" that has the truth
2. There is a "frontend" that displays it
3. State must be "synchronized" between them
4. Components are the unit of composition

We reject all of this.

**Our model**:
1. There is MEANING (tokens)
2. There are OBSERVERS (surfaces)
3. There is PROJECTION (the functor)
4. Coherence is MATHEMATICAL (sheaf theory)

The "frontend" is just one observer among many. The CLI is equally valid. The JSON API is equally valid. A future audio interface is equally valid. They all receive projections of the same semantic reality.

## Components and Interfaces

### The Radical Implications

Before diving into components, understand what we are NOT building:

**We are NOT building**:
- A React application with components
- A design system with buttons and cards
- A state management solution
- A REST API with routes
- A CSS framework

**We ARE building**:
- A **Token Universe** where meaning exists independent of rendering
- A **Projection Functor** that transforms meaning to observation
- A **Polynomial Document** that has modes, not states
- A **Sheaf of Views** that guarantees coherence mathematically
- A **Verification Layer** where every click is a proof

### 1. Token Registry

The single source of truth for all meaning token definitions.

```python
from dataclasses import dataclass, field
from typing import Protocol, Callable, Awaitable
import re

@dataclass(frozen=True)
class TokenPattern:
    """Pattern for recognizing a meaning token in text."""
    name: str
    regex: re.Pattern
    priority: int = 0  # Higher priority matches first

@dataclass(frozen=True)
class Affordance:
    """An interaction possibility offered by a token."""
    name: str
    action: str  # "hover", "click", "drag", "right-click"
    handler: str  # AGENTESE path or callback reference
    enabled: bool = True

@dataclass(frozen=True)
class TokenDefinition:
    """Complete definition of a meaning token type."""
    name: str
    pattern: TokenPattern
    affordances: tuple[Affordance, ...]
    projectors: dict[str, str]  # target → projector module path

class TokenRegistry:
    """Single source of truth for token definitions (AD-011)."""
    
    _tokens: dict[str, TokenDefinition] = {}
    
    @classmethod
    def register(cls, definition: TokenDefinition) -> None:
        """Register a token type."""
        cls._tokens[definition.name] = definition
    
    @classmethod
    def get(cls, name: str) -> TokenDefinition | None:
        """Get token definition by name."""
        return cls._tokens.get(name)
    
    @classmethod
    def recognize(cls, text: str) -> list[tuple[TokenDefinition, re.Match]]:
        """Find all tokens in text, ordered by position then priority."""
        matches = []
        for defn in cls._tokens.values():
            for match in defn.pattern.regex.finditer(text):
                matches.append((defn, match))
        return sorted(matches, key=lambda x: (x[1].start(), -x[0].pattern.priority))

# Core token registrations
CORE_TOKENS = [
    TokenDefinition(
        name="agentese_path",
        pattern=TokenPattern(
            name="agentese_path",
            regex=re.compile(r'`((?:world|self|concept|void|time)\.[a-z_.]+)`'),
            priority=10,
        ),
        affordances=(
            Affordance("hover", "hover", "self.document.token.hover"),
            Affordance("navigate", "click", "self.document.token.navigate"),
            Affordance("context_menu", "right-click", "self.document.token.menu"),
            Affordance("drag_to_repl", "drag", "self.document.token.drag"),
        ),
        projectors={
            "cli": "services.interactive_text.projectors.cli.agentese_path",
            "web": "services.interactive_text.projectors.web.AGENTESEPathToken",
            "json": "services.interactive_text.projectors.json.agentese_path",
        },
    ),
    TokenDefinition(
        name="task_checkbox",
        pattern=TokenPattern(
            name="task_checkbox",
            regex=re.compile(r'- \[([ x])\] (.+?)(?:\n|$)', re.MULTILINE),
            priority=10,
        ),
        affordances=(
            Affordance("toggle", "click", "self.document.task.toggle"),
            Affordance("view_trace", "hover", "self.document.task.trace"),
            Affordance("view_changes", "click", "self.document.task.diff"),
        ),
        projectors={
            "cli": "services.interactive_text.projectors.cli.task_checkbox",
            "web": "services.interactive_text.projectors.web.TaskCheckboxToken",
            "json": "services.interactive_text.projectors.json.task_checkbox",
        },
    ),
    # ... remaining core tokens
]
```

### 2. Meaning Token Base

Abstract base for all meaning tokens with projection capability.

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')  # Projection target type

class MeaningToken(ABC, Generic[T]):
    """Base class for meaning tokens—semantic primitives that project to renderings."""
    
    @property
    @abstractmethod
    def token_type(self) -> str:
        """Token type name from registry."""
        ...
    
    @property
    @abstractmethod
    def source_text(self) -> str:
        """Original text that was recognized as this token."""
        ...
    
    @property
    @abstractmethod
    def source_position(self) -> tuple[int, int]:
        """(start, end) position in source document."""
        ...
    
    @abstractmethod
    async def get_affordances(self, observer: Observer) -> list[Affordance]:
        """Get available affordances for this observer."""
        ...
    
    @abstractmethod
    async def project(self, target: str, observer: Observer) -> T:
        """Project token to target-specific rendering."""
        ...
    
    async def on_interact(self, action: str, observer: Observer, **kwargs) -> InteractionResult:
        """Handle interaction with this token."""
        affordance = next((a for a in await self.get_affordances(observer) if a.action == action), None)
        if not affordance or not affordance.enabled:
            return InteractionResult.not_available(action)
        
        # Invoke AGENTESE handler
        result = await logos.invoke(affordance.handler, observer, token=self, **kwargs)
        
        # Capture trace witness for verification
        witness = await logos.invoke(
            "world.trace.capture",
            observer,
            trace=ExecutionTrace(
                agent_path=f"self.document.token.{self.token_type}",
                operation=action,
                input_data={"token": self.source_text, **kwargs},
                output_data=result,
            ),
        )
        
        return InteractionResult.success(result, witness_id=witness.id)
```

### 3. Document Polynomial

State machine governing document editing modes.

```python
from dataclasses import dataclass
from typing import ClassVar, Literal
from enum import Enum

class DocumentState(Enum):
    VIEWING = "VIEWING"
    EDITING = "EDITING"
    SYNCING = "SYNCING"
    CONFLICTING = "CONFLICTING"

@dataclass(frozen=True)
class DocumentPolynomial:
    """Document as polynomial functor: editing states with mode-dependent inputs.
    
    Per AD-002, documents have state-dependent behavior. The polynomial
    captures valid inputs per state and transition rules.
    """
    
    positions: ClassVar[frozenset[DocumentState]] = frozenset(DocumentState)
    
    @staticmethod
    def directions(state: DocumentState) -> frozenset[str]:
        """Valid inputs per state."""
        return {
            DocumentState.VIEWING: frozenset({"edit", "refresh", "hover", "click", "drag"}),
            DocumentState.EDITING: frozenset({"save", "cancel", "continue_edit", "hover"}),
            DocumentState.SYNCING: frozenset({"wait", "force_local", "force_remote"}),
            DocumentState.CONFLICTING: frozenset({"resolve", "abort", "view_diff"}),
        }[state]
    
    @staticmethod
    def transition(state: DocumentState, input: str) -> tuple[DocumentState, "TransitionOutput"]:
        """State × Input → (NewState, Output)."""
        transitions: dict[tuple[DocumentState, str], tuple[DocumentState, type]] = {
            # VIEWING transitions
            (DocumentState.VIEWING, "edit"): (DocumentState.EDITING, EditSession),
            (DocumentState.VIEWING, "refresh"): (DocumentState.VIEWING, RefreshResult),
            (DocumentState.VIEWING, "hover"): (DocumentState.VIEWING, HoverInfo),
            (DocumentState.VIEWING, "click"): (DocumentState.VIEWING, ClickResult),
            (DocumentState.VIEWING, "drag"): (DocumentState.VIEWING, DragResult),
            
            # EDITING transitions
            (DocumentState.EDITING, "save"): (DocumentState.SYNCING, SaveRequest),
            (DocumentState.EDITING, "cancel"): (DocumentState.VIEWING, CancelResult),
            (DocumentState.EDITING, "continue_edit"): (DocumentState.EDITING, EditContinue),
            (DocumentState.EDITING, "hover"): (DocumentState.EDITING, HoverInfo),
            
            # SYNCING transitions
            (DocumentState.SYNCING, "wait"): (DocumentState.VIEWING, SyncComplete),
            (DocumentState.SYNCING, "force_local"): (DocumentState.VIEWING, LocalWins),
            (DocumentState.SYNCING, "force_remote"): (DocumentState.VIEWING, RemoteWins),
            
            # CONFLICTING transitions
            (DocumentState.CONFLICTING, "resolve"): (DocumentState.VIEWING, Resolved),
            (DocumentState.CONFLICTING, "abort"): (DocumentState.VIEWING, Aborted),
            (DocumentState.CONFLICTING, "view_diff"): (DocumentState.CONFLICTING, DiffView),
        }
        
        if (state, input) in transitions:
            new_state, output_type = transitions[(state, input)]
            return (new_state, output_type())
        
        return (state, NoOp())
    
    @staticmethod
    def verify_laws() -> bool:
        """Verify polynomial laws hold."""
        # Identity: VIEWING with no-op stays VIEWING
        # Determinism: Same state + input always produces same output
        for state in DocumentState:
            for input in DocumentPolynomial.directions(state):
                result1 = DocumentPolynomial.transition(state, input)
                result2 = DocumentPolynomial.transition(state, input)
                if result1[0] != result2[0]:
                    return False
        return True
```

### 4. Document Sheaf

Coherence structure ensuring multi-view consistency.

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

class DocumentView(Protocol):
    """Protocol for document views."""
    view_id: str
    document_path: Path
    tokens: frozenset[str]  # Token IDs visible in this view
    
    def state_of(self, token_id: str) -> Any:
        """Get state of a token in this view."""
        ...
    
    async def update(self, changes: list["TokenChange"]) -> None:
        """Apply changes to this view."""
        ...

@dataclass
class DocumentSheaf:
    """Sheaf structure ensuring multi-view coherence.
    
    The sheaf condition guarantees that local views glue to global state.
    The file on disk is always canonical; views are projections that must reconcile.
    """
    
    document_path: Path
    views: list[DocumentView] = field(default_factory=list)
    _file_watcher: "FileWatcher | None" = None
    
    def overlap(self, v1: DocumentView, v2: DocumentView) -> set[str]:
        """Tokens visible in both views."""
        return set(v1.tokens) & set(v2.tokens)
    
    def compatible(self, v1: DocumentView, v2: DocumentView) -> bool:
        """Views agree on overlapping tokens (sheaf condition)."""
        shared = self.overlap(v1, v2)
        return all(v1.state_of(t) == v2.state_of(t) for t in shared)
    
    def verify_sheaf_condition(self) -> SheafVerification:
        """Verify all views are pairwise compatible."""
        conflicts = []
        for i, v1 in enumerate(self.views):
            for v2 in self.views[i+1:]:
                if not self.compatible(v1, v2):
                    conflicts.append(SheafConflict(v1.view_id, v2.view_id, self.overlap(v1, v2)))
        
        if conflicts:
            return SheafVerification.failure(conflicts)
        return SheafVerification.success()
    
    def glue(self) -> "Document":
        """Combine compatible views into global document.
        
        The file on disk is always canonical—this reads and parses it.
        """
        return Document.from_file(self.document_path)
    
    async def on_file_change(self, change: "FileChange") -> None:
        """Handle file change—broadcast to all views."""
        document = self.glue()
        tokens = document.extract_tokens()
        
        for view in self.views:
            await view.update([TokenChange(t, "modified") for t in tokens])
    
    async def on_view_edit(self, view: DocumentView, edit: "Edit") -> None:
        """Handle edit from a view—apply to file, broadcast to all."""
        # 1. Apply edit to canonical file
        await self._apply_edit_to_file(edit)
        
        # 2. File watcher will trigger on_file_change
        # 3. All views get updated (including the editing view)
    
    async def _apply_edit_to_file(self, edit: "Edit") -> None:
        """Apply edit to file with roundtrip fidelity."""
        content = self.document_path.read_text()
        new_content = edit.apply(content)
        self.document_path.write_text(new_content)
```

### 5. Projection Functor

Natural transformation from meaning tokens to target-specific renderings.

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

Target = TypeVar('Target')

class ProjectionFunctor(ABC, Generic[Target]):
    """Functor projecting meaning tokens to target-specific renderings.
    
    Satisfies naturality: for all state morphisms f : S₁ → S₂,
    P(f(s)) = P_target(P(s)) where P_target is the target's state update.
    """
    
    target_name: str
    
    @abstractmethod
    async def project_token(self, token: MeaningToken, observer: Observer) -> Target:
        """Project a single token."""
        ...
    
    @abstractmethod
    async def project_document(self, document: "Document", observer: Observer) -> Target:
        """Project entire document."""
        ...
    
    async def project_composition(
        self, 
        tokens: list[MeaningToken], 
        composition: str,  # ">>" or "//"
        observer: Observer
    ) -> Target:
        """Project composed tokens.
        
        Horizontal (>>): P(A >> B) = P(A) >> P(B)
        Vertical (//): P(A // B) = P(A) // P(B)
        """
        projections = [await self.project_token(t, observer) for t in tokens]
        return self._compose(projections, composition)
    
    @abstractmethod
    def _compose(self, projections: list[Target], composition: str) -> Target:
        """Compose projected elements."""
        ...

class CLIProjectionFunctor(ProjectionFunctor[str]):
    """Project meaning tokens to Rich terminal output."""
    
    target_name = "cli"
    
    async def project_token(self, token: MeaningToken, observer: Observer) -> str:
        """Project token to Rich markup."""
        match token.token_type:
            case "agentese_path":
                return f"[cyan]{token.source_text}[/cyan]"
            case "task_checkbox":
                checked = "✓" if token.checked else " "
                return f"[{checked}] {token.description}"
            case "image":
                return f"[dim]📷 {token.alt_text}[/dim]"
            case _:
                return token.source_text
    
    async def project_document(self, document: "Document", observer: Observer) -> str:
        """Project document to Rich markup."""
        result = []
        for block in document.blocks:
            if isinstance(block, TokenBlock):
                result.append(await self.project_token(block.token, observer))
            else:
                result.append(block.text)
        return "\n".join(result)
    
    def _compose(self, projections: list[str], composition: str) -> str:
        if composition == ">>":
            return " ".join(projections)
        else:  # "//"
            return "\n".join(projections)

class WebProjectionFunctor(ProjectionFunctor["ReactElement"]):
    """Project meaning tokens to React components."""
    
    target_name = "web"
    
    async def project_token(self, token: MeaningToken, observer: Observer) -> "ReactElement":
        """Project token to React element specification."""
        affordances = await token.get_affordances(observer)
        
        return ReactElement(
            component=f"{token.token_type.title()}Token",
            props={
                "token": token.to_dict(),
                "affordances": [a.to_dict() for a in affordances],
                "observer": observer.to_dict(),
            },
        )
    
    async def project_document(self, document: "Document", observer: Observer) -> "ReactElement":
        """Project document to React element tree."""
        children = []
        for block in document.blocks:
            if isinstance(block, TokenBlock):
                children.append(await self.project_token(block.token, observer))
            else:
                children.append(ReactElement("TextBlock", {"text": block.text}))
        
        return ReactElement("InteractiveDocument", {"children": children})
    
    def _compose(self, projections: list["ReactElement"], composition: str) -> "ReactElement":
        if composition == ">>":
            return ReactElement("HStack", {"children": projections})
        else:  # "//"
            return ReactElement("VStack", {"children": projections})
```

### 6. AGENTESE Integration

AGENTESE nodes for the interactive text system.

```python
from protocols.agentese import node, aspect, AspectCategory, Effect

@node(
    "self.document.interactive",
    dependencies=("interactive_text_service", "verification_service"),
    description="Interactive text rendering and token affordances"
)
@dataclass
class InteractiveTextNode:
    """AGENTESE node for interactive text system."""
    
    service: "InteractiveTextService"
    verification: "VerificationService"
    
    @aspect(category=AspectCategory.PERCEPTION)
    async def manifest(self, observer: Observer, path: Path) -> InteractiveDocument:
        """Render document with observer-appropriate affordances."""
        document = await self.service.load(path)
        tokens = document.extract_tokens()
        affordances = await self.service.get_affordances(tokens, observer)
        
        return InteractiveDocument(
            path=path,
            tokens=tokens,
            affordances=affordances,
            polynomial_state=document.state,
        )
    
    @aspect(category=AspectCategory.MUTATION, effects=[Effect.WRITES("documents")])
    async def toggle_task(self, observer: Observer, task_id: str) -> ToggleResult:
        """Toggle task checkbox, capturing trace witness."""
        # 1. Toggle in document
        result = await self.service.toggle_task(task_id)
        
        # 2. Capture trace witness
        witness = await logos.invoke(
            "world.trace.capture",
            observer,
            trace=ExecutionTrace(
                agent_path="self.document.task",
                operation="toggle",
                input_data={"task_id": task_id, "new_state": result.new_state},
            ),
        )
        
        # 3. Verify if completing
        if result.new_state:
            verification = await self.verification.check_task(task_id)
            if not verification.passed:
                return ToggleResult.warning(
                    message="Task marked complete but verification found issues",
                    issues=verification.issues,
                    witness_id=witness.id,
                )
        
        return ToggleResult.success(witness_id=witness.id)
    
    @aspect(category=AspectCategory.PERCEPTION)
    async def analyze_image(self, observer: Observer, image_path: Path) -> ImageAnalysis:
        """Get AI analysis of image in document context."""
        return await self.service.analyze_image(image_path)
    
    @aspect(category=AspectCategory.PERCEPTION)
    async def hover_token(self, observer: Observer, token_id: str) -> HoverInfo:
        """Get hover information for a token."""
        token = await self.service.get_token(token_id)
        
        match token.token_type:
            case "agentese_path":
                # Get polynomial state from AGENTESE registry
                node = get_registry().get(token.path)
                if node:
                    return HoverInfo(
                        title=token.path,
                        content=await node.manifest(observer),
                        actions=node.aspects,
                    )
                return HoverInfo.ghost(token.path)
            
            case "task_checkbox":
                # Get verification status
                trace = await self.verification.get_task_trace(token.task_id)
                return HoverInfo(
                    title=token.description,
                    content=trace.summary if trace else "No verification trace",
                    actions=["view_trace", "view_diff"],
                )
            
            case _:
                return HoverInfo.default(token)
```

### 7. DataBus Integration

Event coordination across Crown Jewels.

```python
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class DocumentEvent:
    """Event emitted by interactive text system."""
    event_type: Literal[
        "DOCUMENT_OPENED",
        "DOCUMENT_CHANGED", 
        "TOKEN_TOGGLED",
        "TOKEN_HOVERED",
        "VIEW_OPENED",
        "VIEW_CLOSED",
    ]
    document_path: Path
    tokens_affected: tuple[str, ...]
    observer_id: str
    timestamp: datetime

# Wire to SynergyBus for cross-jewel coordination
SYNERGY_WIRING = {
    "document.task_completed": [
        "self.verification.on_task_complete",  # Verification service
        "world.trace.capture",                  # Trace witness
        "self.memory.crystallize",              # M-gent memory
    ],
    "document.token_hovered": [
        "self.document.token.hover",            # Hover handler
    ],
    "document.image_added": [
        "self.document.image.analyze",          # Image analysis
        "self.memory.associate",                # Memory association
    ],
}

async def wire_document_events():
    """Wire document events to cross-jewel handlers."""
    from protocols.synergy import SynergyBus
    
    for pattern, handlers in SYNERGY_WIRING.items():
        for handler in handlers:
            SynergyBus.subscribe(pattern, handler)
```

## Data Models

```python
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from typing import Any

@dataclass(frozen=True)
class Document:
    """A document with extracted meaning tokens."""
    path: Path
    content: str
    blocks: tuple["Block", ...]
    tokens: tuple[MeaningToken, ...]
    state: DocumentState = DocumentState.VIEWING
    
    @classmethod
    def from_file(cls, path: Path) -> "Document":
        """Load document from file."""
        content = path.read_text()
        blocks = parse_markdown(content)
        tokens = extract_tokens(blocks)
        return cls(path=path, content=content, blocks=blocks, tokens=tokens)
    
    def extract_tokens(self) -> list[MeaningToken]:
        """Extract all meaning tokens from document."""
        return list(self.tokens)

@dataclass(frozen=True)
class Block:
    """A block in a markdown document."""
    block_type: str  # "paragraph", "heading", "list", "code", etc.
    text: str
    start_line: int
    end_line: int

@dataclass(frozen=True)
class TokenBlock(Block):
    """A block containing a meaning token."""
    token: MeaningToken

@dataclass(frozen=True)
class InteractiveDocument:
    """Document with interactive affordances for an observer."""
    path: Path
    tokens: list[MeaningToken]
    affordances: dict[str, list[Affordance]]  # token_id → affordances
    polynomial_state: DocumentState

@dataclass(frozen=True)
class ToggleResult:
    """Result of toggling a task checkbox."""
    success: bool
    new_state: bool
    witness_id: str | None
    message: str | None = None
    issues: list[str] = field(default_factory=list)
    
    @classmethod
    def success(cls, witness_id: str) -> "ToggleResult":
        return cls(success=True, new_state=True, witness_id=witness_id)
    
    @classmethod
    def warning(cls, message: str, issues: list[str], witness_id: str) -> "ToggleResult":
        return cls(success=True, new_state=True, witness_id=witness_id, message=message, issues=issues)

@dataclass(frozen=True)
class HoverInfo:
    """Information displayed on token hover."""
    title: str
    content: Any
    actions: list[str] = field(default_factory=list)
    
    @classmethod
    def ghost(cls, path: str) -> "HoverInfo":
        return cls(title=path, content="Path not yet implemented", actions=[])
    
    @classmethod
    def default(cls, token: MeaningToken) -> "HoverInfo":
        return cls(title=token.token_type, content=token.source_text)

@dataclass(frozen=True)
class ImageAnalysis:
    """AI-generated analysis of an image."""
    description: str
    detected_elements: list[str]
    suggested_context: str
    cached: bool = False

@dataclass(frozen=True)
class ReactElement:
    """Specification for a React element (used in web projection)."""
    component: str
    props: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {"component": self.component, "props": self.props}

@dataclass(frozen=True)
class SheafVerification:
    """Result of verifying sheaf condition."""
    passed: bool
    conflicts: list["SheafConflict"] = field(default_factory=list)
    
    @classmethod
    def success(cls) -> "SheafVerification":
        return cls(passed=True)
    
    @classmethod
    def failure(cls, conflicts: list["SheafConflict"]) -> "SheafVerification":
        return cls(passed=False, conflicts=conflicts)

@dataclass(frozen=True)
class SheafConflict:
    """A conflict between two views."""
    view1_id: str
    view2_id: str
    conflicting_tokens: set[str]
```



## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Token Recognition Completeness

*For any* text containing patterns matching the six core token types (AGENTESEPath, TaskCheckbox, Image, CodeBlock, PrincipleRef, RequirementRef), the parser SHALL correctly identify and extract all matching tokens with accurate source positions.

**Validates: Requirements 1.1, 5.1, 6.1, 7.1, 8.1**

### Property 2: Token Affordance Generation

*For any* registered token definition and *for any* supported projection target, the system SHALL generate valid affordances for that token on that target.

**Validates: Requirements 1.2, 1.3**

### Property 3: Projection Functor Composition Law

*For any* two meaning tokens A and B, projecting their horizontal composition SHALL equal composing their projections: P(A >> B) = P(A) >> P(B).

**Validates: Requirements 1.5, 2.6**

### Property 4: Projection Naturality Condition

*For any* meaning token and *for any* state change to that token, projecting before the change then applying the target's state update SHALL produce the same result as applying the change then projecting.

**Validates: Requirements 2.1, 2.3**

### Property 5: Density-Parameterized Projection

*For any* meaning token and *for any* density value (compact, comfortable, spacious), the projection SHALL produce valid target-specific output that differs appropriately by density.

**Validates: Requirements 2.4, 2.5**

### Property 6: Document Polynomial State Validity

*For any* document state and *for any* input, the input is valid if and only if it is in the set of valid inputs for that state, and valid inputs produce deterministic state transitions.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

### Property 7: Document Polynomial Event Emission

*For any* valid state transition in the Document Polynomial, the system SHALL emit a corresponding event through the DataBus.

**Validates: Requirements 3.6, 11.1**

### Property 8: Document Sheaf Coherence

*For any* document opened in multiple views, the sheaf condition SHALL hold: all views with overlapping tokens agree on token state, and compatible views can be glued into a consistent global document.

**Validates: Requirements 4.1, 4.4, 4.5, 4.6**

### Property 9: Document Sheaf Propagation

*For any* edit in any view of a document, the change SHALL propagate to all other views, and the file on disk SHALL reflect the canonical state.

**Validates: Requirements 4.2, 4.3**

### Property 10: AGENTESE Path Affordances

*For any* recognized AGENTESE path token, hover SHALL return polynomial state information, click SHALL produce navigation action, right-click SHALL produce context menu, and drag SHALL produce REPL pre-fill.

**Validates: Requirements 5.2, 5.3, 5.4, 5.5**

### Property 11: Ghost Token Rendering

*For any* AGENTESE path referencing a non-existent node, the system SHALL render it as a ghost token with reduced affordances (no invoke, no state display).

**Validates: Requirements 5.6**

### Property 12: Task Checkbox Toggle with Trace

*For any* task checkbox toggle operation, the system SHALL persist the new state to the source file AND capture a Trace_Witness through the verification system.

**Validates: Requirements 6.2, 6.3, 12.1**

### Property 13: Task Verification Integration

*For any* task with requirement references, the system SHALL link to verification status, and *for any* task completion that fails verification, the system SHALL display warnings with counter-examples.

**Validates: Requirements 6.4, 6.5, 12.2, 12.4**

### Property 14: Image Token Graceful Degradation

*For any* image token, when LLM is available, hover SHALL display AI-generated description; when LLM is unavailable, the image SHALL still render with a "requires connection" indicator.

**Validates: Requirements 7.2, 7.5, 14.1**

### Property 15: Code Block Execution Sandboxing

*For any* code block execution, the execution SHALL occur in a sandboxed environment, and *for any* code block containing AGENTESE invocations, execution traces SHALL be captured.

**Validates: Requirements 8.3, 8.4, 8.6**

### Property 16: Roundtrip Fidelity

*For any* valid markdown document, parsing then rendering SHALL produce byte-identical output to the original: render(parse(doc)) ≡ doc.

**Validates: Requirements 9.2, 9.5, 16.1, 16.2**

### Property 17: Progressive Enhancement

*For any* document, each semantic layer (L1-L4) SHALL add capability without breaking lower layers: a document valid at L1 remains valid when processed at L2, L3, or L4.

**Validates: Requirements 9.6**

### Property 18: Observer-Dependent Projection

*For any* meaning token and *for any* two observers with different umwelts (capabilities, density, role), the projections SHALL differ appropriately while maintaining semantic equivalence.

**Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.6**

### Property 19: Graceful Degradation

*For any* service unavailability (LLM, verification, network), the system SHALL continue to provide document access with degraded functionality clearly indicated, and SHALL reconcile deferred operations when services recover.

**Validates: Requirements 14.1, 14.2, 14.3, 14.4, 14.5, 14.6**

### Property 20: Cross-Jewel Event Coordination

*For any* token interaction that crosses jewel boundaries, events SHALL be wired through DataBus to SynergyBus, maintain causal ordering, and notify appropriate handlers (verification, memory, witness).

**Validates: Requirements 11.2, 11.3, 11.4, 11.5**

### Property 21: Parser Robustness

*For any* input text (including malformed markdown), the parser SHALL not crash and SHALL handle errors gracefully, providing source maps linking tokens to file positions.

**Validates: Requirements 16.5, 16.6**

### Property 22: Localized Token Modification

*For any* token modification, the system SHALL update only the affected region of the document, preserving all other content exactly.

**Validates: Requirements 16.4**

## Error Handling

The system uses sympathetic error handling with the Alive Workshop aesthetic:

```python
@dataclass(frozen=True)
class InteractiveTextError:
    """Sympathetic error with learning opportunities."""
    category: str
    message: str  # Warm, clear language
    context: dict[str, Any]
    suggestion: str | None
    affected_tokens: list[str] = field(default_factory=list)

# Sympathetic error messages
SYMPATHETIC_MESSAGES = {
    "token_parse_error": (
        "I couldn't quite understand this part of the document. "
        "Let me show you what I expected and suggest a fix."
    ),
    "sheaf_conflict": (
        "These views have gotten out of sync. "
        "Here's where they diverge and how we can bring them together."
    ),
    "verification_failed": (
        "The task is marked complete, but I found some concerns. "
        "Let me show you what I noticed so we can address it together."
    ),
    "service_unavailable": (
        "I can't reach the {service} service right now. "
        "I'll keep working with what I have and sync up when it's back."
    ),
    "ghost_path": (
        "This path ({path}) doesn't exist yet. "
        "It might be planned for the future, or there could be a typo."
    ),
}

async def handle_error(error: Exception, context: dict) -> InteractiveTextError:
    """Convert exception to sympathetic error."""
    match error:
        case TokenParseError(position=pos, expected=exp):
            return InteractiveTextError(
                category="parse",
                message=SYMPATHETIC_MESSAGES["token_parse_error"],
                context={"position": pos, "expected": exp},
                suggestion=f"Try: {exp}",
            )
        case SheafConflictError(conflicts=conflicts):
            return InteractiveTextError(
                category="coherence",
                message=SYMPATHETIC_MESSAGES["sheaf_conflict"],
                context={"conflicts": [c.to_dict() for c in conflicts]},
                suggestion="Refresh all views or resolve conflicts manually",
            )
        case _:
            return InteractiveTextError(
                category="unknown",
                message="Something unexpected happened. Let me try to help.",
                context={"error": str(error)},
                suggestion=None,
            )
```

## Testing Strategy

### Dual Testing Approach

**Unit Tests**: Specific examples, edge cases, integration points
- Token pattern recognition for each of the six core types
- Document polynomial state transitions
- Projection functor output for each target
- Error message formatting and sympathetic language

**Property-Based Tests**: Universal properties across all inputs
- All 22 correctness properties listed above
- Using Hypothesis for Python property-based testing
- Minimum 100 iterations per property test
- Each test tagged: **Feature: meaning-token-frontend, Property N: [property text]**

### Custom Generators

```python
from hypothesis import strategies as st, given

# Token generators
@st.composite
def agentese_path_strategy(draw):
    """Generate random AGENTESE paths."""
    context = draw(st.sampled_from(["world", "self", "concept", "void", "time"]))
    segments = draw(st.lists(st.from_regex(r'[a-z_]+', fullmatch=True), min_size=1, max_size=5))
    return f"`{context}.{'.'.join(segments)}`"

@st.composite
def task_checkbox_strategy(draw):
    """Generate random task checkboxes."""
    checked = draw(st.booleans())
    description = draw(st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_characters='\n')))
    return f"- [{'x' if checked else ' '}] {description}"

@st.composite
def markdown_document_strategy(draw):
    """Generate random markdown documents with tokens."""
    blocks = draw(st.lists(
        st.one_of(
            st.text(min_size=1, max_size=200),
            agentese_path_strategy(),
            task_checkbox_strategy(),
        ),
        min_size=1,
        max_size=20,
    ))
    return "\n\n".join(blocks)

@st.composite
def observer_strategy(draw):
    """Generate random observers with different umwelts."""
    return Observer(
        id=draw(st.uuids()).hex,
        capabilities=draw(st.frozensets(st.sampled_from(["llm", "verification", "network"]))),
        density=draw(st.sampled_from(["compact", "comfortable", "spacious"])),
        role=draw(st.sampled_from(["viewer", "editor", "admin"])),
    )

@st.composite
def document_state_strategy(draw):
    """Generate random document states."""
    return draw(st.sampled_from(list(DocumentState)))

# Property test examples
@given(doc=markdown_document_strategy())
def test_roundtrip_fidelity(doc: str):
    """Property 16: Roundtrip fidelity."""
    parsed = parse_markdown(doc)
    rendered = render_markdown(parsed)
    assert rendered == doc, f"Roundtrip failed: {doc!r} != {rendered!r}"

@given(state=document_state_strategy(), input=st.text(min_size=1, max_size=20))
def test_polynomial_determinism(state: DocumentState, input: str):
    """Property 6: Document polynomial state validity."""
    valid_inputs = DocumentPolynomial.directions(state)
    if input in valid_inputs:
        result1 = DocumentPolynomial.transition(state, input)
        result2 = DocumentPolynomial.transition(state, input)
        assert result1[0] == result2[0], "Non-deterministic transition"
```

## Implementation Notes

### Crown Jewel Structure

The "frontend" is eliminated. What remains is projection infrastructure within each Crown Jewel:

```
services/interactive-text/           # THE CORE JEWEL
├── __init__.py                      # Public API
├── universe.py                      # Token Universe definition
├── functor.py                       # Projection Functor implementation
├── polynomial.py                    # Document state machine
├── sheaf.py                         # Multi-view coherence
├── tokens/                          # Token type implementations
│   ├── __init__.py
│   ├── base.py                      # MeaningToken base class
│   ├── agentese_path.py             # Portal to agent system
│   ├── task_checkbox.py             # Proof of completion
│   ├── image.py                     # Multimodal context
│   ├── code_block.py                # Executable action
│   ├── principle_ref.py             # Anchor to principles
│   └── requirement_ref.py           # Trace to requirements
├── projectors/                      # Projection implementations
│   ├── __init__.py
│   ├── base.py                      # ProjectionFunctor base
│   ├── cli.py                       # Rich terminal projection
│   ├── tui.py                       # Textual widget projection
│   ├── web.py                       # DOM element projection
│   ├── json.py                      # API response projection
│   ├── marimo.py                    # anywidget projection
│   └── audio.py                     # Future: sonification
├── agentese_nodes.py                # AGENTESE integration
├── events.py                        # DataBus event definitions
├── persistence.py                   # File operations
├── observers/                       # Observer implementations
│   ├── __init__.py
│   ├── cli_observer.py              # Terminal observer
│   ├── web_observer.py              # Browser observer
│   └── api_observer.py              # Programmatic observer
└── _tests/
    ├── test_universe.py
    ├── test_functor.py
    ├── test_polynomial.py
    ├── test_sheaf.py
    └── test_properties.py           # Property-based tests

# THE WEB "FRONTEND" IS JUST A THIN PROJECTION RECEIVER
impl/claude/web/                     # NOT a frontend—a projection receiver
├── src/
│   ├── receiver.tsx                 # Receives projections, renders DOM
│   ├── observer.ts                  # Web observer implementation
│   └── shell.tsx                    # Minimal shell (routing from AGENTESE)
└── package.json                     # Minimal dependencies
```

### The Web Receiver (Not a Frontend)

The traditional `web/` directory is radically simplified. It is not a frontend—it is a **projection receiver**:

```typescript
// impl/claude/web/src/receiver.tsx
// This is the ENTIRE web "frontend"

import { useProjection } from './observer';

/**
 * The Projection Receiver.
 * 
 * This is NOT a React application. It is a thin layer that:
 * 1. Establishes an Observer connection to the projection functor
 * 2. Receives projected DOM elements
 * 3. Renders them
 * 
 * There are no components. There is no state management.
 * There is only projection reception.
 */
export function ProjectionReceiver() {
  const { projection, observer } = useProjection();
  
  // The projection IS the UI. We just render it.
  return (
    <div 
      className="projection-surface"
      data-observer-id={observer.id}
      data-density={observer.density}
    >
      {projection.render()}
    </div>
  );
}

// The observer hook connects to the projection functor
function useProjection() {
  const observer = useObserver();  // From AGENTESE context
  const [projection, setProjection] = useState<Projection | null>(null);
  
  useEffect(() => {
    // Subscribe to projections for this observer
    const unsubscribe = ProjectionFunctor.subscribe(observer, setProjection);
    return unsubscribe;
  }, [observer]);
  
  return { projection, observer };
}
```

### Eliminating React Components

Traditional React components are replaced by **token projectors**:

```typescript
// BEFORE: Traditional React component
function TaskList({ tasks }) {
  const [checked, setChecked] = useState({});
  return (
    <ul>
      {tasks.map(task => (
        <li key={task.id}>
          <input 
            type="checkbox" 
            checked={checked[task.id]}
            onChange={() => handleToggle(task.id)}
          />
          {task.description}
        </li>
      ))}
    </ul>
  );
}

// AFTER: Token projector (Python, projects to any surface)
class TaskCheckboxProjector(ProjectionFunctor[DOMElement]):
    """Projects TaskCheckbox tokens to DOM elements."""
    
    async def project_token(self, token: TaskCheckboxToken, observer: Observer) -> DOMElement:
        affordances = await token.get_affordances(observer)
        
        return DOMElement(
            tag="div",
            attrs={
                "class": "token task-checkbox",
                "data-token-id": token.id,
                "data-checked": str(token.checked).lower(),
            },
            children=[
                DOMElement(
                    tag="input",
                    attrs={
                        "type": "checkbox",
                        "checked": token.checked,
                        # Affordance wiring—not event handlers
                        "data-affordance": "toggle",
                        "data-handler": affordances["toggle"].handler,
                    },
                ),
                DOMElement(tag="span", children=[token.description]),
            ],
            # Affordances are data, not code
            affordances=affordances,
        )
```

### Eliminating State Management

State management (Redux, Zustand, etc.) is replaced by **Document Polynomial + Sheaf**:

```python
# BEFORE: Redux-style state management
# store.js, actions.js, reducers.js, selectors.js, thunks.js...
# Hundreds of lines of boilerplate

# AFTER: Document Polynomial (complete state machine in ~50 lines)
@dataclass(frozen=True)
class DocumentPolynomial:
    """The ENTIRE state management solution."""
    
    @staticmethod
    def directions(state: DocumentState) -> frozenset[str]:
        """What inputs are valid in this state?"""
        return {
            DocumentState.VIEWING: frozenset({"edit", "refresh", "hover", "click", "drag"}),
            DocumentState.EDITING: frozenset({"save", "cancel", "continue_edit", "hover"}),
            DocumentState.SYNCING: frozenset({"wait", "force_local", "force_remote"}),
            DocumentState.CONFLICTING: frozenset({"resolve", "abort", "view_diff"}),
        }[state]
    
    @staticmethod
    def transition(state: DocumentState, input: str) -> tuple[DocumentState, Any]:
        """State × Input → (NewState, Output). That's it. That's state management."""
        # ... transitions defined above
```

### Eliminating CSS

CSS is replaced by **density-parameterized projection**:

```python
# BEFORE: CSS files, Tailwind classes, styled-components...
# .task-checkbox { padding: 8px; }
# @media (max-width: 768px) { .task-checkbox { padding: 4px; } }

# AFTER: Density is a projection parameter
DENSITY_PARAMS = {
    "compact": {"padding": 4, "font_size": 14, "spacing": 2},
    "comfortable": {"padding": 8, "font_size": 16, "spacing": 4},
    "spacious": {"padding": 12, "font_size": 18, "spacing": 8},
}

async def project_token(self, token: MeaningToken, observer: Observer) -> DOMElement:
    params = DENSITY_PARAMS[observer.density]
    
    return DOMElement(
        tag="div",
        style={
            "padding": f"{params['padding']}px",
            "font-size": f"{params['font_size']}px",
        },
        # ...
    )
```

### Eliminating API Routes

API routes are replaced by **AGENTESE paths**:

```python
# BEFORE: Express/FastAPI routes
# @router.get("/api/tasks/{task_id}")
# @router.post("/api/tasks/{task_id}/toggle")
# @router.get("/api/documents/{doc_id}")
# ... hundreds of route definitions

# AFTER: AGENTESE paths (the protocol IS the API)
@node("self.document.task")
class TaskNode:
    @aspect(category=AspectCategory.PERCEPTION)
    async def manifest(self, observer: Observer, task_id: str) -> Task:
        """GET /api/tasks/{task_id} is now: logos.invoke("self.document.task.manifest", ...)"""
        ...
    
    @aspect(category=AspectCategory.MUTATION)
    async def toggle(self, observer: Observer, task_id: str) -> ToggleResult:
        """POST /api/tasks/{task_id}/toggle is now: logos.invoke("self.document.task.toggle", ...)"""
        ...

# The AGENTESE gateway auto-exposes all nodes. No routes to maintain.
```

### Integration with Formal Verification

The interactive text system integrates deeply with the formal verification metatheory:

```python
# Task completion creates trace witness
async def on_task_toggle(task_id: str, new_state: bool) -> ToggleResult:
    # 1. Update file (source of truth)
    await update_task_in_file(task_id, new_state)
    
    # 2. Capture trace witness (formal verification)
    witness = await logos.invoke(
        "world.trace.capture",
        observer,
        trace=ExecutionTrace(
            agent_path="self.document.task",
            operation="toggle",
            input_data={"task_id": task_id, "state": new_state},
        ),
    )
    
    # 3. Link to verification graph
    await logos.invoke(
        "self.verification.link_trace",
        observer,
        trace_id=witness.id,
        requirement_refs=task.requirement_refs,
    )
    
    # 4. Verify if completing
    if new_state:
        verification = await logos.invoke(
            "self.verification.check_task",
            observer,
            task_id=task_id,
        )
        if not verification.passed:
            return ToggleResult.warning(
                message="Task marked complete but verification found issues",
                issues=verification.issues,
                witness_id=witness.id,
            )
    
    return ToggleResult.success(witness_id=witness.id)
```

### Performance Considerations

- **Incremental parsing**: Only re-parse changed regions
- **Token caching**: Cache affordance computations per observer
- **Lazy projection**: Defer projection until token is visible
- **Sheaf optimization**: Only verify coherence for overlapping tokens
- **Event batching**: Batch DataBus events for efficiency

---

*"The text lives. The spec breathes. The document acts."*

