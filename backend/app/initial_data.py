import asyncio
import logging

from app import crud
from app.core.config import settings
from app.core.db import close_mongo_connection, connect_to_mongo, get_database
from app.models import UserCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# abcdef

async def init() -> None:
    await connect_to_mongo()
    db = get_database()
    user = await crud.get_user_by_email(db=db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        await crud.create_user(db=db, user_create=user_in)
    await close_mongo_connection()


def main() -> None:
    logger.info("Creating initial data")
    asyncio.run(init())
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
