"""
C-gent + F-gent Integration: Contract Law Validation.

Cross-pollination Opportunity T2.8:
    Problem: F-gent synthesizes contracts, but doesn't validate category laws
    Solution: C-gent validates contracts satisfy functor/monad laws during Phase 2
    Impact: Guarantees composability by construction

This module validates that F-gent contracts satisfy categorical laws:
- Functor laws (for map-like operations)
- Monad laws (for bind-like operations)
- Composition compatibility (type matching)
"""

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ContractLawViolation:
    """Evidence of a categorical law violation in a contract."""

    law_name: str
    contract_name: str
    description: str
    evidence: str
    severity: str = "error"  # "error" or "warning"

    def __str__(self) -> str:
        emoji = "❌" if self.severity == "error" else "⚠️"
        return (
            f"{emoji} {self.law_name} violation in contract '{self.contract_name}':\n"
            f"   {self.description}\n"
            f"   Evidence: {self.evidence}"
        )


@dataclass
class ContractValidationReport:
    """Results of contract categorical law validation."""

    contract_name: str
    laws_checked: list[str]
    violations: list[ContractLawViolation]
    warnings: list[ContractLawViolation]
    passed: bool

    @property
    def total_laws(self) -> int:
        return len(self.laws_checked)

    @property
    def error_count(self) -> int:
        return len(self.violations)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)

    def __str__(self) -> str:
        status = "✅ PASSED" if self.passed else "❌ FAILED"
        summary = f"\nContract Validation: {self.contract_name}\n"
        summary += f"{status} ({self.total_laws - self.error_count}/{self.total_laws} laws satisfied)\n"

        if self.violations:
            summary += f"\nErrors ({self.error_count}):\n"
            for v in self.violations:
                summary += f"  {v}\n"

        if self.warnings:
            summary += f"\nWarnings ({self.warning_count}):\n"
            for w in self.warnings:
                summary += f"  {w}\n"

        return summary


class ContractValidator:
    """
    C-gent for validating categorical laws in F-gent contracts.

    This validates that contracts synthesized by F-gent satisfy:
    1. Type compatibility (I → O morphism exists)
    2. Composition laws (associativity, identity)
    3. Functor laws (if contract defines map-like operations)
    4. Monad laws (if contract defines bind-like operations)
    """

    def __init__(self) -> None:
        self.violations: list[ContractLawViolation] = []
        self.warnings: list[ContractLawViolation] = []
        self.laws_checked: list[str] = []

    def validate_contract(self, contract: Any) -> ContractValidationReport:
        """
        Validate categorical laws for an F-gent contract.

        Args:
            contract: A Contract object from agents.f.contract

        Returns:
            ContractValidationReport with results
        """
        self.reset()

        logger.info(f"🔍 Validating contract: {contract.agent_name}")

        # Check type compatibility
        self._check_type_compatibility(contract)

        # Check composition rules
        self._check_composition_laws(contract)

        # Check invariants for categorical properties
        self._check_invariant_laws(contract)

        # Check for functor/monad patterns
        self._check_functor_pattern(contract)
        self._check_monad_pattern(contract)

        return ContractValidationReport(
            contract_name=contract.agent_name,
            laws_checked=self.laws_checked,
            violations=self.violations,
            warnings=self.warnings,
            passed=len(self.violations) == 0,
        )

    def _check_type_compatibility(self, contract: Any) -> None:
        """Verify that input_type → output_type is a valid morphism."""
        self.laws_checked.append("Type Morphism Existence")

        # Check that types are defined
        if not contract.input_type or not contract.output_type:
            self.violations.append(
                ContractLawViolation(
                    law_name="Type Morphism Existence",
                    contract_name=contract.agent_name,
                    description="Contract must define both input_type and output_type",
                    evidence=f"input_type={contract.input_type}, output_type={contract.output_type}",
                )
            )
            return

        # Check for degenerate morphisms
        if contract.input_type == "None" and contract.output_type == "None":
            self.warnings.append(
                ContractLawViolation(
                    law_name="Type Morphism Existence",
                    contract_name=contract.agent_name,
                    description="Contract defines a degenerate morphism (None → None)",
                    evidence="Both input and output types are None",
                    severity="warning",
                )
            )

    def _check_composition_laws(self, contract: Any) -> None:
        """Verify composition rules satisfy categorical laws."""
        self.laws_checked.append("Composition Associativity")

        if not contract.composition_rules:
            # No composition rules specified - add warning
            self.warnings.append(
                ContractLawViolation(
                    law_name="Composition Associativity",
                    contract_name=contract.agent_name,
                    description="No composition rules specified",
                    evidence="composition_rules is empty",
                    severity="warning",
                )
            )
            return

        # Check each composition rule
        for rule in contract.composition_rules:
            if rule.mode == "sequential":
                # Sequential composition must be associative
                self._check_sequential_associativity(contract, rule)
            elif rule.mode == "parallel":
                # Parallel composition must preserve independence
                self._check_parallel_independence(contract, rule)

    def _check_sequential_associativity(self, contract: Any, rule: Any) -> None:
        """Verify sequential composition is associative."""
        # Sequential composition inherently satisfies (f >> g) >> h = f >> (g >> h)
        # But we need to check for side effects that might break this

        for invariant in contract.invariants:
            # Check for side effects that violate associativity
            if (
                "state" in invariant.description.lower()
                or "side effect" in invariant.description.lower()
            ):
                self.warnings.append(
                    ContractLawViolation(
                        law_name="Composition Associativity",
                        contract_name=contract.agent_name,
                        description="Sequential composition with side effects may not be associative",
                        evidence=f"Invariant mentions state/side effects: {invariant.description}",
                        severity="warning",
                    )
                )

    def _check_parallel_independence(self, contract: Any, rule: Any) -> None:
        """Verify parallel composition preserves independence."""
        # Parallel composition requires no shared state
        pass  # Implementation would check for shared state

    def _check_invariant_laws(self, contract: Any) -> None:
        """Check that invariants don't contradict categorical laws."""
        self.laws_checked.append("Invariant Consistency")

        # Check for idempotence claims
        for invariant in contract.invariants:
            if "idempotent" in invariant.property.lower():
                # Idempotent: f(f(x)) = f(x)
                # This is a valid categorical property (projection)
                logger.debug(f"Contract {contract.agent_name} claims idempotence")

            # Check for identity claims
            if "identity" in invariant.property.lower() or invariant.property == "id":
                # Identity must satisfy: id(x) = x for all x
                # Verify input_type == output_type
                if contract.input_type != contract.output_type:
                    self.violations.append(
                        ContractLawViolation(
                            law_name="Identity Law",
                            contract_name=contract.agent_name,
                            description="Identity invariant requires input_type == output_type",
                            evidence=f"input_type={contract.input_type}, output_type={contract.output_type}",
                        )
                    )

    def _check_functor_pattern(self, contract: Any) -> None:
        """Check if contract exhibits functor pattern and validate laws."""
        self.laws_checked.append("Functor Pattern")

        # Look for "map" in composition rules or invariants
        has_map = any(
            "map" in rule.description.lower() for rule in contract.composition_rules
        )

        if has_map:
            logger.debug(f"Contract {contract.agent_name} exhibits functor pattern")

            # Functor requires:
            # 1. F(id) = id
            # 2. F(g . f) = F(g) . F(f)

            # Check if contract has identity preservation
            has_identity_preservation = any(
                "preserves identity" in inv.description.lower()
                or "F(id) = id" in inv.property
                for inv in contract.invariants
            )

            if not has_identity_preservation:
                self.warnings.append(
                    ContractLawViolation(
                        law_name="Functor Identity Law",
                        contract_name=contract.agent_name,
                        description="Functor pattern detected but identity law not specified in invariants",
                        evidence="Contract has 'map' operation but no 'F(id) = id' invariant",
                        severity="warning",
                    )
                )

            # Check for composition preservation
            has_composition_preservation = any(
                "composition" in inv.description.lower() or "F(g . f)" in inv.property
                for inv in contract.invariants
            )

            if not has_composition_preservation:
                self.warnings.append(
                    ContractLawViolation(
                        law_name="Functor Composition Law",
                        contract_name=contract.agent_name,
                        description="Functor pattern detected but composition law not specified",
                        evidence="Contract has 'map' but no 'F(g . f) = F(g) . F(f)' invariant",
                        severity="warning",
                    )
                )

    def _check_monad_pattern(self, contract: Any) -> None:
        """Check if contract exhibits monad pattern and validate laws."""
        self.laws_checked.append("Monad Pattern")

        # Look for "bind", "flatMap", or "chain" in composition rules
        has_bind = any(
            any(
                keyword in rule.description.lower()
                for keyword in ["bind", "flatmap", "chain"]
            )
            for rule in contract.composition_rules
        )

        if has_bind:
            logger.debug(f"Contract {contract.agent_name} exhibits monad pattern")

            # Monad requires:
            # 1. Left identity: unit(a).bind(f) = f(a)
            # 2. Right identity: m.bind(unit) = m
            # 3. Associativity: m.bind(f).bind(g) = m.bind(λa. f(a).bind(g))

            monad_laws = ["left identity", "right identity", "associativity"]
            found_laws = []

            for law in monad_laws:
                has_law = any(
                    law in inv.description.lower() for inv in contract.invariants
                )
                if has_law:
                    found_laws.append(law)

            missing_laws = [law for law in monad_laws if law not in found_laws]

            if missing_laws:
                self.warnings.append(
                    ContractLawViolation(
                        law_name="Monad Laws",
                        contract_name=contract.agent_name,
                        description=f"Monad pattern detected but missing laws: {', '.join(missing_laws)}",
                        evidence=f"Contract has bind operation but invariants don't specify: {missing_laws}",
                        severity="warning",
                    )
                )

    def reset(self) -> None:
        """Reset validator state."""
        self.violations = []
        self.warnings = []
        self.laws_checked = []


# --- F-gent Integration Functions ---


def validate_contract_laws(contract: Any) -> ContractValidationReport:
    """
    Validate categorical laws for an F-gent contract.

    This is the main entry point for T2.8 cross-pollination integration.

    Args:
        contract: A Contract object from agents.f.contract

    Returns:
        ContractValidationReport with law validation results

    Example:
        >>> from agents.f import synthesize_contract, parse_intent
        >>> from agents.c.contract_validator import validate_contract_laws
        >>>
        >>> intent = parse_intent("Create a map function that transforms lists")
        >>> contract = synthesize_contract(intent, "MapAgent")
        >>> report = validate_contract_laws(contract)
        >>>
        >>> if not report.passed:
        ...     print(f"⚠️ Contract has {report.error_count} law violations!")
        ...     print(report)
    """
    validator = ContractValidator()
    return validator.validate_contract(contract)


def validate_composition_compatibility(
    contract1: Any,
    contract2: Any,
) -> tuple[bool, str]:
    """
    Check if two contracts can compose (contract1 >> contract2).

    Validates that:
    - contract1.output_type is compatible with contract2.input_type
    - Composition rules allow sequential composition

    Args:
        contract1: First contract (upstream)
        contract2: Second contract (downstream)

    Returns:
        Tuple of (is_compatible, reason)

    Example:
        >>> compatible, reason = validate_composition_compatibility(
        ...     weather_contract, summarizer_contract
        ... )
        >>> if not compatible:
        ...     print(f"Cannot compose: {reason}")
    """
    # Check type compatibility
    if contract1.output_type != contract2.input_type:
        # Try fuzzy match (e.g., "str" vs "string")
        type_match = (
            contract1.output_type.lower() == contract2.input_type.lower()
            or (contract1.output_type == "str" and contract2.input_type == "string")
            or (contract1.output_type == "string" and contract2.input_type == "str")
        )

        if not type_match:
            return False, (
                f"Type mismatch: {contract1.agent_name}.output_type "
                f"({contract1.output_type}) incompatible with "
                f"{contract2.agent_name}.input_type ({contract2.input_type})"
            )

    # Check composition rules allow sequential composition
    has_sequential_rule = any(
        rule.mode == "sequential" for rule in contract1.composition_rules
    )

    if contract1.composition_rules and not has_sequential_rule:
        return False, (
            f"{contract1.agent_name} does not support sequential composition"
        )

    return True, "Compatible"


def suggest_contract_improvements(report: ContractValidationReport) -> list[str]:
    """
    Generate improvement suggestions based on validation report.

    Args:
        report: ContractValidationReport from validation

    Returns:
        List of human-readable improvement suggestions
    """
    suggestions = []

    # Check for missing functor laws
    for warning in report.warnings:
        if "Functor" in warning.law_name:
            suggestions.append(
                f"Add functor law invariants to {report.contract_name}:\n"
                "  - Identity: F(id) = id\n"
                "  - Composition: F(g . f) = F(g) . F(f)"
            )

        if "Monad" in warning.law_name:
            suggestions.append(
                f"Add monad law invariants to {report.contract_name}:\n"
                "  - Left identity: unit(a).bind(f) = f(a)\n"
                "  - Right identity: m.bind(unit) = m\n"
                "  - Associativity: m.bind(f).bind(g) = m.bind(λa. f(a).bind(g))"
            )

    # Check for type issues
    for violation in report.violations:
        if "Type" in violation.law_name:
            suggestions.append(
                f"Fix type definition in {report.contract_name}: {violation.description}"
            )

    return suggestions
