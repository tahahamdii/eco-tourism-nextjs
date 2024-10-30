import numpy as np
import pandas as pd


def generate_soil_data(n_samples=1000):
    np.random.seed(42)

    soil_ph = np.random.uniform(5.0, 8.5, n_samples)  # pH levels between 5 and 8.5
    moisture = np.random.uniform(10, 50, n_samples)  # Moisture level as percentage
    nitrogen = np.random.uniform(0, 100, n_samples)  # Nitrogen content (mg/kg)
    phosphorus = np.random.uniform(0, 100, n_samples)  # Phosphorus content (mg/kg)
    potassium = np.random.uniform(0, 100, n_samples)  # Potassium content (mg/kg)
    organic_matter = np.random.uniform(1, 10, n_samples)  # Organic matter percentage


    soil_fertility_score = (
                                   0.2 * (soil_ph - 5) +
                                   0.5 * (moisture / 50) +
                                   0.3 * (nitrogen / 100) +
                                   0.4 * (phosphorus / 100) +
                                   0.4 * (potassium / 100) +
                                   0.3 * (organic_matter / 10)
                           ) * 100

    # Making sure fertility scores are in range 0-100
    soil_fertility_score = np.clip(soil_fertility_score, 0, 100)

    # Creating the DataFrame
    data = {
        'soil_ph': soil_ph,
        'moisture': moisture,
        'nitrogen': nitrogen,
        'phosphorus': phosphorus,
        'potassium': potassium,
        'organic_matter': organic_matter,
        'soil_fertility_score': soil_fertility_score
    }

    df = pd.DataFrame(data)
    return df


# Generate 1000 samples
soil_data = generate_soil_data(1000)

# Save the dataset as CSV for later use
soil_data.to_csv('soil_fertility_data.csv', index=False)

print(soil_data.head())  # Show the first few rows
