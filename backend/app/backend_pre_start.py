import asyncio
import logging

from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.db import close_mongo_connection, connect_to_mongo, get_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init() -> None:
    try:
        await connect_to_mongo()
        db = get_database()
        await db.command("ping")
        await close_mongo_connection()
    except Exception as e:
        logger.error(e)
        raise e


def main() -> None:
    logger.info("Initializing service")
    asyncio.run(init())
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
