from pymongo import MongoClient
from pymongo.database import Database
from app.config import settings
from app.models import MetadataRecord
import logging

logger = logging.getLogger(__name__)

_client: MongoClient | None = None
_db: Database | None = None

# Establish MongoDB connection and create indexes.
def connect_db() -> None:
    global _client, _db
    _client = MongoClient(
        settings.mongo_uri,
        serverSelectionTimeoutMS=5000,
    )
    _db = _client[settings.mongo_db_name]

    # Create unique index on URL for fast lookups
    _db.metadata.create_index("url", unique=True)
    logger.info("Connected to MongoDB and ensured indexes.")

# Close MongoDB connection
def close_db() -> None:
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
        logger.info("MongoDB connection closed.")


def get_db() -> Database:
   
    if _db is None:
        raise RuntimeError("Database not initialised. Call connect_db() first.")
    return _db

# Look up a metadata record by URL
def find_metadata_by_url(url: str) -> dict | None:
    db = get_db()
    return db.metadata.find_one({"url": url}, {"_id": 0})

# Insert or update a metadata record.
def upsert_metadata(record: MetadataRecord) -> None:
    db = get_db()
    doc = record.model_dump()
    db.metadata.update_one(
        {"url": record.url},
        {"$set": doc},
        upsert=True,
    )
    logger.info("Upserted metadata for %s", record.url)
