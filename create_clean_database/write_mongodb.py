import os
import json
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")

# Base folder where all your datasets live
base_folder = "data"

# Loop through each dataset folder under 'data/'
for folder_name in os.listdir(base_folder):
    dataset_path = os.path.join(base_folder, folder_name)
    # print(dataset_path)

    if os.path.isdir(dataset_path):
        if dataset_path.endswith("_json"):
            db = client[folder_name.replace("_json", "")]  # DB name: adventure_works, bike_store, etc.
            # print(db)
            print(f"\n Using database: {db.name}")

            # Loop through JSON files in this dataset folder
            for file_name in os.listdir(dataset_path):
                if file_name.endswith(".json"):
                    collection_name = file_name.replace('.json', '')
                    file_path = os.path.join(dataset_path, file_name)

                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)

                            if isinstance(data, list):
                                db[collection_name].insert_many(data)
                            elif isinstance(data, dict):
                                db[collection_name].insert_one(data)
                            else:
                                print(f"Skipped {file_name}: invalid format")

                            print(f"Inserted into collection: {collection_name}")

                    except Exception as e:
                        print(f"Error loading {file_path}: {e}")

print("\n🎉 All JSON files loaded into their respective MongoDB databases!")
