import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

def perform_time_series_analysis(data, station_id):
    station_data = data[data['station_id'] == station_id].set_index('last_reported')
    
    # Resample data to hourly frequency
    hourly_data = station_data['num_bikes_available'].resample('H').mean()
    
    # Fit ARIMA model
    model = ARIMA(hourly_data, order=(1, 1, 1))
    results = model.fit()
    
    # Make predictions
    forecast = results.forecast(steps=24)
    
    return forecast

