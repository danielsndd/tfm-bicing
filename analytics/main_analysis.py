from data_loader import load_sample_data, preprocess_data
from visualizations import plot_station_availability, plot_hourly_usage, create_station_map, plot_weekly_heatmap
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def prepare_features(merged_data):
    features = merged_data[['hour', 'day_of_week', 'is_weekend', 'station_id']]
    features = pd.get_dummies(features, columns=['station_id'])
    return features

def train_prediction_model(merged_data):
    X = prepare_features(merged_data)
    y_bikes = merged_data['num_bikes_available']
    y_docks = merged_data['num_docks_available']
    
    X_train, X_test, y_bikes_train, y_bikes_test, y_docks_train, y_docks_test = train_test_split(
        X, y_bikes, y_docks, test_size=0.2, random_state=42)
    
    rf_bikes = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_docks = RandomForestRegressor(n_estimators=100, random_state=42)
    
    rf_bikes.fit(X_train, y_bikes_train)
    rf_docks.fit(X_train, y_docks_train)
    
    bikes_pred = rf_bikes.predict(X_test)
    docks_pred = rf_docks.predict(X_test)
    
    bikes_mse = mean_squared_error(y_bikes_test, bikes_pred)
    bikes_r2 = r2_score(y_bikes_test, bikes_pred)
    docks_mse = mean_squared_error(y_docks_test, docks_pred)
    docks_r2 = r2_score(y_docks_test, docks_pred)
    
    logger.info(f"Bikes prediction - MSE: {bikes_mse:.2f}, R2: {bikes_r2:.2f}")
    logger.info(f"Docks prediction - MSE: {docks_mse:.2f}, R2: {docks_r2:.2f}")
    
    return rf_bikes, rf_docks

def main():
    stations_info, status_sample = load_sample_data()
    if stations_info is None or status_sample is None:
        logger.error("Failed to load sample data")
        return
    
    merged_data = preprocess_data(stations_info, status_sample)
    
    # Visualizations
    station_id = merged_data['station_id'].iloc[0]
    availability_plot = plot_station_availability(merged_data, station_id)
    availability_plot.show()
    
    hourly_usage_chart = plot_hourly_usage(merged_data)
    hourly_usage_chart.save('hourly_usage.html')
    
    station_map = create_station_map(stations_info)
    station_map.save('station_map.html')
    
    weekly_heatmap = plot_weekly_heatmap(merged_data)
    weekly_heatmap.show()
    
    # Train prediction models
    rf_bikes, rf_docks = train_prediction_model(merged_data)
    
    # Example prediction
    example_features = prepare_features(merged_data.iloc[:1])
    predicted_bikes = rf_bikes.predict(example_features)
    predicted_docks = rf_docks.predict(example_features)
    
    logger.info(f"Predicted bikes available: {predicted_bikes[0]:.2f}")
    logger.info(f"Predicted docks available: {predicted_docks[0]:.2f}")

if __name__ == "__main__":
    main()
