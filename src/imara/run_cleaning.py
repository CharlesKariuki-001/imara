"""
Simple runner that loads a CSV, cleans it with Imara, and prints a clear summary.
"""

from pathlib import Path

from imara.cleaner import clean_rows
from imara.csv_loader import load_csv


def run_cleaning(csv_path: str | Path) -> None:
    """Load a CSV file, clean its transactions, and print a human-readable summary."""

    path = Path(csv_path)

    print(f"\nLoading: {path}")
    rows = load_csv(path)
    result = clean_rows(rows)

    print()
    print("IMARA CLEANING RESULT")
    print("=" * 60)
    print(f"Total rows processed : {result.total_rows}")
    print(f"Clean transactions   : {len(result.clean_transactions)}")
    print(f"Rejected rows        : {len(result.rejected_rows)}")
    print(f"Success rate         : {result.success_rate:.1%}")
    print("=" * 60)

    # ---- Clean transactions ----
    print("\nCLEAN TRANSACTIONS")
    print("-" * 60)

    if not result.clean_transactions:
        print("  (none)")
    else:
        for t in result.clean_transactions:
            desc = t.description or "-"
            print(
                f"  {t.transaction_id:<12} | "
                f"{t.transaction_date} | "
                f"{t.amount:>12} | "
                f"{desc}"
            )

    # ---- Rejected rows ----
    print("\nREJECTED ROWS")
    print("-" * 60)

    if not result.rejected_rows:
        print("  (none)")
    else:
        for r in result.rejected_rows:
            print(f"  Row {r.row_number:>3}: {r.reason}")

    print()


if __name__ == "__main__":
    sample_file = Path("data/sample/messy_transactions.csv")
    run_cleaning(sample_file)