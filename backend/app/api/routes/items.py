import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, DatabaseDep
from app.models import ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, Message
from app.items.service import (
    create_item as create_item_record,
    delete_item as delete_item_record,
    get_item_by_id,
    list_items,
    update_item as update_item_record,
)

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ItemsPublic)
async def read_items(
    db: DatabaseDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve items.
    """

    items, count = await list_items(db=db, current_user=current_user, skip=skip, limit=limit)
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
    item = await get_item_by_id(db=db, item_id=id)
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
    return await create_item_record(db=db, item_in=item_in, owner_id=current_user.id)


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
    item = await get_item_by_id(db=db, item_id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    updated_item = await update_item_record(db=db, item_id=id, item_in=item_in)
    return updated_item or item


@router.delete("/{id}")
async def delete_item(
    db: DatabaseDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    item = await get_item_by_id(db=db, item_id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await delete_item_record(db=db, item_id=id)
    return Message(message="Item deleted successfully")
