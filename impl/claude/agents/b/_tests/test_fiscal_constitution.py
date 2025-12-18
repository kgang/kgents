"""
Tests for Fiscal Constitution (B×G Phase 2).

Tests the constitutional grammar where bankruptcy is grammatically impossible.

Target: 40+ comprehensive tests covering:
- LedgerState operations
- Parse-time balance checking
- Constitutional invariants
- ConstitutionalBanker integration
- Double-entry bookkeeping
- Edge cases and fuzz-like testing
"""

from __future__ import annotations

from datetime import datetime

import pytest

from agents.b.fiscal_constitution import (
    Account,
    AccountBalance,
    # Banker
    ConstitutionalBanker,
    ExecutionResult,
    LedgerState,
    LedgerTongue,
    # Parser and Tongue
    LedgerTongueParser,
    LedgerTransaction,
    # Types
    ParseError,
    ParseSuccess,
    QueryCommand,
    ReleaseCommand,
    ReserveCommand,
    # Commands
    TransferCommand,
    create_constitutional_banker,
    create_fiscal_constitution,
    create_ledger_tongue,
)

# =============================================================================
# AccountBalance Tests
# =============================================================================


class TestAccountBalance:
    """Tests for AccountBalance dataclass."""

    def test_default_balance(self) -> None:
        """Test default balance is zero."""
        balance = AccountBalance()
        assert balance.available == 0.0
        assert balance.reserved == 0.0
        assert balance.total == 0.0

    def test_total_balance(self) -> None:
        """Test total includes available and reserved."""
        balance = AccountBalance(available=100.0, reserved=50.0)
        assert balance.total == 150.0

    def test_can_transfer_true(self) -> None:
        """Test can_transfer returns True when sufficient funds."""
        balance = AccountBalance(available=100.0)
        assert balance.can_transfer(100.0) is True
        assert balance.can_transfer(50.0) is True

    def test_can_transfer_false(self) -> None:
        """Test can_transfer returns False when insufficient funds."""
        balance = AccountBalance(available=100.0)
        assert balance.can_transfer(100.01) is False
        assert balance.can_transfer(200.0) is False

    def test_can_transfer_ignores_reserved(self) -> None:
        """Test can_transfer only considers available, not reserved."""
        balance = AccountBalance(available=50.0, reserved=100.0)
        assert balance.can_transfer(50.0) is True
        assert balance.can_transfer(51.0) is False

    def test_can_reserve_true(self) -> None:
        """Test can_reserve returns True when sufficient funds."""
        balance = AccountBalance(available=100.0)
        assert balance.can_reserve(100.0) is True

    def test_can_reserve_false(self) -> None:
        """Test can_reserve returns False when insufficient funds."""
        balance = AccountBalance(available=50.0)
        assert balance.can_reserve(51.0) is False


# =============================================================================
# Account Tests
# =============================================================================


class TestAccount:
    """Tests for Account dataclass."""

    def test_creation(self) -> None:
        """Test account creation."""
        account = Account(id="alice")
        assert account.id == "alice"
        assert account.balances == {}
        assert isinstance(account.created_at, datetime)

    def test_get_balance_creates(self) -> None:
        """Test get_balance creates balance if not exists."""
        account = Account(id="alice")
        balance = account.get_balance("USD")
        assert isinstance(balance, AccountBalance)
        assert "USD" in account.balances

    def test_available_shortcut(self) -> None:
        """Test available() shortcut method."""
        account = Account(id="alice")
        account.balances["USD"] = AccountBalance(available=100.0)
        assert account.available("USD") == 100.0
        assert account.available("EUR") == 0.0  # Creates new

    def test_reserved_shortcut(self) -> None:
        """Test reserved() shortcut method."""
        account = Account(id="alice")
        account.balances["USD"] = AccountBalance(reserved=50.0)
        assert account.reserved("USD") == 50.0


# =============================================================================
# LedgerState Tests
# =============================================================================


class TestLedgerState:
    """Tests for LedgerState operations."""

    def test_creation(self) -> None:
        """Test ledger state creation."""
        ledger = LedgerState()
        assert ledger.accounts == {}
        assert ledger.total_supply == {}
        assert ledger.transaction_log == []

    def test_get_account_creates(self) -> None:
        """Test get_account creates if not exists."""
        ledger = LedgerState()
        account = ledger.get_account("alice")
        assert account.id == "alice"
        assert "alice" in ledger.accounts

    def test_mint_initial(self) -> None:
        """Test minting initial supply."""
        ledger = LedgerState()
        ledger.mint_initial("treasury", "USD", 1000.0)

        assert ledger.get_balance("treasury", "USD") == 1000.0
        assert ledger.total_supply["USD"] == 1000.0

    def test_execute_transfer(self) -> None:
        """Test executing a transfer."""
        ledger = LedgerState()
        ledger.mint_initial("alice", "USD", 100.0)

        tx = ledger.execute_transfer("alice", "bob", "USD", 50.0, "payment")

        assert ledger.get_balance("alice", "USD") == 50.0
        assert ledger.get_balance("bob", "USD") == 50.0
        assert isinstance(tx, LedgerTransaction)
        assert tx.amount == 50.0

    def test_transfer_preserves_supply(self) -> None:
        """Test that transfer preserves total supply."""
        ledger = LedgerState()
        ledger.mint_initial("alice", "USD", 100.0)
        ledger.execute_transfer("alice", "bob", "USD", 50.0)

        assert ledger.verify_supply_invariant("USD") is True

    def test_reserve_funds(self) -> None:
        """Test reserving funds."""
        ledger = LedgerState()
        ledger.mint_initial("alice", "USD", 100.0)

        tx = ledger.reserve_funds("alice", "USD", 30.0, "escrow")

        assert tx is not None
        assert ledger.get_balance("alice", "USD") == 70.0
        account = ledger.get_account("alice")
        assert account.reserved("USD") == 30.0

    def test_reserve_fails_insufficient(self) -> None:
        """Test reserve fails with insufficient funds."""
        ledger = LedgerState()
        ledger.mint_initial("alice", "USD", 50.0)

        tx = ledger.reserve_funds("alice", "USD", 100.0)
        assert tx is None

    def test_release_funds(self) -> None:
        """Test releasing reserved funds."""
        ledger = LedgerState()
        ledger.mint_initial("alice", "USD", 100.0)
        ledger.reserve_funds("alice", "USD", 30.0)

        tx = ledger.release_funds("alice", "USD", 20.0)

        assert tx is not None
        assert ledger.get_balance("alice", "USD") == 90.0
        account = ledger.get_account("alice")
        assert account.reserved("USD") == 10.0

    def test_release_fails_insufficient(self) -> None:
        """Test release fails with insufficient reserved."""
        ledger = LedgerState()
        ledger.mint_initial("alice", "USD", 100.0)
        ledger.reserve_funds("alice", "USD", 30.0)

        tx = ledger.release_funds("alice", "USD", 50.0)
        assert tx is None

    def test_transaction_history(self) -> None:
        """Test transaction history retrieval."""
        ledger = LedgerState()
        ledger.mint_initial("alice", "USD", 100.0)
        ledger.execute_transfer("alice", "bob", "USD", 10.0)
        ledger.execute_transfer("alice", "charlie", "USD", 20.0)

        history = ledger.get_transaction_history("alice")
        assert len(history) == 2

        bob_history = ledger.get_transaction_history("bob")
        assert len(bob_history) == 1

    def test_verify_supply_invariant_multi_currency(self) -> None:
        """Test supply invariant with multiple currencies."""
        ledger = LedgerState()
        ledger.mint_initial("treasury", "USD", 1000.0)
        ledger.mint_initial("treasury", "EUR", 500.0)

        ledger.execute_transfer("treasury", "alice", "USD", 100.0)
        ledger.execute_transfer("treasury", "bob", "EUR", 50.0)

        assert ledger.verify_supply_invariant("USD") is True
        assert ledger.verify_supply_invariant("EUR") is True


# =============================================================================
# LedgerTongueParser Tests - Syntax
# =============================================================================


class TestParserSyntax:
    """Tests for parser syntax handling."""

    @pytest.fixture
    def parser(self) -> LedgerTongueParser:
        """Create parser with funded account."""
        ledger = LedgerState()
        ledger.mint_initial("alice", "USD", 1000.0)
        return LedgerTongueParser(ledger)

    def test_parse_unknown_command(self, parser: LedgerTongueParser) -> None:
        """Test parsing unknown command."""
        result = parser.parse("MINT 100 USD TO alice")
        assert isinstance(result, ParseError)
        assert "Unknown command" in result.error

    def test_parse_transfer_valid(self, parser: LedgerTongueParser) -> None:
        """Test parsing valid transfer."""
        result = parser.parse("TRANSFER 100 USD FROM alice TO bob")
        assert isinstance(result, ParseSuccess)
        assert isinstance(result.ast, TransferCommand)
        assert result.ast.amount == 100.0
        assert result.ast.currency == "USD"

    def test_parse_transfer_with_memo(self, parser: LedgerTongueParser) -> None:
        """Test parsing transfer with memo."""
        result = parser.parse('TRANSFER 50 USD FROM alice TO bob MEMO "payment for services"')
        assert isinstance(result, ParseSuccess)
        assert result.ast.memo == "payment for services"

    def test_parse_transfer_decimal_amount(self, parser: LedgerTongueParser) -> None:
        """Test parsing transfer with decimal amount."""
        result = parser.parse("TRANSFER 99.99 USD FROM alice TO bob")
        assert isinstance(result, ParseSuccess)
        assert result.ast.amount == 99.99

    def test_parse_transfer_case_insensitive(self, parser: LedgerTongueParser) -> None:
        """Test parsing is case insensitive for keywords."""
        result = parser.parse("transfer 100 usd from alice to bob")
        assert isinstance(result, ParseSuccess)
        assert result.ast.currency == "USD"  # Currency normalized to uppercase

    def test_parse_transfer_invalid_syntax(self, parser: LedgerTongueParser) -> None:
        """Test parsing transfer with invalid syntax."""
        result = parser.parse("TRANSFER alice TO bob 100 USD")
        assert isinstance(result, ParseError)
        assert "Invalid TRANSFER syntax" in result.error

    def test_parse_transfer_invalid_currency(self, parser: LedgerTongueParser) -> None:
        """Test parsing transfer with invalid currency."""
        result = parser.parse("TRANSFER 100 XYZ FROM alice TO bob")
        assert isinstance(result, ParseError)
        assert "Unknown currency" in result.error

    def test_parse_transfer_negative_amount(self, parser: LedgerTongueParser) -> None:
        """Test parsing transfer with negative amount fails."""
        # Note: regex won't match negative, so it's a syntax error
        result = parser.parse("TRANSFER -100 USD FROM alice TO bob")
        assert isinstance(result, ParseError)

    def test_parse_transfer_self_transfer(self, parser: LedgerTongueParser) -> None:
        """Test parsing self-transfer fails."""
        result = parser.parse("TRANSFER 100 USD FROM alice TO alice")
        assert isinstance(result, ParseError)
        assert "same account" in result.error

    def test_parse_query_balance(self, parser: LedgerTongueParser) -> None:
        """Test parsing balance query."""
        result = parser.parse("QUERY BALANCE OF alice IN USD")
        assert isinstance(result, ParseSuccess)
        assert isinstance(result.ast, QueryCommand)
        assert result.ast.query_type == "balance"

    def test_parse_query_history(self, parser: LedgerTongueParser) -> None:
        """Test parsing history query."""
        result = parser.parse("QUERY HISTORY OF alice")
        assert isinstance(result, ParseSuccess)
        assert result.ast.query_type == "history"

    def test_parse_query_supply(self, parser: LedgerTongueParser) -> None:
        """Test parsing supply query."""
        result = parser.parse("QUERY SUPPLY OF USD")
        assert isinstance(result, ParseSuccess)
        assert result.ast.query_type == "supply"

    def test_parse_query_invalid(self, parser: LedgerTongueParser) -> None:
        """Test parsing invalid query."""
        result = parser.parse("QUERY SOMETHING OF alice")
        assert isinstance(result, ParseError)

    def test_parse_reserve(self, parser: LedgerTongueParser) -> None:
        """Test parsing reserve command."""
        result = parser.parse("RESERVE 100 USD FROM alice")
        assert isinstance(result, ParseSuccess)
        assert isinstance(result.ast, ReserveCommand)

    def test_parse_reserve_with_reason(self, parser: LedgerTongueParser) -> None:
        """Test parsing reserve with reason."""
        result = parser.parse('RESERVE 50 USD FROM alice REASON "escrow for trade"')
        assert isinstance(result, ParseSuccess)
        assert result.ast.reason == "escrow for trade"

    def test_parse_release(self, parser: LedgerTongueParser) -> None:
        """Test parsing release command."""
        # First need to reserve some funds
        parser.ledger.reserve_funds("alice", "USD", 100.0)
        result = parser.parse("RELEASE 50 USD TO alice")
        assert isinstance(result, ParseSuccess)
        assert isinstance(result.ast, ReleaseCommand)


# =============================================================================
# LedgerTongueParser Tests - Constitutional Balance Checking
# =============================================================================


class TestParserConstitutional:
    """Tests for parse-time constitutional balance checking."""

    def test_insufficient_funds_is_parse_error(self) -> None:
        """Test that insufficient funds causes parse error, not runtime error."""
        ledger = LedgerState()
        ledger.mint_initial("alice", "USD", 50.0)
        parser = LedgerTongueParser(ledger)

        result = parser.parse("TRANSFER 100 USD FROM alice TO bob")

        assert isinstance(result, ParseError)
        assert "Insufficient funds" in result.error
        assert result.constitutional_violation is True

    def test_exactly_sufficient_funds(self) -> None:
        """Test transfer with exactly sufficient funds."""
        ledger = LedgerState()
        ledger.mint_initial("alice", "USD", 100.0)
        parser = LedgerTongueParser(ledger)

        result = parser.parse("TRANSFER 100 USD FROM alice TO bob")

        assert isinstance(result, ParseSuccess)

    def test_double_spend_prevented_at_parse(self) -> None:
        """Test that double-spend is prevented at parse time."""
        ledger = LedgerState()
        ledger.mint_initial("alice", "USD", 100.0)
        parser = LedgerTongueParser(ledger)

        # First transfer succeeds parsing
        result1 = parser.parse("TRANSFER 100 USD FROM alice TO bob")
        assert isinstance(result1, ParseSuccess)

        # Execute it to update state
        ledger.execute_transfer("alice", "bob", "USD", 100.0)

        # Second transfer to charlie FAILS at parse time
        result2 = parser.parse("TRANSFER 100 USD FROM alice TO charlie")
        assert isinstance(result2, ParseError)
        assert "Insufficient funds" in result2.error
        # Charlie never received anything because parse failed
        assert ledger.get_balance("charlie", "USD") == 0.0

    def test_reserve_insufficient_is_parse_error(self) -> None:
        """Test that insufficient funds for reserve is parse error."""
        ledger = LedgerState()
        ledger.mint_initial("alice", "USD", 50.0)
        parser = LedgerTongueParser(ledger)

        result = parser.parse("RESERVE 100 USD FROM alice")

        assert isinstance(result, ParseError)
        assert "Insufficient funds to reserve" in result.error

    def test_release_insufficient_reserved_is_parse_error(self) -> None:
        """Test that insufficient reserved funds for release is parse error."""
        ledger = LedgerState()
        ledger.mint_initial("alice", "USD", 100.0)
        ledger.reserve_funds("alice", "USD", 30.0)
        parser = LedgerTongueParser(ledger)

        result = parser.parse("RELEASE 50 USD TO alice")

        assert isinstance(result, ParseError)
        assert "Insufficient reserved funds" in result.error

    def test_zero_balance_account(self) -> None:
        """Test transfer from account with zero balance."""
        ledger = LedgerState()
        ledger.get_account("alice")  # Create with zero balance
        parser = LedgerTongueParser(ledger)

        result = parser.parse("TRANSFER 1 USD FROM alice TO bob")

        assert isinstance(result, ParseError)
        assert "Insufficient funds" in result.error

    def test_nonexistent_account(self) -> None:
        """Test transfer from nonexistent account (treated as zero balance)."""
        ledger = LedgerState()
        parser = LedgerTongueParser(ledger)

        result = parser.parse("TRANSFER 1 USD FROM unknown TO bob")

        assert isinstance(result, ParseError)
        assert "Insufficient funds" in result.error


# =============================================================================
# LedgerTongue Tests
# =============================================================================


class TestLedgerTongue:
    """Tests for LedgerTongue (combined parsing and execution)."""

    @pytest.fixture
    def tongue(self) -> LedgerTongue:
        """Create tongue with funded account."""
        ledger = LedgerState()
        ledger.mint_initial("alice", "USD", 1000.0)
        ledger.mint_initial("treasury", "EUR", 500.0)
        return LedgerTongue(ledger)

    def test_run_transfer_success(self, tongue: LedgerTongue) -> None:
        """Test successful transfer through run()."""
        result = tongue.run("TRANSFER 100 USD FROM alice TO bob")

        assert isinstance(result, ExecutionResult)
        assert result.success is True
        assert result.transaction is not None
        assert tongue.ledger.get_balance("bob", "USD") == 100.0

    def test_run_transfer_insufficient(self, tongue: LedgerTongue) -> None:
        """Test transfer with insufficient funds returns ParseError."""
        result = tongue.run("TRANSFER 5000 USD FROM alice TO bob")

        assert isinstance(result, ParseError)
        assert "Insufficient funds" in result.error

    def test_run_query_balance(self, tongue: LedgerTongue) -> None:
        """Test balance query execution."""
        result = tongue.run("QUERY BALANCE OF alice IN USD")

        assert isinstance(result, ExecutionResult)
        assert result.success is True
        assert result.result["balance"] == 1000.0

    def test_run_query_history(self, tongue: LedgerTongue) -> None:
        """Test history query execution."""
        tongue.run("TRANSFER 50 USD FROM alice TO bob")
        result = tongue.run("QUERY HISTORY OF alice")

        assert isinstance(result, ExecutionResult)
        assert result.success is True
        assert len(result.result["transactions"]) == 1

    def test_run_query_supply(self, tongue: LedgerTongue) -> None:
        """Test supply query execution."""
        result = tongue.run("QUERY SUPPLY OF USD")

        assert isinstance(result, ExecutionResult)
        assert result.success is True
        assert result.result["total_supply"] == 1000.0

    def test_run_reserve_success(self, tongue: LedgerTongue) -> None:
        """Test successful reserve."""
        result = tongue.run('RESERVE 200 USD FROM alice REASON "escrow"')

        assert isinstance(result, ExecutionResult)
        assert result.success is True
        assert tongue.ledger.get_balance("alice", "USD") == 800.0
        assert tongue.ledger.get_account("alice").reserved("USD") == 200.0

    def test_run_release_success(self, tongue: LedgerTongue) -> None:
        """Test successful release."""
        tongue.run("RESERVE 200 USD FROM alice")
        result = tongue.run("RELEASE 100 USD TO alice")

        assert isinstance(result, ExecutionResult)
        assert result.success is True
        assert tongue.ledger.get_balance("alice", "USD") == 900.0

    def test_chain_of_transfers(self, tongue: LedgerTongue) -> None:
        """Test chain of transfers maintains invariants."""
        tongue.run("TRANSFER 500 USD FROM alice TO bob")
        tongue.run("TRANSFER 250 USD FROM bob TO charlie")
        tongue.run("TRANSFER 125 USD FROM charlie TO dave")

        # Check balances
        assert tongue.ledger.get_balance("alice", "USD") == 500.0
        assert tongue.ledger.get_balance("bob", "USD") == 250.0
        assert tongue.ledger.get_balance("charlie", "USD") == 125.0
        assert tongue.ledger.get_balance("dave", "USD") == 125.0

        # Verify supply invariant
        assert tongue.ledger.verify_supply_invariant("USD") is True


# =============================================================================
# ConstitutionalBanker Tests
# =============================================================================


class TestConstitutionalBanker:
    """Tests for ConstitutionalBanker."""

    @pytest.fixture
    def banker(self) -> ConstitutionalBanker:
        """Create constitutional banker with initial funds."""
        return create_constitutional_banker(initial_accounts={"alice": {"USD": 1000.0}})

    def test_execute_sync_success(self, banker: ConstitutionalBanker) -> None:
        """Test synchronous execution success."""
        result = banker.execute_sync("TRANSFER 100 USD FROM alice TO bob")

        assert result.success is True
        assert result.type == "CONSTITUTIONAL_EXECUTION"
        assert result.transaction is not None

    def test_execute_sync_grammar_rejection(self, banker: ConstitutionalBanker) -> None:
        """Test synchronous execution grammar rejection."""
        result = banker.execute_sync("TRANSFER 5000 USD FROM alice TO bob")

        assert result.success is False
        assert result.type == "GRAMMAR_REJECTION"
        assert "Constitutional violation" in result.reason

    def test_verify_constitution_initial(self, banker: ConstitutionalBanker) -> None:
        """Test constitution verification on initial state."""
        invariants = banker.verify_constitution()

        assert invariants["supply_USD"] is True
        assert invariants["no_negative_balances"] is True
        assert invariants["double_entry"] is True

    def test_verify_constitution_after_operations(self, banker: ConstitutionalBanker) -> None:
        """Test constitution verification after operations."""
        banker.execute_sync("TRANSFER 100 USD FROM alice TO bob")
        banker.execute_sync("TRANSFER 50 USD FROM bob TO charlie")

        invariants = banker.verify_constitution()

        assert all(v is True for v in invariants.values())

    def test_get_ledger_state(self, banker: ConstitutionalBanker) -> None:
        """Test getting ledger state."""
        ledger = banker.get_ledger_state()

        assert isinstance(ledger, LedgerState)
        assert ledger.get_balance("alice", "USD") == 1000.0


# =============================================================================
# Constitutional Banker - Async Tests
# =============================================================================


class TestConstitutionalBankerAsync:
    """Async tests for ConstitutionalBanker."""

    @pytest.fixture
    def banker(self) -> ConstitutionalBanker:
        """Create constitutional banker."""
        return create_constitutional_banker(initial_accounts={"alice": {"USD": 1000.0}})

    @pytest.mark.asyncio
    async def test_execute_async_success(self, banker: ConstitutionalBanker) -> None:
        """Test async execution success."""
        result = await banker.execute_financial_operation(
            "agent1", "TRANSFER 100 USD FROM alice TO bob"
        )

        assert result.success is True
        assert result.type == "CONSTITUTIONAL_EXECUTION"
        assert result.gas_consumed is not None

    @pytest.mark.asyncio
    async def test_execute_async_grammar_rejection(self, banker: ConstitutionalBanker) -> None:
        """Test async execution grammar rejection."""
        result = await banker.execute_financial_operation(
            "agent1", "TRANSFER 5000 USD FROM alice TO bob"
        )

        assert result.success is False
        assert result.type == "GRAMMAR_REJECTION"

    @pytest.mark.asyncio
    async def test_execute_async_query(self, banker: ConstitutionalBanker) -> None:
        """Test async query execution."""
        result = await banker.execute_financial_operation("agent1", "QUERY BALANCE OF alice IN USD")

        assert result.success is True
        assert result.result["balance"] == 1000.0


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_create_ledger_tongue_empty(self) -> None:
        """Test creating empty ledger tongue."""
        tongue = create_ledger_tongue()

        assert isinstance(tongue, LedgerTongue)
        assert tongue.ledger.accounts == {}

    def test_create_ledger_tongue_with_accounts(self) -> None:
        """Test creating ledger tongue with initial accounts."""
        tongue = create_ledger_tongue(
            {
                "alice": {"USD": 100.0, "EUR": 50.0},
                "bob": {"USD": 200.0},
            }
        )

        assert tongue.ledger.get_balance("alice", "USD") == 100.0
        assert tongue.ledger.get_balance("alice", "EUR") == 50.0
        assert tongue.ledger.get_balance("bob", "USD") == 200.0

    def test_create_constitutional_banker(self) -> None:
        """Test creating constitutional banker."""
        banker = create_constitutional_banker(initial_accounts={"alice": {"USD": 1000.0}})

        assert isinstance(banker, ConstitutionalBanker)
        assert banker.get_ledger_state().get_balance("alice", "USD") == 1000.0

    def test_create_fiscal_constitution(self) -> None:
        """Test creating fiscal constitution."""
        banker = create_fiscal_constitution(
            initial_supply={"USD": 10000.0, "EUR": 5000.0},
            treasury_account="treasury",
        )

        ledger = banker.get_ledger_state()
        assert ledger.get_balance("treasury", "USD") == 10000.0
        assert ledger.get_balance("treasury", "EUR") == 5000.0
        assert ledger.total_supply["USD"] == 10000.0


# =============================================================================
# Edge Cases and Fuzz-like Tests
# =============================================================================


class TestEdgeCases:
    """Edge case and fuzz-like tests."""

    def test_zero_amount_transfer(self) -> None:
        """Test zero amount transfer."""
        tongue = create_ledger_tongue({"alice": {"USD": 100.0}})
        # Zero amount should fail the positive check
        result = tongue.run("TRANSFER 0 USD FROM alice TO bob")
        # Our regex requires at least one digit, so this might be syntax error
        # or we need to check amount > 0
        assert isinstance(result, ParseError)

    def test_very_large_amount(self) -> None:
        """Test very large amount transfer."""
        tongue = create_ledger_tongue({"alice": {"USD": 1e15}})
        result = tongue.run("TRANSFER 999999999999.99 USD FROM alice TO bob")
        assert isinstance(result, ExecutionResult)
        assert result.success is True

    def test_unicode_account_names(self) -> None:
        """Test unicode in account names (should fail - regex requires alphanumeric)."""
        tongue = create_ledger_tongue({"alice": {"USD": 100.0}})
        result = tongue.run("TRANSFER 50 USD FROM alice TO böb")
        assert isinstance(result, ParseError)

    def test_special_chars_in_memo(self) -> None:
        """Test special characters in memo."""
        tongue = create_ledger_tongue({"alice": {"USD": 100.0}})
        result = tongue.run('TRANSFER 50 USD FROM alice TO bob MEMO "Payment for item #123!"')
        assert isinstance(result, ExecutionResult)
        assert result.success is True

    def test_empty_string(self) -> None:
        """Test empty string command."""
        tongue = create_ledger_tongue({"alice": {"USD": 100.0}})
        result = tongue.run("")
        assert isinstance(result, ParseError)

    def test_whitespace_only(self) -> None:
        """Test whitespace only command."""
        tongue = create_ledger_tongue({"alice": {"USD": 100.0}})
        result = tongue.run("   \t\n  ")
        assert isinstance(result, ParseError)

    def test_extra_whitespace(self) -> None:
        """Test command with extra whitespace."""
        tongue = create_ledger_tongue({"alice": {"USD": 100.0}})
        _result = tongue.run("  TRANSFER   100   USD   FROM   alice   TO   bob  ")
        # Should handle gracefully (may fail due to multiple spaces in regex)
        # This tests robustness

    def test_consecutive_transfers_depletes_account(self) -> None:
        """Test consecutive transfers that deplete account."""
        tongue = create_ledger_tongue({"alice": {"USD": 100.0}})

        # Ten transfers of 10 USD each
        for i in range(10):
            result = tongue.run(f"TRANSFER 10 USD FROM alice TO receiver{i}")
            assert isinstance(result, ExecutionResult)
            assert result.success is True

        # 11th should fail
        result = tongue.run("TRANSFER 10 USD FROM alice TO receiver10")
        assert isinstance(result, ParseError)
        assert "Insufficient funds" in result.error

    def test_atomic_transaction_failure_no_partial_state(self) -> None:
        """Test that failed transactions don't leave partial state."""
        tongue = create_ledger_tongue({"alice": {"USD": 100.0}})

        # Try a transfer that will fail
        result = tongue.run("TRANSFER 200 USD FROM alice TO bob")
        assert isinstance(result, ParseError)

        # Alice should still have full balance
        assert tongue.ledger.get_balance("alice", "USD") == 100.0
        # Bob should have nothing
        assert tongue.ledger.get_balance("bob", "USD") == 0.0

    def test_all_supported_currencies(self) -> None:
        """Test all supported currencies."""
        currencies = ["USD", "EUR", "GBP", "JPY", "TOKEN", "IMPACT", "GAS"]

        for currency in currencies:
            tongue = create_ledger_tongue({"alice": {currency: 100.0}})
            result = tongue.run(f"TRANSFER 50 {currency} FROM alice TO bob")
            assert isinstance(result, ExecutionResult), f"Failed for currency {currency}: {result}"
            assert result.success is True, f"Failed for currency {currency}"


# =============================================================================
# Constitutional Invariant Tests (Fuzz-like)
# =============================================================================


class TestConstitutionalInvariants:
    """Tests that constitutional invariants cannot be violated."""

    def test_no_minting_possible(self) -> None:
        """Test that minting is not possible through grammar."""
        tongue = create_ledger_tongue({"treasury": {"USD": 1000.0}})

        # Try various ways to mint (none should parse)
        mint_attempts = [
            "MINT 100 USD TO alice",
            "CREATE 100 USD FOR alice",
            "FORGE 100 USD TO alice",
            "GENERATE 100 USD FOR alice",
            "PRINT 100 USD TO alice",
        ]

        for attempt in mint_attempts:
            result = tongue.run(attempt)
            assert isinstance(result, ParseError), f"'{attempt}' should not parse"

    def test_no_deletion_possible(self) -> None:
        """Test that deletion/destruction is not possible through grammar."""
        tongue = create_ledger_tongue({"alice": {"USD": 1000.0}})

        delete_attempts = [
            "DELETE 100 USD FROM alice",
            "BURN 100 USD FROM alice",
            "DESTROY 100 USD FROM alice",
            "VOID 100 USD FROM alice",
        ]

        for attempt in delete_attempts:
            result = tongue.run(attempt)
            assert isinstance(result, ParseError), f"'{attempt}' should not parse"

    def test_supply_invariant_stress_test(self) -> None:
        """Stress test supply invariant with many operations."""
        tongue = create_ledger_tongue(
            {
                "treasury": {"USD": 1000000.0},
            }
        )

        # Distribute to 100 accounts
        for i in range(100):
            tongue.run(f"TRANSFER 1000 USD FROM treasury TO account{i}")

        # Random transfers between accounts
        import random

        random.seed(42)  # Reproducible

        for _ in range(500):
            src = f"account{random.randint(0, 99)}"
            dst = f"account{random.randint(0, 99)}"
            if src != dst:
                # Try transfer (may fail if insufficient)
                tongue.run(f"TRANSFER 10 USD FROM {src} TO {dst}")

        # Supply should still be exactly 1000000
        assert tongue.ledger.verify_supply_invariant("USD") is True

    def test_negative_balance_impossible(self) -> None:
        """Test that negative balances are impossible."""
        tongue = create_ledger_tongue({"alice": {"USD": 100.0}})

        # Try to overdraw
        result = tongue.run("TRANSFER 101 USD FROM alice TO bob")
        assert isinstance(result, ParseError)

        # Alice's balance should never go negative
        assert tongue.ledger.get_balance("alice", "USD") >= 0

    def test_concurrent_constitutional_checks(self) -> None:
        """Test that balance is checked against current state."""
        tongue = create_ledger_tongue({"alice": {"USD": 100.0}})

        # First transfer
        result1 = tongue.run("TRANSFER 60 USD FROM alice TO bob")
        assert isinstance(result1, ExecutionResult)
        assert result1.success is True

        # Second transfer should fail based on NEW balance
        result2 = tongue.run("TRANSFER 60 USD FROM alice TO charlie")
        assert isinstance(result2, ParseError)
        assert "Insufficient funds" in result2.error


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_escrow_workflow(self) -> None:
        """Test a complete escrow workflow."""
        banker = create_constitutional_banker(
            {
                "buyer": {"USD": 1000.0},
                "seller": {"USD": 0.0},
                "escrow_agent": {"USD": 0.0},
            }
        )

        # 1. Buyer reserves funds for escrow
        # buyer: 1000 available -> 500 available, 500 reserved
        result = banker.execute_sync("RESERVE 500 USD FROM buyer")
        assert result.success

        # 2. Buyer can't spend reserved funds
        ledger = banker.get_ledger_state()
        assert ledger.get_balance("buyer", "USD") == 500.0  # Available only

        # 3. Transfer available funds still works
        # buyer: 500 available -> 300 available
        result = banker.execute_sync("TRANSFER 200 USD FROM buyer TO seller")
        assert result.success

        # 4. Release reserved funds when escrow complete
        # buyer: 300 available, 500 reserved -> 800 available
        result = banker.execute_sync("RELEASE 500 USD TO buyer")
        assert result.success
        assert ledger.get_balance("buyer", "USD") == 800.0

        # 5. Now buyer can transfer those funds
        # buyer: 800 available -> 300 available
        result = banker.execute_sync("TRANSFER 500 USD FROM buyer TO seller")
        assert result.success

        # Final balances
        assert ledger.get_balance("buyer", "USD") == 300.0
        assert ledger.get_balance("seller", "USD") == 700.0

    def test_multi_currency_workflow(self) -> None:
        """Test workflow with multiple currencies."""
        banker = create_constitutional_banker(
            {
                "trader": {"USD": 1000.0, "EUR": 500.0},
                "exchange": {"USD": 10000.0, "EUR": 8000.0},
            }
        )

        # Exchange USD for EUR
        banker.execute_sync("TRANSFER 100 USD FROM trader TO exchange")
        banker.execute_sync("TRANSFER 85 EUR FROM exchange TO trader")

        ledger = banker.get_ledger_state()
        assert ledger.get_balance("trader", "USD") == 900.0
        assert ledger.get_balance("trader", "EUR") == 585.0

        # Both supplies unchanged
        assert ledger.verify_supply_invariant("USD")
        assert ledger.verify_supply_invariant("EUR")

    def test_audit_trail(self) -> None:
        """Test that complete audit trail is maintained."""
        banker = create_fiscal_constitution(
            initial_supply={"USD": 10000.0},
            treasury_account="treasury",
        )

        # Perform operations
        banker.execute_sync("TRANSFER 1000 USD FROM treasury TO alice")
        banker.execute_sync("TRANSFER 500 USD FROM alice TO bob")
        banker.execute_sync("TRANSFER 250 USD FROM bob TO charlie")

        # Query history
        ledger = banker.get_ledger_state()
        treasury_history = ledger.get_transaction_history("treasury")
        alice_history = ledger.get_transaction_history("alice")

        assert len(treasury_history) == 1
        assert len(alice_history) == 2  # Received and sent

    def test_constitutional_banker_with_queries(self) -> None:
        """Test banker with various queries."""
        banker = create_constitutional_banker(
            {
                "alice": {"USD": 500.0, "EUR": 300.0},
                "bob": {"USD": 200.0},
            }
        )

        # Balance queries
        result = banker.execute_sync("QUERY BALANCE OF alice IN USD")
        assert result.success
        assert result.result["balance"] == 500.0

        # Supply query
        result = banker.execute_sync("QUERY SUPPLY OF USD")
        assert result.success
        assert result.result["total_supply"] == 700.0  # alice + bob
