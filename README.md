# Test0326
Test on Thursday - create a simple analyzer agent

## Average Revenue by Physician — Streamlit App

An interactive web app that lets you upload a CSV and instantly see average
revenue broken down by physician.

### Prerequisites

* Python 3.9 or later

### Quick start

```bash
# 1. Clone the repo (if you haven't already)
git clone https://github.com/damiancercone2017/Test0326.git
cd Test0326

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the app
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

### Using the app

1. Click **Browse files** and select a CSV file.
2. The CSV must contain at minimum two columns: `physician` and `revenue`.
3. The app will display:
   - A table of average revenue per physician.
   - A bar chart visualising the results.
   - A **Download aggregated CSV** button.

### Running the original script (CLI)

```bash
# Uses 'your_data_file.csv' by default, or pass a path as the first argument
python avg_revenue_by_physician.py path/to/your_data.csv
```
