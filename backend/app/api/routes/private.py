from typing import Any
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import DatabaseDep
from app.core.security import get_password_hash
from app.models import (
    User,
    UserPublic,
)

router = APIRouter(tags=["private"], prefix="/private")


class PrivateUserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    is_verified: bool = False


@router.post("/users/", response_model=UserPublic)
async def create_user(user_in: PrivateUserCreate, db: DatabaseDep) -> Any:
    """
    Create a new user.
    """

    user = User(
        id=uuid4(),
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
    )

    payload = user.model_dump(exclude={"id"})
    payload["_id"] = str(user.id)
    await db.users.insert_one(payload)

    return user
