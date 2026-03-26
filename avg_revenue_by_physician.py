import matplotlib.pyplot as plt
import pandas as pd


def compute_average_revenue(df):
    """Return a Series of average revenue grouped by physician.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame that must contain 'physician' and 'revenue' columns.

    Returns
    -------
    pandas.Series
        Mean revenue per physician, indexed by physician name.

    Raises
    ------
    ValueError
        If required columns are missing or 'revenue' column is non-numeric.
    """
    missing = [c for c in ('physician', 'revenue') if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required column(s): {', '.join(missing)}. "
            "The CSV must contain 'physician' and 'revenue' columns."
        )
    if not pd.api.types.is_numeric_dtype(df['revenue']):
        raise ValueError(
            "The 'revenue' column must contain numeric values."
        )
    return df.groupby('physician')['revenue'].mean()


if __name__ == '__main__':
    import sys

    csv_path = sys.argv[1] if len(sys.argv) > 1 else 'your_data_file.csv'
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(
            f"Error: '{csv_path}' not found. "
            "Please create the file or pass a CSV path as an argument:\n"
            "  python avg_revenue_by_physician.py path/to/your_data.csv"
        )
        sys.exit(1)
    average_revenue = compute_average_revenue(df)

    # Print existing tabular output
    print(average_revenue)

    # Plotting the line graph
    try:
        plt.figure(figsize=(10, 5))
        plt.plot(average_revenue.index, average_revenue.values, marker='o')
        plt.title('Average Revenue by Physician')
        plt.xlabel('Physician')
        plt.ylabel('Average Revenue')
        plt.xticks(rotation=45)
        plt.grid()
        plt.savefig('avg_revenue_by_physician_line.png')
        plt.show()
    except ImportError:
        print('Matplotlib is not installed. Skipping plot display.')