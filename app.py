"""
Combined Streamlit app: Average Revenue by Physician.

New single-file app that includes:
- flexible CSV/TSV ingest (delimiter auto-detect)
- case-insensitive / whitespace-tolerant headers
- revenue coercion to numeric (handles "$", commas, etc.)
- improved matplotlib charts:
  - sorted bar chart with labels
  - sorted line graph (option 1)
  - histogram (distribution of raw revenue)
  - box plot (outliers)

Run:
  pip install -r requirements.txt
  streamlit run combined_app.py
"""

from io import BytesIO

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
import streamlit as st


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df


def _coerce_revenue_to_numeric(series: pd.Series) -> pd.Series:
    # Handles values like "$1,234.56", "1,234", " 1234 ", etc.
    s = (
        series.astype(str)
        .str.replace(r"[\$,]", "", regex=True)
        .str.strip()
    )
    return pd.to_numeric(s, errors="coerce")


def compute_average_revenue(df: pd.DataFrame) -> pd.Series:
    """
    Return a Series of average revenue grouped by physician.

    Requires columns (case-insensitive):
      - physician
      - revenue (coerced to numeric)
    """
    df = _normalize_columns(df)

    missing = [c for c in ("physician", "revenue") if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required column(s): {', '.join(missing)}.\n"
            "Your file must contain columns for physician and revenue "
            "(header case/spaces are OK)."
        )

    df["revenue"] = _coerce_revenue_to_numeric(df["revenue"])

    if df["revenue"].isna().any():
        bad = df[df["revenue"].isna()][["physician", "revenue"]].head(10)
        raise ValueError(
            "The revenue column contains non-numeric values in some rows.\n"
            "Example rows with bad revenue values (showing up to 10):\n"
            f"{bad}"
        )

    return df.groupby("physician")["revenue"].mean()


st.title("Average Revenue by Physician")
st.write(
    "Upload a CSV/TSV file containing at least two columns: "
    "**physician** and **revenue** (header case/spaces are OK)."
)

uploaded_file = st.file_uploader("Choose a file", type=["csv", "tsv", "txt"])

if uploaded_file is not None:
    # --- Read (auto-detect delimiter) ---
    try:
        df_raw = pd.read_csv(uploaded_file, sep=None, engine="python")
    except Exception as exc:
        st.error(f"Could not read the uploaded file: {exc}")
        st.stop()

    # --- Compute aggregated results ---
    try:
        avg_series = compute_average_revenue(df_raw)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    result_df = avg_series.reset_index()
    result_df.columns = ["Physician", "Average Revenue"]

    # --- Display table ---
    st.subheader("Aggregated Results")
    display_df = result_df.copy()
    display_df["Average Revenue"] = display_df["Average Revenue"].map(lambda x: f"${x:,.2f}")
    st.dataframe(display_df, use_container_width=True)

    # Prepare normalized df for distribution charts
    df_norm = _normalize_columns(df_raw)
    df_norm["revenue"] = _coerce_revenue_to_numeric(df_norm["revenue"])

    # --- Chart options ---
    st.subheader("Charts")

    top_n = st.slider(
        "Show top N physicians",
        min_value=1,
        max_value=max(1, len(result_df)),
        value=min(20, len(result_df)),
    )

    # Sorted subset
    plot_df = result_df.sort_values("Average Revenue", ascending=False).head(top_n)

    # --- Bar chart (sorted) ---
    st.markdown("**Average Revenue by Physician (Bar, sorted)**")
    fig_bar, ax_bar = plt.subplots(figsize=(12, 6))

    bars = ax_bar.bar(
        plot_df["Physician"],
        plot_df["Average Revenue"],
        color="steelblue",
        edgecolor="black",
        linewidth=0.3,
    )

    ax_bar.set_title("Average Revenue by Physician")
    ax_bar.set_xlabel("Physician")
    ax_bar.set_ylabel("Average Revenue")
    ax_bar.yaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.0f}"))
    ax_bar.grid(axis="y", linestyle="--", alpha=0.35)
    plt.setp(ax_bar.get_xticklabels(), rotation=45, ha="right")

    for rect in bars:
        h = rect.get_height()
        ax_bar.annotate(
            f"${h:,.0f}",
            xy=(rect.get_x() + rect.get_width() / 2, h),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    st.pyplot(fig_bar)

    # --- Line chart (sorted) [Option 1] ---
    st.markdown("**Average Revenue by Physician (Line, sorted)**")
    fig_line, ax_line = plt.subplots(figsize=(12, 5))

    ax_line.plot(
        plot_df["Physician"],
        plot_df["Average Revenue"],
        marker="o",
        linewidth=2,
        color="teal",
    )

    ax_line.set_title("Average Revenue by Physician (sorted)")
    ax_line.set_xlabel("Physician")
    ax_line.set_ylabel("Average Revenue")
    ax_line.yaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.0f}"))
    ax_line.grid(axis="y", linestyle="--", alpha=0.35)
    plt.setp(ax_line.get_xticklabels(), rotation=45, ha="right")

    plt.tight_layout()
    st.pyplot(fig_line)

    # --- Histogram (raw revenue distribution) ---
    st.markdown("**Revenue Distribution (Histogram)**")
    fig_hist, ax_hist = plt.subplots(figsize=(10, 4))
    rev = df_norm["revenue"].dropna()
    ax_hist.hist(rev, bins=30, color="slategray", edgecolor="white")
    ax_hist.set_title("Revenue Distribution (all rows)")
    ax_hist.set_xlabel("Revenue")
    ax_hist.set_ylabel("Count")
    ax_hist.xaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.0f}"))
    ax_hist.grid(axis="y", linestyle="--", alpha=0.35)
    plt.tight_layout()
    st.pyplot(fig_hist)

    # --- Box plot (raw revenue outliers) ---
    st.markdown("**Revenue Box Plot (Outliers)**")
    fig_box, ax_box = plt.subplots(figsize=(10, 2.5))
    ax_box.boxplot(rev, vert=False, patch_artist=True)
    ax_box.set_title("Revenue Box Plot (all rows)")
    ax_box.set_xlabel("Revenue")
    ax_box.xaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.0f}"))
    ax_box.grid(axis="x", linestyle="--", alpha=0.35)
    plt.tight_layout()
    st.pyplot(fig_box)

    # --- Download aggregated results ---
    st.subheader("Download Results")
    csv_buffer = BytesIO()
    result_df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    st.download_button(
        label="Download aggregated CSV",
        data=csv_buffer.getvalue(),
        file_name="avg_revenue_by_physician.csv",
        mime="text/csv",
    )
