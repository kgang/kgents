"""
N-gent Bard: The Storyteller.

The Bard transforms crystals into narrative. This is a READ-TIME operation.
The Historian collects stones; the Bard casts shadows when the sun is out.

Philosophy:
    Story is a Read-Time projection, not a Write-Time artifact.
    The same crystals can yield TECHNICAL logs, NOIR detective stories,
    or MINIMAL operational notes - the perspective is chosen at read-time.

    This is Rashomon for agents: multiple valid tellings of the same events.

Components:
    - NarrativeGenre: The voice and style of the telling
    - Verbosity: How much detail to include
    - NarrativeRequest: What to tell and how
    - Chapter: A coherent unit of the narrative
    - Narrative: The Bard's output
    - Bard: The storyteller agent
    - ForensicBard: The detective - specializes in crash analysis
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from .types import SemanticTrace


class NarrativeGenre(Enum):
    """
    The genre determines voice, style, and interpretation.

    Each genre provides a different lens through which to view
    the same sequence of events.
    """

    TECHNICAL = "technical"  # Timestamps, structured logs
    LITERARY = "literary"  # Engaging narrative with character
    NOIR = "noir"  # Hardboiled detective fiction
    SYSADMIN = "sysadmin"  # Terse operational notes
    MINIMAL = "minimal"  # Most compact summary possible
    DETECTIVE = "detective"  # Mystery investigation style


class Verbosity(Enum):
    """How much detail to include in the narrative."""

    TERSE = "terse"  # One sentence per event
    NORMAL = "normal"  # Balanced brevity and detail
    VERBOSE = "verbose"  # All details, explain reasoning


class Perspective(Enum):
    """Narrative perspective for the story."""

    FIRST_PERSON = "first_person"  # I/we - as if from the agent
    SECOND_PERSON = "second_person"  # You - addressing the reader
    THIRD_PERSON = "third_person"  # They/it - observer perspective


@dataclass
class Chapter:
    """
    A coherent unit of the narrative.

    Chapters are detected by:
    - Agent changes
    - Temporal gaps (> 1 minute)
    - Error/recovery cycles
    - Thematic shifts
    """

    name: str
    start_trace_id: str
    end_trace_id: str
    theme: str
    agents_involved: list[str]
    trace_count: int = 0
    duration_ms: int = 0

    def __post_init__(self):
        """Ensure agents_involved is a list."""
        if isinstance(self.agents_involved, set):
            self.agents_involved = list(self.agents_involved)


@dataclass
class NarrativeRequest:
    """
    A request to the Bard.

    Specifies what crystals to include and how to tell the story.
    """

    traces: list[SemanticTrace]
    genre: NarrativeGenre = NarrativeGenre.TECHNICAL
    perspective: Perspective = Perspective.THIRD_PERSON
    verbosity: Verbosity = Verbosity.NORMAL

    # Optional filters
    focus_agents: list[str] | None = None  # Only include these agents
    filter_actions: list[str] | None = None  # Only include these actions
    exclude_actions: list[str] | None = None  # Exclude these actions

    # Optional customization
    title: str | None = None
    custom_prompt: str | None = None

    def filtered_traces(self) -> list[SemanticTrace]:
        """Apply filters and return matching traces."""
        result = self.traces

        if self.focus_agents:
            result = [t for t in result if t.agent_id in self.focus_agents]

        if self.filter_actions:
            result = [t for t in result if t.action in self.filter_actions]

        if self.exclude_actions:
            result = [t for t in result if t.action not in self.exclude_actions]

        return result


@dataclass
class Narrative:
    """
    The output of the Bard.

    Contains the story text plus metadata about what was told.
    """

    text: str
    genre: NarrativeGenre
    traces_used: list[SemanticTrace]
    chapters: list[Chapter]
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def title(self) -> str:
        """Get the narrative title."""
        return self.metadata.get("title", "Untitled Narrative")

    @property
    def total_duration_ms(self) -> int:
        """Total duration across all traces."""
        return sum(t.duration_ms for t in self.traces_used)

    @property
    def total_gas(self) -> int:
        """Total gas consumed across all traces."""
        return sum(t.gas_consumed for t in self.traces_used)

    @property
    def agent_count(self) -> int:
        """Number of unique agents involved."""
        return len(set(t.agent_id for t in self.traces_used))

    def render(self, format: str = "text") -> str:
        """Render the narrative in the requested format."""
        if format == "markdown":
            return self._to_markdown()
        if format == "html":
            return self._to_html()
        return self.text

    def _to_markdown(self) -> str:
        """Render as Markdown."""
        lines = [f"# {self.title}\n"]

        # Metadata section
        lines.append(f"*Genre: {self.genre.value}*")
        lines.append(
            f"*Traces: {len(self.traces_used)} | Duration: {self.total_duration_ms}ms*\n"
        )

        # Chapters
        for chapter in self.chapters:
            lines.append(f"## {chapter.name}")
            lines.append(
                f"*Theme: {chapter.theme} | Agents: {', '.join(chapter.agents_involved)}*\n"
            )

        # Main text
        lines.append("---\n")
        lines.append(self.text)

        return "\n".join(lines)

    def _to_html(self) -> str:
        """Render as HTML."""
        lines = ["<!DOCTYPE html>", "<html>", "<head>", f"<title>{self.title}</title>"]
        lines.append(
            "<style>body{font-family:system-ui;max-width:800px;margin:auto;padding:20px}"
            ".meta{color:#666;font-style:italic}.chapter{margin:20px 0}</style>"
        )
        lines.extend(["</head>", "<body>"])
        lines.append(f"<h1>{self.title}</h1>")
        lines.append(f'<p class="meta">Genre: {self.genre.value}</p>')

        for chapter in self.chapters:
            lines.append('<div class="chapter">')
            lines.append(f"<h2>{chapter.name}</h2>")
            lines.append(f'<p class="meta">Theme: {chapter.theme}</p>')
            lines.append("</div>")

        lines.append(f"<p>{self.text.replace(chr(10), '<br>')}</p>")
        lines.append("</body></html>")
        return "\n".join(lines)


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol for LLM providers used by the Bard."""

    async def generate(self, prompt: str) -> str:
        """Generate text from a prompt."""
        ...


class SimpleLLMProvider:
    """A simple LLM provider for testing that generates deterministic output."""

    def __init__(self, response: str | None = None):
        self.response = response
        self.last_prompt: str | None = None
        self.call_count = 0

    async def generate(self, prompt: str) -> str:
        """Generate a response (or return the configured response)."""
        self.last_prompt = prompt
        self.call_count += 1

        if self.response:
            return self.response

        # Default: generate a simple summary
        return f"[Generated narrative from {self.call_count} call(s)]"


class Bard:
    """
    The Storyteller. Runs POST-MORTEM.

    Takes cold crystals and projects them into story.
    This is a Read-Time operation - the same crystals can
    yield different stories depending on genre and perspective.

    The Bard doesn't modify crystals; it only reads them.
    """

    def __init__(self, llm: LLMProvider | None = None):
        """Initialize the Bard with an optional LLM provider."""
        self.llm = llm or SimpleLLMProvider()

    async def invoke(self, request: NarrativeRequest) -> Narrative:
        """
        Cast the shadow. Generate a narrative from crystals.

        Args:
            request: The narrative request with traces and settings

        Returns:
            A Narrative with text, chapters, and metadata
        """
        traces = request.filtered_traces()

        if not traces:
            return Narrative(
                text="No events to narrate.",
                genre=request.genre,
                traces_used=[],
                chapters=[],
                metadata={"title": request.title or "Empty Narrative"},
            )

        # Build and execute the prompt
        prompt = self._build_prompt(request, traces)
        story_text = await self.llm.generate(prompt)

        # Identify chapter structure
        chapters = self._identify_chapters(traces)

        return Narrative(
            text=story_text,
            genre=request.genre,
            traces_used=traces,
            chapters=chapters,
            metadata={
                "title": request.title or self._generate_title(traces),
                "perspective": request.perspective.value,
                "verbosity": request.verbosity.value,
                "trace_count": len(traces),
            },
        )

    def _build_prompt(
        self, request: NarrativeRequest, traces: list[SemanticTrace]
    ) -> str:
        """Build the prompt for the LLM."""
        crystals_formatted = self._format_crystals(traces)

        genre_instructions = self._genre_instructions()
        verbosity_instructions = self._verbosity_instructions()

        prompt = f"""You are the Bard, a storyteller who transforms execution traces into narratives.

GENRE: {request.genre.value}
STYLE: {genre_instructions[request.genre]}

VERBOSITY: {request.verbosity.value}
{verbosity_instructions[request.verbosity]}

PERSPECTIVE: {request.perspective.value}

Here are the execution crystals (semantic traces):

{crystals_formatted}

Now tell the story of what happened."""

        if request.custom_prompt:
            prompt += f"\n\nADDITIONAL INSTRUCTIONS:\n{request.custom_prompt}"

        return prompt

    def _genre_instructions(self) -> dict[NarrativeGenre, str]:
        """Get instructions for each genre."""
        return {
            NarrativeGenre.TECHNICAL: (
                "Write a technical log with timestamps. "
                "Format: [HH:MM:SS] Agent: Action (inputs -> outputs)"
            ),
            NarrativeGenre.LITERARY: (
                "Write an engaging narrative with character and drama. "
                "Personify the agents. Use vivid language."
            ),
            NarrativeGenre.NOIR: (
                "Write in the style of hardboiled detective fiction. "
                "The code came in like trouble on a rainy night..."
            ),
            NarrativeGenre.SYSADMIN: (
                "Write terse operational notes. Just the facts. No flourish."
            ),
            NarrativeGenre.MINIMAL: (
                "Write the most compact summary possible. "
                "One line per significant event."
            ),
            NarrativeGenre.DETECTIVE: (
                "Write as if investigating a mystery. "
                "Clues, deductions, timeline analysis."
            ),
        }

    def _verbosity_instructions(self) -> dict[Verbosity, str]:
        """Get instructions for each verbosity level."""
        return {
            Verbosity.TERSE: "Be extremely brief. One sentence per event.",
            Verbosity.NORMAL: "Balance brevity and detail.",
            Verbosity.VERBOSE: "Include all details. Explain reasoning.",
        }

    def _format_crystals(self, traces: list[SemanticTrace]) -> str:
        """Format crystals for the prompt."""
        lines = []
        for t in traces:
            time_str = t.timestamp.strftime("%H:%M:%S")
            inputs_str = _truncate_dict(t.inputs, 100)
            outputs_str = _truncate_dict(t.outputs, 100) if t.outputs else "None"

            lines.append(
                f"- [{time_str}] Agent={t.agent_id} ({t.agent_genus}), "
                f"Action={t.action}, Inputs={inputs_str}, Outputs={outputs_str}, "
                f"Duration={t.duration_ms}ms"
            )
        return "\n".join(lines)

    def _identify_chapters(self, traces: list[SemanticTrace]) -> list[Chapter]:
        """
        Identify chapter boundaries in the trace sequence.

        Heuristics:
        - Agent changes (new agent not in current chapter)
        - Temporal gaps > 60 seconds
        - Error traces (ERROR action)
        """
        if not traces:
            return []

        chapters: list[Chapter] = []
        chapter_traces: list[SemanticTrace] = []
        current_agents: set[str] = set()
        chapter_start_id = traces[0].trace_id

        for i, trace in enumerate(traces):
            # Detect chapter break conditions
            is_break = False

            # Agent change (new agent not in current chapter)
            if trace.agent_id not in current_agents and len(current_agents) > 0:
                is_break = True

            # Error action
            elif trace.action == "ERROR":
                is_break = True

            # Temporal gap > 60 seconds
            elif (
                i > 0
                and (trace.timestamp - traces[i - 1].timestamp).total_seconds() > 60
            ):
                is_break = True

            # Commit current chapter if break detected
            if is_break and chapter_traces:
                chapters.append(
                    Chapter(
                        name=f"Chapter {len(chapters) + 1}",
                        start_trace_id=chapter_start_id,
                        end_trace_id=chapter_traces[-1].trace_id,
                        theme=self._infer_theme(chapter_traces),
                        agents_involved=list(current_agents),
                        trace_count=len(chapter_traces),
                        duration_ms=sum(t.duration_ms for t in chapter_traces),
                    )
                )

                # Start new chapter
                chapter_start_id = trace.trace_id
                chapter_traces = []
                current_agents = set()

            # Add to current chapter
            chapter_traces.append(trace)
            current_agents.add(trace.agent_id)

        # Final chapter
        if chapter_traces:
            chapters.append(
                Chapter(
                    name=f"Chapter {len(chapters) + 1}",
                    start_trace_id=chapter_start_id,
                    end_trace_id=chapter_traces[-1].trace_id,
                    theme=self._infer_theme(chapter_traces),
                    agents_involved=list(current_agents),
                    trace_count=len(chapter_traces),
                    duration_ms=sum(t.duration_ms for t in chapter_traces),
                )
            )

        return chapters

    def _infer_theme(self, traces: list[SemanticTrace]) -> str:
        """Infer a theme from a sequence of traces."""
        actions = [t.action for t in traces]

        # Priority-based theme inference
        if "ERROR" in actions:
            return "Error Handling"
        if "GENERATE" in actions:
            return "Generation"
        if "VALIDATE" in actions:
            return "Validation"
        if "DECIDE" in actions:
            return "Decision Making"
        if "COMPOSE" in actions:
            return "Composition"
        if "PARSE" in actions:
            return "Parsing"
        if "LOOKUP" in actions:
            return "Data Retrieval"
        if "TRANSFORM" in actions:
            return "Transformation"

        return "Processing"

    def _generate_title(self, traces: list[SemanticTrace]) -> str:
        """Generate a title for the narrative."""
        if not traces:
            return "Empty Execution"

        agents = sorted(set(t.agent_id for t in traces))
        if len(agents) == 1:
            return f"The {agents[0]} Execution"
        elif len(agents) <= 3:
            return f"The {', '.join(agents[:-1])} and {agents[-1]} Collaboration"
        else:
            return f"Multi-Agent Execution ({len(agents)} agents)"


@dataclass
class Diagnosis:
    """
    A crash diagnosis from the ForensicBard.

    Contains analysis, probable cause, and remediation suggestions.
    """

    narrative: str
    failure_trace: SemanticTrace
    probable_cause: str
    echo_command: str  # Command to replay the failure
    similar_failures: list[SemanticTrace] = field(default_factory=list)
    context_traces: list[SemanticTrace] = field(default_factory=list)
    severity: str = "unknown"

    @property
    def is_deterministic(self) -> bool:
        """Can this failure be reliably reproduced?"""
        from .types import Determinism

        return self.failure_trace.determinism == Determinism.DETERMINISTIC

    @property
    def agent_history(self) -> list[str]:
        """Get the sequence of agents leading to failure."""
        return [t.agent_id for t in self.context_traces] + [self.failure_trace.agent_id]


class ForensicBard(Bard):
    """
    The Detective. Specializes in crash narratives.

    ForensicBard analyzes failure traces and produces diagnoses
    with probable causes and remediation suggestions.
    """

    def __init__(self, llm: LLMProvider | None = None):
        """Initialize the ForensicBard."""
        super().__init__(llm)

    async def diagnose(
        self,
        failure_trace: SemanticTrace,
        context_traces: list[SemanticTrace] | None = None,
        similar_failures: list[SemanticTrace] | None = None,
    ) -> Diagnosis:
        """
        Produce a crash diagnosis.

        Args:
            failure_trace: The trace where failure occurred
            context_traces: Events leading up to the failure
            similar_failures: Historical failures with similar patterns

        Returns:
            A Diagnosis with analysis and remediation
        """
        context = context_traces or []
        similar = similar_failures or []

        # Build forensic prompt
        prompt = self._build_forensic_prompt(failure_trace, context, similar)
        analysis = await self.llm.generate(prompt)

        # Extract probable cause from analysis
        probable_cause = self._extract_cause(analysis)

        # Determine severity
        severity = self._assess_severity(failure_trace, context)

        return Diagnosis(
            narrative=analysis,
            failure_trace=failure_trace,
            probable_cause=probable_cause,
            echo_command=f"kgents echo {failure_trace.trace_id}",
            similar_failures=similar,
            context_traces=context,
            severity=severity,
        )

    def _build_forensic_prompt(
        self,
        failure: SemanticTrace,
        context: list[SemanticTrace],
        similar: list[SemanticTrace],
    ) -> str:
        """Build a forensic analysis prompt."""
        context_formatted = self._format_crystals(context) if context else "None"
        similar_formatted = (
            self._format_similar_failures(similar) if similar else "None"
        )

        return f"""You are a forensic analyst investigating a system failure.

THE FAILURE:
- Timestamp: {failure.timestamp}
- Agent: {failure.agent_id} ({failure.agent_genus})
- Action: {failure.action}
- Inputs: {_truncate_dict(failure.inputs, 200)}
- Outputs: {_truncate_dict(failure.outputs, 200) if failure.outputs else "None"}
- Duration: {failure.duration_ms}ms
- Determinism: {failure.determinism.value}

CONTEXT (events leading up to failure):
{context_formatted}

SIMILAR HISTORICAL FAILURES:
{similar_formatted}

ANALYZE:
1. What was the agent trying to do?
2. What went wrong?
3. What is the probable root cause?
4. How might this be prevented in the future?

Be specific. Reference trace IDs where relevant."""

    def _format_similar_failures(self, failures: list[SemanticTrace]) -> str:
        """Format similar failures for the prompt."""
        if not failures:
            return "No similar failures found."

        lines = []
        for f in failures[:5]:  # Limit to 5 similar failures
            error_msg = f.outputs.get("error", "Unknown") if f.outputs else "Unknown"
            lines.append(
                f"- [{f.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] "
                f"Agent={f.agent_id}, Error={error_msg}"
            )
        return "\n".join(lines)

    def _extract_cause(self, analysis: str) -> str:
        """Extract the probable cause from analysis."""
        lines = analysis.split("\n")

        # Look for explicit cause indicators
        for line in lines:
            lower = line.lower()
            if "root cause" in lower:
                return line.strip().lstrip("- ").lstrip("* ")
            if "probable cause" in lower:
                return line.strip().lstrip("- ").lstrip("* ")
            if "because" in lower and len(line) > 20:
                return line.strip()

        # Fallback: first non-empty line
        for line in lines:
            if line.strip():
                return line.strip()[:200]

        return "Unable to determine cause"

    def _assess_severity(
        self, failure: SemanticTrace, context: list[SemanticTrace]
    ) -> str:
        """Assess the severity of the failure."""
        # Check for cascade indicators
        cascade_count = sum(1 for t in context if t.action == "ERROR")
        if cascade_count >= 3:
            return "critical"

        # Check for chaotic (external) failures
        from .types import Determinism

        if failure.determinism == Determinism.CHAOTIC:
            return "high"

        # Check for long duration (may indicate resource issues)
        if failure.duration_ms > 5000:
            return "medium"

        return "low"


def _truncate_dict(d: dict[str, Any] | None, max_len: int) -> str:
    """Truncate a dict representation to max_len characters."""
    if d is None:
        return "None"
    s = str(d)
    if len(s) <= max_len:
        return s
    return s[: max_len - 3] + "..."
