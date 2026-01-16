"""
K-Block Boundary Detection Service.

Identifies natural boundaries for aggregating functions into K-blocks.

Philosophy:
    "K-blocks are coherence windows—not too small (inane), not too large (incomprehensible)."
    "Automatically identify code domains or airtight bulkhead abstraction boundaries."

Strategies:
- FILE: One K-block per file (trivial baseline)
- CLASS: One K-block per class
- IMPORT: Cluster by shared imports (semantic proximity)
- CALLGRAPH: Strongly connected components
- SEMANTIC: Embedding similarity (future: LLM-based)
- GALOIS: Restructuring fixed points (future: D-gent integration)
- HYBRID: Combine signals adaptively (recommended)

Target: 500-5000 tokens per K-block, ideal ~2000 (short essay length)

See: spec/crown-jewels/code.md (boundary detection design)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable


@dataclass(frozen=True)
class FunctionCrystal:
    """
    A crystallized function artifact.

    Atomic unit of code analysis. K-blocks aggregate these.
    """

    id: str  # Unique identifier (e.g., "file.py:ClassName.method_name")
    name: str  # Function/method name
    file_path: str  # Absolute path to source file
    line_range: tuple[int, int]  # (start_line, end_line)
    signature: str  # Full signature (def foo(a: int, b: str) -> bool)
    docstring: str | None  # Docstring if present
    class_name: str | None  # Parent class if method

    # Semantic edges
    imports: frozenset[str] = field(default_factory=frozenset)  # Imported modules
    calls: frozenset[str] = field(default_factory=frozenset)  # IDs of called functions
    called_by: frozenset[str] = field(default_factory=frozenset)  # IDs of callers

    # Metadata
    is_test: bool = False
    is_private: bool = False  # Starts with _
    is_async: bool = False


@dataclass(frozen=True)
class KBlockCandidate:
    """
    A candidate K-block boundary.

    Represents a proposed grouping of functions into a coherent K-block.
    """

    function_ids: frozenset[str]
    boundary_type: str  # "FILE", "CLASS", "IMPORT_CLUSTER", "SCC", "HYBRID"
    confidence: float  # 0.0-1.0
    rationale: str  # Human-readable explanation
    estimated_tokens: int

    @property
    def within_size_heuristic(self) -> bool:
        """Check if candidate falls within 500-5000 token sweet spot."""
        return 500 <= self.estimated_tokens <= 5000

    @property
    def is_too_small(self) -> bool:
        """Below minimum threshold—may be inane."""
        return self.estimated_tokens < 500

    @property
    def is_too_large(self) -> bool:
        """Above maximum threshold—may be incomprehensible."""
        return self.estimated_tokens > 5000


@dataclass(frozen=True)
class SplitSuggestion:
    """
    Suggestion to split an oversized K-block.

    Provides rationale and proposed split points.
    """

    kblock_id: str
    current_size: int
    proposed_splits: list[KBlockCandidate]
    rationale: str
    confidence: float


@dataclass(frozen=True)
class MergeSuggestion:
    """
    Suggestion to merge coupled K-blocks.

    Identifies small, highly-coupled blocks that should merge.
    """

    kblock_ids: frozenset[str]
    current_sizes: list[int]
    merged_size: int
    coupling_score: float  # 0.0-1.0
    rationale: str
    confidence: float


class BoundaryStrategy(Enum):
    """
    K-block boundary detection strategy.

    Each strategy identifies boundaries using different signals:
    - FILE: Filesystem structure
    - CLASS: Object-oriented boundaries
    - IMPORT: Semantic import graph
    - CALLGRAPH: Control flow analysis
    - SEMANTIC: Embedding similarity (LLM-based)
    - GALOIS: Categorical restructuring (D-gent)
    - HYBRID: Multi-signal fusion (recommended)
    """

    FILE = auto()
    CLASS = auto()
    IMPORT = auto()
    CALLGRAPH = auto()
    SEMANTIC = auto()
    GALOIS = auto()
    HYBRID = auto()


class BoundaryDetector:
    """
    Detect natural K-block boundaries from function crystals.

    Core Service:
        Takes a collection of FunctionCrystals and proposes KBlockCandidates
        using various strategies (file, class, import graph, call graph).

    Philosophy:
        K-blocks should be "airtight bulkheads"—internally coherent,
        externally decoupled. We want strong internal coupling (high coherence),
        weak external coupling (low interference).

    Teaching:
        gotcha: Token estimation is approximate (1 token ≈ 4 chars).
                For production, integrate tiktoken for accurate counts.
                (Evidence: test_boundary.py::test_token_estimation)

        gotcha: CALLGRAPH strategy requires building directed graph first.
                Strongly connected components may not align with intuition.
                (Evidence: test_boundary.py::test_callgraph_strategy)
    """

    def __init__(
        self,
        min_tokens: int = 500,
        max_tokens: int = 5000,
        target_tokens: int = 2000,
    ):
        """
        Initialize boundary detector with size heuristics.

        Args:
            min_tokens: Minimum tokens per K-block (below = inane)
            max_tokens: Maximum tokens per K-block (above = incomprehensible)
            target_tokens: Ideal target size (short essay)
        """
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
        self.target_tokens = target_tokens

    async def detect_boundaries(
        self,
        functions: list[FunctionCrystal],
        strategy: BoundaryStrategy = BoundaryStrategy.HYBRID,
    ) -> list[KBlockCandidate]:
        """
        Find natural K-block boundaries using specified strategy.

        Args:
            functions: List of function crystals to analyze
            strategy: Detection strategy to use

        Returns:
            List of K-block candidates with confidence scores
        """
        if strategy == BoundaryStrategy.FILE:
            return self._detect_file_boundaries(functions)
        elif strategy == BoundaryStrategy.CLASS:
            return self._detect_class_boundaries(functions)
        elif strategy == BoundaryStrategy.IMPORT:
            return self._detect_import_boundaries(functions)
        elif strategy == BoundaryStrategy.CALLGRAPH:
            return self._detect_callgraph_boundaries(functions)
        elif strategy == BoundaryStrategy.HYBRID:
            return self._detect_hybrid_boundaries(functions)
        else:
            raise NotImplementedError(f"Strategy {strategy} not yet implemented")

    async def suggest_splits(
        self,
        kblock_id: str,
        functions: list[FunctionCrystal],
    ) -> list[SplitSuggestion]:
        """
        Suggest how to split an oversized K-block.

        Analyzes internal structure and proposes natural split points
        (by class, by import clusters, by weakly-connected subgraphs).

        Args:
            kblock_id: ID of the oversized K-block
            functions: Functions contained in the K-block

        Returns:
            List of split suggestions with rationale
        """
        current_size = self.estimate_tokens(functions)

        if current_size <= self.max_tokens:
            return []  # No split needed

        # Try splitting by class first
        class_candidates = self._detect_class_boundaries(functions)
        if all(c.within_size_heuristic for c in class_candidates):
            return [
                SplitSuggestion(
                    kblock_id=kblock_id,
                    current_size=current_size,
                    proposed_splits=class_candidates,
                    rationale="Split by class—all classes fall within size heuristic",
                    confidence=0.9,
                )
            ]

        # Try splitting by call graph
        callgraph_candidates = self._detect_callgraph_boundaries(functions)
        if all(c.within_size_heuristic for c in callgraph_candidates):
            return [
                SplitSuggestion(
                    kblock_id=kblock_id,
                    current_size=current_size,
                    proposed_splits=callgraph_candidates,
                    rationale="Split by strongly connected components in call graph",
                    confidence=0.75,
                )
            ]

        # Fallback: split into equal chunks
        chunk_size = len(functions) // 2
        chunks = [functions[:chunk_size], functions[chunk_size:]]
        fallback_candidates = [
            KBlockCandidate(
                function_ids=frozenset(f.id for f in chunk),
                boundary_type="MANUAL_SPLIT",
                confidence=0.5,
                rationale=f"Manual split (chunk {i + 1})",
                estimated_tokens=self.estimate_tokens(chunk),
            )
            for i, chunk in enumerate(chunks)
        ]

        return [
            SplitSuggestion(
                kblock_id=kblock_id,
                current_size=current_size,
                proposed_splits=fallback_candidates,
                rationale="No natural boundary—manual split into halves",
                confidence=0.5,
            )
        ]

    async def suggest_merges(
        self,
        kblocks: list[tuple[str, list[FunctionCrystal]]],
    ) -> list[MergeSuggestion]:
        """
        Suggest K-blocks that should merge.

        Identifies small K-blocks with high coupling that should combine.

        Args:
            kblocks: List of (kblock_id, functions) tuples

        Returns:
            List of merge suggestions with coupling scores
        """
        suggestions: list[MergeSuggestion] = []

        # Find pairs of small blocks with high coupling
        for i, (id_a, funcs_a) in enumerate(kblocks):
            size_a = self.estimate_tokens(funcs_a)
            if size_a >= self.max_tokens:
                continue  # Too large to merge

            for id_b, funcs_b in kblocks[i + 1 :]:
                size_b = self.estimate_tokens(funcs_b)
                merged_size = size_a + size_b

                if merged_size > self.max_tokens:
                    continue  # Would exceed max

                # Compute coupling
                coupling = self.compute_coupling(funcs_a, funcs_b)

                if coupling > 0.3:  # High coupling threshold
                    suggestions.append(
                        MergeSuggestion(
                            kblock_ids=frozenset([id_a, id_b]),
                            current_sizes=[size_a, size_b],
                            merged_size=merged_size,
                            coupling_score=coupling,
                            rationale=f"High coupling ({coupling:.2f}) between small blocks",
                            confidence=min(0.9, coupling),
                        )
                    )

        return suggestions

    def estimate_tokens(self, functions: list[FunctionCrystal]) -> int:
        """
        Estimate token count for a set of functions.

        Uses rough heuristic: 1 token ≈ 4 characters.
        Considers signature, docstring, and estimated body length.

        Args:
            functions: Functions to estimate

        Returns:
            Estimated token count

        Teaching:
            gotcha: This is a rough estimate. For production accuracy,
                    integrate tiktoken library for model-specific counts.
                    (Evidence: OpenAI tokenizer docs)
        """
        total_chars = 0
        for f in functions:
            # Signature
            total_chars += len(f.signature)

            # Docstring
            if f.docstring:
                total_chars += len(f.docstring)

            # Body estimate: line_range * avg 40 chars/line
            line_count = f.line_range[1] - f.line_range[0]
            total_chars += line_count * 40

        # Convert chars to tokens (1 token ≈ 4 chars for English/code)
        return total_chars // 4

    def compute_coherence(self, functions: list[FunctionCrystal]) -> float:
        """
        Compute internal coherence score for a set of functions.

        Coherence = internal calls / total possible calls
        High coherence → functions call each other frequently
        Low coherence → isolated functions

        Args:
            functions: Functions to analyze

        Returns:
            Coherence score in [0.0, 1.0]
        """
        if len(functions) <= 1:
            return 1.0  # Single function is trivially coherent

        function_ids = {f.id for f in functions}
        internal_calls = sum(len(f.calls & function_ids) for f in functions)

        # Maximum possible calls = n * (n-1) for n functions
        n = len(functions)
        max_calls = n * (n - 1)

        return internal_calls / max_calls if max_calls > 0 else 1.0

    def compute_coupling(
        self,
        inside: list[FunctionCrystal],
        outside: list[FunctionCrystal],
    ) -> float:
        """
        Compute external coupling score between two sets of functions.

        Coupling = cross-boundary calls / total possible cross calls
        High coupling → sets should merge
        Low coupling → sets are independent

        Args:
            inside: First set of functions
            outside: Second set of functions

        Returns:
            Coupling score in [0.0, 1.0]
        """
        inside_ids = {f.id for f in inside}
        outside_ids = {f.id for f in outside}

        # Count calls from inside → outside
        inside_to_outside = sum(len(f.calls & outside_ids) for f in inside)

        # Count calls from outside → inside
        outside_to_inside = sum(len(f.calls & inside_ids) for f in outside)

        cross_calls = inside_to_outside + outside_to_inside

        # Maximum cross calls = len(inside) * len(outside) * 2 (bidirectional)
        max_cross = len(inside) * len(outside) * 2

        return cross_calls / max_cross if max_cross > 0 else 0.0

    # -------------------------------------------------------------------------
    # Strategy Implementations
    # -------------------------------------------------------------------------

    def _detect_file_boundaries(self, functions: list[FunctionCrystal]) -> list[KBlockCandidate]:
        """
        FILE strategy: One K-block per file.

        Simplest baseline—respects filesystem boundaries.
        """
        by_file: dict[str, list[FunctionCrystal]] = {}
        for f in functions:
            by_file.setdefault(f.file_path, []).append(f)

        candidates = []
        for file_path, funcs in by_file.items():
            candidates.append(
                KBlockCandidate(
                    function_ids=frozenset(f.id for f in funcs),
                    boundary_type="FILE",
                    confidence=1.0,  # Trivial boundary
                    rationale=f"All functions from {file_path}",
                    estimated_tokens=self.estimate_tokens(funcs),
                )
            )

        return candidates

    def _detect_class_boundaries(self, functions: list[FunctionCrystal]) -> list[KBlockCandidate]:
        """
        CLASS strategy: One K-block per class.

        Groups methods by class. Standalone functions form their own blocks.
        """
        by_class: dict[str, list[FunctionCrystal]] = {}
        for f in functions:
            key: str = f"{f.file_path}::{f.class_name}" if f.class_name else f.id
            by_class.setdefault(key, []).append(f)

        candidates = []
        for key, funcs in by_class.items():
            if len(funcs) == 1 and funcs[0].class_name is None:
                # Standalone function
                rationale = f"Standalone function: {funcs[0].name}"
            else:
                # Class methods
                class_name = funcs[0].class_name or "module"
                rationale = f"Class: {class_name} ({len(funcs)} methods)"

            candidates.append(
                KBlockCandidate(
                    function_ids=frozenset(f.id for f in funcs),
                    boundary_type="CLASS",
                    confidence=0.85,
                    rationale=rationale,
                    estimated_tokens=self.estimate_tokens(funcs),
                )
            )

        return candidates

    def _detect_import_boundaries(self, functions: list[FunctionCrystal]) -> list[KBlockCandidate]:
        """
        IMPORT strategy: Cluster by shared imports.

        Uses Jaccard similarity on import sets to find semantic clusters.
        """
        # Build import similarity graph
        clusters = self._cluster_by_imports(functions, threshold=0.3)

        candidates = []
        for i, cluster in enumerate(clusters):
            candidates.append(
                KBlockCandidate(
                    function_ids=frozenset(f.id for f in cluster),
                    boundary_type="IMPORT_CLUSTER",
                    confidence=0.7,
                    rationale=f"Import cluster {i + 1} ({len(cluster)} functions)",
                    estimated_tokens=self.estimate_tokens(cluster),
                )
            )

        return candidates

    def _detect_callgraph_boundaries(
        self, functions: list[FunctionCrystal]
    ) -> list[KBlockCandidate]:
        """
        CALLGRAPH strategy: Strongly connected components.

        Finds SCCs in the call graph—functions that call each other cyclically.
        """
        # Build call graph
        sccs = self._find_strongly_connected_components(functions)

        candidates = []
        for i, scc in enumerate(sccs):
            candidates.append(
                KBlockCandidate(
                    function_ids=frozenset(f.id for f in scc),
                    boundary_type="SCC",
                    confidence=0.8,
                    rationale=f"Strongly connected component {i + 1}",
                    estimated_tokens=self.estimate_tokens(scc),
                )
            )

        return candidates

    def _detect_hybrid_boundaries(self, functions: list[FunctionCrystal]) -> list[KBlockCandidate]:
        """
        HYBRID strategy: Combine multiple signals adaptively.

        Algorithm:
        1. Start with FILE boundaries
        2. Split if > max_tokens using CLASS
        3. Further split using CALLGRAPH if still too large
        4. Merge if < min_tokens and high coupling

        This is the recommended strategy—balances all signals.
        """
        # Start with file boundaries
        candidates = self._detect_file_boundaries(functions)

        # Split oversized candidates
        refined: list[KBlockCandidate] = []
        for candidate in candidates:
            if candidate.is_too_large:
                # Try class split
                funcs = [f for f in functions if f.id in candidate.function_ids]
                class_splits = self._detect_class_boundaries(funcs)

                if all(c.within_size_heuristic for c in class_splits):
                    refined.extend(class_splits)
                else:
                    # Further split by call graph
                    for class_candidate in class_splits:
                        if class_candidate.is_too_large:
                            class_funcs = [f for f in funcs if f.id in class_candidate.function_ids]
                            callgraph_splits = self._detect_callgraph_boundaries(class_funcs)
                            refined.extend(callgraph_splits)
                        else:
                            refined.append(class_candidate)
            else:
                refined.append(candidate)

        # TODO: Merge small, highly-coupled candidates
        # (Deferred to suggest_merges for now)

        # Update boundary_type and confidence
        final = []
        for c in refined:
            final.append(
                KBlockCandidate(
                    function_ids=c.function_ids,
                    boundary_type="HYBRID",
                    confidence=0.85,
                    rationale=f"Hybrid boundary ({c.boundary_type} origin)",
                    estimated_tokens=c.estimated_tokens,
                )
            )

        return final

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    def _cluster_by_imports(
        self, functions: list[FunctionCrystal], threshold: float = 0.3
    ) -> list[list[FunctionCrystal]]:
        """
        Cluster functions by import similarity (Jaccard).

        Args:
            functions: Functions to cluster
            threshold: Minimum Jaccard similarity to cluster

        Returns:
            List of clusters (each cluster is a list of functions)
        """
        # Simple greedy clustering
        clusters: list[list[FunctionCrystal]] = []
        assigned: set[str] = set()

        for f in functions:
            if f.id in assigned:
                continue

            # Start new cluster
            cluster = [f]
            assigned.add(f.id)

            # Find similar functions
            for g in functions:
                if g.id in assigned:
                    continue

                similarity = self._jaccard_similarity(f.imports, g.imports)
                if similarity >= threshold:
                    cluster.append(g)
                    assigned.add(g.id)

            clusters.append(cluster)

        return clusters

    def _jaccard_similarity(self, a: frozenset[str], b: frozenset[str]) -> float:
        """Compute Jaccard similarity between two sets."""
        if not a and not b:
            return 1.0
        intersection = len(a & b)
        union = len(a | b)
        return intersection / union if union > 0 else 0.0

    def _find_strongly_connected_components(
        self, functions: list[FunctionCrystal]
    ) -> list[list[FunctionCrystal]]:
        """
        Find strongly connected components in call graph using Tarjan's algorithm.

        Args:
            functions: Functions to analyze

        Returns:
            List of SCCs (each SCC is a list of functions)
        """
        # Build adjacency list
        id_to_func = {f.id: f for f in functions}
        adj: dict[str, list[str]] = {f.id: list(f.calls & id_to_func.keys()) for f in functions}

        # Tarjan's algorithm state
        index_counter = [0]
        stack: list[str] = []
        lowlinks: dict[str, int] = {}
        index: dict[str, int] = {}
        on_stack: set[str] = set()
        sccs: list[list[str]] = []

        def strongconnect(v: str) -> None:
            # Set depth index for v
            index[v] = index_counter[0]
            lowlinks[v] = index_counter[0]
            index_counter[0] += 1
            stack.append(v)
            on_stack.add(v)

            # Consider successors
            for w in adj.get(v, []):
                if w not in index:
                    # Successor w not yet visited
                    strongconnect(w)
                    lowlinks[v] = min(lowlinks[v], lowlinks[w])
                elif w in on_stack:
                    # Successor w is on stack (in current SCC)
                    lowlinks[v] = min(lowlinks[v], index[w])

            # If v is a root node, pop the stack
            if lowlinks[v] == index[v]:
                component: list[str] = []
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    component.append(w)
                    if w == v:
                        break
                sccs.append(component)

        # Run Tarjan on all nodes
        for f_id in adj:
            if f_id not in index:
                strongconnect(f_id)

        # Convert IDs back to FunctionCrystals
        return [[id_to_func[fid] for fid in scc] for scc in sccs]
