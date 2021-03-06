"""
Pre-start script run before tests, to verify database connectivity.
"""

import asyncio
import logging

from sqlalchemy import text
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.logging_config import logging_dict_config
from app.tests.conftest import TestingSessionLocal

# Wait for 5 minutes, stopping for 1 second after an unsuccessful try
MAX_TRIES = 60 * 5
WAIT_SECONDS = 1

logging.config.dictConfig(logging_dict_config)
LOGGER = logging.getLogger("tests_pre_start")


@retry(
    stop=stop_after_attempt(MAX_TRIES),
    wait=wait_fixed(WAIT_SECONDS),
    before=before_log(LOGGER, logging.INFO),
    after=after_log(LOGGER, logging.WARN),
)
async def verify_db_connectivity() -> None:
    """
    Verify database connectivity.
    """

    try:
        # Try to create a session and execute a statement to check if database is
        # available
        async with TestingSessionLocal() as db_session:
            await db_session.execute(text("SELECT 1;"))

        LOGGER.info("Database connection successful")

    except Exception as exception:
        LOGGER.exception(exception)
        raise


async def main() -> None:
    """
    Driver function.
    """

    LOGGER.info("Initializing service")
    await verify_db_connectivity()
    LOGGER.info("Service finished initializing")


if __name__ == "__main__":
    asyncio.run(main())
