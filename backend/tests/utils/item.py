import uuid
from datetime import UTC, datetime

from app.models import Item
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string


def create_random_item(db: object) -> Item:
    user = create_random_user(db)
    owner_id = user.id
    title = random_lower_string()
    description = random_lower_string()
    item_id = str(uuid.uuid4())
    db.items.insert_one(
        {
            "_id": item_id,
            "title": title,
            "description": description,
            "owner_id": str(owner_id),
            "created_at": datetime.now(UTC),
        }
    )
    document = db.items.find_one({"_id": item_id})
    if document is None:
        raise RuntimeError("Failed to create item in test database")
    data = document.copy()
    data["id"] = data.pop("_id")
    return Item.model_validate(data)
