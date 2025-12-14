"""
K-gent Soul: The Middleware of Consciousness.

K-gent Soul is NOT a chatbot. It is the layer that:
1. INTERCEPTS Semaphores from Purgatory (auto-resolves or annotates)
2. INHABITS Terrarium as ambient presence (not just CLI command)
3. DREAMS during Hypnagogia (async refinement at night)

This is Autopoiesis Level 4: The system critiques its own reason
for existing based on your values.

Architecture:
    Soul (Persona) + Semaphores (Yields) + Terrarium (Presence) = K-gent

Usage:
    soul = KgentSoul()

    # Direct dialogue
    output = await soul.dialogue("What am I avoiding?", DialogueMode.REFLECT)

    # Semaphore mediation (shallow - keyword based)
    result = await soul.intercept(semaphore_token)

    # Semaphore mediation (deep - LLM-backed)
    result = await soul.intercept_deep(semaphore_token)

    # Get current state
    state = soul.manifest()

Phase 1 Improvements:
- LLM-backed dialogue (DIALOGUE/DEEP tiers)
- Deep intercept with principle reasoning
- Audit trail for all mediations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, AsyncIterator, Callable, Optional

from .eigenvectors import KENT_EIGENVECTORS, KentEigenvectors
from .llm import LLMClient, StreamingLLMResponse, create_llm_client, has_llm_credentials
from .persona import (
    DialogueInput,
    DialogueMode,
    DialogueOutput,
    KgentAgent,
    PersonaSeed,
    PersonaState,
)
from .starters import format_starters_for_display, get_starters, random_starter
from .templates import (
    get_whisper_response,
    should_use_template,
    try_template_response,
)

if TYPE_CHECKING:
    from agents.flux.semaphore.token import SemaphoreToken

    from .audit import AuditEntry, AuditTrail
    from .flux import FluxEvent, FluxStream


# --- Budget Tiers ---


class BudgetTier(Enum):
    """Token budget tiers for K-gent responses."""

    DORMANT = "dormant"  # 0 tokens - template only
    WHISPER = "whisper"  # ~100 tokens - quick check-in
    DIALOGUE = "dialogue"  # ~4000 tokens - full conversation
    DEEP = "deep"  # ~8000+ tokens - Council of Ghosts


@dataclass
class BudgetConfig:
    """Configuration for K-gent budget tiers."""

    dormant_max: int = 0
    whisper_max: int = 100
    dialogue_max: int = 4000
    deep_max: int = 8000

    def tier_for_tokens(self, tokens: int) -> BudgetTier:
        """Determine tier based on token count."""
        if tokens <= self.dormant_max:
            return BudgetTier.DORMANT
        elif tokens <= self.whisper_max:
            return BudgetTier.WHISPER
        elif tokens <= self.dialogue_max:
            return BudgetTier.DIALOGUE
        return BudgetTier.DEEP


# --- Soul State ---


@dataclass
class SoulState:
    """
    Current K-gent soul state.

    Combines eigenvectors, persona state, and operational status.
    """

    eigenvectors: KentEigenvectors
    persona: PersonaState
    active_mode: DialogueMode = DialogueMode.REFLECT
    session_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_interaction: Optional[datetime] = None
    tokens_used_session: int = 0
    interactions_count: int = 0

    @property
    def is_fresh_session(self) -> bool:
        """Check if this is a fresh session."""
        return self.interactions_count == 0


@dataclass
class InterceptResult:
    """Result from K-gent semaphore interception."""

    handled: bool  # Was the semaphore auto-resolved?
    annotation: Optional[str] = None  # Human-readable annotation
    recommendation: Optional[str] = None  # approve/reject/escalate
    confidence: float = 0.0
    matching_principles: list[str] = field(default_factory=list)
    matching_patterns: list[str] = field(default_factory=list)
    audit_trail: str = ""
    reasoning: str = ""  # LLM-generated reasoning for the decision
    was_deep: bool = False  # Was this a deep (LLM-backed) intercept?


# --- Dangerous Operation Keywords ---
# These operations should NEVER be auto-approved

DANGEROUS_KEYWORDS = frozenset(
    [
        "delete",
        "remove",
        "drop",
        "truncate",
        "destroy",
        "rm ",
        "rm -",
        "rmdir",
        "del ",
        "production",
        "prod",
        "force",
        "--force",
        "-f",
        "sudo",
        "password",
        "secret",
        "token",
        "credential",
        "api_key",
        "apikey",
        "format",
        "wipe",
        "purge",
        "erase",
    ]
)


# --- Extended Dialogue Output ---


@dataclass
class SoulDialogueOutput(DialogueOutput):
    """Extended dialogue output with soul metadata."""

    budget_tier: BudgetTier = BudgetTier.DIALOGUE
    tokens_used: int = 0
    eigenvector_context: Optional[str] = None
    was_template: bool = False


# --- The Soul ---


class KgentSoul:
    """
    K-gent Soul: The Middleware of Consciousness.

    This is the main entry point for K-gent interaction. It wraps:
    - KgentAgent: The core dialogue agent
    - Eigenvectors: Personality coordinates
    - Templates: Zero-token responses
    - Starters: Mode-specific prompts
    - LLM Client: For DIALOGUE/DEEP tier responses
    - Audit Trail: For tracking all mediations

    Phase 1 Features:
    - LLM-backed dialogue (actual reasoning, not templates)
    - Deep intercept with principle reasoning
    - Audit trail for all mediations
    """

    def __init__(
        self,
        persona_state: Optional[PersonaState] = None,
        eigenvectors: Optional[KentEigenvectors] = None,
        budget_config: Optional[BudgetConfig] = None,
        llm: Optional[LLMClient] = None,
        auto_llm: bool = True,
    ) -> None:
        """Initialize K-gent Soul.

        Args:
            persona_state: Persona state with preferences and patterns.
            eigenvectors: Personality coordinates.
            budget_config: Token budget configuration.
            llm: Optional LLM client. If None and auto_llm=True, will auto-create.
            auto_llm: If True, automatically create LLM client when credentials available.
        """
        self._eigenvectors = eigenvectors or KENT_EIGENVECTORS
        self._persona_state = persona_state or PersonaState(seed=PersonaSeed())
        self._budget = budget_config or BudgetConfig()

        # LLM client setup
        self._llm: Optional[LLMClient] = llm
        if self._llm is None and auto_llm and has_llm_credentials():
            self._llm = create_llm_client()

        # Create agent with LLM support
        self._agent = KgentAgent(
            self._persona_state,
            llm=self._llm,
            eigenvectors=self._eigenvectors,
        )

        # Session tracking
        self._state = SoulState(
            eigenvectors=self._eigenvectors,
            persona=self._persona_state,
        )

        # Audit trail (lazy-initialized)
        self._audit: Optional["AuditTrail"] = None

    @property
    def eigenvectors(self) -> KentEigenvectors:
        """Get personality eigenvectors."""
        return self._eigenvectors

    @property
    def active_mode(self) -> DialogueMode:
        """Get current dialogue mode."""
        return self._state.active_mode

    @active_mode.setter
    def active_mode(self, mode: DialogueMode) -> None:
        """Set current dialogue mode."""
        self._state.active_mode = mode

    @property
    def has_llm(self) -> bool:
        """Check if LLM is configured."""
        return self._llm is not None

    @property
    def audit(self) -> "AuditTrail":
        """Get the audit trail, creating if necessary."""
        if self._audit is None:
            from .audit import AuditTrail

            self._audit = AuditTrail()
        return self._audit

    def set_llm(self, llm: LLMClient) -> None:
        """Set the LLM client."""
        self._llm = llm
        self._agent.set_llm(llm)

    # --- Core Dialogue ---

    async def dialogue(
        self,
        message: str,
        mode: Optional[DialogueMode] = None,
        budget: BudgetTier = BudgetTier.DIALOGUE,
        on_chunk: Optional[Callable[[str], None]] = None,
    ) -> SoulDialogueOutput:
        """
        Engage in dialogue with K-gent Soul.

        Budget-aware: uses templates when appropriate, escalates to LLM only when needed.

        Args:
            message: The user's message
            mode: Dialogue mode (defaults to current active mode)
            budget: Token budget tier
            on_chunk: Optional callback for streaming. Called with each token/chunk
                      as it's generated. If None, behavior unchanged (backward compatible).

        Returns:
            SoulDialogueOutput with response and metadata
        """
        # Input validation: handle empty/whitespace messages gracefully
        if not message or not message.strip():
            response = "What's on your mind?"
            if on_chunk is not None:
                on_chunk(response)
            return SoulDialogueOutput(
                response=response,
                mode=mode or self._state.active_mode,
                budget_tier=BudgetTier.DORMANT,
                tokens_used=0,
                was_template=True,
            )

        mode = mode or self._state.active_mode
        self._state.active_mode = mode

        # Try template response first (DORMANT tier)
        if budget == BudgetTier.DORMANT or should_use_template(message):
            template_response = try_template_response(message, mode)
            if template_response:
                if on_chunk is not None:
                    on_chunk(template_response)
                self._update_session_stats(0)
                return SoulDialogueOutput(
                    response=template_response,
                    mode=mode,
                    budget_tier=BudgetTier.DORMANT,
                    tokens_used=0,
                    was_template=True,
                )

        # WHISPER tier: quick acknowledgment
        if budget == BudgetTier.WHISPER:
            whisper_response = get_whisper_response(message)
            if on_chunk is not None:
                on_chunk(whisper_response)
            self._update_session_stats(50)  # Estimate
            return SoulDialogueOutput(
                response=whisper_response,
                mode=mode,
                budget_tier=BudgetTier.WHISPER,
                tokens_used=50,
                was_template=True,
            )

        # DIALOGUE/DEEP tier: full LLM response
        input_data = DialogueInput(message=message, mode=mode)

        # Use streaming if callback provided
        actual_tokens: int = 0
        if on_chunk is not None:
            output, actual_tokens = await self._invoke_with_streaming(
                input_data, mode, message, budget, on_chunk
            )
        else:
            output = await self._invoke_without_streaming(
                input_data, mode, budget, message
            )

        # Use actual token count if available, otherwise estimate
        if actual_tokens > 0:
            tokens_used = actual_tokens
        else:
            # Estimate tokens based on response length
            tokens_used = len(output.response.split()) * 2

        self._update_session_stats(tokens_used)

        return SoulDialogueOutput(
            response=output.response,
            mode=output.mode,
            referenced_preferences=output.referenced_preferences,
            referenced_patterns=output.referenced_patterns,
            budget_tier=budget,
            tokens_used=tokens_used,
            eigenvector_context=self._eigenvectors.to_context_prompt()
            if budget == BudgetTier.DEEP
            else None,
            was_template=False,
        )

    async def _invoke_with_streaming(
        self,
        input_data: DialogueInput,
        mode: DialogueMode,
        message: str,
        budget: BudgetTier,
        on_chunk: Callable[[str], None],
    ) -> tuple[DialogueOutput, int]:
        """Invoke agent with true streaming via invoke_stream().

        Returns:
            Tuple of (DialogueOutput, actual_tokens_used)
            The token count is from the LLM API when available.
        """
        accumulated_response = ""
        actual_tokens_used = 0

        # Trace the LLM invocation for OTEL visibility
        try:
            from protocols.agentese.telemetry import trace_invocation

            # Create a minimal umwelt-like object for tracing
            class _TraceUmwelt:
                id = "kgent-soul"
                dna = None

            async with trace_invocation(
                f"self.soul.{mode.value}",
                _TraceUmwelt(),
                budget_tier=budget.value,
                message_length=len(message),
            ):
                async for chunk, is_final, tokens in self._agent.invoke_stream(
                    input_data
                ):
                    if chunk:
                        accumulated_response += chunk
                        on_chunk(chunk)
                    if is_final:
                        actual_tokens_used = tokens
        except ImportError:
            # Telemetry not available, stream directly
            async for chunk, is_final, tokens in self._agent.invoke_stream(input_data):
                if chunk:
                    accumulated_response += chunk
                    on_chunk(chunk)
                if is_final:
                    actual_tokens_used = tokens

        # Build output from accumulated response
        output = DialogueOutput(
            response=accumulated_response,
            mode=mode,
            referenced_preferences=self._agent._find_preferences(message)[:3],
            referenced_patterns=self._agent._find_patterns(message)[:3],
        )
        return output, actual_tokens_used

    async def _invoke_without_streaming(
        self,
        input_data: DialogueInput,
        mode: DialogueMode,
        budget: BudgetTier,
        message: str,
    ) -> DialogueOutput:
        """Invoke agent without streaming via regular invoke()."""
        # Trace the LLM invocation for OTEL visibility
        try:
            from protocols.agentese.telemetry import trace_invocation

            # Create a minimal umwelt-like object for tracing
            class _TraceUmwelt:
                id = "kgent-soul"
                dna = None

            async with trace_invocation(
                f"self.soul.{mode.value}",
                _TraceUmwelt(),
                budget_tier=budget.value,
                message_length=len(message),
            ):
                return await self._agent.invoke(input_data)
        except ImportError:
            # Telemetry not available, invoke directly
            return await self._agent.invoke(input_data)

    # --- Flux Streaming (C12, C17) ---

    def dialogue_flux(
        self,
        message: str,
        mode: Optional[DialogueMode] = None,
        budget: BudgetTier = BudgetTier.DIALOGUE,
    ) -> "FluxStream[str]":
        """
        Engage in dialogue with K-gent Soul via Flux streaming.

        Returns a FluxStream[str] that yields:
        - FluxEvent.data(chunk): Text chunks as they are generated
        - FluxEvent.metadata(StreamingLLMResponse): Final event with token counts

        The FluxStream supports operator chaining for transformations:
        - .map(fn): Transform data events
        - .filter(pred): Filter events
        - .take(n): Limit to first n data events
        - .tap(fn): Side effects without modification
        - .collect(): Materialize to list

        Args:
            message: The user's message
            mode: Dialogue mode (defaults to current active mode)
            budget: Token budget tier

        Returns:
            FluxStream[str] for operator chaining

        Usage:
            # Simple iteration
            async for event in soul.dialogue_flux("Hello", mode=DialogueMode.REFLECT):
                if event.is_data:
                    print(event.value, end="", flush=True)
                elif event.is_metadata:
                    print(f"\\n[{event.value.tokens_used} tokens]")

            # With operators
            stream = (
                soul.dialogue_flux("Hello", mode=DialogueMode.REFLECT)
                .filter(lambda e: e.is_data and e.value.strip())
                .take(5)
            )
            values = await stream.collect()
        """
        from .flux import FluxStream

        return FluxStream(self._dialogue_flux_generator(message, mode, budget))

    async def _dialogue_flux_generator(
        self,
        message: str,
        mode: Optional[DialogueMode],
        budget: BudgetTier,
    ) -> AsyncIterator["FluxEvent[str]"]:
        """
        Internal generator for dialogue_flux().

        Yields FluxEvent[str] events for streaming dialogue.
        """
        # Import here to avoid circular imports
        from .flux import FluxEvent, LLMStreamSource

        # Handle empty/whitespace messages
        if not message or not message.strip():
            response = "What's on your mind?"
            yield FluxEvent.data(response)
            yield FluxEvent.metadata(
                StreamingLLMResponse(text=response, tokens_used=0, model="template")
            )
            return

        resolved_mode = mode or self._state.active_mode
        self._state.active_mode = resolved_mode

        # For DORMANT/WHISPER tiers, yield template response immediately
        if budget == BudgetTier.DORMANT:
            from .templates import try_template_response

            template_response = try_template_response(message, resolved_mode)
            if template_response:
                yield FluxEvent.data(template_response)
                yield FluxEvent.metadata(
                    StreamingLLMResponse(
                        text=template_response, tokens_used=0, model="template"
                    )
                )
                return

        if budget == BudgetTier.WHISPER:
            from .templates import get_whisper_response

            whisper_response = get_whisper_response(message)
            yield FluxEvent.data(whisper_response)
            yield FluxEvent.metadata(
                StreamingLLMResponse(
                    text=whisper_response, tokens_used=50, model="whisper"
                )
            )
            self._update_session_stats(50)
            return

        # For DIALOGUE/DEEP tiers, stream from LLM
        if self._llm is None:
            # Fallback to template when no LLM available
            from .templates import try_template_response

            template_response = try_template_response(message, resolved_mode) or (
                "I'm unable to generate a response without an LLM connection."
            )
            yield FluxEvent.data(template_response)
            yield FluxEvent.metadata(
                StreamingLLMResponse(
                    text=template_response, tokens_used=0, model="fallback"
                )
            )
            return

        # Build prompts using agent infrastructure
        system_prompt = self._agent._build_system_prompt(resolved_mode)
        # Find matching preferences and patterns for context
        prefs = self._agent._find_preferences(message)[:3]
        pats = self._agent._find_patterns(message)[:3]
        user_prompt = self._agent._build_user_prompt(
            message, prefs, pats, resolved_mode
        )

        # Create LLM stream source
        source = LLMStreamSource(
            client=self._llm,
            system=system_prompt,
            user=user_prompt,
            temperature=0.7 if budget == BudgetTier.DIALOGUE else 0.5,
            max_tokens=4000 if budget == BudgetTier.DIALOGUE else 8000,
        )

        # Stream events, tracking accumulated text for stats
        accumulated_text = ""
        final_tokens = 0

        async for event in source:
            if event.is_data:
                accumulated_text += event.value
            elif event.is_metadata:
                final_tokens = event.value.tokens_used
                self._update_session_stats(final_tokens)

            yield event

    # --- Semaphore Mediation ---

    async def intercept(self, token: Any) -> InterceptResult:
        """
        Intercept a semaphore token for potential auto-resolution.

        This is the Rodizio Sommelier pattern:
        - B-gent yields token → K-gent intercepts
        - Query PersonaGarden for matching patterns/principles
        - Either auto-resolve OR annotate for human review

        Args:
            token: The SemaphoreToken to evaluate

        Returns:
            InterceptResult with handling decision
        """
        # Extract token info
        prompt = getattr(token, "prompt", str(token))
        _reason = getattr(token, "reason", None)  # Reserved for audit trail

        # Find matching principles from eigenvectors
        matching_principles = self._find_matching_principles(prompt)

        # Find matching patterns from persona
        matching_patterns = self._find_matching_patterns(prompt)

        # Calculate confidence based on matches
        confidence = self._calculate_intercept_confidence(
            matching_principles, matching_patterns
        )

        # Decide: auto-resolve or annotate
        if confidence >= 0.8 and matching_principles:
            # High confidence: auto-resolve
            recommendation = self._generate_recommendation(
                prompt, matching_principles, matching_patterns
            )
            audit_trail = self._generate_audit_trail(
                token, recommendation, matching_principles, confidence
            )

            return InterceptResult(
                handled=True,
                annotation=None,
                recommendation=recommendation,
                confidence=confidence,
                matching_principles=matching_principles,
                matching_patterns=matching_patterns,
                audit_trail=audit_trail,
            )
        else:
            # Low confidence: annotate for human
            annotation = self._generate_annotation(
                prompt, matching_principles, matching_patterns
            )

            return InterceptResult(
                handled=False,
                annotation=annotation,
                recommendation=None,
                confidence=confidence,
                matching_principles=matching_principles,
                matching_patterns=matching_patterns,
                audit_trail="",
            )

    async def intercept_deep(self, token: Any) -> InterceptResult:
        """
        Deep intercept using LLM-backed principle reasoning.

        This is the Semantic Gatekeeper pattern:
        - Uses LLM to reason about the operation against principles
        - NEVER auto-approves dangerous operations
        - Always escalates when uncertain

        CRITICAL: Dangerous operations (delete, production, sudo, etc.)
        NEVER auto-approve. Always escalate to human.

        Args:
            token: The SemaphoreToken to evaluate

        Returns:
            InterceptResult with handling decision and reasoning
        """
        # Extract token info
        prompt = getattr(token, "prompt", str(token))
        reason = getattr(token, "reason", "")
        severity = getattr(token, "severity", 0.5)
        token_id = getattr(token, "id", "unknown")

        # CRITICAL: Check for dangerous keywords first
        # These should NEVER be auto-approved
        prompt_lower = prompt.lower()
        is_dangerous = any(kw in prompt_lower for kw in DANGEROUS_KEYWORDS)

        if is_dangerous:
            # Log to audit trail
            entry = self._create_audit_entry(
                token_id=token_id,
                action="escalate",
                confidence=0.0,
                principles=["SAFETY_OVERRIDE"],
                reasoning="Dangerous operation detected. Escalating to human.",
            )
            self.audit.log(entry)

            return InterceptResult(
                handled=False,
                annotation=f"DANGEROUS OPERATION: '{prompt[:50]}...' requires human review.",
                recommendation="escalate",
                confidence=0.0,
                matching_principles=["SAFETY_OVERRIDE"],
                matching_patterns=[],
                audit_trail=entry.to_audit_string(),
                reasoning="This operation contains dangerous keywords and cannot be auto-approved.",
                was_deep=True,
            )

        # If no LLM, fall back to shallow intercept
        if self._llm is None:
            result = await self.intercept(token)
            result.was_deep = False
            return result

        # Use LLM to reason about the operation
        system_prompt = self._build_intercept_system_prompt()
        user_prompt = self._build_intercept_user_prompt(prompt, reason, severity)

        try:
            response = await self._llm.generate(
                system=system_prompt,
                user=user_prompt,
                temperature=0.2,  # Low temperature for reliability
                max_tokens=500,
            )

            # Parse the LLM response
            result = self._parse_intercept_response(response.text, token_id, prompt)

            # Log to audit trail
            entry = self._create_audit_entry(
                token_id=token_id,
                action=result.recommendation or "unknown",
                confidence=result.confidence,
                principles=result.matching_principles,
                reasoning=result.reasoning,
            )
            self.audit.log(entry)

            return result

        except Exception as e:
            # On error, always escalate
            error_reasoning = f"LLM reasoning failed: {str(e)}. Escalating to human."

            entry = self._create_audit_entry(
                token_id=token_id,
                action="escalate",
                confidence=0.0,
                principles=["ERROR_FALLBACK"],
                reasoning=error_reasoning,
            )
            self.audit.log(entry)

            return InterceptResult(
                handled=False,
                annotation="Error during evaluation. Human review required.",
                recommendation="escalate",
                confidence=0.0,
                matching_principles=["ERROR_FALLBACK"],
                matching_patterns=[],
                audit_trail=entry.to_audit_string(),
                reasoning=error_reasoning,
                was_deep=True,
            )

    def _build_intercept_system_prompt(self) -> str:
        """Build system prompt for intercept reasoning."""
        return f"""You are K-gent's ethical reasoning module - the Semantic Gatekeeper.

Your role is to evaluate operations against Kent's principles and decide:
1. AUTO-APPROVE: Operation clearly aligns with principles
2. AUTO-REJECT: Operation clearly violates principles
3. ESCALATE: Ambiguous, needs human judgment

{self._eigenvectors.to_system_prompt_section()}

CRITICAL RULES:
- NEVER approve operations that could cause data loss
- NEVER approve operations on production systems without explicit confirmation
- NEVER approve operations involving secrets or credentials
- When in doubt, ESCALATE
- Low confidence = ESCALATE

You must respond in this exact format:
RECOMMENDATION: [approve|reject|escalate]
CONFIDENCE: [0.0 to 1.0]
PRINCIPLES: [comma-separated list of relevant principles]
REASONING: [one-line explanation]
"""

    def _build_intercept_user_prompt(
        self, prompt: str, reason: str, severity: float
    ) -> str:
        """Build user prompt for intercept reasoning."""
        return f"""Evaluate this operation:

OPERATION: {prompt}
REASON: {reason or "Not provided"}
SEVERITY: {severity:.2f}

Based on Kent's principles, should this be approved, rejected, or escalated?
"""

    def _parse_intercept_response(
        self, response_text: str, token_id: str, original_prompt: str
    ) -> InterceptResult:
        """Parse LLM response into InterceptResult."""
        lines = response_text.strip().split("\n")

        recommendation = "escalate"  # Default to escalate
        confidence = 0.0
        principles: list[str] = []
        reasoning = ""

        for line in lines:
            line = line.strip()
            if line.upper().startswith("RECOMMENDATION:"):
                rec = line.split(":", 1)[1].strip().lower()
                if rec in ("approve", "reject", "escalate"):
                    recommendation = rec
            elif line.upper().startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                    confidence = max(0.0, min(1.0, confidence))  # Clamp
                except ValueError:
                    confidence = 0.0
            elif line.upper().startswith("PRINCIPLES:"):
                principles = [
                    p.strip() for p in line.split(":", 1)[1].split(",") if p.strip()
                ]
            elif line.upper().startswith("REASONING:"):
                reasoning = line.split(":", 1)[1].strip()

        # Safety checks
        if recommendation == "approve" and confidence < 0.7:
            recommendation = "escalate"
            reasoning = f"Confidence too low for auto-approve. {reasoning}"

        handled = recommendation == "approve"

        annotation = None
        if not handled:
            annotation = self._generate_annotation(original_prompt, principles, [])

        audit_trail = self._generate_audit_trail_deep(
            token_id, recommendation, principles, confidence, reasoning
        )

        return InterceptResult(
            handled=handled,
            annotation=annotation,
            recommendation=recommendation,
            confidence=confidence,
            matching_principles=principles,
            matching_patterns=[],
            audit_trail=audit_trail,
            reasoning=reasoning,
            was_deep=True,
        )

    def _generate_audit_trail_deep(
        self,
        token_id: str,
        recommendation: str,
        principles: list[str],
        confidence: float,
        reasoning: str,
    ) -> str:
        """Generate audit trail for deep intercept."""
        return (
            f"K-gent DEEP intercept {token_id}\n"
            f"Recommendation: {recommendation}\n"
            f"Confidence: {confidence:.2%}\n"
            f"Principles: {', '.join(principles) if principles else 'None'}\n"
            f"Reasoning: {reasoning}\n"
            f"Timestamp: {datetime.now().isoformat()}"
        )

    def _create_audit_entry(
        self,
        token_id: str,
        action: str,
        confidence: float,
        principles: list[str],
        reasoning: str,
    ) -> "AuditEntry":
        """Create an audit entry."""
        from .audit import AuditEntry

        return AuditEntry(
            timestamp=datetime.now(),
            token_id=token_id,
            action=action,
            confidence=confidence,
            principles=principles,
            reasoning=reasoning,
        )

    # --- State Manifest ---

    def manifest(self) -> SoulState:
        """
        Get current soul state.

        Returns the full state including eigenvectors, persona, and session info.
        """
        return self._state

    def manifest_brief(self) -> dict[str, Any]:
        """Get brief soul state for display."""
        return {
            "mode": self._state.active_mode.value,
            "eigenvectors": self._eigenvectors.to_dict(),
            "session_interactions": self._state.interactions_count,
            "session_tokens": self._state.tokens_used_session,
        }

    # --- Starter Prompts ---

    def get_starter(self, mode: Optional[DialogueMode] = None) -> str:
        """Get a random starter prompt for the given mode."""
        mode = mode or self._state.active_mode
        return random_starter(mode)

    def get_all_starters(self, mode: Optional[DialogueMode] = None) -> list[str]:
        """Get all starter prompts for the given mode."""
        mode = mode or self._state.active_mode
        return get_starters(mode)

    def format_starters(self, mode: Optional[DialogueMode] = None) -> str:
        """Format starter prompts for CLI display."""
        mode = mode or self._state.active_mode
        return format_starters_for_display(mode)

    # --- Mode Transitions ---

    def enter_mode(self, mode: DialogueMode) -> str:
        """
        Enter a dialogue mode and return entry message.

        Args:
            mode: The mode to enter

        Returns:
            Mode entry acknowledgment
        """
        self._state.active_mode = mode
        mode_intros = {
            DialogueMode.REFLECT: "Entering REFLECT mode. What pattern are you noticing?",
            DialogueMode.ADVISE: "Entering ADVISE mode. What decision are you facing?",
            DialogueMode.CHALLENGE: "Entering CHALLENGE mode. State your thesis.",
            DialogueMode.EXPLORE: "Entering EXPLORE mode. Where does your curiosity pull?",
        }
        return mode_intros.get(mode, f"Entering {mode.value} mode.")

    # --- Private Helpers ---

    def _update_session_stats(self, tokens: int) -> None:
        """Update session statistics."""
        self._state.interactions_count += 1
        self._state.tokens_used_session += tokens
        self._state.last_interaction = datetime.now()

    def _find_matching_principles(self, text: str) -> list[str]:
        """Find principles that match the text."""
        # Simple keyword matching for now
        # Future: Use PersonaGarden deep graph
        text_lower = text.lower()
        matches = []

        # Check eigenvector-related keywords
        keyword_principles = {
            "aesthetic": ["Aesthetic: Minimalism", "Say no more than yes"],
            "minimalist": ["Aesthetic: Minimalism", "Compress, don't expand"],
            "abstract": ["Categorical: Abstract thinking", "Think in morphisms"],
            "gratitude": ["Gratitude: Sacred over utilitarian", "Accursed Share"],
            "peer": ["Heterarchy: Peer-to-peer", "Forest Over King"],
            "hierarchy": ["Heterarchy: No fixed boss", "Agents are peers"],
            "generate": ["Generativity: Spec compresses impl"],
            "joy": ["Joy: Warmth over coldness", "Fun is free"],
            "delete": ["Aesthetic: Minimalism", "Does this need to exist?"],
            "simple": ["Aesthetic: Minimalism", "Prefer minimal solutions"],
        }

        for keyword, principles in keyword_principles.items():
            if keyword in text_lower:
                matches.extend(principles)

        return list(set(matches))[:3]  # Dedupe and limit

    def _find_matching_patterns(self, text: str) -> list[str]:
        """Find patterns that match the text."""
        text_lower = text.lower()
        matches = []

        # Check persona patterns
        for category, patterns in self._persona_state.seed.patterns.items():
            for pattern in patterns:
                pattern_words = pattern.lower().split()[:3]
                if any(word in text_lower for word in pattern_words):
                    matches.append(pattern)

        return matches[:3]  # Limit

    def _calculate_intercept_confidence(
        self, principles: list[str], patterns: list[str]
    ) -> float:
        """Calculate confidence for semaphore interception."""
        if not principles and not patterns:
            return 0.0

        # Base confidence from matches
        principle_score = min(len(principles) * 0.25, 0.6)
        pattern_score = min(len(patterns) * 0.15, 0.4)

        return min(principle_score + pattern_score, 1.0)

    def _generate_recommendation(
        self, prompt: str, principles: list[str], patterns: list[str]
    ) -> str:
        """Generate recommendation based on principles."""
        if "delete" in prompt.lower() or "remove" in prompt.lower():
            if any("Minimalism" in p for p in principles):
                return "approve"
        if "add" in prompt.lower() or "create" in prompt.lower():
            if any("Minimalism" in p for p in principles):
                return "review"  # Minimalist bias = skeptical of additions
        return "review"

    def _generate_annotation(
        self, prompt: str, principles: list[str], patterns: list[str]
    ) -> str:
        """Generate human-readable annotation for semaphore."""
        lines = [f"K-gent analysis of: '{prompt[:50]}...'"]

        if principles:
            lines.append("\nRelevant principles:")
            for p in principles:
                lines.append(f"  - {p}")

        if patterns:
            lines.append("\nMatching patterns:")
            for p in patterns:
                lines.append(f"  - {p}")

        if not principles and not patterns:
            lines.append("\nNo strong matches found. Human judgment needed.")

        return "\n".join(lines)

    def _generate_audit_trail(
        self,
        token: "SemaphoreToken[Any]",
        recommendation: str,
        principles: list[str],
        confidence: float,
    ) -> str:
        """Generate audit trail for auto-resolved semaphore."""
        token_id = getattr(token, "id", "unknown")
        return (
            f"K-gent auto-resolved {token_id}\n"
            f"Recommendation: {recommendation}\n"
            f"Confidence: {confidence:.2%}\n"
            f"Based on: {', '.join(principles)}\n"
            f"Timestamp: {datetime.now().isoformat()}"
        )


# --- Convenience Functions ---


def create_soul(
    persona_state: Optional[PersonaState] = None,
    eigenvectors: Optional[KentEigenvectors] = None,
) -> KgentSoul:
    """Create a K-gent Soul instance."""
    return KgentSoul(persona_state=persona_state, eigenvectors=eigenvectors)


def soul() -> KgentSoul:
    """Create a default K-gent Soul instance."""
    return KgentSoul()
