import asyncio
from unittest.mock import AsyncMock, patch

from app.tests_pre_start import init, logger


def test_init_successful_connection() -> None:
    db_mock = AsyncMock()

    with (
        patch("app.tests_pre_start.connect_to_mongo", new=AsyncMock()),
        patch("app.tests_pre_start.get_database", return_value=db_mock),
        patch("app.tests_pre_start.close_mongo_connection", new=AsyncMock()),
        patch.object(logger, "info"),
        patch.object(logger, "error"),
        patch.object(logger, "warn"),
    ):
        try:
            asyncio.run(init())
            connection_successful = True
        except Exception:
            connection_successful = False

        assert connection_successful, (
            "The database connection should be successful and not raise an exception."
        )
        db_mock.command.assert_awaited_once_with("ping")
