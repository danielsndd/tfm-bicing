import os
import sys
from fetching import fetch_raw_data
from preprocessing import preprocess_data
from storing import store_data
from config import timing_decorator

@timing_decorator
def process_file(file_name, raw_data):
    print(f"Processing file: {file_name}")
    
    # Filter raw data for the current file
    file_data = [row for row in raw_data if row["file_name"] == os.path.basename(file_name)]
    
    # Preprocess the data
    processed_data = preprocess_data(file_data)
    
    # Store the processed data if not empty
    if processed_data:
        store_data(processed_data, file_name)
    else:
        print("No data to store after processing.")

def main():
    # Check if a file name is provided as a command-line argument
    if len(sys.argv) < 2:
        print("Please provide a CSV file name as an argument.")
        return

    file_name = sys.argv[1]
    
    # Use the provided file path directly
    file_path = file_name

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    # Fetch raw data for the specified file
    raw_data = fetch_raw_data(file_path)
    
    if not raw_data:
        print("No data fetched from the file.")
        return
    
    # Process the file
    _, processing_time = process_file(file_name, raw_data)
    
    print(f"Data processing completed for {file_name}.")
    print(f"Total processing time: {processing_time:.2f} seconds")

if __name__ == "__main__":
    main()
