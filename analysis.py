import pandas as pd
import matplotlib.pyplot as plt

# Load your CSV file
data = pd.read_csv('test_data.csv')  # Replace with your actual file path

# Calculate percentage of correct == True for each category
category_percentages = data.groupby('category')['correct'].apply(lambda x: (x == "TRUE").mean() * 100)

# Plotting
plt.figure(figsize=(10, 6))
category_percentages.plot(kind='bar', color='skyblue')
plt.title('Percentage of Correct == True by Category')
plt.xlabel('Category')
plt.ylabel('Percentage')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
