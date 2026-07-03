import uuid
from typing import Any

from app.core.db import MongoDatabase
from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, User, UserCreate, UserUpdate


def user_from_document(document: dict[str, Any] | None) -> User | None:
    if document is None:
        return None
    data = document.copy()
    data["id"] = data.pop("_id")
    return User.model_validate(data)


def item_from_document(document: dict[str, Any] | None) -> Item | None:
    if document is None:
        return None
    data = document.copy()
    data["id"] = data.pop("_id")
    return Item.model_validate(data)


async def create_user(*, db: MongoDatabase, user_create: UserCreate) -> User:
    db_obj = User(
        **user_create.model_dump(exclude={"password"}),
        hashed_password=get_password_hash(user_create.password),
    )
    payload = db_obj.model_dump(exclude={"id", "password"})
    payload["_id"] = str(db_obj.id)
    await db.users.insert_one(payload)
    return db_obj


async def update_user(*, db: MongoDatabase, db_user: User, user_in: UserUpdate) -> User:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    if "password" in user_data:
        user_data.pop("password")

    update_data = {**user_data, **extra_data}
    if update_data:
        await db.users.update_one({"_id": str(db_user.id)}, {"$set": update_data})
        updated_document = await db.users.find_one({"_id": str(db_user.id)})
        updated_user = user_from_document(updated_document)
        if updated_user:
            return updated_user
    return db_user


async def get_user_by_email(*, db: MongoDatabase, email: str) -> User | None:
    session_user = await db.users.find_one({"email": email})
    return user_from_document(session_user)


async def get_user_by_id(*, db: MongoDatabase, user_id: str) -> User | None:
    user_document = await db.users.find_one({"_id": user_id})
    return user_from_document(user_document)


# Dummy hash to use for timing attack prevention when user is not found
# This is an Argon2 hash of a random password, used to ensure constant-time comparison
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"


async def authenticate(*, db: MongoDatabase, email: str, password: str) -> User | None:
    db_user = await get_user_by_email(db=db, email=email)
    if not db_user:
        # Prevent timing attacks by running password verification even when user doesn't exist
        # This ensures the response time is similar whether or not the email exists
        verify_password(password, DUMMY_HASH)
        return None
    verified, updated_password_hash = verify_password(password, db_user.hashed_password)
    if not verified:
        return None
    if updated_password_hash:
        await db.users.update_one(
            {"_id": str(db_user.id)},
            {"$set": {"hashed_password": updated_password_hash}},
        )
        db_user.hashed_password = updated_password_hash
    return db_user


async def create_item(
    *, db: MongoDatabase, item_in: ItemCreate, owner_id: uuid.UUID
) -> Item:
    db_item = Item(**item_in.model_dump(), owner_id=owner_id)
    payload = db_item.model_dump(exclude={"id"})
    payload["_id"] = str(db_item.id)
    payload["owner_id"] = str(owner_id)
    await db.items.insert_one(payload)
    return db_item
