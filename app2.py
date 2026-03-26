#!/usr/bin/env python3
"""
CSV Upload Agent

A simple Gradio web agent that lets users upload a CSV file,
preview its contents, and view basic summary statistics.

Usage:
    python app2.py
"""

import io

import gradio as gr
import pandas as pd


def process_csv(file) -> tuple[str, str, str]:
    """
    Accept an uploaded CSV file and return:
      - a preview of the first 10 rows (as an HTML table),
      - basic shape/column info,
      - descriptive statistics.
    """
    if file is None:
        return "No file uploaded.", "", ""

    try:
        df = pd.read_csv(file.name)
    except Exception as exc:
        return f"Error reading file: {exc}", "", ""

    if df.empty:
        return "The uploaded CSV file contains no data.", "", ""

    # --- Preview ---
    preview = df.head(10).to_html(index=False, border=0, classes="preview-table")

    # --- Info ---
    buf = io.StringIO()
    df.info(buf=buf)
    info_text = (
        f"Rows: {df.shape[0]:,}   |   Columns: {df.shape[1]}\n\n"
        f"Column names:\n  " + "\n  ".join(df.columns.tolist()) + "\n\n"
        f"dtypes:\n" + buf.getvalue()
    )

    # --- Statistics ---
    stats_html = df.describe(include="all").to_html(border=0, classes="stats-table")

    return preview, info_text, stats_html


with gr.Blocks(title="CSV Upload Agent") as demo:
    gr.Markdown("# CSV Upload Agent")
    gr.Markdown("Upload a CSV file to preview its contents and view summary statistics.")

    with gr.Row():
        file_input = gr.File(label="Upload CSV", file_types=[".csv"])

    upload_btn = gr.Button("Analyze", variant="primary")

    with gr.Tab("Preview (first 10 rows)"):
        preview_output = gr.HTML()

    with gr.Tab("Info"):
        info_output = gr.Textbox(label="Dataset Info", lines=20, interactive=False)

    with gr.Tab("Statistics"):
        stats_output = gr.HTML()

    upload_btn.click(
        fn=process_csv,
        inputs=[file_input],
        outputs=[preview_output, info_output, stats_output],
    )

if __name__ == "__main__":
    demo.launch()
