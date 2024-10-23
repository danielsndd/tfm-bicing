import requests
import pandas as pd
import schedule
import time
from datetime import datetime, timedelta
from pymongo import MongoClient, ASCENDING
import logging
import pytz

# Set up logging to a file that can be accessed from the VM
logging.basicConfig(filename='/home/danys/output.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Set the time zone to Europe/Madrid (Barcelona)
tz = pytz.timezone('Europe/Madrid')

# API details
url_status = 'https://opendata-ajuntament.barcelona.cat/data/dataset/estat-estacions-bicing/resource/1b215493-9e63-4a12-8980-2d7e0fa19f85/download/recurs.json'
url_info = 'https://opendata-ajuntament.barcelona.cat/data/dataset/informacio-estacions-bicing/resource/f60e9291-5aaa-417d-9b91-612a9de800aa/download/recurs.json'
token = '2ca37380d6d8b99b65c69d116eb583b03f3f6ef31e0d9d4822a12dd8ccc89417'

headers = {
    'Authorization': token,
    'Accept': 'application/json'
}

# MongoDB connection
client = MongoClient('mongodb+srv://danielsnd:asDxCdsan21@tfm.l0wwv.mongodb.net/tfm?retryWrites=true&w=majority')
db = client['tfm']

# Updated collections
stations_info_collection = db['stations_info']
stations_status_collection = db['stations_status']
bicing_data_collection = db['bicing_data']

# Ensure indexes for unique identifiers to optimize lookup
bicing_data_collection.create_index(
    [
        ("station_id", ASCENDING),
        ("last_reported", ASCENDING),
        ("num_bikes_available_types.mechanical", ASCENDING),
        ("num_bikes_available_types.ebike", ASCENDING)
    ],
    unique=True
)

stations_status_collection.create_index(
    [
        ("station_id", ASCENDING),
        ("last_reported", ASCENDING),
        ("num_bikes_available_types.mechanical", ASCENDING),
        ("num_bikes_available_types.ebike", ASCENDING)
    ],
    unique=True
)

def fetch_data():
    try:
        response_status = requests.get(url_status, headers=headers, timeout=10)
        response_info = requests.get(url_info, headers=headers, timeout=10)

        if response_status.status_code == 200 and response_info.status_code == 200:
            data_status = response_status.json()
            data_info = response_info.json()

            df_status = pd.DataFrame(data_status['data']['stations'])
            df_info = pd.DataFrame(data_info['data']['stations'])

            df_combined = pd.merge(df_status, df_info, on='station_id')

            # Convert 'last_reported' to datetime in the Barcelona timezone
            df_combined['last_reported'] = pd.to_datetime(df_combined['last_reported'], unit='s').dt.tz_localize('UTC').dt.tz_convert(tz)

            # Ensure 'num_bikes_available_types' is correctly parsed
            df_combined['num_bikes_available_types'] = df_combined['num_bikes_available_types'].apply(
                lambda x: x if isinstance(x, dict) else eval(x) if isinstance(x, str) else {'mechanical': 0, 'ebike': 0}
            )

            # Add 'last_fetched' column in Barcelona time zone with manual +2 hour adjustment
            df_combined['last_fetched'] = pd.to_datetime(datetime.now(tz) + timedelta(hours=2))

            # Create 'unique_id' for filtering duplicates
            df_combined['unique_id'] = df_combined.apply(
                lambda row: f"{row['station_id']}_{row['last_reported'].timestamp()}_{row['num_bikes_available_types'].get('ebike', 0)}_{row['num_bikes_available_types'].get('mechanical', 0)}",
                axis=1
            )

            logging.info("Data fetched successfully.")
            return df_combined
        else:
            logging.error(f"Failed to fetch data. Status codes: {response_status.status_code}, {response_info.status_code}")
            return None
    except requests.Timeout:
        logging.error("Connection timed out while fetching data from the API.")
        return None
    except requests.RequestException as e:
        logging.error(f"An error occurred while making the request: {e}")
        return None

def fetch_data_with_retry(retries=3, delay=5):
    """Attempt to fetch data with retries in case of failure."""
    for attempt in range(retries):
        data = fetch_data()
        if data is not None and not data.empty:
            return data  # Successfully fetched data
        logging.warning(f"Attempt {attempt+1} failed, retrying in {delay} seconds...")
        time.sleep(delay)

    logging.error("Failed to fetch data after multiple retries.")
    return None

def store_data(df):
    """Store fetched data into MongoDB."""
    inserted_bicing = 0
    inserted_status = 0

    for _, row in df.iterrows():
        unique_id = row['unique_id']

        # Check if the unique_id already exists in 'bicing_data'
        bicing_exists = bicing_data_collection.find_one({"unique_id": unique_id})
        status_exists = stations_status_collection.find_one({"unique_id": unique_id})

        if not bicing_exists and not status_exists:
            # Bicing Data (all variables)
            bicing_data = row.to_dict()
            bicing_data['unique_id'] = unique_id  # Add unique_id
            bicing_data_collection.insert_one(bicing_data)
            inserted_bicing += 1

            # Stations Info (static data)
            station_info = {
                'station_id': row['station_id'],
                'name': row['name'],
                'lat': row['lat'],
                'lon': row['lon'],
                'altitude': row['altitude'],
                'cross_street': row.get('cross_street', ''),  # Use get() in case this field doesn't exist
                'post_code': row['post_code']
            }
            stations_info_collection.update_one(
                {'station_id': row['station_id']},
                {'$set': station_info},
                upsert=True
            )

            # Stations Status (dynamic data)
            station_status = {
                'station_id': row['station_id'],
                'capacity': row['capacity'],
                'num_bikes_available': row['num_bikes_available'],
                'num_bikes_available_types': row['num_bikes_available_types'],
                'num_docks_available': row['num_docks_available'],
                'last_reported': row['last_reported'],
                'last_fetched': row['last_fetched'],
                'unique_id': unique_id  # Add unique_id
            }
            stations_status_collection.insert_one(station_status)
            inserted_status += 1
        else:
            # Duplicate found, skip insertion
            continue

    logging.info(f"Inserted {inserted_bicing} new documents into 'bicing_data'.")
    logging.info(f"Inserted {inserted_status} new documents into 'stations_status'.")

def fetch_and_store_data():
    df = fetch_data_with_retry()
    if df is not None:
        store_data(df)
    else:
        logging.error("No data to store.")

# Schedule the job to run every 5 minutes
schedule.every(5).minutes.do(fetch_and_store_data)

if __name__ == "__main__":
    logging.info(f"Script started at {datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')}.")
    while True:
        schedule.run_pending()
        time.sleep(1)