import pandas as pd
import numpy as np

# Define sample Tunisian cities, products, and related attributes
locations = ["Tunis", "Sfax", "Sousse", "Gabès", "Kairouan", "Monastir", "Mahdia", "Bizerte", "Nabeul", "Tozeur"]
products = ["Urea Fertilizer", "Hybrid Corn Seed", "Drip Irrigation Kit", "NPK Fertilizer", "Organic Compost",
            "Ammonium Nitrate", "Herbicide", "Water-Soluble Fertilizer", "Mulching Film", "Date Palm Fertilizer"]
seasons = ["Spring", "Summer", "Fall", "Winter"]
crop_types = ["Wheat", "Corn", "Vegetables", "Olive Trees", "Tomatoes", "Citrus", "Dates", "Strawberries"]
soil_types = ["Loamy", "Sandy", "Clay", "Peaty", "Sandy-Loamy", "Arid"]
weather_conditions = ["Rainy", "Sunny", "Cold", "Windy", "Hot", "Mild", "Very Hot"]

# Generate synthetic data
np.random.seed(42)
data = {
    "Location": np.random.choice(locations, 500),
    "Product": np.random.choice(products, 500),
    "SalesVolume": np.random.randint(50, 800, 500),  # Simulated sales volume from 50 to 800
    "Season": np.random.choice(seasons, 500),
    "CropType": np.random.choice(crop_types, 500),
    "SoilType": np.random.choice(soil_types, 500),
    "WeatherCondition": np.random.choice(weather_conditions, 500)
}

# Create DataFrame
df = pd.DataFrame(data)

# Save the dataset to a CSV file for later use
df.to_csv("tunisian_agriculture_sales_data.csv", index=False)

