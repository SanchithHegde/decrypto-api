"""
Pre-start script to verify database connectivity.
"""

import logging

from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app import LOGGER
from app.db.session import SessionLocal

# Wait for 5 minutes, stopping for 1 second after an unsuccessful try
MAX_TRIES = 60 * 5
WAIT_SECONDS = 1


@retry(
    stop=stop_after_attempt(MAX_TRIES),
    wait=wait_fixed(WAIT_SECONDS),
    before=before_log(LOGGER, logging.INFO),
    after=after_log(LOGGER, logging.WARN),
)
def verify_db_connectivity() -> None:
    """
    Verify database connectivity.
    """

    try:
        # Try to create a session and execute a statement to check if database is
        # available
        db_session = SessionLocal()
        db_session.execute("SELECT 1;")  # type: ignore

    except Exception as exception:
        LOGGER.exception(exception)
        raise


def main() -> None:
    """
    Driver function.
    """

    LOGGER.info("Initializing service")
    verify_db_connectivity()
    LOGGER.info("Service finished initializing")


if __name__ == "__main__":
    main()
