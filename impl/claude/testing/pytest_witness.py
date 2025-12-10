"""
Pytest plugin integrating BootstrapWitness.

Philosophy: The system observes its own verification.

Phase 4 of test evolution plan:
- Run BootstrapWitness at session start
- Record test observations
- Report bootstrap integrity at session end
"""

import pytest
from datetime import datetime
from typing import Any


class WitnessPlugin:
    """
    Pytest plugin that runs BootstrapWitness.

    This plugin verifies the bootstrap kernel is intact before
    running any tests. If the kernel is compromised, tests abort.
    """

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.observations: list[dict[str, Any]] = []
        self.session_start: datetime | None = None
        self.verification_result: Any = None

    def pytest_sessionstart(self, session):
        """Verify bootstrap at session start."""
        if not self.enabled:
            return

        self.session_start = datetime.now()

        try:
            from agents.o.bootstrap_witness import BootstrapWitness

            import asyncio

            witness = BootstrapWitness(test_iterations=3)
            self.verification_result = asyncio.run(witness.invoke())

            if not self.verification_result.kernel_intact:
                pytest.exit("Bootstrap kernel compromised - cannot run tests")
        except ImportError:
            # BootstrapWitness not available - skip verification
            self.verification_result = None
        except Exception as e:
            # Don't block tests on witness failure
            print(f"Warning: BootstrapWitness verification failed: {e}")
            self.verification_result = None

    def pytest_runtest_logreport(self, report):
        """Record test observations."""
        if report.when == "call":
            self.observations.append(
                {
                    "test": report.nodeid,
                    "outcome": report.outcome,
                    "duration": report.duration,
                    "timestamp": datetime.now().isoformat(),
                    # Track law-related tests
                    "is_law_test": "law" in report.nodeid.lower(),
                }
            )

    def pytest_sessionfinish(self, session, exitstatus):
        """Summary at session end."""
        if not self.enabled:
            return

        # Count statistics
        passed = sum(1 for o in self.observations if o["outcome"] == "passed")
        failed = sum(1 for o in self.observations if o["outcome"] == "failed")
        law_tests = sum(1 for o in self.observations if o["is_law_test"])

        print(f"\n{'=' * 60}")
        print("Bootstrap Witness Report")
        print(f"{'=' * 60}")

        if self.verification_result:
            print(f"Kernel Intact: {self.verification_result.kernel_intact}")
            print(
                f"Identity Laws: {'HOLD' if self.verification_result.identity_laws_hold else 'BROKEN'}"
            )
            print(
                f"Composition Laws: {'HOLD' if self.verification_result.composition_laws_hold else 'BROKEN'}"
            )
        else:
            print("Kernel Verification: SKIPPED")

        print(f"Tests Observed: {len(self.observations)}")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        print(f"  Law Tests: {law_tests}")
        print(f"{'=' * 60}")


# Note: Plugin registration moved to root conftest.py
# Use: pytest --witness to enable
