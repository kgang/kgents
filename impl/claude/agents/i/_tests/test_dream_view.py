"""
Tests for DreamReportRenderer (Instance DB Phase 6).

Tests dream report rendering, morning briefing, and neurogenesis visualization.
"""

import pytest

from agents.i.dream_view import (
    DreamPhase,
    MaintenanceChunk,
    MigrationProposal,
    Question,
    SimpleDreamReport,
    create_mock_dream_report,
    create_mock_questions,
    render_briefing_question,
    render_dream_report,
    render_dream_report_compact,
    render_migration_proposals,
    render_migration_sql,
    render_morning_briefing,
    render_phase_bar,
    render_phase_indicator,
)


class TestDreamPhase:
    """Tests for DreamPhase enum."""

    def test_phase_values(self) -> None:
        """Test phase enum values."""
        assert DreamPhase.AWAKE.value == "awake"
        assert DreamPhase.REM_CONSOLIDATION.value == "rem_consolidation"
        assert DreamPhase.INTERRUPTED.value == "interrupted"

    def test_all_phases(self) -> None:
        """Test all phases exist."""
        phases = [
            DreamPhase.AWAKE,
            DreamPhase.ENTERING_REM,
            DreamPhase.REM_CONSOLIDATION,
            DreamPhase.REM_MAINTENANCE,
            DreamPhase.REM_REFLECTION,
            DreamPhase.WAKING,
            DreamPhase.INTERRUPTED,
        ]
        assert len(phases) == 7


class TestQuestion:
    """Tests for Question dataclass."""

    def test_create_question(self) -> None:
        """Test creating a question."""
        q = Question(
            question_id="q-001",
            question_text="What is the answer?",
            context={"key": "value"},
            priority=2,
        )

        assert q.question_id == "q-001"
        assert q.answered is False
        assert q.priority == 2


class TestMigrationProposal:
    """Tests for MigrationProposal dataclass."""

    def test_create_proposal(self) -> None:
        """Test creating a proposal."""
        p = MigrationProposal(
            proposal_id="p-001",
            table="memories",
            action="add_column",
            column_name="tags",
            column_type="TEXT",
            confidence=0.85,
        )

        assert p.proposal_id == "p-001"
        assert p.approved is False
        assert p.confidence == 0.85


class TestPhaseIndicator:
    """Tests for phase indicator rendering."""

    def test_awake_indicator(self) -> None:
        """Test awake phase indicator."""
        indicator = render_phase_indicator(DreamPhase.AWAKE)
        assert indicator == "○"

    def test_rem_consolidation_indicator(self) -> None:
        """Test REM consolidation indicator."""
        indicator = render_phase_indicator(DreamPhase.REM_CONSOLIDATION)
        assert indicator == "●"

    def test_interrupted_indicator(self) -> None:
        """Test interrupted indicator."""
        indicator = render_phase_indicator(DreamPhase.INTERRUPTED)
        assert indicator == "⊗"

    def test_string_phase(self) -> None:
        """Test with string phase."""
        indicator = render_phase_indicator("awake")
        assert indicator == "○"


class TestPhaseBar:
    """Tests for phase bar rendering."""

    def test_awake_bar(self) -> None:
        """Test awake phase bar."""
        bar = render_phase_bar(DreamPhase.AWAKE)
        assert "[" in bar and "]" in bar
        assert "○" in bar

    def test_consolidation_bar(self) -> None:
        """Test consolidation phase bar."""
        bar = render_phase_bar(DreamPhase.REM_CONSOLIDATION)
        assert "●" in bar

    def test_interrupted_bar(self) -> None:
        """Test interrupted phase bar."""
        bar = render_phase_bar(DreamPhase.INTERRUPTED)
        assert "INTERRUPTED" in bar

    def test_string_phase(self) -> None:
        """Test with string phase."""
        bar = render_phase_bar("rem_maintenance")
        assert "[" in bar and "]" in bar


class TestDreamReportRendering:
    """Tests for dream report rendering."""

    def test_render_simple_report(self) -> None:
        """Test rendering a simple report."""
        report = create_mock_dream_report()
        output = render_dream_report(report)

        assert "DREAM REPORT" in output
        assert report.dream_id in output

    def test_render_report_has_box(self) -> None:
        """Test report has ASCII box."""
        report = create_mock_dream_report()
        output = render_dream_report(report)

        assert "╔" in output
        assert "╚" in output
        assert "║" in output

    def test_render_report_shows_phase(self) -> None:
        """Test report shows phase bar."""
        report = create_mock_dream_report()
        output = render_dream_report(report)

        assert "Phase:" in output

    def test_render_interrupted_report(self) -> None:
        """Test rendering interrupted report."""
        report = create_mock_dream_report(interrupted=True)
        output = render_dream_report(report)

        assert "INTERRUPTED" in output
        assert "⚠" in output or "High-surprise" in output

    def test_render_report_from_dict(self) -> None:
        """Test rendering from dict."""
        data = {
            "dream_id": "test-dream",
            "started_at": "2024-01-01T00:00:00",
            "completed_at": None,
            "phase_reached": "rem_consolidation",
            "interrupted": False,
            "chunks_completed": 50,
            "chunks_total": 100,
            "questions_generated": 3,
            "duration_ms": 1500.0,
        }

        output = render_dream_report(data)
        assert "test-dream" in output

    def test_render_report_shows_progress(self) -> None:
        """Test report shows progress bar."""
        report = create_mock_dream_report(chunks_completed=50, chunks_total=100)
        output = render_dream_report(report)

        assert "Progress:" in output
        assert "█" in output or "░" in output
        assert "50%" in output


class TestDreamReportCompact:
    """Tests for compact dream report rendering."""

    def test_compact_format(self) -> None:
        """Test compact rendering."""
        report = create_mock_dream_report()
        output = render_dream_report_compact(report)

        # Should be single line
        assert "\n" not in output
        assert "[" in output and "]" in output

    def test_compact_shows_status(self) -> None:
        """Test compact shows status."""
        report = create_mock_dream_report()
        output = render_dream_report_compact(report)

        assert "✓" in output or "!" in output

    def test_compact_from_dict(self) -> None:
        """Test compact from dict."""
        data = {
            "phase_reached": "rem_consolidation",
            "interrupted": False,
            "chunks_completed": 50,
            "chunks_total": 100,
            "questions_generated": 3,
        }

        output = render_dream_report_compact(data)
        assert "Q: 3" in output


class TestMorningBriefing:
    """Tests for morning briefing rendering."""

    def test_empty_briefing(self) -> None:
        """Test rendering empty briefing."""
        output = render_morning_briefing([])

        assert "MORNING BRIEFING" in output
        assert "No questions pending" in output

    def test_briefing_with_questions(self) -> None:
        """Test rendering with questions."""
        questions = create_mock_questions(3)
        output = render_morning_briefing(questions)

        assert "MORNING BRIEFING" in output
        assert "3 question(s)" in output

    def test_briefing_has_box(self) -> None:
        """Test briefing has ASCII box."""
        questions = create_mock_questions(2)
        output = render_morning_briefing(questions)

        assert "╔" in output
        assert "╚" in output

    def test_briefing_shows_questions(self) -> None:
        """Test briefing shows question text."""
        questions = create_mock_questions(1)
        output = render_morning_briefing(questions)

        assert "[1]" in output  # Question number

    def test_briefing_from_dicts(self) -> None:
        """Test briefing from dict list."""
        questions = [
            {
                "question_id": "q-001",
                "question_text": "Test question?",
                "priority": 2,
                "answered": False,
            }
        ]

        output = render_morning_briefing(questions)
        assert "Test question?" in output or "Test" in output


class TestBriefingQuestion:
    """Tests for individual question rendering."""

    def test_render_question(self) -> None:
        """Test rendering single question."""
        q = create_mock_questions(1)[0]
        output = render_briefing_question(q, number=1)

        assert "Question 1" in output

    def test_render_high_priority(self) -> None:
        """Test high priority indicator."""
        q = Question(
            question_id="q-001",
            question_text="Important?",
            priority=3,
        )
        output = render_briefing_question(q)

        assert "HIGH PRIORITY" in output or "⚠️" in output

    def test_render_from_dict(self) -> None:
        """Test from dict."""
        data = {
            "question_text": "Test?",
            "context": {"key": "value"},
            "priority": 1,
        }

        output = render_briefing_question(data)
        assert "Test?" in output


class TestMigrationProposals:
    """Tests for migration proposal rendering."""

    def test_empty_proposals(self) -> None:
        """Test rendering empty proposals."""
        output = render_migration_proposals([])
        assert "No pending" in output

    def test_render_proposals(self) -> None:
        """Test rendering proposals."""
        proposals = [
            MigrationProposal(
                proposal_id="p-001",
                table="memories",
                action="add_column",
                column_name="tags",
                column_type="TEXT",
                confidence=0.85,
            )
        ]

        output = render_migration_proposals(proposals)

        assert "SCHEMA NEUROGENESIS" in output
        assert "memories" in output
        assert "tags" in output

    def test_render_confidence_bar(self) -> None:
        """Test confidence bar rendering."""
        proposals = [
            MigrationProposal(
                proposal_id="p-001",
                table="test",
                action="add_column",
                column_name="col",
                column_type="TEXT",
                confidence=0.8,
            )
        ]

        output = render_migration_proposals(proposals)
        assert "█" in output or "Confidence" in output

    def test_render_from_dicts(self) -> None:
        """Test from dict list."""
        proposals = [
            {
                "proposal_id": "p-001",
                "table": "test",
                "action": "add_column",
                "column_name": "col",
                "column_type": "TEXT",
                "confidence": 0.9,
            }
        ]

        output = render_migration_proposals(proposals)
        assert "test" in output


class TestMigrationSQL:
    """Tests for migration SQL generation."""

    def test_add_column_sql(self) -> None:
        """Test add_column SQL."""
        p = MigrationProposal(
            proposal_id="p-001",
            table="memories",
            action="add_column",
            column_name="tags",
            column_type="TEXT",
            confidence=0.9,
        )

        sql = render_migration_sql(p)
        assert "ALTER TABLE memories ADD COLUMN tags TEXT" in sql

    def test_drop_column_sql(self) -> None:
        """Test drop_column SQL."""
        p = MigrationProposal(
            proposal_id="p-001",
            table="memories",
            action="drop_column",
            column_name="old_col",
            column_type="TEXT",
            confidence=0.9,
        )

        sql = render_migration_sql(p)
        assert "DROP COLUMN" in sql

    def test_create_index_sql(self) -> None:
        """Test create_index SQL."""
        p = MigrationProposal(
            proposal_id="p-001",
            table="memories",
            action="create_index",
            column_name="tags",
            column_type="TEXT",
            confidence=0.9,
        )

        sql = render_migration_sql(p)
        assert "CREATE INDEX" in sql
        assert "memories" in sql
        assert "tags" in sql

    def test_from_dict(self) -> None:
        """Test from dict."""
        data = {
            "table": "test",
            "action": "add_column",
            "column_name": "col",
            "column_type": "INTEGER",
        }

        sql = render_migration_sql(data)
        assert "ALTER TABLE test ADD COLUMN col INTEGER" in sql


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_mock_dream_report(self) -> None:
        """Test mock report factory."""
        report = create_mock_dream_report()

        assert isinstance(report, SimpleDreamReport)
        assert report.dream_id is not None
        assert report.started_at is not None

    def test_create_mock_dream_report_interrupted(self) -> None:
        """Test mock interrupted report."""
        report = create_mock_dream_report(interrupted=True)

        assert report.interrupted is True
        assert report.interrupt_reason is not None

    def test_create_mock_dream_report_custom_chunks(self) -> None:
        """Test mock with custom chunks."""
        report = create_mock_dream_report(
            chunks_completed=75,
            chunks_total=150,
        )

        assert report.chunks_completed == 75
        assert report.chunks_total == 150

    def test_create_mock_questions(self) -> None:
        """Test mock questions factory."""
        questions = create_mock_questions(3)

        assert len(questions) == 3
        assert all(isinstance(q, Question) for q in questions)

    def test_create_mock_questions_limited(self) -> None:
        """Test mock questions with limit."""
        questions = create_mock_questions(1)
        assert len(questions) == 1
