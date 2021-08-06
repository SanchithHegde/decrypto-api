"""
Script to add initial data to database.
"""

import logging

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.logging_config import logging_dict_config

logging.config.dictConfig(logging_dict_config)
LOGGER = logging.getLogger("initial_data")


def init() -> None:
    """
    Creates initial data in the database.
    """

    db_session = SessionLocal()
    init_db(db_session)


def main() -> None:
    """
    Driver function.
    """

    LOGGER.info("Creating initial data")
    init()
    LOGGER.info("Initial data created")


if __name__ == "__main__":
    main()
