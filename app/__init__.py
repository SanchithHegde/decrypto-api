"""
The Decrypto API.
"""

import logging

import structlog

# Enable logging
LOGGER = structlog.getLogger(__name__)

# SQLAlchemy logging
# Set to INFO for logging queries,
# DEBUG for logging query results in addition to queries
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
