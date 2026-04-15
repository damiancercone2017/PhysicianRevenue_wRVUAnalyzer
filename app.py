import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Function to handle input and preprocessing
def process_data(file_path):
    # Read the data
    data = pd.read_csv(file_path, delimiter=',')
    # Coerce the revenue and wRVU columns
    if 'revenue' in data.columns:
        data['revenue'] = data['revenue'].replace({'\$': '', ',': ''}, regex=True).astype(float)
    if 'wRVU' in data.columns:
        data['wRVU'] = pd.to_numeric(data['wRVU'], errors='coerce')

    # Validate for bad rows
    bad_rows = data[data[['revenue', 'wRVU']].isnull().any(axis=1)]
    if not bad_rows.empty:
        print('Bad Rows:')
        print(bad_rows)

    # Drop bad rows for further calculations
    data = data.dropna(subset=['revenue', 'wRVU'])

    # Per-physician averages
    averages = data.groupby('physician').agg({'revenue': 'mean', 'wRVU': 'mean'}).reset_index()
    averages.columns = ['Physician', 'Average Revenue', 'Average wRVU']

    # Show averages
    print(averages)

    # Plotting
    plt.figure(figsize=(12, 6))

    # Bar chart for average revenue
    plt.subplot(1, 3, 1)
    sns.barplot(x='Physician', y='Average Revenue', data=averages)
    plt.title('Average Revenue per Physician')
    plt.xticks(rotation=90)

    # Bar chart for average wRVU
    plt.subplot(1, 3, 2)
    sns.barplot(x='Physician', y='Average wRVU', data=averages)
    plt.title('Average wRVU per Physician')
    plt.xticks(rotation=90)

    # Scatter plot for average revenue vs wRVU
    plt.subplot(1, 3, 3)
    sns.scatterplot(data=averages, x='Average Revenue', y='Average wRVU')
    plt.title('Average Revenue vs Average wRVU')
    plt.xlabel('Average Revenue')
    plt.ylabel('Average wRVU')

    plt.tight_layout()
    plt.show()

    # Histogram and box plot (ensure they work)
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    sns.histplot(data['revenue'], bins=20, kde=True)
    plt.title('Revenue Distribution')

    plt.subplot(1, 2, 2)
    sns.boxplot(x=data['revenue'])
    plt.title('Revenue Box Plot')
    plt.tight_layout()
    plt.show()

    # Update CSV download to include new columns
    averages.to_csv('updated_averages.csv', index=False)

# Call the function (add your file path)
# process_data('your_file_path_here.csv')

