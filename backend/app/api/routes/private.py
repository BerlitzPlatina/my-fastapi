from typing import Any
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import DatabaseDep
from app.models import UserCreate, UserPublic
from app.users.service import create_user as create_user_record

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

    return await create_user_record(
        db=db,
        user_create=UserCreate(
            email=user_in.email,
            password=user_in.password,
            full_name=user_in.full_name,
        ),
    )
