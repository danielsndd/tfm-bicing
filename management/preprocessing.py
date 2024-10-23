from config import convert_timestamp_to_iso

def preprocess_data(raw_data):
    processed_data = []
    error_count = 0
    for row in raw_data:
        try:
            # Check if any of the required fields are 'NA'
            if any(row[field] == 'NA' for field in ['station_id', 'num_bikes_available', 'num_docks_available', 'last_reported']):
                raise ValueError("Required field is 'NA'")

            processed_row = {
                "station_id": int(row["station_id"]),
                "capacity": int(row["num_bikes_available"]) + int(row["num_docks_available"]),
                "num_bikes_available": int(row["num_bikes_available"]),
                "num_bikes_available_types": {
                    "mechanical": int(row["num_bikes_available_types.mechanical"]) if row["num_bikes_available_types.mechanical"] != 'NA' else 0,
                    "ebike": int(row["num_bikes_available_types.ebike"]) if row["num_bikes_available_types.ebike"] != 'NA' else 0
                },
                "num_docks_available": int(row["num_docks_available"]),
                "last_reported": convert_timestamp_to_iso(row["last_reported"])
            }
            processed_data.append(processed_row)
        except ValueError as e:
            error_count += 1
            print(f"Error processing row: {row}")
            print(f"Error message: {str(e)}")
    
    print(f"Processed {len(processed_data)} rows successfully.")
    print(f"Encountered {error_count} errors during processing.")
    
    return processed_data
