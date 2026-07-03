import uuid
from datetime import UTC, datetime

from fastapi.encoders import jsonable_encoder
from pwdlib.hashers.bcrypt import BcryptHasher

from app.core.security import get_password_hash, verify_password
from app.models import User
from tests.utils.utils import random_email, random_lower_string


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
    password_hash: str,
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
            "hashed_password": password_hash,
            "created_at": datetime.now(UTC),
        }
    )
    user = _user_from_document(db.users.find_one({"_id": user_id}))
    if user is None:
        raise RuntimeError("Failed to create user in test database")
    return user


def test_create_user(db: object) -> None:
    email = random_email()
    password = random_lower_string()
    user = _insert_user(db, email=email, password_hash=get_password_hash(password))
    assert user.email == email
    assert hasattr(user, "hashed_password")


def test_authenticate_user(db: object) -> None:
    email = random_email()
    password = random_lower_string()
    _insert_user(db, email=email, password_hash=get_password_hash(password))

    user = db.users.find_one({"email": email})
    assert user is not None
    verified, _ = verify_password(password, user["hashed_password"])
    assert verified


def test_not_authenticate_user(db: object) -> None:
    email = random_email()
    password = random_lower_string()
    user = db.users.find_one({"email": email})
    assert user is None


def test_check_if_user_is_active(db: object) -> None:
    email = random_email()
    password = random_lower_string()
    user = _insert_user(db, email=email, password_hash=get_password_hash(password))
    assert user.is_active is True


def test_check_if_user_is_active_inactive(db: object) -> None:
    email = random_email()
    password = random_lower_string()
    user = _insert_user(
        db,
        email=email,
        password_hash=get_password_hash(password),
        is_active=False,
    )
    assert user.is_active is False


def test_check_if_user_is_superuser(db: object) -> None:
    email = random_email()
    password = random_lower_string()
    user = _insert_user(
        db,
        email=email,
        password_hash=get_password_hash(password),
        is_superuser=True,
    )
    assert user.is_superuser is True


def test_check_if_user_is_superuser_normal_user(db: object) -> None:
    username = random_email()
    password = random_lower_string()
    user = _insert_user(db, email=username, password_hash=get_password_hash(password))
    assert user.is_superuser is False


def test_get_user(db: object) -> None:
    password = random_lower_string()
    username = random_email()
    user = _insert_user(
        db,
        email=username,
        password_hash=get_password_hash(password),
        is_superuser=True,
    )
    user_2 = _user_from_document(db.users.find_one({"_id": str(user.id)}))
    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


def test_update_user(db: object) -> None:
    password = random_lower_string()
    email = random_email()
    user = _insert_user(
        db,
        email=email,
        password_hash=get_password_hash(password),
        is_superuser=True,
    )
    new_password = random_lower_string()
    db.users.update_one(
        {"_id": str(user.id)},
        {"$set": {"hashed_password": get_password_hash(new_password)}},
    )
    user_2 = _user_from_document(db.users.find_one({"_id": str(user.id)}))
    assert user_2
    assert user.email == user_2.email
    verified, _ = verify_password(new_password, user_2.hashed_password)
    assert verified


def test_authenticate_user_with_bcrypt_upgrades_to_argon2(db: object) -> None:
    email = random_email()
    password = random_lower_string()

    bcrypt_hasher = BcryptHasher()
    bcrypt_hash = bcrypt_hasher.hash(password)
    assert bcrypt_hash.startswith("$2")

    user = _insert_user(db, email=email, password_hash=bcrypt_hash)

    verified, updated_hash = verify_password(password, user.hashed_password)
    assert verified
    assert updated_hash is not None

    db.users.update_one(
        {"_id": str(user.id)},
        {"$set": {"hashed_password": updated_hash}},
    )
    reloaded = _user_from_document(db.users.find_one({"_id": str(user.id)}))
    assert reloaded
    assert reloaded.hashed_password.startswith("$argon2")
