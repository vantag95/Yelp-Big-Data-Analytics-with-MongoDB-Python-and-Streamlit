import pandas as pd
from pymongo import MongoClient

# Change this to your real file name and extension
DATA_PATH = "yelp_database.csv"  # or "yelp_data.csv"

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "bigdata_db"
RAW_COLLECTION = "yelp_raw"


def main() -> None:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    coll = db[RAW_COLLECTION]

    # Read Excel or CSV
    if DATA_PATH.endswith(".xlsx"):
        df = pd.read_excel(DATA_PATH)
    else:
        df = pd.read_csv(DATA_PATH)

    print("Loaded rows from file:", len(df))

    # Convert DataFrame rows to list of dicts
    records = df.to_dict(orient="records")

    # Replace existing raw data
    coll.delete_many({})
    if records:
        coll.insert_many(records)

    print("Raw row count in Mongo:", coll.count_documents({}))


if __name__ == "__main__":
    main()
