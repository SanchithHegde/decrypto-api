"""
The Decrypto API.
"""

import logging

import coloredlogs  # type: ignore

# Enable logging
LOGGER = logging.getLogger(__name__)
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
coloredlogs.install(level=LOG_LEVEL, logger=LOGGER, fmt=LOG_FORMAT)

# SQLAlchemy logging
# Set to INFO for logging queries,
# DEBUG for logging query results in addition to queries
coloredlogs.install(
    level=logging.WARN, logger=logging.getLogger("sqlalchemy.engine"), fmt=LOG_FORMAT
)
