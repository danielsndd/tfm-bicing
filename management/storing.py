from pymongo import MongoClient
from config import MONGO_URI, DATABASE_NAME, get_collection_name

def store_data(processed_data, file_name):
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection_name = get_collection_name(file_name)
    collection = db[collection_name]
    
    # Insert the processed data into the appropriate collection
    collection.insert_many(processed_data)
    
    print(f"Stored {len(processed_data)} documents in collection: {collection_name}")
    client.close()

