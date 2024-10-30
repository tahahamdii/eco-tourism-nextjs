from flask import Flask, request, jsonify
import joblib
import numpy as np

# Load the model and label encoders
model = joblib.load("model/sales_prediction_model.joblib")
label_encoders = joblib.load("model/label_encoders.joblib")

# Initialize Flask app
app = Flask(__name__)

# Define the predict endpoint
@app.route('/predict', methods=['POST'])
def predict():
    # Parse JSON input
    data = request.get_json()

    # Extract input values from JSON
    location = data.get("Location")
    product = data.get("Product")
    season = data.get("Season")
    crop_type = data.get("CropType")
    soil_type = data.get("SoilType")
    weather_condition = data.get("WeatherCondition")

    # Encode categorical values using the loaded label encoders
    try:
        location_encoded = label_encoders["Location"].transform([location])[0]
        product_encoded = label_encoders["Product"].transform([product])[0]
        season_encoded = label_encoders["Season"].transform([season])[0]
        crop_type_encoded = label_encoders["CropType"].transform([crop_type])[0]
        soil_type_encoded = label_encoders["SoilType"].transform([soil_type])[0]
        weather_encoded = label_encoders["WeatherCondition"].transform([weather_condition])[0]
    except KeyError as e:
        return jsonify({"error": f"Invalid input: {str(e)}"}), 400

    # Create a numpy array with the encoded inputs
    input_data = np.array([[location_encoded, product_encoded, season_encoded,
                            crop_type_encoded, soil_type_encoded, weather_encoded]])

    # Predict sales volume
    prediction = model.predict(input_data)
    predicted_sales_volume = prediction[0]

    # Return the prediction as JSON
    return jsonify({"predicted_sales_volume": predicted_sales_volume})

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
