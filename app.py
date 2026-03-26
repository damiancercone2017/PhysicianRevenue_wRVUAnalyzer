"""Streamlit app: Average Revenue by Physician.

Upload a CSV file with 'physician' and 'revenue' columns to compute and
visualise average revenue per physician, then download the aggregated results.
"""

from io import BytesIO

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from avg_revenue_by_physician import compute_average_revenue

st.title("Average Revenue by Physician")
st.write(
    "Upload a CSV file containing at least two columns: "
    "**physician** and **revenue**."
)

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    # --- Read CSV ---
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as exc:
        st.error(f"Could not read the uploaded file as a CSV: {exc}")
        st.stop()

    # --- Validate & Compute ---
    try:
        average_revenue = compute_average_revenue(df)
    except ValueError as exc:
        st.error(
            f"{exc}\n\n"
            "Please upload a CSV that contains the columns **physician** "
            "and **revenue**, where **revenue** holds numeric values."
        )
        st.stop()

    # --- Display table ---
    st.subheader("Aggregated Results")
    result_df = average_revenue.reset_index()
    result_df.columns = ["Physician", "Average Revenue"]
    st.dataframe(result_df)

    # --- Plot ---
    st.subheader("Chart")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(average_revenue.index, average_revenue.values, color="steelblue")
    ax.set_title("Average Revenue by Physician")
    ax.set_xlabel("Physician")
    ax.set_ylabel("Average Revenue")
    plt.xticks(rotation=45, ha="right")
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    st.pyplot(fig)

    # --- Download button ---
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
