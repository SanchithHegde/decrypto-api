"""
The Decrypto API.
"""

import structlog
from structlog.stdlib import AsyncBoundLogger

# Enable logging
LOGGER: AsyncBoundLogger = structlog.getLogger(__name__)
