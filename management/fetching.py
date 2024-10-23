import os
import csv
from config import RAW_DATA_DIR

def fetch_raw_data(file_path):
    raw_data = []
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            row['file_name'] = os.path.basename(file_path)  # Add file_name to each row
            raw_data.append(row)
    return raw_data
