"""
CSV loader for Imara.

Responsibilities:
- Read a CSV file safely
- Return rows as a list of dictionaries
- Handle common real-world messiness (BOM, whitespace, empty rows, etc.)
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def load_csv(path: str | Path) -> list[dict[str, Any]]:
    """
    Read a CSV file and return its rows as dictionaries.

    The first non-empty row is treated as the header.
    Empty rows are skipped.
    Leading/trailing whitespace is stripped from both headers and values.

    Parameters
    ----------
    path : str | Path
        Path to the CSV file.

    Returns
    -------
    list[dict[str, Any]]
        List of row dictionaries. Keys come from the header row.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the path is not a file, the file has no header, or no usable rows.
    """
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    # Try the two most common delimiters used in real exports
    for delimiter in (",", ";"):
        try:
            rows = _read_with_delimiter(file_path, delimiter)
            if rows:
                return rows
        except Exception:
            # Try the next delimiter
            continue

    # If both failed, raise a clear error
    raise ValueError(
        f"Could not read a valid CSV from {file_path}. "
        "Please check that the file has a header row and uses comma or semicolon delimiters."
    )


def _read_with_delimiter(file_path: Path, delimiter: str) -> list[dict[str, Any]]:
    """Internal helper that attempts to read the file with a specific delimiter."""
    with file_path.open(
        mode="r",
        encoding="utf-8-sig",  # Handles Excel BOM
        newline="",
    ) as file:
        reader = csv.DictReader(file, delimiter=delimiter)

        if reader.fieldnames is None:
            raise ValueError("CSV file does not contain a header row.")

        # Clean header names (remove leading/trailing spaces)
        cleaned_fieldnames = [name.strip() if name else name for name in reader.fieldnames]
        reader.fieldnames = cleaned_fieldnames

        rows: list[dict[str, Any]] = []

        for row in reader:
            # Skip completely empty rows
            if not any(value and str(value).strip() for value in row.values()):
                continue

            # Strip whitespace from every value
            cleaned_row = {
                key: (value.strip() if isinstance(value, str) else value)
                for key, value in row.items()
            }
            rows.append(cleaned_row)

        if not rows:
            raise ValueError("CSV file contains no usable data rows.")

        return rows