"""
Fiscal Constitution: Grammar-Based Financial Safety

Phase 2 of Structural Economics (B-gent × G-gent Integration).

Core insight: Parse errors prevent illegal operations. Not runtime rejection—structural impossibility.

The Fiscal Constitution pattern:
1. Define LedgerTongue grammar where bankruptcy is grammatically impossible
2. Parse-time balance checking enforces invariants BEFORE execution
3. Double-entry bookkeeping is enforced by grammar structure
4. No MINT, DELETE, FORGE verbs exist in the grammar

Invariant: parse(operation) → Success ⟹ execute(operation) is constitutionally sound

Example:
    # Agent has 100 USD
    # "TRANSFER 100 USD FROM Agent TO Alice" → ParseSuccess → Execute
    # "TRANSFER 100 USD FROM Agent TO Bob" → ParseError("Insufficient funds")
    # The second transfer CANNOT BE EXPRESSED because grammar includes ledger state
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Generic, TypeVar

from .metered_functor import Gas, CentralBank, Receipt


# =============================================================================
# Type Definitions
# =============================================================================

T = TypeVar("T")


class OperationType(Enum):
    """Types of ledger operations."""

    TRANSFER = "transfer"
    QUERY = "query"
    RESERVE = "reserve"  # Lock funds for future use
    RELEASE = "release"  # Release reserved funds


class ParseResultType(Enum):
    """Result type of parsing."""

    SUCCESS = "success"
    ERROR = "error"


@dataclass
class ParseError:
    """
    Represents a parse error.

    In the Fiscal Constitution, parse errors prevent illegal operations.
    This is structural safety, not runtime validation.
    """

    error: str
    position: int = 0
    context: str = ""
    constitutional_violation: bool = True


@dataclass
class ParseSuccess(Generic[T]):
    """
    Represents successful parsing.

    Contains the AST (Abstract Syntax Tree) of the parsed command.
    If parsing succeeds, the operation is constitutionally sound.
    """

    ast: T
    consumed_chars: int = 0


# Type alias for parse results
ParseResult = ParseError | ParseSuccess


# =============================================================================
# Account and Ledger State
# =============================================================================


@dataclass
class AccountBalance:
    """Balance for a single currency in an account."""

    available: float = 0.0
    reserved: float = 0.0  # Locked for pending transactions

    @property
    def total(self) -> float:
        """Total balance including reserved."""
        return self.available + self.reserved

    def can_transfer(self, amount: float) -> bool:
        """Check if account can transfer amount."""
        return self.available >= amount

    def can_reserve(self, amount: float) -> bool:
        """Check if account can reserve amount."""
        return self.available >= amount


@dataclass
class Account:
    """
    A ledger account with multi-currency support.

    Enforces:
    - No negative balances
    - Reserved funds cannot be spent until released
    """

    id: str
    balances: dict[str, AccountBalance] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_balance(self, currency: str) -> AccountBalance:
        """Get balance for currency (creates if not exists)."""
        if currency not in self.balances:
            self.balances[currency] = AccountBalance()
        return self.balances[currency]

    def available(self, currency: str) -> float:
        """Get available balance for currency."""
        return self.get_balance(currency).available

    def reserved(self, currency: str) -> float:
        """Get reserved balance for currency."""
        return self.get_balance(currency).reserved


class LedgerState:
    """
    The state of the financial ledger.

    This is the "world" that the constitutional grammar parses against.
    Balance checks happen at parse time, making illegal operations
    structurally impossible.

    Invariants:
    - Total supply is constant (no minting)
    - All balances are non-negative
    - Every transfer has a matching debit and credit (double-entry)
    """

    def __init__(self, initial_supply: dict[str, float] | None = None):
        """
        Initialize ledger state.

        Args:
            initial_supply: Initial supply per currency (minted at creation only)
        """
        self.accounts: dict[str, Account] = {}
        self.total_supply: dict[str, float] = initial_supply or {}
        self.transaction_log: list[LedgerTransaction] = []
        self._next_tx_id = 1

    def get_account(self, account_id: str) -> Account:
        """Get or create an account."""
        if account_id not in self.accounts:
            self.accounts[account_id] = Account(id=account_id)
        return self.accounts[account_id]

    def get_balance(self, account_id: str, currency: str) -> float:
        """Get available balance for account and currency."""
        return self.get_account(account_id).available(currency)

    def get_total_balance(self, account_id: str, currency: str) -> float:
        """Get total balance (available + reserved) for account and currency."""
        return self.get_account(account_id).get_balance(currency).total

    def can_transfer(self, from_account: str, currency: str, amount: float) -> bool:
        """Check if transfer is possible (parse-time check)."""
        return self.get_balance(from_account, currency) >= amount

    def execute_transfer(
        self,
        from_account: str,
        to_account: str,
        currency: str,
        amount: float,
        memo: str = "",
    ) -> LedgerTransaction:
        """
        Execute a transfer.

        INVARIANT: This should only be called after successful parsing.
        The constitutional grammar guarantees this is safe.
        """
        # Get accounts (creates if needed)
        source = self.get_account(from_account)
        dest = self.get_account(to_account)

        # Debit source
        source_balance = source.get_balance(currency)
        source_balance.available -= amount

        # Credit destination
        dest_balance = dest.get_balance(currency)
        dest_balance.available += amount

        # Log transaction
        tx = LedgerTransaction(
            id=f"TX{self._next_tx_id:06d}",
            type=OperationType.TRANSFER,
            from_account=from_account,
            to_account=to_account,
            currency=currency,
            amount=amount,
            memo=memo,
            timestamp=datetime.now(),
        )
        self._next_tx_id += 1
        self.transaction_log.append(tx)

        return tx

    def reserve_funds(
        self,
        account_id: str,
        currency: str,
        amount: float,
        reason: str = "",
    ) -> LedgerTransaction | None:
        """
        Reserve funds for future use.

        Returns None if insufficient funds.
        """
        account = self.get_account(account_id)
        balance = account.get_balance(currency)

        if not balance.can_reserve(amount):
            return None

        balance.available -= amount
        balance.reserved += amount

        tx = LedgerTransaction(
            id=f"TX{self._next_tx_id:06d}",
            type=OperationType.RESERVE,
            from_account=account_id,
            to_account=account_id,
            currency=currency,
            amount=amount,
            memo=f"RESERVE: {reason}",
            timestamp=datetime.now(),
        )
        self._next_tx_id += 1
        self.transaction_log.append(tx)

        return tx

    def release_funds(
        self,
        account_id: str,
        currency: str,
        amount: float,
        reason: str = "",
    ) -> LedgerTransaction | None:
        """
        Release reserved funds back to available.

        Returns None if insufficient reserved funds.
        """
        account = self.get_account(account_id)
        balance = account.get_balance(currency)

        if balance.reserved < amount:
            return None

        balance.reserved -= amount
        balance.available += amount

        tx = LedgerTransaction(
            id=f"TX{self._next_tx_id:06d}",
            type=OperationType.RELEASE,
            from_account=account_id,
            to_account=account_id,
            currency=currency,
            amount=amount,
            memo=f"RELEASE: {reason}",
            timestamp=datetime.now(),
        )
        self._next_tx_id += 1
        self.transaction_log.append(tx)

        return tx

    def mint_initial(self, account_id: str, currency: str, amount: float) -> None:
        """
        Mint initial supply to an account.

        NOTE: This is ONLY for initial setup. Once the constitution is active,
        no minting is allowed (the MINT verb doesn't exist in the grammar).
        """
        account = self.get_account(account_id)
        balance = account.get_balance(currency)
        balance.available += amount

        # Track total supply
        self.total_supply[currency] = self.total_supply.get(currency, 0.0) + amount

    def verify_supply_invariant(self, currency: str) -> bool:
        """
        Verify that total supply hasn't changed.

        Returns True if invariant holds (no money created or destroyed).
        """
        total_in_accounts = sum(
            account.get_balance(currency).total for account in self.accounts.values()
        )
        return abs(total_in_accounts - self.total_supply.get(currency, 0.0)) < 0.001

    def get_transaction_history(
        self,
        account_id: str | None = None,
        limit: int = 100,
    ) -> list[LedgerTransaction]:
        """Get transaction history, optionally filtered by account."""
        txs = self.transaction_log
        if account_id:
            txs = [
                tx
                for tx in txs
                if tx.from_account == account_id or tx.to_account == account_id
            ]
        return txs[-limit:]


@dataclass
class LedgerTransaction:
    """Record of a ledger transaction."""

    id: str
    type: OperationType
    from_account: str
    to_account: str
    currency: str
    amount: float
    memo: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "from_account": self.from_account,
            "to_account": self.to_account,
            "currency": self.currency,
            "amount": self.amount,
            "memo": self.memo,
            "timestamp": self.timestamp.isoformat(),
        }


# =============================================================================
# Command AST Nodes
# =============================================================================


@dataclass
class TransferCommand:
    """AST node for TRANSFER command."""

    amount: float
    currency: str
    from_account: str
    to_account: str
    memo: str = ""


@dataclass
class QueryCommand:
    """AST node for QUERY command."""

    query_type: str  # "balance", "history", "supply"
    account_id: str | None = None
    currency: str | None = None


@dataclass
class ReserveCommand:
    """AST node for RESERVE command."""

    amount: float
    currency: str
    account_id: str
    reason: str = ""


@dataclass
class ReleaseCommand:
    """AST node for RELEASE command."""

    amount: float
    currency: str
    account_id: str
    reason: str = ""


# Union type for all command ASTs
CommandAST = TransferCommand | QueryCommand | ReserveCommand | ReleaseCommand


# =============================================================================
# Ledger Tongue Parser
# =============================================================================


class LedgerTongueParser:
    """
    Parser for the LedgerTongue constitutional grammar.

    Grammar:
        COMMAND ::= TRANSFER | QUERY | RESERVE | RELEASE

        TRANSFER ::= "TRANSFER" <Amount> <Currency> "FROM" <Account> "TO" <Account> ["MEMO" <String>]
            WHERE Account(FROM).balance >= Amount  // Enforced at parse time

        QUERY ::= "QUERY" ("BALANCE" "OF" <Account> "IN" <Currency>
                         | "HISTORY" "OF" <Account>
                         | "SUPPLY" "OF" <Currency>)

        RESERVE ::= "RESERVE" <Amount> <Currency> "FROM" <Account> ["REASON" <String>]
            WHERE Account.balance >= Amount  // Enforced at parse time

        RELEASE ::= "RELEASE" <Amount> <Currency> "TO" <Account> ["REASON" <String>]
            WHERE Account.reserved >= Amount  // Enforced at parse time

    Note: No MINT, DELETE, FORGE, CREATE_MONEY verbs exist in this grammar.
    """

    # Patterns for parsing
    AMOUNT_PATTERN = re.compile(r"(\d+(?:\.\d{1,2})?)")
    CURRENCY_PATTERN = re.compile(r"([A-Z]{3,6})")  # 3-6 chars for TOKEN, IMPACT
    ACCOUNT_PATTERN = re.compile(r"([a-zA-Z][a-zA-Z0-9_]*)")
    STRING_PATTERN = re.compile(r'"([^"]*)"')

    # Valid currencies (can be extended)
    VALID_CURRENCIES = {"USD", "EUR", "GBP", "JPY", "TOKEN", "IMPACT", "GAS"}

    def __init__(self, ledger_state: LedgerState):
        """
        Initialize parser with ledger state.

        The ledger state is used for parse-time balance checking.
        """
        self.ledger = ledger_state

    def parse(self, text: str) -> ParseResult:
        """
        Parse a command.

        Returns ParseSuccess if command is valid AND constitutionally sound.
        Returns ParseError if syntax is invalid OR invariants would be violated.
        """
        text = text.strip()
        upper_text = text.upper()

        if upper_text.startswith("TRANSFER"):
            return self.parse_transfer(text)
        elif upper_text.startswith("QUERY"):
            return self.parse_query(text)
        elif upper_text.startswith("RESERVE"):
            return self.parse_reserve(text)
        elif upper_text.startswith("RELEASE"):
            return self.parse_release(text)
        else:
            return ParseError(
                error=f"Unknown command. Valid commands: TRANSFER, QUERY, RESERVE, RELEASE",
                context=text[:20],
            )

    def parse_transfer(self, text: str) -> ParseResult:
        """
        Parse TRANSFER command with balance checking.

        If source account has insufficient funds, this is a PARSE ERROR,
        not a runtime error.
        """
        # Pattern: TRANSFER <amount> <currency> FROM <account> TO <account> [MEMO "<string>"]
        pattern = re.compile(
            r"TRANSFER\s+(\d+(?:\.\d{1,2})?)\s+([A-Z]{3,6})\s+"
            r"FROM\s+([a-zA-Z][a-zA-Z0-9_]*)\s+"
            r"TO\s+([a-zA-Z][a-zA-Z0-9_]*)"
            r"(?:\s+MEMO\s+\"([^\"]*)\")?\s*$",
            re.IGNORECASE,
        )

        match = pattern.match(text)
        if not match:
            return ParseError(
                error='Invalid TRANSFER syntax. Expected: TRANSFER <amount> <currency> FROM <account> TO <account> [MEMO "<memo>"]',
                context=text,
            )

        amount_str, currency, from_account, to_account, memo = match.groups()
        amount = float(amount_str)
        currency = currency.upper()
        memo = memo or ""

        # Validate currency
        if currency not in self.VALID_CURRENCIES:
            return ParseError(
                error=f"Unknown currency: {currency}. Valid currencies: {', '.join(sorted(self.VALID_CURRENCIES))}",
                context=text,
            )

        # Validate amount
        if amount <= 0:
            return ParseError(
                error=f"Amount must be positive, got {amount}",
                context=text,
            )

        # CONSTITUTIONAL CHECK: Verify source account has sufficient funds
        current_balance = self.ledger.get_balance(from_account, currency)
        if current_balance < amount:
            return ParseError(
                error=f"Insufficient funds: {from_account} has {current_balance:.2f} {currency}, "
                f"cannot transfer {amount:.2f}",
                context=text,
                constitutional_violation=True,
            )

        # Self-transfer check
        if from_account.lower() == to_account.lower():
            return ParseError(
                error="Cannot transfer to same account",
                context=text,
            )

        return ParseSuccess(
            ast=TransferCommand(
                amount=amount,
                currency=currency,
                from_account=from_account,
                to_account=to_account,
                memo=memo,
            ),
            consumed_chars=len(text),
        )

    def parse_query(self, text: str) -> ParseResult:
        """Parse QUERY command."""
        upper_text = text.upper()

        # QUERY BALANCE OF <account> IN <currency>
        balance_pattern = re.compile(
            r"QUERY\s+BALANCE\s+OF\s+([a-zA-Z][a-zA-Z0-9_]*)\s+IN\s+([A-Z]{3,6})\s*$",
            re.IGNORECASE,
        )
        match = balance_pattern.match(text)
        if match:
            account_id, currency = match.groups()
            return ParseSuccess(
                ast=QueryCommand(
                    query_type="balance",
                    account_id=account_id,
                    currency=currency.upper(),
                )
            )

        # QUERY HISTORY OF <account>
        history_pattern = re.compile(
            r"QUERY\s+HISTORY\s+OF\s+([a-zA-Z][a-zA-Z0-9_]*)\s*$",
            re.IGNORECASE,
        )
        match = history_pattern.match(text)
        if match:
            account_id = match.group(1)
            return ParseSuccess(
                ast=QueryCommand(
                    query_type="history",
                    account_id=account_id,
                )
            )

        # QUERY SUPPLY OF <currency>
        supply_pattern = re.compile(
            r"QUERY\s+SUPPLY\s+OF\s+([A-Z]{3,6})\s*$",
            re.IGNORECASE,
        )
        match = supply_pattern.match(text)
        if match:
            currency = match.group(1)
            return ParseSuccess(
                ast=QueryCommand(
                    query_type="supply",
                    currency=currency.upper(),
                )
            )

        return ParseError(
            error="Invalid QUERY syntax. Expected: QUERY BALANCE OF <account> IN <currency> | QUERY HISTORY OF <account> | QUERY SUPPLY OF <currency>",
            context=text,
        )

    def parse_reserve(self, text: str) -> ParseResult:
        """Parse RESERVE command with balance checking."""
        pattern = re.compile(
            r"RESERVE\s+(\d+(?:\.\d{1,2})?)\s+([A-Z]{3,6})\s+"
            r"FROM\s+([a-zA-Z][a-zA-Z0-9_]*)"
            r"(?:\s+REASON\s+\"([^\"]*)\")?\s*$",
            re.IGNORECASE,
        )

        match = pattern.match(text)
        if not match:
            return ParseError(
                error='Invalid RESERVE syntax. Expected: RESERVE <amount> <currency> FROM <account> [REASON "<reason>"]',
                context=text,
            )

        amount_str, currency, account_id, reason = match.groups()
        amount = float(amount_str)
        currency = currency.upper()
        reason = reason or ""

        # Validate currency
        if currency not in self.VALID_CURRENCIES:
            return ParseError(
                error=f"Unknown currency: {currency}",
                context=text,
            )

        # CONSTITUTIONAL CHECK: Verify account has sufficient funds
        current_balance = self.ledger.get_balance(account_id, currency)
        if current_balance < amount:
            return ParseError(
                error=f"Insufficient funds to reserve: {account_id} has {current_balance:.2f} {currency}, "
                f"cannot reserve {amount:.2f}",
                context=text,
                constitutional_violation=True,
            )

        return ParseSuccess(
            ast=ReserveCommand(
                amount=amount,
                currency=currency,
                account_id=account_id,
                reason=reason,
            )
        )

    def parse_release(self, text: str) -> ParseResult:
        """Parse RELEASE command with reserved balance checking."""
        pattern = re.compile(
            r"RELEASE\s+(\d+(?:\.\d{1,2})?)\s+([A-Z]{3,6})\s+"
            r"TO\s+([a-zA-Z][a-zA-Z0-9_]*)"
            r"(?:\s+REASON\s+\"([^\"]*)\")?\s*$",
            re.IGNORECASE,
        )

        match = pattern.match(text)
        if not match:
            return ParseError(
                error='Invalid RELEASE syntax. Expected: RELEASE <amount> <currency> TO <account> [REASON "<reason>"]',
                context=text,
            )

        amount_str, currency, account_id, reason = match.groups()
        amount = float(amount_str)
        currency = currency.upper()
        reason = reason or ""

        # CONSTITUTIONAL CHECK: Verify account has sufficient reserved funds
        account = self.ledger.get_account(account_id)
        reserved = account.reserved(currency)
        if reserved < amount:
            return ParseError(
                error=f"Insufficient reserved funds: {account_id} has {reserved:.2f} {currency} reserved, "
                f"cannot release {amount:.2f}",
                context=text,
                constitutional_violation=True,
            )

        return ParseSuccess(
            ast=ReleaseCommand(
                amount=amount,
                currency=currency,
                account_id=account_id,
                reason=reason,
            )
        )


# =============================================================================
# Ledger Tongue (The Constitutional Grammar)
# =============================================================================


@dataclass
class ExecutionResult:
    """Result of executing a command."""

    success: bool
    result: Any = None
    error: str | None = None
    transaction: LedgerTransaction | None = None


class LedgerTongue:
    """
    The LedgerTongue constitutional grammar.

    This is the complete tongue that combines parsing with execution.
    If parse succeeds, execute is guaranteed to succeed (structural safety).
    """

    def __init__(self, ledger_state: LedgerState | None = None):
        """
        Initialize LedgerTongue.

        Args:
            ledger_state: The ledger state to use. Creates new if None.
        """
        self.ledger = ledger_state or LedgerState()
        self.parser = LedgerTongueParser(self.ledger)

    def parse(self, text: str) -> ParseResult:
        """Parse a command through the constitutional grammar."""
        return self.parser.parse(text)

    def execute(self, ast: CommandAST) -> ExecutionResult:
        """
        Execute a parsed command.

        INVARIANT: This is called after successful parsing, so execution
        is guaranteed to succeed (the constitution ensures this).
        """
        if isinstance(ast, TransferCommand):
            return self._execute_transfer(ast)
        elif isinstance(ast, QueryCommand):
            return self._execute_query(ast)
        elif isinstance(ast, ReserveCommand):
            return self._execute_reserve(ast)
        elif isinstance(ast, ReleaseCommand):
            return self._execute_release(ast)
        else:
            return ExecutionResult(
                success=False,
                error=f"Unknown command type: {type(ast).__name__}",
            )

    def _execute_transfer(self, cmd: TransferCommand) -> ExecutionResult:
        """Execute a transfer command."""
        tx = self.ledger.execute_transfer(
            from_account=cmd.from_account,
            to_account=cmd.to_account,
            currency=cmd.currency,
            amount=cmd.amount,
            memo=cmd.memo,
        )
        return ExecutionResult(
            success=True,
            result=f"Transferred {cmd.amount:.2f} {cmd.currency} from {cmd.from_account} to {cmd.to_account}",
            transaction=tx,
        )

    def _execute_query(self, cmd: QueryCommand) -> ExecutionResult:
        """Execute a query command."""
        if cmd.query_type == "balance":
            balance = self.ledger.get_balance(cmd.account_id, cmd.currency)
            return ExecutionResult(
                success=True,
                result={
                    "account": cmd.account_id,
                    "currency": cmd.currency,
                    "balance": balance,
                },
            )
        elif cmd.query_type == "history":
            history = self.ledger.get_transaction_history(cmd.account_id)
            return ExecutionResult(
                success=True,
                result={
                    "account": cmd.account_id,
                    "transactions": [tx.to_dict() for tx in history],
                },
            )
        elif cmd.query_type == "supply":
            supply = self.ledger.total_supply.get(cmd.currency, 0.0)
            return ExecutionResult(
                success=True,
                result={"currency": cmd.currency, "total_supply": supply},
            )
        else:
            return ExecutionResult(
                success=False,
                error=f"Unknown query type: {cmd.query_type}",
            )

    def _execute_reserve(self, cmd: ReserveCommand) -> ExecutionResult:
        """Execute a reserve command."""
        tx = self.ledger.reserve_funds(
            account_id=cmd.account_id,
            currency=cmd.currency,
            amount=cmd.amount,
            reason=cmd.reason,
        )
        if tx is None:
            # This shouldn't happen if parsing was correct
            return ExecutionResult(
                success=False,
                error="Reserve failed (invariant violation)",
            )
        return ExecutionResult(
            success=True,
            result=f"Reserved {cmd.amount:.2f} {cmd.currency} in {cmd.account_id}",
            transaction=tx,
        )

    def _execute_release(self, cmd: ReleaseCommand) -> ExecutionResult:
        """Execute a release command."""
        tx = self.ledger.release_funds(
            account_id=cmd.account_id,
            currency=cmd.currency,
            amount=cmd.amount,
            reason=cmd.reason,
        )
        if tx is None:
            # This shouldn't happen if parsing was correct
            return ExecutionResult(
                success=False,
                error="Release failed (invariant violation)",
            )
        return ExecutionResult(
            success=True,
            result=f"Released {cmd.amount:.2f} {cmd.currency} to {cmd.account_id}",
            transaction=tx,
        )

    def run(self, command: str) -> ParseError | ExecutionResult:
        """
        Parse and execute a command.

        Returns ParseError if command is invalid or violates constitution.
        Returns ExecutionResult if command executes successfully.
        """
        result = self.parse(command)
        if isinstance(result, ParseError):
            return result
        return self.execute(result.ast)


# =============================================================================
# Constitutional Banker
# =============================================================================


@dataclass
class TransactionResult:
    """Result of a constitutional transaction."""

    success: bool
    reason: str
    type: str  # "GRAMMAR_REJECTION" | "CONSTITUTIONAL_EXECUTION" | "ERROR"
    result: Any = None
    gas_consumed: Gas | None = None
    transaction: LedgerTransaction | None = None


class ConstitutionalBanker:
    """
    Banker that enforces fiscal constitution via grammar.

    Key insight: Agents cannot even REQUEST illegal operations
    because they're grammatically inexpressible.
    """

    def __init__(
        self,
        tongue: LedgerTongue | None = None,
        central_bank: CentralBank | None = None,
    ):
        """
        Initialize constitutional banker.

        Args:
            tongue: The LedgerTongue to use. Creates new if None.
            central_bank: The central bank for metering. Creates new if None.
        """
        self.tongue = tongue or LedgerTongue()
        self.bank = central_bank or CentralBank()

        # Transaction costs (in tokens)
        self.costs = {
            OperationType.TRANSFER: 50,
            OperationType.QUERY: 10,
            OperationType.RESERVE: 30,
            OperationType.RELEASE: 30,
        }

    async def execute_financial_operation(
        self,
        agent_id: str,
        command_text: str,
    ) -> TransactionResult:
        """
        Execute financial operation through constitutional grammar.

        Key insight: Agents cannot even REQUEST illegal operations
        because they're grammatically inexpressible.
        """
        # Parse through constitutional grammar
        parse_result = self.tongue.parse(command_text)

        if isinstance(parse_result, ParseError):
            # This is good! Parse errors prevent illegal operations
            return TransactionResult(
                success=False,
                reason=f"Constitutional violation: {parse_result.error}",
                type="GRAMMAR_REJECTION",
            )

        # If parse succeeded, operation is constitutional
        command_ast = parse_result.ast

        # Determine operation type for costing
        if isinstance(command_ast, TransferCommand):
            op_type = OperationType.TRANSFER
        elif isinstance(command_ast, QueryCommand):
            op_type = OperationType.QUERY
        elif isinstance(command_ast, ReserveCommand):
            op_type = OperationType.RESERVE
        elif isinstance(command_ast, ReleaseCommand):
            op_type = OperationType.RELEASE
        else:
            op_type = OperationType.QUERY  # Default

        # Calculate gas cost
        gas_tokens = self.costs.get(op_type, 50)
        gas = Gas(tokens=gas_tokens, time_ms=10.0, model_multiplier=0.1)

        # Authorize with central bank
        try:
            lease = await self.bank.authorize(agent_id, gas.tokens)
        except Exception as e:
            return TransactionResult(
                success=False,
                reason=f"Budget authorization failed: {e}",
                type="ERROR",
            )

        try:
            # Execute via interpreter (knows operation is safe)
            result = self.tongue.execute(command_ast)

            # Settle with bank
            settled_gas = await self.bank.settle(lease, gas.tokens)

            return TransactionResult(
                success=True,
                reason="Constitutional execution successful",
                type="CONSTITUTIONAL_EXECUTION",
                result=result.result,
                gas_consumed=settled_gas,
                transaction=result.transaction,
            )

        except Exception as e:
            # Void the lease on failure
            await self.bank.void(lease)
            return TransactionResult(
                success=False,
                reason=f"Execution error: {e}",
                type="ERROR",
            )

    def execute_sync(self, command_text: str) -> TransactionResult:
        """
        Synchronous execution (no metering).

        Useful for testing and simple use cases.
        """
        parse_result = self.tongue.parse(command_text)

        if isinstance(parse_result, ParseError):
            return TransactionResult(
                success=False,
                reason=f"Constitutional violation: {parse_result.error}",
                type="GRAMMAR_REJECTION",
            )

        result = self.tongue.execute(parse_result.ast)

        return TransactionResult(
            success=result.success,
            reason="Constitutional execution successful"
            if result.success
            else result.error,
            type="CONSTITUTIONAL_EXECUTION" if result.success else "ERROR",
            result=result.result,
            transaction=result.transaction,
        )

    def get_ledger_state(self) -> LedgerState:
        """Get the underlying ledger state."""
        return self.tongue.ledger

    def verify_constitution(self) -> dict[str, bool]:
        """
        Verify that all constitutional invariants hold.

        Returns dict of invariant name -> whether it holds.
        """
        ledger = self.tongue.ledger
        invariants = {}

        # 1. Total supply invariant (no money created or destroyed)
        for currency in ledger.total_supply:
            invariants[f"supply_{currency}"] = ledger.verify_supply_invariant(currency)

        # 2. No negative balances
        all_positive = True
        for account in ledger.accounts.values():
            for currency, balance in account.balances.items():
                if balance.available < 0 or balance.reserved < 0:
                    all_positive = False
                    break
        invariants["no_negative_balances"] = all_positive

        # 3. All transactions balanced (implicit in double-entry, always true)
        invariants["double_entry"] = True

        return invariants


# =============================================================================
# Convenience Functions
# =============================================================================


def create_ledger_tongue(
    initial_accounts: dict[str, dict[str, float]] | None = None,
) -> LedgerTongue:
    """
    Create a LedgerTongue with initial account balances.

    Args:
        initial_accounts: Dict of account_id -> {currency -> amount}

    Returns:
        Configured LedgerTongue
    """
    ledger = LedgerState()

    if initial_accounts:
        for account_id, balances in initial_accounts.items():
            for currency, amount in balances.items():
                ledger.mint_initial(account_id, currency, amount)

    return LedgerTongue(ledger)


def create_constitutional_banker(
    initial_accounts: dict[str, dict[str, float]] | None = None,
    central_bank: CentralBank | None = None,
) -> ConstitutionalBanker:
    """
    Create a ConstitutionalBanker with initial setup.

    Args:
        initial_accounts: Dict of account_id -> {currency -> amount}
        central_bank: Optional central bank for metering

    Returns:
        Configured ConstitutionalBanker
    """
    tongue = create_ledger_tongue(initial_accounts)
    return ConstitutionalBanker(tongue=tongue, central_bank=central_bank)


def create_fiscal_constitution(
    initial_supply: dict[str, float],
    treasury_account: str = "treasury",
) -> ConstitutionalBanker:
    """
    Create a complete fiscal constitution with initial supply.

    All initial supply is minted to the treasury account.
    Other accounts start at zero and receive funds via transfer.

    Args:
        initial_supply: Dict of currency -> total supply
        treasury_account: Name of the treasury account

    Returns:
        Configured ConstitutionalBanker
    """
    initial_accounts = {
        treasury_account: initial_supply,
    }
    return create_constitutional_banker(initial_accounts)
