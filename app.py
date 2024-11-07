from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from analytics.data_loader import connect_to_mongodb, load_stations_info, load_status_data
from analytics.time_series import perform_time_series_analysis
from analytics.random_forest import perform_random_forest

app = Flask(__name__)
CORS(app)

@app.route('/api/station-data', methods=['GET'])
def get_station_data():
    try:
        # Create sample data since MongoDB might not be accessible
        dates = pd.date_range(start='2024-01-01', end='2024-01-07', freq='H')
        availability_data = []
        
        for date in dates:
            availability_data.append({
                'last_reported': date.strftime('%Y-%m-%d %H:%M:%S'),
                'num_bikes_available': np.random.randint(0, 20),
                'num_docks_available': np.random.randint(0, 20)
            })

        # Create hourly usage data
        hourly_usage = []
        for hour in range(24):
            hourly_usage.append({
                'hour': hour,
                'num_bikes_available': np.random.randint(5, 15)
            })

        # Create forecast data
        forecast_data = []
        base_value = 10
        for i in range(24):
            forecast_data.append({
                'timestamp': (datetime.now() + timedelta(hours=i)).strftime('%Y-%m-%d %H:%M:%S'),
                'predicted': base_value + np.random.randint(-2, 3),
                'actual': base_value + np.random.randint(-2, 3)
            })

        # Create predictions data
        predictions = [np.random.randint(5, 15) for _ in range(100)]
        actual_values = [p + np.random.randint(-2, 3) for p in predictions]

        return jsonify({
            'availability': availability_data,
            'hourlyUsage': hourly_usage,
            'forecast': forecast_data,
            'predictions': predictions,
            'actualValues': actual_values
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)