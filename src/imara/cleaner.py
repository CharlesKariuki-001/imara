"""
Imara Cleaner v0.2

Converts messy financial transaction rows into clean, structured data.

Deliberately conservative:
ambiguous or risky values are rejected rather than guessed.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import re
from typing import Any


@dataclass
class CleanTransaction:
    """A transaction that Imara successfully cleaned."""

    transaction_id: str
    transaction_date: date
    amount: Decimal
    description: str | None = None


@dataclass
class RejectedRow:
    """A transaction row that Imara could not safely clean."""

    row_number: int
    raw_data: dict[str, Any]
    reason: str


@dataclass
class CleaningResult:
    """The complete result produced by the cleaner."""

    clean_transactions: list[CleanTransaction]
    rejected_rows: list[RejectedRow]

    @property
    def total_rows(self) -> int:
        """Return the total number of rows processed."""

        return len(self.clean_transactions) + len(self.rejected_rows)

    @property
    def success_rate(self) -> float:
        """Return the percentage of rows successfully cleaned."""

        if self.total_rows == 0:
            return 0.0

        return len(self.clean_transactions) / self.total_rows


def normalize_column_name(name: str) -> str:
    """
    Normalize column names so different naming styles can match.

    Examples:

        Transaction ID -> transactionid
        transaction_id -> transactionid
        Transaction-ID -> transactionid
    """

    return re.sub(r"[\s_-]+", "", name.strip().lower())


def find_field(
    row: dict[str, Any],
    possible_names: list[str],
) -> Any | None:
    """Find a field even when the input column uses another name."""

    normalized_row = {
        normalize_column_name(str(key)): value
        for key, value in row.items()
    }

    for name in possible_names:
        normalized_name = normalize_column_name(name)

        if normalized_name in normalized_row:
            return normalized_row[normalized_name]

    return None


def parse_date(value: Any) -> date | None:
    """
    Convert supported date formats into a Python date.

    Supported examples:

        2026-09-21
        2026/09/21
        21-09-2026
        21/09/2026
        21.09.2026
        21 Sep 2026
        5 Oct 2026
        5 October 2026

    Ambiguous formats are intentionally limited rather than guessed.
    """

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d.%m.%Y",
        "%d %b %Y",
        "%d %B %Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    return None


def parse_amount(value: Any) -> Decimal | None:
    """
    Convert a clearly formatted monetary value into Decimal.

    Safe examples:

        KSh 1,500       -> 1500
        KSh  2 500      -> 2500
        KSh3,750        -> 3750
        KES 15,000      -> 15000
        1,250.50        -> 1250.50
        1800            -> 1800

    Rejected deliberately:

        2.500           -> ambiguous
        -1,200.50       -> negative
        CASH_ONLY       -> not a number
        KSh              -> currency with no number
    """

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    # Reject negative values for the current transaction model.
    #
    # This is a Week 1 policy, not a permanent financial rule.
    if text.startswith("-"):
        return None

    # Remove supported currency labels.
    #
    # IMPORTANT:
    # There is deliberately NO word boundary here.
    #
    # This allows both:
    #
    #     KSh 3,750
    #     KSh3,750
    #
    # to be recognized.
    text = re.sub(
        r"(?:KSh|KES|USD|EUR|GBP)",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()

    # Currency with no numeric value left.
    if not text:
        return None

    # Remove spaces used as thousands separators.
    text = text.replace(" ", "")

    # Reject ambiguous formats such as:
    #
    #     2.500
    #
    # This could represent 2,500 in some systems
    # or 2.500 in others.
    if re.fullmatch(r"\d+\.\d{3}", text):
        return None

    # Remove comma thousands separators.
    text = text.replace(",", "")

    # Accept only normal decimal numbers.
    #
    # Maximum of two decimal places because we are
    # currently dealing with normal monetary amounts.
    if not re.fullmatch(r"\d+(?:\.\d{1,2})?", text):
        return None

    try:
        amount = Decimal(text)
    except InvalidOperation:
        return None

    if amount < 0:
        return None

    return amount


def clean_row(
    row: dict[str, Any],
    row_number: int,
) -> CleanTransaction | RejectedRow:
    """
    Clean a single row.

    Returns either:
        CleanTransaction
    or:
        RejectedRow
    """

    transaction_id = find_field(
        row,
        [
            "transaction_id",
            "transaction id",
            "txn_id",
            "txn id",
            "txnid",
            "reference",
            "ref",
            "id",
        ],
    )

    transaction_date = find_field(
        row,
        [
            "date",
            "transaction_date",
            "transaction date",
            "transaction_date_time",
            "transaction datetime",
        ],
    )

    amount = find_field(
        row,
        [
            "amount",
            "transaction_amount",
            "transaction amount",
            "value",
        ],
    )

    # Prefer actual description fields.
    description = find_field(
        row,
        [
            "description",
            "details",
            "narration",
            "memo",
            "particulars",
        ],
    )

    # If no description exists, use Account as fallback.
    #
    # This keeps the current sample dataset useful.
    # Later we should give Account its own field instead
    # of treating it as description.
    if description is None:
        description = find_field(row, ["account"])

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    if transaction_id is None or not str(transaction_id).strip():
        return RejectedRow(
            row_number=row_number,
            raw_data=row,
            reason="Missing transaction ID",
        )

    parsed_date = parse_date(transaction_date)

    if parsed_date is None:
        return RejectedRow(
            row_number=row_number,
            raw_data=row,
            reason="Invalid or missing date",
        )

    parsed_amount = parse_amount(amount)

    if parsed_amount is None:
        return RejectedRow(
            row_number=row_number,
            raw_data=row,
            reason="Invalid, ambiguous, or missing amount",
        )

    # Clean description.
    clean_description = None

    if description is not None:
        text = str(description).strip()

        if text:
            clean_description = text

    return CleanTransaction(
        transaction_id=str(transaction_id).strip(),
        transaction_date=parsed_date,
        amount=parsed_amount,
        description=clean_description,
    )


def clean_rows(rows: list[dict[str, Any]]) -> CleaningResult:
    """Clean a collection of transaction rows."""

    clean_transactions: list[CleanTransaction] = []
    rejected_rows: list[RejectedRow] = []

    # CSV row 1 is the header.
    # Therefore the first transaction is row 2.
    for row_number, row in enumerate(rows, start=2):
        result = clean_row(row, row_number)

        if isinstance(result, CleanTransaction):
            clean_transactions.append(result)
        else:
            rejected_rows.append(result)

    return CleaningResult(
        clean_transactions=clean_transactions,
        rejected_rows=rejected_rows,
    )