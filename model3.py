from flask import Flask, request, jsonify
import joblib
import numpy as np
import datetime

# Load the model and label encoders
model = joblib.load("model/best_selling_product_model.joblib")
label_encoders = joblib.load("model/label_encoderss.joblib")

# Initialize Flask app
app = Flask(__name__)

# Define the prediction endpoint
@app.route('/predict', methods=['POST'])
def predict():
    # Get data from request body
    data = request.get_json()
    city = data.get("City")
    date = data.get("Date")

    # Parse the date and extract month and season
    try:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
        month = date_obj.month
        # Map month to season
        season_mapping = {
            1: "Winter", 2: "Winter", 12: "Winter",
            3: "Spring", 4: "Spring", 5: "Spring",
            6: "Summer", 7: "Summer", 8: "Summer",
            9: "Fall", 10: "Fall", 11: "Fall"
        }
        season = season_mapping[month]
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    # Encode inputs
    try:
        city_encoded = label_encoders["City"].transform([city])[0]
        season_encoded = label_encoders["Season"].transform([season])[0]
    except KeyError as e:
        return jsonify({"error": f"Invalid input: {str(e)}"}), 400

    # Prepare data for prediction
    input_data = np.array([[city_encoded, month, season_encoded]])

    # Make the prediction
    product_encoded = model.predict(input_data)[0]
    product = label_encoders["Product"].inverse_transform([product_encoded])[0]

    # Return the prediction
    return jsonify({"best_selling_product": product})

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
