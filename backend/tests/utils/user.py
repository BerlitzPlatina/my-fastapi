import uuid
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import get_password_hash
from app.models import User
from tests.utils.utils import random_email, random_lower_string


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> dict[str, str]:
    data = {"username": email, "password": password}

    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def _user_from_document(document: dict | None) -> User | None:
    if document is None:
        return None
    data = document.copy()
    data["id"] = data.pop("_id")
    return User.model_validate(data)


def _insert_user(
    db: object,
    *,
    email: str,
    password: str,
    full_name: str | None = None,
    is_superuser: bool = False,
    is_active: bool = True,
) -> User:
    user_id = str(uuid.uuid4())
    db.users.insert_one(
        {
            "_id": user_id,
            "email": email,
            "is_active": is_active,
            "is_superuser": is_superuser,
            "full_name": full_name,
            "hashed_password": get_password_hash(password),
            "created_at": datetime.now(UTC),
        }
    )
    user = _user_from_document(db.users.find_one({"_id": user_id}))
    if user is None:
        raise RuntimeError("Failed to create user in test database")
    return user


def create_random_user(db: object) -> User:
    email = random_email()
    password = random_lower_string()
    return _insert_user(db, email=email, password=password)


def authentication_token_from_email(
    *, client: TestClient, email: str, db: object
) -> dict[str, str]:
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    password = random_lower_string()
    user = db.users.find_one({"email": email})
    if not user:
        _insert_user(db, email=email, password=password)
    else:
        db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"hashed_password": get_password_hash(password)}},
        )

    return user_authentication_headers(client=client, email=email, password=password)
