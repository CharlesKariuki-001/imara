"""
Tests for Imara Cleaner v0.2
"""

from datetime import date
from decimal import Decimal

from imara.cleaner import (
    CleanTransaction,
    RejectedRow,
    clean_row,
    clean_rows,
    parse_amount,
    parse_date,
)


# ---------- Date parsing ----------

def test_parse_valid_date():
    result = parse_date("2026-09-21")
    assert result == date(2026, 9, 21)


def test_parse_supported_date_format():
    result = parse_date("21/09/2026")
    assert result == date(2026, 9, 21)


def test_parse_dot_date_format():
    result = parse_date("20.09.2026")
    assert result == date(2026, 9, 20)


def test_parse_written_month_date():
    result = parse_date("23 Sep 2026")
    assert result == date(2026, 9, 23)


def test_parse_written_full_month_date():
    result = parse_date("5 October 2026")
    assert result == date(2026, 10, 5)


def test_invalid_date_returns_none():
    result = parse_date("32/13/2026")
    assert result is None


# ---------- Amount parsing ----------

def test_parse_amount_with_currency_and_comma():
    result = parse_amount("KSh 2,500")
    assert result == Decimal("2500")


def test_parse_amount_with_decimal():
    result = parse_amount("1,250.50")
    assert result == Decimal("1250.50")


def test_parse_amount_with_kes():
    result = parse_amount("KES 15,000")
    assert result == Decimal("15000")


def test_parse_amount_without_currency():
    result = parse_amount("1800")
    assert result == Decimal("1800")


def test_parse_amount_with_internal_spaces():
    result = parse_amount("KSh  2 500")
    assert result == Decimal("2500")


def test_parse_amount_without_space_after_currency():
    result = parse_amount("KSh3,750")
    assert result == Decimal("3750")


def test_invalid_amount_returns_none():
    result = parse_amount("CASH_ONLY")
    assert result is None


def test_currency_without_number_returns_none():
    result = parse_amount("KSh")
    assert result is None


def test_ambiguous_thousands_format_is_rejected():
    result = parse_amount("2.500")
    assert result is None


def test_negative_amount_is_rejected():
    result = parse_amount("-1,200.50")
    assert result is None


# ---------- Row cleaning ----------

def test_missing_transaction_id_is_rejected():
    row = {
        "Txn_ID": "",
        "Date": "2026-09-21",
        "Amount": "KSh 500",
    }
    result = clean_row(row, row_number=2)
    assert isinstance(result, RejectedRow)
    assert result.reason == "Missing transaction ID"


def test_valid_transaction_is_cleaned():
    row = {
        "Txn_ID": "TX001",
        "Date": "21/09/2026",
        "Amount": "KSh 2,500",
        "Account": "Main Till",
    }
    result = clean_row(row, row_number=2)

    assert isinstance(result, CleanTransaction)
    assert result.transaction_id == "TX001"
    assert result.transaction_date == date(2026, 9, 21)
    assert result.amount == Decimal("2500")
    assert result.description == "Main Till"


def test_mixed_rows_produce_clean_and_rejected_results():
    rows = [
        {
            "Txn_ID": "TX001",
            "Date": "2026-09-21",
            "Amount": "KSh 500",
        },
        {
            "Txn_ID": "",
            "Date": "2026-09-21",
            "Amount": "KSh 700",
        },
        {
            "Txn_ID": "TX003",
            "Date": "not-a-date",
            "Amount": "KSh 900",
        },
    ]
    result = clean_rows(rows)

    assert len(result.clean_transactions) == 1
    assert len(result.rejected_rows) == 2
    assert result.total_rows == 3


def test_different_column_names_are_supported():
    row = {
        "Transaction ID": "TX100",
        "Transaction Date": "2026-09-21",
        "Transaction Amount": "1000",
    }
    result = clean_row(row, row_number=2)

    assert isinstance(result, CleanTransaction)
    assert result.transaction_id == "TX100"
    assert result.amount == Decimal("1000")