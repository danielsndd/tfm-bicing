import os
from datetime import datetime
import time

# MongoDB configuration
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "tfm"

# Raw data directory
RAW_DATA_DIR = os.path.join("raw-data", "raw-stations-status")

# Mapping of month names to collection names
MONTH_COLLECTIONS = {
    "Gener": "status_jan",
    "Febrer": "status_feb",
    "Marc": "status_mar",
    "Abril": "status_apr",
    "Maig": "status_may",
    "Juny": "status_jun",
    "Juliol": "status_jul",
    "Agost": "status_aug",
    "Setembre": "status_sep",
    "Octubre": "status_oct",
    "Novembre": "status_nov",
    "Desembre": "status_dec"
}

# Function to get the collection name based on the file name
def get_collection_name(file_name):
    parts = file_name.split("_")
    if len(parts) > 2:
        month = parts[2]
        return MONTH_COLLECTIONS.get(month, "unknown")
    return "unknown"

# Function to convert timestamp to ISO date
def convert_timestamp_to_iso(timestamp):
    return datetime.fromtimestamp(int(timestamp)).isoformat()

def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        processing_time = end_time - start_time
        print(f"Processing time: {processing_time:.2f} seconds")
        return result, processing_time
    return wrapper
