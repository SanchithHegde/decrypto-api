"""
The Decrypto API.
"""

import logging
from logging import LogRecord

import coloredlogs  # type: ignore
from starlette_context import context
from starlette_context.errors import ContextDoesNotExistError


class AppFilter(logging.Filter):  # pylint: disable=too-few-public-methods
    """
    A filter to set the request ID for each log record, if available.
    """

    def filter(self, record: LogRecord) -> bool:
        try:
            request_id: str = context["X-Request-ID"]

        except ContextDoesNotExistError:
            # Outside a request-response cycle, request ID will be unavailable
            request_id = "Request ID unavailable"

        record.request_id = request_id  # type: ignore

        return True


# Enable logging
LOGGER = logging.getLogger(__name__)
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] %(message)s"
LOGGER.addFilter(AppFilter())
coloredlogs.install(level=LOG_LEVEL, logger=LOGGER, fmt=LOG_FORMAT, milliseconds=True)

# SQLAlchemy logging
# Set to INFO for logging queries,
# DEBUG for logging query results in addition to queries
coloredlogs.install(
    level=logging.WARNING, logger=logging.getLogger("sqlalchemy.engine"), fmt=LOG_FORMAT
)
