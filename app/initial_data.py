"""
Script to add initial data to database.
"""

import asyncio
import logging

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.logging_config import logging_dict_config

logging.config.dictConfig(logging_dict_config)
LOGGER = logging.getLogger("initial_data")


async def init() -> None:
    """
    Creates initial data in the database.
    """

    async with SessionLocal() as db_session:
        await init_db(db_session)


async def main() -> None:
    """
    Driver function.
    """

    LOGGER.info("Creating initial data")
    await init()
    LOGGER.info("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
