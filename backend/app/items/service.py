import uuid
from typing import Any

from app.core.db import MongoDatabase
from app.models import Item, ItemCreate, ItemUpdate, User


def item_from_document(document: dict[str, Any] | None) -> Item | None:
    if document is None:
        return None
    data = document.copy()
    data["id"] = data.pop("_id")
    return Item.model_validate(data)


async def list_items(
    *, db: MongoDatabase, current_user: User, skip: int, limit: int
) -> tuple[list[Item], int]:
    if current_user.is_superuser:
        count = await db.items.count_documents({})
        cursor = db.items.find().sort("created_at", -1).skip(skip).limit(limit)
    else:
        filter_query = {"owner_id": str(current_user.id)}
        count = await db.items.count_documents(filter_query)
        cursor = db.items.find(filter_query).sort("created_at", -1).skip(skip).limit(limit)

    items = [item_from_document(document) async for document in cursor]
    return [item for item in items if item is not None], count


async def create_item(*, db: MongoDatabase, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item(**item_in.model_dump(), owner_id=owner_id)
    payload = db_item.model_dump(exclude={"id"})
    payload["_id"] = str(db_item.id)
    payload["owner_id"] = str(owner_id)
    await db.items.insert_one(payload)
    return db_item


async def get_item_by_id(*, db: MongoDatabase, item_id: uuid.UUID) -> Item | None:
    return item_from_document(await db.items.find_one({"_id": str(item_id)}))


async def update_item(*, db: MongoDatabase, item_id: uuid.UUID, item_in: ItemUpdate) -> Item | None:
    item = await get_item_by_id(db=db, item_id=item_id)
    if not item:
        return None

    update_dict = item_in.model_dump(exclude_unset=True)
    if update_dict:
        await db.items.update_one({"_id": str(item_id)}, {"$set": update_dict})
        updated_document = await db.items.find_one({"_id": str(item_id)})
        return item_from_document(updated_document) or item
    return item


async def delete_item(*, db: MongoDatabase, item_id: uuid.UUID) -> None:
    await db.items.delete_one({"_id": str(item_id)})

