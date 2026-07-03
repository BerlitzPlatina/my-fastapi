from fastapi.testclient import TestClient

from app.core.config import settings


def test_create_user(client: TestClient, db: object) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/private/users/",
        json={
            "email": "pollo@listo.com",
            "password": "password123",
            "full_name": "Pollo Listo",
        },
    )

    assert r.status_code == 200

    data = r.json()

    user = db.users.find_one({"_id": data["id"]})

    assert user
    assert user["email"] == "pollo@listo.com"
    assert user["full_name"] == "Pollo Listo"
