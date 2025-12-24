"""
Tests for experiment types.

Tests:
- Type creation and validation
- Serialization (to_dict/from_dict)
- Config dispatch
- Evidence bundle calculation

Philosophy:
    "Types are contracts. Tests verify the contracts hold."
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from services.experiment.types import (
    EvidenceBundle,
    Experiment,
    ExperimentConfig,
    ExperimentStatus,
    ExperimentType,
    GenerateConfig,
    LawsConfig,
    ParseConfig,
    Trial,
    generate_experiment_id,
)


def test_experiment_id_generation():
    """Test that experiment IDs are unique."""
    id1 = generate_experiment_id()
    id2 = generate_experiment_id()

    assert id1.startswith("exp-")
    assert id2.startswith("exp-")
    assert id1 != id2


def test_trial_creation():
    """Test trial creation."""
    trial = Trial(
        index=0,
        input="test input",
        output="test output",
        success=True,
        duration_ms=100.0,
        confidence=1.0,
    )

    assert trial.index == 0
    assert trial.success is True
    assert trial.duration_ms == 100.0


def test_trial_serialization():
    """Test trial to_dict/from_dict."""
    original = Trial(
        index=5,
        input="input",
        output="output",
        success=False,
        duration_ms=200.0,
        confidence=0.5,
        error="Test error",
    )

    # Serialize
    data = original.to_dict()
    assert data["index"] == 5
    assert data["success"] is False
    assert data["error"] == "Test error"

    # Deserialize
    restored = Trial.from_dict(data)
    assert restored.index == original.index
    assert restored.success == original.success
    assert restored.error == original.error


def test_evidence_bundle():
    """Test evidence bundle creation."""
    bundle = EvidenceBundle(
        trials_total=10,
        trials_success=7,
        success_rate=0.7,
        mean_confidence=0.75,
        std_confidence=0.2,
        mean_duration_ms=150.0,
    )

    assert bundle.trials_total == 10
    assert bundle.trials_success == 7
    assert bundle.trials_failed == 3
    assert bundle.success_rate == 0.7


def test_evidence_bundle_serialization():
    """Test evidence bundle to_dict/from_dict."""
    original = EvidenceBundle(
        trials_total=20,
        trials_success=15,
        success_rate=0.75,
        mean_confidence=0.8,
        std_confidence=0.15,
        mean_duration_ms=100.0,
        stopped_early=True,
    )

    data = original.to_dict()
    restored = EvidenceBundle.from_dict(data)

    assert restored.trials_total == original.trials_total
    assert restored.success_rate == original.success_rate
    assert restored.stopped_early == original.stopped_early


def test_generate_config():
    """Test GenerateConfig creation."""
    config = GenerateConfig(
        spec="def add(a, b): return a + b",
        model="claude-sonnet-4-20250514",
        budget=100_000,
        adaptive=True,
        confidence_threshold=0.95,
        n=10,
    )

    assert config.type == ExperimentType.GENERATE
    assert config.spec == "def add(a, b): return a + b"
    assert config.adaptive is True
    assert config.confidence_threshold == 0.95


def test_generate_config_serialization():
    """Test GenerateConfig to_dict/from_dict."""
    original = GenerateConfig(
        spec="def foo(): pass",
        adaptive=True,
        confidence_threshold=0.99,
        n=20,
    )

    data = original.to_dict()
    assert data["type"] == "generate"
    assert data["spec"] == "def foo(): pass"

    restored = GenerateConfig.from_dict(data)
    assert restored.spec == original.spec
    assert restored.adaptive == original.adaptive


def test_parse_config():
    """Test ParseConfig creation."""
    config = ParseConfig(
        input_text="malformed json here",
        strategy="lazy_validation",
        n=100,
    )

    assert config.type == ExperimentType.PARSE
    assert config.input_text == "malformed json here"
    assert config.strategy == "lazy_validation"


def test_laws_config():
    """Test LawsConfig creation."""
    config = LawsConfig(
        target="services/tooling/base.py:Tool",
        laws=["identity", "associativity"],
        n=10,
    )

    assert config.type == ExperimentType.LAWS
    assert config.target == "services/tooling/base.py:Tool"
    assert "identity" in config.laws


def test_experiment_creation():
    """Test Experiment creation."""
    config = GenerateConfig(spec="test", n=5)

    experiment = Experiment(config=config)

    assert experiment.id.startswith("exp-")
    assert experiment.status == ExperimentStatus.PENDING
    assert len(experiment.trials) == 0
    assert experiment.evidence is None


def test_experiment_with_trials():
    """Test Experiment with trials."""
    config = GenerateConfig(spec="test", n=3)

    trials = [
        Trial(
            index=i,
            input="input",
            output="output",
            success=True,
            duration_ms=100.0,
        )
        for i in range(3)
    ]

    experiment = Experiment(
        config=config,
        status=ExperimentStatus.COMPLETED,
        trials=trials,
    )

    assert experiment.trial_count == 3


def test_experiment_duration():
    """Test experiment duration calculation."""
    config = GenerateConfig(spec="test")

    now = datetime.now(UTC)
    experiment = Experiment(
        config=config,
        started_at=now,
        completed_at=now,
    )

    # Duration should be very small (nearly instant)
    duration = experiment.duration_seconds
    assert duration is not None
    assert duration >= 0
    assert duration < 1.0  # Should be less than 1 second


def test_experiment_serialization():
    """Test Experiment to_dict/from_dict."""
    config = GenerateConfig(spec="test", n=5)

    original = Experiment(
        id="exp-test123",
        config=config,
        status=ExperimentStatus.COMPLETED,
        trials=[
            Trial(
                index=0,
                input="input",
                output="output",
                success=True,
                duration_ms=100.0,
            )
        ],
    )

    # Serialize
    data = original.to_dict()
    assert data["id"] == "exp-test123"
    assert data["status"] == "completed"

    # Deserialize
    restored = Experiment.from_dict(data)
    assert restored.id == original.id
    assert restored.status == original.status
    assert len(restored.trials) == 1


def test_config_dispatch():
    """Test that ExperimentConfig.from_dict dispatches to correct subclass."""
    # Generate config
    gen_data = {
        "type": "generate",
        "spec": "def foo(): pass",
        "adaptive": True,
        "confidence_threshold": 0.95,
        "max_trials": 100,
        "n": 10,
    }

    gen_config = ExperimentConfig.from_dict(gen_data)
    assert isinstance(gen_config, GenerateConfig)
    assert gen_config.spec == "def foo(): pass"

    # Parse config
    parse_data = {
        "type": "parse",
        "input_text": "test",
        "strategy": "lazy",
        "adaptive": False,
        "confidence_threshold": 0.95,
        "max_trials": 100,
        "n": 10,
    }

    parse_config = ExperimentConfig.from_dict(parse_data)
    assert isinstance(parse_config, ParseConfig)
    assert parse_config.input_text == "test"

    # Laws config
    laws_data = {
        "type": "laws",
        "target": "test.py:Foo",
        "laws": ["identity"],
        "adaptive": False,
        "confidence_threshold": 0.95,
        "max_trials": 100,
        "n": 10,
    }

    laws_config = ExperimentConfig.from_dict(laws_data)
    assert isinstance(laws_config, LawsConfig)
    assert laws_config.target == "test.py:Foo"


def test_experiment_type_enum():
    """Test ExperimentType enum."""
    assert ExperimentType.GENERATE.value == "generate"
    assert ExperimentType.PARSE.value == "parse"
    assert ExperimentType.LAWS.value == "laws"
    assert ExperimentType.COMPOSE.value == "compose"
    assert ExperimentType.PRINCIPLE.value == "principle"


def test_experiment_status_enum():
    """Test ExperimentStatus enum."""
    assert ExperimentStatus.PENDING.value == "pending"
    assert ExperimentStatus.RUNNING.value == "running"
    assert ExperimentStatus.COMPLETED.value == "completed"
    assert ExperimentStatus.FAILED.value == "failed"
    assert ExperimentStatus.STOPPED.value == "stopped"
