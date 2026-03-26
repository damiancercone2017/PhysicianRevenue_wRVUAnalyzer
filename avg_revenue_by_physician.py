"""
avg_revenue_by_physician.py
----------------------------
Calculates average revenue by physician from an uploaded data file.

Supported file formats: CSV, Excel (.xlsx / .xls)

Expected columns (case-insensitive):
  - A column whose name contains "physician" (e.g. "Physician", "Physician Name", "Doctor")
  - A column whose name contains "revenue" (e.g. "Revenue", "Total Revenue", "Net Revenue")

Usage
-----
Command-line:
    python avg_revenue_by_physician.py <path_to_file>

Interactive (no argument):
    python avg_revenue_by_physician.py
    # You will be prompted to enter the file path.

Programmatic:
    from avg_revenue_by_physician import calculate_avg_revenue
    result = calculate_avg_revenue("data.csv")
    print(result)
"""

import sys
import os
import pandas as pd


# ---------------------------------------------------------------------------
# Core calculation
# ---------------------------------------------------------------------------

def _find_column(df: pd.DataFrame, keyword: str) -> str:
    """Return the first column name that contains *keyword* (case-insensitive)."""
    matches = [col for col in df.columns if keyword.lower() in col.lower()]
    if not matches:
        raise ValueError(
            f"No column containing '{keyword}' found in the file. "
            f"Available columns: {list(df.columns)}"
        )
    return matches[0]


def calculate_avg_revenue(file_path: str) -> pd.DataFrame:
    """
    Load *file_path* and return a DataFrame with the average revenue per physician,
    sorted from highest to lowest average revenue.

    Parameters
    ----------
    file_path : str
        Path to a CSV or Excel file.

    Returns
    -------
    pd.DataFrame
        Columns: [physician_col, "Average Revenue"]
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(file_path)
    elif ext in (".xlsx", ".xls"):
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: '{ext}'. Use .csv or .xlsx/.xls")

    physician_col = _find_column(df, "physician")
    revenue_col = _find_column(df, "revenue")

    # Coerce revenue to numeric, ignoring non-numeric values
    df[revenue_col] = pd.to_numeric(df[revenue_col], errors="coerce")

    result = (
        df.groupby(physician_col)[revenue_col]
        .mean()
        .reset_index()
        .rename(columns={revenue_col: "Average Revenue"})
        .sort_values("Average Revenue", ascending=False)
        .reset_index(drop=True)
    )

    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input("Enter the path to your data file (CSV or Excel): ").strip()

    if not os.path.isfile(file_path):
        print(f"Error: File not found: '{file_path}'")
        sys.exit(1)

    try:
        result = calculate_avg_revenue(file_path)
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    print("\nAverage Revenue by Physician")
    print("=" * 40)
    print(result.to_string(index=False))
    print()


if __name__ == "__main__":
    main()
