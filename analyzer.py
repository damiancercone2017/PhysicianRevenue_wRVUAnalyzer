#!/usr/bin/env python3
"""
Revenue and wRVU Analyzer

Analyzes revenue and wRVUs (work Relative Value Units) from uploaded CSV or Excel data.

Usage:
    python analyzer.py <data_file> [options]

Examples:
    python analyzer.py data.csv
    python analyzer.py data.xlsx --group-by provider
    python analyzer.py data.csv --group-by month --top 10
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
from tabulate import tabulate


# ---------------------------------------------------------------------------
# Column name aliases – map common variations to canonical names
# ---------------------------------------------------------------------------
COLUMN_ALIASES = {
    "revenue": [
        "revenue", "total_revenue", "total revenue", "net_revenue", "net revenue",
        "payment", "payments", "charges", "charge", "amount", "total amount",
        "gross_revenue", "gross revenue",
    ],
    "wrvus": [
        "wrvus", "wrvu", "work_rvus", "work rvus", "work rvu", "work_rvu",
        "relative_value_units", "relative value units", "rvus", "rvu",
        "total_wrvus", "total wrvus", "total_rvus", "total rvus",
    ],
    "provider": [
        "provider", "physician", "doctor", "clinician", "provider_name",
        "provider name", "physician_name", "physician name", "name",
        "rendering_provider", "rendering provider",
    ],
    "date": [
        "date", "service_date", "service date", "dos", "encounter_date",
        "encounter date", "month", "period", "year_month", "year month",
        "posting_date", "posting date",
    ],
    "specialty": [
        "specialty", "speciality", "department", "dept", "division",
        "service_line", "service line",
    ],
    "cpt": [
        "cpt", "cpt_code", "cpt code", "procedure_code", "procedure code",
        "code", "hcpcs",
    ],
}


def _normalize_columns(df: pd.DataFrame) -> dict[str, str]:
    """
    Return a mapping {canonical_name: actual_column} for each canonical name
    that can be matched in the dataframe.
    """
    lower_to_actual = {c.lower().strip(): c for c in df.columns}
    mapping: dict[str, str] = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in lower_to_actual:
                mapping[canonical] = lower_to_actual[alias]
                break
    return mapping


def load_data(filepath: str) -> pd.DataFrame:
    """Load data from a CSV or Excel file."""
    path = Path(filepath)
    if not path.exists():
        sys.exit(f"Error: File '{filepath}' not found.")

    suffix = path.suffix.lower()
    try:
        if suffix == ".csv":
            df = pd.read_csv(filepath)
        elif suffix in (".xlsx", ".xls"):
            df = pd.read_excel(filepath)
        else:
            sys.exit(f"Error: Unsupported file type '{suffix}'. Use .csv, .xlsx, or .xls.")
    except Exception as exc:  # noqa: BLE001
        sys.exit(f"Error reading file: {exc}")

    if df.empty:
        sys.exit("Error: The uploaded file contains no data.")

    return df


def _fmt_currency(value: float) -> str:
    return f"${value:,.2f}"


def _fmt_number(value: float) -> str:
    return f"{value:,.2f}"


def _fmt_int(value: float) -> str:
    return f"{int(value):,}"


# ---------------------------------------------------------------------------
# Analysis functions
# ---------------------------------------------------------------------------

def overall_summary(df: pd.DataFrame, col_map: dict[str, str]) -> None:
    """Print high-level totals."""
    print("\n" + "=" * 60)
    print("OVERALL SUMMARY")
    print("=" * 60)

    rows = [["Total Records", f"{len(df):,}"]]

    if "revenue" in col_map:
        total_rev = df[col_map["revenue"]].sum()
        rows.append(["Total Revenue", _fmt_currency(total_rev)])

    if "wrvus" in col_map:
        total_wrvus = df[col_map["wrvus"]].sum()
        rows.append(["Total wRVUs", _fmt_number(total_wrvus)])

    if "revenue" in col_map and "wrvus" in col_map:
        total_wrvus = df[col_map["wrvus"]].sum()
        total_rev = df[col_map["revenue"]].sum()
        if total_wrvus > 0:
            rev_per_wrvu = total_rev / total_wrvus
            rows.append(["Revenue per wRVU", _fmt_currency(rev_per_wrvu)])

    if "provider" in col_map:
        rows.append(["Unique Providers", f"{df[col_map['provider']].nunique():,}"])

    if "specialty" in col_map:
        rows.append(["Unique Specialties", f"{df[col_map['specialty']].nunique():,}"])

    print(tabulate(rows, headers=["Metric", "Value"], tablefmt="simple"))


def group_analysis(
    df: pd.DataFrame,
    col_map: dict[str, str],
    group_by: str,
    top_n: int = 0,
) -> None:
    """Print aggregated revenue and wRVUs grouped by a dimension."""
    dimension_map = {
        "provider": "provider",
        "specialty": "specialty",
        "month": "date",
        "date": "date",
        "cpt": "cpt",
        "department": "specialty",
    }
    canonical = dimension_map.get(group_by.lower(), group_by.lower())

    if canonical not in col_map:
        print(f"\nWarning: column for '{group_by}' not found. Skipping group analysis.")
        return

    group_col = col_map[canonical]
    agg: dict[str, pd.NamedAgg] = {}

    if "revenue" in col_map:
        agg["Revenue"] = pd.NamedAgg(column=col_map["revenue"], aggfunc="sum")
    if "wrvus" in col_map:
        agg["wRVUs"] = pd.NamedAgg(column=col_map["wrvus"], aggfunc="sum")

    if not agg:
        print("\nWarning: No revenue or wRVU columns found.")
        return

    grouped = df.groupby(group_col).agg(**agg).reset_index()
    grouped.rename(columns={group_col: group_by.title()}, inplace=True)

    if "Revenue" in grouped.columns and "wRVUs" in grouped.columns:
        grouped["Rev/wRVU"] = grouped.apply(
            lambda r: r["Revenue"] / r["wRVUs"] if r["wRVUs"] > 0 else 0, axis=1
        )
        grouped.sort_values("Revenue", ascending=False, inplace=True)
    elif "Revenue" in grouped.columns:
        grouped.sort_values("Revenue", ascending=False, inplace=True)
    else:
        grouped.sort_values("wRVUs", ascending=False, inplace=True)

    if top_n > 0:
        grouped = grouped.head(top_n)

    # Format for display
    display = grouped.copy()
    if "Revenue" in display.columns:
        display["Revenue"] = display["Revenue"].apply(_fmt_currency)
    if "wRVUs" in display.columns:
        display["wRVUs"] = display["wRVUs"].apply(_fmt_number)
    if "Rev/wRVU" in display.columns:
        display["Rev/wRVU"] = display["Rev/wRVU"].apply(_fmt_currency)

    title = f"ANALYSIS BY {group_by.upper()}"
    if top_n > 0:
        title += f" (TOP {top_n})"
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    print(tabulate(display, headers="keys", tablefmt="simple", showindex=False))


def date_trend(df: pd.DataFrame, col_map: dict[str, str]) -> None:
    """Print monthly trend if a date column is available."""
    if "date" not in col_map:
        return

    date_col = col_map["date"]
    df = df.copy()

    try:
        df["_period"] = pd.to_datetime(df[date_col], infer_datetime_format=True, errors="coerce")
        if df["_period"].isna().all():
            # Maybe already stored as YYYY-MM strings
            df["_period"] = df[date_col].astype(str)
        else:
            df["_period"] = df["_period"].dt.to_period("M").astype(str)
    except Exception:  # noqa: BLE001
        return

    agg: dict[str, pd.NamedAgg] = {}
    if "revenue" in col_map:
        agg["Revenue"] = pd.NamedAgg(column=col_map["revenue"], aggfunc="sum")
    if "wrvus" in col_map:
        agg["wRVUs"] = pd.NamedAgg(column=col_map["wrvus"], aggfunc="sum")

    if not agg:
        return

    trend = df.groupby("_period").agg(**agg).reset_index()
    trend.rename(columns={"_period": "Period"}, inplace=True)
    trend.sort_values("Period", inplace=True)

    if "Revenue" in trend.columns and "wRVUs" in trend.columns:
        trend["Rev/wRVU"] = trend.apply(
            lambda r: r["Revenue"] / r["wRVUs"] if r["wRVUs"] > 0 else 0, axis=1
        )

    display = trend.copy()
    if "Revenue" in display.columns:
        display["Revenue"] = display["Revenue"].apply(_fmt_currency)
    if "wRVUs" in display.columns:
        display["wRVUs"] = display["wRVUs"].apply(_fmt_number)
    if "Rev/wRVU" in display.columns:
        display["Rev/wRVU"] = display["Rev/wRVU"].apply(_fmt_currency)

    print("\n" + "=" * 60)
    print("MONTHLY TREND")
    print("=" * 60)
    print(tabulate(display, headers="keys", tablefmt="simple", showindex=False))


def detect_and_report(df: pd.DataFrame, col_map: dict[str, str]) -> None:
    """Auto-detect interesting dimensions and print additional analysis."""
    for dim in ("provider", "specialty", "cpt"):
        if dim in col_map:
            group_analysis(df, col_map, dim, top_n=10)

    date_trend(df, col_map)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def analyze(filepath: str, group_by: str | None = None, top_n: int = 0) -> None:
    """Run the full analysis pipeline."""
    df = load_data(filepath)
    col_map = _normalize_columns(df)

    if not col_map:
        print("Warning: Could not identify any known columns.")
        print(f"Columns found: {list(df.columns)}")
        return

    print(f"\nLoaded {len(df):,} rows from '{filepath}'")
    print(f"Detected columns: {col_map}")

    overall_summary(df, col_map)

    if group_by:
        group_analysis(df, col_map, group_by, top_n=top_n)
    else:
        detect_and_report(df, col_map)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze revenue and wRVUs from an uploaded CSV or Excel file."
    )
    parser.add_argument("file", help="Path to the data file (CSV or Excel)")
    parser.add_argument(
        "--group-by",
        metavar="DIMENSION",
        help=(
            "Group results by a dimension: provider, specialty, month, cpt, department. "
            "If omitted, all available dimensions are shown automatically."
        ),
    )
    parser.add_argument(
        "--top",
        type=int,
        default=0,
        metavar="N",
        help="Limit grouped results to the top N rows (default: show all)",
    )
    args = parser.parse_args()
    analyze(args.file, group_by=args.group_by, top_n=args.top)


if __name__ == "__main__":
    main()
