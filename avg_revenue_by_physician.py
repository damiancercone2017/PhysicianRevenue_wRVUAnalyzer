import matplotlib.pyplot as plt
import pandas as pd

# Existing code to calculate average revenue by physician
# Assuming you have a DataFrame `df` with the necessary data

df = pd.read_csv('your_data_file.csv')  # Replace with your actual data file
average_revenue = df.groupby('physician')['revenue'].mean()

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