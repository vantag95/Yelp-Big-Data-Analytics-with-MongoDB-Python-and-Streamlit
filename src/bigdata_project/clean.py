from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, field_validator
from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "bigdata_db"
RAW_COLLECTION = "yelp_raw"
CLEAN_COLLECTION = "yelp_clean"


class YelpRecord(BaseModel):
    ID: Optional[int] = None
    Time_GMT: Optional[datetime] = None
    Phone: Optional[str] = None
    Organization: Optional[str] = None
    OLF: Optional[str] = None
    Rating: Optional[float] = None
    NumberReview: Optional[int] = None
    Category: Optional[str] = None
    Country: Optional[str] = None
    CountryCode: Optional[str] = None
    State: Optional[str] = None
    City: Optional[str] = None
    Street: Optional[str] = None
    Building: Optional[str] = None

    @field_validator("Organization", "Category", "Country", "State", "City", "Street", "Building", mode="before")
    @classmethod
    def normalize_text(cls, v: Any):
        if v is None:
            return None
        return str(v).strip().title()

    @field_validator("Rating", mode="before")
    @classmethod
    def rating_to_float(cls, v: Any):
        if v is None or v == "":
            return 0.0
        try:
            return float(v)
        except Exception:
            return 0.0

    @field_validator("NumberReview", mode="before")
    @classmethod
    def reviews_to_int(cls, v: Any):
        if v is None or v == "":
            return 0
        try:
            return int(v)
        except Exception:
            return 0

    @field_validator("Time_GMT", mode="before")
    @classmethod
    def parse_time(cls, v: Any):
        if v is None or v == "":
            return None
        if isinstance(v, datetime):
            return v
        # Try ISO and common formats; ignore if it fails
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y %H:%M", "%m/%d/%Y"):
            try:
                return datetime.strptime(str(v), fmt)
            except Exception:
                continue
        try:
            return datetime.fromisoformat(str(v))
        except Exception:
            return None


def main() -> None:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    raw = db[RAW_COLLECTION]
    clean = db[CLEAN_COLLECTION]

    docs = list(raw.find({}))
    print("Raw docs read from Mongo:", len(docs))

    clean_docs = []

    for d in docs:
        d.pop("_id", None)
        try:
            rec = YelpRecord(**d)
        except Exception:
            # if something is still bad, skip it
            continue

        clean_docs.append(rec.model_dump())

    clean.delete_many({})
    if clean_docs:
        clean.insert_many(clean_docs)

    print("Clean row count in Mongo:", clean.count_documents({}))


if __name__ == "__main__":
    main()
