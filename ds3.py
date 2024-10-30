import pandas as pd
import numpy as np

# Define sample Tunisian cities, products, months, and seasons
cities = ["Tunis", "Sfax", "Sousse", "Gabès", "Kairouan", "Monastir", "Mahdia", "Bizerte", "Nabeul", "Tozeur"]
products = ["Fertilizer A", "Organic Compost", "Soil Enhancer B", "Potash Fertilizer", "Nitrogen Supplement",
            "Mulch Sheets", "Seed Enhancer", "Soil Conditioner", "Plant Growth Regulator", "Water Retainer"]
months = np.arange(1, 13)  # Months from 1 (January) to 12 (December)
seasons = ["Winter", "Spring", "Summer", "Fall"]

# Map months to seasons
season_mapping = {
    1: "Winter", 2: "Winter", 12: "Winter",
    3: "Spring", 4: "Spring", 5: "Spring",
    6: "Summer", 7: "Summer", 8: "Summer",
    9: "Fall", 10: "Fall", 11: "Fall"
}

# Generate synthetic data
np.random.seed(42)
data = {
    "City": np.random.choice(cities, 500),
    "Product": np.random.choice(products, 500),
    "SalesVolume": np.random.randint(50, 1000, 500),  # Simulated sales volume from 50 to 1000
    "Month": np.random.choice(months, 500),
}
# Convert months to seasons
data["Season"] = [season_mapping[month] for month in data["Month"]]

# Create DataFrame
df = pd.DataFrame(data)

# Save dataset to a CSV file
df.to_csv("tunisian_product_sales_data.csv", index=False)