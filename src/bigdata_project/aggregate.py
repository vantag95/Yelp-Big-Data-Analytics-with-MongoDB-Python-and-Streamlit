from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "bigdata_db"
CLEAN_COLLECTION = "yelp_clean"
AGG_CITY_COLLECTION = "agg_city"
AGG_STATE_COLLECTION = "agg_state"


def aggregate_by_city() -> None:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    clean = db[CLEAN_COLLECTION]
    out = db[AGG_CITY_COLLECTION]

    pipeline = [
        {"$match": {"City": {"$ne": None, "$ne": ""}}},
        {
            "$group": {
                "_id": "$City",
                "avg_rating": {"$avg": "$Rating"},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"count": -1}},
    ]
    results = list(clean.aggregate(pipeline))
    out.delete_many({})
    if results:
        out.insert_many(results)
    print("agg_city documents:", out.count_documents({}))


def aggregate_by_state() -> None:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    clean = db[CLEAN_COLLECTION]
    out = db[AGG_STATE_COLLECTION]

    pipeline = [
        {"$match": {"State": {"$ne": None, "$ne": ""}}},
        {
            "$group": {
                "_id": "$State",
                "avg_rating": {"$avg": "$Rating"},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"count": -1}},
    ]
    results = list(clean.aggregate(pipeline))
    out.delete_many({})
    if results:
        out.insert_many(results)
    print("agg_state documents:", out.count_documents({}))


def main() -> None:
    aggregate_by_city()
    aggregate_by_state()
    print("Aggregations complete.")


if __name__ == "__main__":
    main()
