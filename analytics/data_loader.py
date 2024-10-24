import pymongo
import pandas as pd
from datetime import datetime, timedelta
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_to_mongodb():
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["tfm"]
        logger.info("Successfully connected to MongoDB")
        return db
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        return None

def load_stations_info(db):
    try:
        stations_info = pd.DataFrame(list(db.stations_info.find()))
        logger.info(f"Loaded {len(stations_info)} stations")
        return stations_info
    except Exception as e:
        logger.error(f"Error loading stations info: {e}")
        return pd.DataFrame()

def load_status_data(db, start_date, end_date):
    try:
        # Convert start_date and end_date to strings in ISO format
        start_date_str = start_date.isoformat()
        end_date_str = end_date.isoformat()
        
        logger.info(f"Querying data between {start_date_str} and {end_date_str}")

        # Compare last_reported as strings
        pipeline = [
            {"$match": {
                "last_reported": {
                    "$gte": start_date_str,
                    "$lt": end_date_str
                }
            }},
            {"$project": {
                "station_id": 1,
                "num_bikes_available": 1,
                "num_docks_available": 1,
                "last_reported": 1
            }}
        ]
        status_data = list(db.status_09.aggregate(pipeline))
        logger.info(f"Loaded {len(status_data)} status records")
        if len(status_data) == 0:
            logger.info(f"No data found between {start_date_str} and {end_date_str}")
            min_date = db.status_09.find_one({}, sort=[("last_reported", 1)])
            max_date = db.status_09.find_one({}, sort=[("last_reported", -1)])
            if min_date and max_date:
                logger.info(f"Data range in collection: {min_date['last_reported']} to {max_date['last_reported']}")
            else:
                logger.info("No data found in the collection")
        return pd.DataFrame(status_data)
    except Exception as e:
        logger.error(f"Error loading status data: {e}")
        return pd.DataFrame()
    
def preprocess_data(stations_info, status_data):
    logger.info("Starting data preprocessing")
    
    # Convert last_reported to datetime
    status_data['last_reported'] = pd.to_datetime(status_data['last_reported'], errors='coerce')
    
    # Merge data
    merged_data = pd.merge(status_data, stations_info, on='station_id', how='inner')
    logger.info(f"Merged data shape: {merged_data.shape}")
    
    # Filter non-existent stations
    valid_stations = merged_data['station_id'].unique()
    merged_data = merged_data[merged_data['station_id'].isin(valid_stations)]
    logger.info(f"Data shape after filtering non-existent stations: {merged_data.shape}")
    
    # Add time-based features
    merged_data['hour'] = merged_data['last_reported'].dt.hour
    merged_data['day_of_week'] = merged_data['last_reported'].dt.dayofweek
    merged_data['is_weekend'] = merged_data['day_of_week'].isin([5, 6]).astype(int)
    
    logger.info("Data preprocessing completed")
    return merged_data

def load_sample_data():
    db = connect_to_mongodb()
    if db is None:
        return None, None

    stations_info = load_stations_info(db)
    if stations_info.empty:
        return None, None

    # Filter out skipped stations
    skipped_stations = [16, 38, 44, 55, 59, 93, 169, 172, 181, 407, 453] + list(range(520, 526)) + list(range(527, 537))
    stations_info = stations_info[~stations_info['station_id'].isin(skipped_stations)]

    # Correctly initialize start_date and end_date as datetime objects
    start_date = datetime(2024, 8, 31, 23, 55)
    end_date = datetime(2024, 10, 1, 0, 15)
    
    logger.info(f"Attempting to load status data for one day in September 2024")
    
    status_data = load_status_data(db, start_date, end_date)
    
    if not status_data.empty:
        # Randomly sample 10% of the data
        status_data = status_data.sample(frac=0.1, random_state=42)
        logger.info(f"Successfully loaded and sampled data for one day in September 2024")
        return stations_info, status_data

    return None, None

if __name__ == "__main__":
    stations_info, status_data = load_sample_data()
    if stations_info is not None and status_data is not None:
        merged_data = preprocess_data(stations_info, status_data)
        print(merged_data.head())
        print(merged_data.describe())
    else:
        logger.error("Failed to load sample data")
