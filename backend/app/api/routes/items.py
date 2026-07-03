import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import CurrentUser, DatabaseDep
from app.models import ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, Message

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ItemsPublic)
async def read_items(
    db: DatabaseDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve items.
    """

    if current_user.is_superuser:
        count = await db.items.count_documents({})
        cursor = db.items.find().sort("created_at", -1).skip(skip).limit(limit)
    else:
        count = await db.items.count_documents({"owner_id": str(current_user.id)})
        cursor = (
            db.items.find({"owner_id": str(current_user.id)})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )

    items = [crud.item_from_document(document) async for document in cursor]
    items_public = [
        ItemPublic.model_validate(item.model_dump())
        for item in items
        if item is not None
    ]
    return ItemsPublic(data=items_public, count=count)


@router.get("/{id}", response_model=ItemPublic)
async def read_item(db: DatabaseDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get item by ID.
    """
    item = crud.item_from_document(await db.items.find_one({"_id": str(id)}))
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return item


@router.post("/", response_model=ItemPublic)
async def create_item(
    *, db: DatabaseDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """
    Create new item.
    """
    return await crud.create_item(db=db, item_in=item_in, owner_id=current_user.id)


@router.put("/{id}", response_model=ItemPublic)
async def update_item(
    *,
    db: DatabaseDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: ItemUpdate,
) -> Any:
    """
    Update an item.
    """
    item = crud.item_from_document(await db.items.find_one({"_id": str(id)}))
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_dict = item_in.model_dump(exclude_unset=True)
    if update_dict:
        await db.items.update_one({"_id": str(id)}, {"$set": update_dict})
        updated_document = await db.items.find_one({"_id": str(id)})
        item = crud.item_from_document(updated_document) or item
    return item


@router.delete("/{id}")
async def delete_item(
    db: DatabaseDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    item = crud.item_from_document(await db.items.find_one({"_id": str(id)}))
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await db.items.delete_one({"_id": str(id)})
    return Message(message="Item deleted successfully")
