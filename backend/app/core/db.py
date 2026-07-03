from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient  # type: ignore[import-not-found]

from app.core.config import settings

type MongoDocument = dict[str, Any]
type MongoDatabase = Any
type MongoClient = Any

client: MongoClient | None = None
database: MongoDatabase | None = None


async def connect_to_mongo() -> None:
    global client, database
    if client is not None and database is not None:
        return

    client = AsyncIOMotorClient(str(settings.MONGODB_URI))
    database = client[settings.MONGODB_DB]
    await database.command("ping")
    await ensure_indexes()


def get_database() -> MongoDatabase:
    if database is None:
        raise RuntimeError("MongoDB is not initialized")
    return database


async def close_mongo_connection() -> None:
    global client, database
    if client is not None:
        client.close()
    client = None
    database = None


async def ensure_indexes() -> None:
    db = get_database()
    await db.users.create_index("email", unique=True)
    await db.users.create_index("created_at")
    await db.items.create_index("owner_id")
    await db.items.create_index("created_at")
