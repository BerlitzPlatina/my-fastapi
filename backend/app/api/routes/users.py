import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app import crud
from app.api.deps import CurrentUser, DatabaseDep, get_current_active_superuser
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import (
    Message,
    UpdatePassword,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.utils import generate_new_account_email, send_email

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
async def read_users(db: DatabaseDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """
    count = await db.users.count_documents({})
    cursor = db.users.find().sort("created_at", -1).skip(skip).limit(limit)
    users = [crud.user_from_document(document) async for document in cursor]
    users_public = [
        UserPublic.model_validate(user.model_dump())
        for user in users
        if user is not None
    ]
    return UsersPublic(data=users_public, count=count)


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
)
async def create_user(*, db: DatabaseDep, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    user = await crud.get_user_by_email(db=db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    user = await crud.create_user(db=db, user_create=user_in)
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email,
            username=user_in.email,
            password=user_in.password,
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return user


@router.patch("/me", response_model=UserPublic)
async def update_user_me(
    *, db: DatabaseDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """
    if user_in.email:
        existing_user = await crud.get_user_by_email(db=db, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    user_data = user_in.model_dump(exclude_unset=True)
    if user_data:
        await db.users.update_one({"_id": str(current_user.id)}, {"$set": user_data})
        updated = await db.users.find_one({"_id": str(current_user.id)})
        current_user = crud.user_from_document(updated) or current_user
    return current_user


@router.patch("/me/password", response_model=Message)
async def update_password_me(
    *, db: DatabaseDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    verified, _ = verify_password(body.current_password, current_user.hashed_password)
    if not verified:
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400,
            detail="New password cannot be the same as the current one",
        )

    hashed_password = get_password_hash(body.new_password)
    await db.users.update_one(
        {"_id": str(current_user.id)},
        {"$set": {"hashed_password": hashed_password}},
    )
    return Message(message="Password updated successfully")


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.delete("/me", response_model=Message)
async def delete_user_me(db: DatabaseDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Super users are not allowed to delete themselves",
        )
    await db.items.delete_many({"owner_id": str(current_user.id)})
    await db.users.delete_one({"_id": str(current_user.id)})
    return Message(message="User deleted successfully")


@router.post("/signup", response_model=UserPublic)
async def register_user(db: DatabaseDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user = await crud.get_user_by_email(db=db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user_create = UserCreate.model_validate(
        {
            "email": user_in.email,
            "password": user_in.password,
            "full_name": user_in.full_name,
        }
    )
    return await crud.create_user(db=db, user_create=user_create)


@router.get("/{user_id}", response_model=UserPublic)
async def read_user_by_id(
    user_id: uuid.UUID, db: DatabaseDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    user = await crud.get_user_by_id(db=db, user_id=str(user_id))
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
async def update_user(
    *,
    db: DatabaseDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """
    db_user = await crud.get_user_by_id(db=db, user_id=str(user_id))
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user_in.email:
        existing_user = await crud.get_user_by_email(db=db, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    return await crud.update_user(db=db, db_user=db_user, user_in=user_in)


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
async def delete_user(
    db: DatabaseDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """
    Delete a user.
    """
    user = await crud.get_user_by_id(db=db, user_id=str(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        raise HTTPException(
            status_code=403,
            detail="Super users are not allowed to delete themselves",
        )
    await db.items.delete_many({"owner_id": str(user_id)})
    await db.users.delete_one({"_id": str(user_id)})
    return Message(message="User deleted successfully")
