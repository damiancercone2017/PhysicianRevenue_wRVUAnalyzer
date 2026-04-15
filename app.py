import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np

# Page config
st.set_page_config(page_title="Physician Dashboard", layout="wide")

# Clean professional styling
st.markdown("""
    <style>
        .main { background-color: #f8f9fa; }
        h1 { color: #1a3c5e; }
        h2, h3 { color: #2c5f8a; }
        .stDownloadButton > button {
            background-color: #1a3c5e;
            color: white;
            border-radius: 6px;
        }
    </style>
""", unsafe_allow_html=True)

# Professional color palette
PALETTE = ["#1a3c5e", "#2c7bb6", "#5aafe0", "#a8d5f5", "#d9edf7"]

st.title("Physician Revenue & wRVU Dashboard")
st.markdown("---")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    # Read the data
    data = pd.read_csv(uploaded_file, delimiter=',')

    # Coerce the revenue and wRVU columns
    if 'revenue' in data.columns:
        data['revenue'] = data['revenue'].replace({'\\$': '', ',': ''}, regex=True).astype(float)
    if 'wRVU' in data.columns:
        data['wRVU'] = pd.to_numeric(data['wRVU'], errors='coerce')

    # Validate for bad rows
    bad_rows = data[data[['revenue', 'wRVU']].isnull().any(axis=1)]
    if not bad_rows.empty:
        st.warning("Bad Rows Found:")
        st.dataframe(bad_rows)

    # Drop bad rows
    data = data.dropna(subset=['revenue', 'wRVU'])

    # Per-physician averages
    averages = data.groupby('physician').agg({'revenue': 'mean', 'wRVU': 'mean'}).reset_index()
    averages.columns = ['Physician', 'Average Revenue', 'Average wRVU']

    # --- FILTERS ---
    st.sidebar.header("Filters")
    all_physicians = sorted(averages['Physician'].unique().tolist())
    selected_physicians = st.sidebar.multiselect(
        "Select Physicians", options=all_physicians, default=all_physicians
    )

    min_rev, max_rev = float(averages['Average Revenue'].min()), float(averages['Average Revenue'].max())
    revenue_range = st.sidebar.slider(
        "Average Revenue Range",
        min_value=min_rev, max_value=max_rev,
        value=(min_rev, max_rev),
        format="$%.0f"
    )

    min_wrvu, max_wrvu = float(averages['Average wRVU'].min()), float(averages['Average wRVU'].max())
    wrvu_range = st.sidebar.slider(
        "Average wRVU Range",
        min_value=min_wrvu, max_value=max_wrvu,
        value=(min_wrvu, max_wrvu)
    )

    # Apply filters
    filtered = averages[
        (averages['Physician'].isin(selected_physicians)) &
        (averages['Average Revenue'] >= revenue_range[0]) &
        (averages['Average Revenue'] <= revenue_range[1]) &
        (averages['Average wRVU'] >= wrvu_range[0]) &
        (averages['Average wRVU'] <= wrvu_range[1])
    ]

    # --- SUMMARY METRICS ---
    st.subheader("Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Physicians Shown", len(filtered))
    col2.metric("Avg Revenue", f"${filtered['Average Revenue'].mean():,.0f}")
    col3.metric("Avg wRVU", f"{filtered['Average wRVU'].mean():,.1f}")
    st.markdown("---")

    # --- PHYSICIAN AVERAGES TABLE ---
    st.subheader("Physician Averages")
    st.dataframe(
        filtered.style.format({"Average Revenue": "${:,.2f}", "Average wRVU": "{:,.2f}"}),
        use_container_width=True
    )
    st.markdown("---")

    # --- CHART STYLING HELPER ---
    def style_axis(ax, title, xlabel="", ylabel=""):
        ax.set_title(title, fontsize=13, fontweight='bold', color='#1a3c5e', pad=12)
        ax.set_xlabel(xlabel, fontsize=10, color='#444')
        ax.set_ylabel(ylabel, fontsize=10, color='#444')
        ax.tick_params(colors='#444')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#cccccc')
        ax.spines['bottom'].set_color('#cccccc')
        ax.set_facecolor('#f8f9fa')

    # --- BAR CHARTS ---
    st.subheader("Revenue & wRVU by Physician")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.patch.set_facecolor('#f8f9fa')

    # Revenue bar chart
    bars1 = sns.barplot(x='Physician', y='Average Revenue', data=filtered,
                        palette=PALETTE, ax=axes[0], edgecolor='white', linewidth=0.8)
    for bar in bars1.patches:
        bars1.annotate(f"${bar.get_height():,.0f}",
                       (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                       ha='center', va='bottom', fontsize=8, color='#1a3c5e', fontweight='bold')
    axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    style_axis(axes[0], 'Average Revenue per Physician', ylabel='Average Revenue')
    axes[0].tick_params(axis='x', rotation=45)

    # wRVU bar chart
    bars2 = sns.barplot(x='Physician', y='Average wRVU', data=filtered,
                        palette=PALETTE, ax=axes[1], edgecolor='white', linewidth=0.8)
    for bar in bars2.patches:
        bars2.annotate(f"{bar.get_height():,.1f}",
                       (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                       ha='center', va='bottom', fontsize=8, color='#1a3c5e', fontweight='bold')
    style_axis(axes[1], 'Average wRVU per Physician', ylabel='Average wRVU')
    axes[1].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    st.pyplot(fig)
    st.markdown("---")

    # --- SCATTER PLOT ---
    st.subheader("Revenue vs wRVU")
    fig2, ax = plt.subplots(figsize=(8, 5))
    fig2.patch.set_facecolor('#f8f9fa')

    sns.scatterplot(data=filtered, x='Average Revenue', y='Average wRVU',
                    color='#2c7bb6', s=120, edgecolor='#1a3c5e', linewidth=0.8, ax=ax)

    # Label each point with physician name
    for _, row in filtered.iterrows():
        ax.annotate(row['Physician'], (row['Average Revenue'], row['Average wRVU']),
                    textcoords="offset points", xytext=(8, 4), fontsize=8, color='#444')

    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    style_axis(ax, 'Average Revenue vs Average wRVU', xlabel='Average Revenue', ylabel='Average wRVU')

    plt.tight_layout()
    st.pyplot(fig2)
    st.markdown("---")

    # --- DISTRIBUTION CHARTS ---
    st.subheader("Revenue Distribution")
    filtered_data = data[data['physician'].isin(selected_physicians)]
    fig3, axes3 = plt.subplots(1, 2, figsize=(14, 5))
    fig3.patch.set_facecolor('#f8f9fa')

    sns.histplot(filtered_data['revenue'], bins=20, kde=True, ax=axes3[0],
                 color='#2c7bb6', edgecolor='white', linewidth=0.5)
    axes3[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    style_axis(axes3[0], 'Revenue Distribution', xlabel='Revenue', ylabel='Count')

    sns.boxplot(x=filtered_data['revenue'], ax=axes3[1],
                color='#5aafe0', linewidth=1.2,
                flierprops=dict(marker='o', markerfacecolor='#1a3c5e', markersize=5))
    axes3[1].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    style_axis(axes3[1], 'Revenue Box Plot', xlabel='Revenue')

    plt.tight_layout()
    st.pyplot(fig3)
    st.markdown("---")

    # --- DOWNLOAD ---
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button("⬇ Download Filtered Averages CSV", csv, "updated_averages.csv", "text/csv")

else:
    st.info("Please upload a CSV file to get started.")
