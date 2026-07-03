import uuid
from datetime import UTC, datetime
from unittest.mock import patch

from fastapi.testclient import TestClient
from pwdlib.hashers.bcrypt import BcryptHasher

from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.utils import generate_password_reset_token
from tests.utils.user import user_authentication_headers
from tests.utils.utils import random_email, random_lower_string


def _insert_user(
    db: object,
    *,
    email: str,
    password_hash: str,
    full_name: str | None = None,
    is_superuser: bool = False,
    is_active: bool = True,
) -> str:
    user_id = str(uuid.uuid4())
    db.users.insert_one(
        {
            "_id": user_id,
            "email": email,
            "is_active": is_active,
            "is_superuser": is_superuser,
            "full_name": full_name,
            "hashed_password": password_hash,
            "created_at": datetime.now(UTC),
        }
    )
    return user_id


def test_get_access_token(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]


def test_get_access_token_incorrect_password(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": "incorrect",
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    assert r.status_code == 400


def test_use_access_token(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/login/test-token",
        headers=superuser_token_headers,
    )
    result = r.json()
    assert r.status_code == 200
    assert "email" in result


def test_recovery_password(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    with (
        patch("app.core.config.settings.SMTP_HOST", "smtp.example.com"),
        patch("app.core.config.settings.SMTP_USER", "admin@example.com"),
    ):
        email = "test@example.com"
        r = client.post(
            f"{settings.API_V1_STR}/password-recovery/{email}",
            headers=normal_user_token_headers,
        )
        assert r.status_code == 200
        assert r.json() == {
            "message": "If that email is registered, we sent a password recovery link"
        }


def test_recovery_password_user_not_exits(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    email = "jVgQr@example.com"
    r = client.post(
        f"{settings.API_V1_STR}/password-recovery/{email}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 200
    assert r.json() == {
        "message": "If that email is registered, we sent a password recovery link"
    }


def test_reset_password(client: TestClient, db: object) -> None:
    email = random_email()
    password = random_lower_string()
    new_password = random_lower_string()

    _insert_user(
        db,
        email=email,
        full_name="Test User",
        password_hash=get_password_hash(password),
    )
    token = generate_password_reset_token(email=email)
    headers = user_authentication_headers(client=client, email=email, password=password)
    data = {"new_password": new_password, "token": token}

    r = client.post(
        f"{settings.API_V1_STR}/reset-password/",
        headers=headers,
        json=data,
    )

    assert r.status_code == 200
    assert r.json() == {"message": "Password updated successfully"}

    user = db.users.find_one({"email": email})
    assert user is not None
    verified, _ = verify_password(new_password, user["hashed_password"])
    assert verified


def test_reset_password_invalid_token(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"new_password": "changethis", "token": "invalid"}
    r = client.post(
        f"{settings.API_V1_STR}/reset-password/",
        headers=superuser_token_headers,
        json=data,
    )
    response = r.json()

    assert "detail" in response
    assert r.status_code == 400
    assert response["detail"] == "Invalid token"


def test_login_with_bcrypt_password_upgrades_to_argon2(
    client: TestClient, db: object
) -> None:
    email = random_email()
    password = random_lower_string()

    bcrypt_hasher = BcryptHasher()
    bcrypt_hash = bcrypt_hasher.hash(password)
    assert bcrypt_hash.startswith("$2")

    user_id = _insert_user(db, email=email, password_hash=bcrypt_hash)

    login_data = {"username": email, "password": password}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    assert r.status_code == 200
    tokens = r.json()
    assert "access_token" in tokens

    updated_user = db.users.find_one({"_id": user_id})
    assert updated_user is not None
    assert updated_user["hashed_password"].startswith("$argon2")

    verified, updated_hash = verify_password(password, updated_user["hashed_password"])
    assert verified
    assert updated_hash is None


def test_login_with_argon2_password_keeps_hash(
    client: TestClient, db: object
) -> None:
    email = random_email()
    password = random_lower_string()

    argon2_hash = get_password_hash(password)
    assert argon2_hash.startswith("$argon2")

    user_id = _insert_user(db, email=email, password_hash=argon2_hash)

    login_data = {"username": email, "password": password}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    assert r.status_code == 200
    tokens = r.json()
    assert "access_token" in tokens

    updated_user = db.users.find_one({"_id": user_id})
    assert updated_user is not None
    assert updated_user["hashed_password"] == argon2_hash
    assert updated_user["hashed_password"].startswith("$argon2")
