import uuid
from datetime import UTC, datetime
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient

from app.core.config import settings
from app.core.security import get_password_hash
from app.main import app
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers


def _cleanup_collections(db: MongoClient) -> None:
    db.items.delete_many({})
    db.users.delete_many({})


def _ensure_superuser(db: MongoClient) -> None:
    superuser = db.users.find_one({"email": settings.FIRST_SUPERUSER})
    if superuser is not None:
        return
    db.users.insert_one(
        {
            "_id": str(uuid.uuid4()),
            "email": settings.FIRST_SUPERUSER,
            "is_active": True,
            "is_superuser": True,
            "full_name": None,
            "hashed_password": get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            "created_at": datetime.now(UTC),
        }
    )


@pytest.fixture(scope="session")
def client() -> Generator[TestClient]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session", autouse=True)
def db(client: TestClient) -> Generator[MongoClient]:
    mongo_client = MongoClient(str(settings.MONGODB_URI))
    database = mongo_client[settings.MONGODB_DB]
    _cleanup_collections(database)
    _ensure_superuser(database)
    yield database
    _cleanup_collections(database)
    mongo_client.close()


@pytest.fixture(scope="session")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="session")
def normal_user_token_headers(
    client: TestClient, db: MongoClient
) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )
